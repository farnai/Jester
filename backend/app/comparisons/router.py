import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
import psycopg
from psycopg.types.json import Jsonb

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.astrology.natal import recalculate_user_astrology
from backend.app.compatibility.engine import CompatibilityEngine
from backend.app.core.database import get_db
from backend.app.core.errors import ForbiddenException, JesterAPIException, PrivacySafeNotFoundException
from backend.app.comparisons.models import CompareRequest, StructuredCompatibilityResponse
from backend.app.connections.router import get_canonical_pair
from backend.app.interpretation.engine import interpretation_engine

router = APIRouter(tags=["compare"])
compatibility_engine = CompatibilityEngine()


@router.post("/compare", response_model=StructuredCompatibilityResponse)
async def compare_users(
    payload: CompareRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> StructuredCompatibilityResponse:
    """
    Compares authenticated user with target user.
    Enforces that active accepted connection exists and users are not blocked.
    Derives identity strictly from JWT.sub.
    """
    if current_user.id == payload.target_user_id:
        raise JesterAPIException(
            status_code=400,
            error_code="self_comparison_not_allowed",
            message="Cannot compare a user with themselves.",
        )

    user_a, user_b = get_canonical_pair(current_user.id, payload.target_user_id)

    with db.cursor() as cur:
        # Check active connection
        cur.execute("SELECT public.has_active_connection(%s, %s) as is_active;", (user_a, user_b))
        res = cur.fetchone()
        if not res or not res["is_active"]:
            raise ForbiddenException("Active connection required to view compatibility")

        # Check block status
        cur.execute("SELECT public.is_user_blocked(%s, %s) as is_blocked;", (current_user.id, payload.target_user_id))
        block_res = cur.fetchone()
        if block_res and block_res["is_blocked"]:
            raise PrivacySafeNotFoundException("User not found or unavailable.")

        # Load current birth data versions and precision
        cur.execute(
            "SELECT user_id, data_version, birth_time_precision FROM public.birth_data WHERE user_id IN (%s, %s);",
            (user_a, user_b),
        )
        rows = cur.fetchall()
        if len(rows) < 2:
            raise JesterAPIException(
                status_code=404,
                error_code="birth_data_missing",
                message="Both users must have completed birth data onboarding.",
            )

        birth_info = {r["user_id"]: r for r in rows}
        ver_a = birth_info[user_a]["data_version"]
        ver_b = birth_info[user_b]["data_version"]
        prec_a = birth_info[user_a]["birth_time_precision"]
        prec_b = birth_info[user_b]["birth_time_precision"]

        # Check existing cached result
        engine_ver = "synastry-v1.0.0"
        cur.execute(
            "SELECT * FROM public.compatibility_results WHERE user_a_id = %s AND user_b_id = %s;",
            (user_a, user_b),
        )
        existing = cur.fetchone()

        pair_seed = f"{user_a}:{user_b}:{ver_a}:{ver_b}"
        if (
            existing
            and existing["user_a_birth_data_version"] == ver_a
            and existing["user_b_birth_data_version"] == ver_b
            and existing["engine_version"] == engine_ver
        ):
            # Derive data quality for cached response
            is_unknown = prec_a == "unknown" or prec_b == "unknown"
            is_approx = prec_a == "approximate" or prec_b == "approximate"
            confidence = 0.75 if is_unknown else (0.85 if is_approx else 1.0)
            data_quality = {
                "time_precision": "unknown" if is_unknown else ("approximate" if is_approx else "exact"),
                "confidence": confidence,
                "houses_used": not is_unknown,
                "ascendant_used": not is_unknown,
            }

            raw_signals = existing["signals"] if isinstance(existing["signals"], list) else []
            enriched_signals = interpretation_engine.resolve_signals(raw_signals, seed=pair_seed)
            cached_score = float(existing["score"])
            primary_interpretation = interpretation_engine.get_primary_relationship_interpretation(
                cached_score, raw_signals, seed=pair_seed
            )
            cached_dimensions = existing.get("dimensions") if isinstance(existing.get("dimensions"), dict) else {}
            deep_payload = interpretation_engine.build_deep_analysis_payload(
                score=cached_score,
                signals=raw_signals,
                evidence_trace=existing.get("evidence_trace") or [],
                confidence=confidence,
                seed=pair_seed,
            )

            cached_starters = interpretation_engine.resolve_conversation_starters(
                raw_signals, seed=pair_seed
            ) or (existing["conversation_starters"] if isinstance(existing["conversation_starters"], list) else [])

            return StructuredCompatibilityResponse(
                id=existing["id"],
                target_user_id=payload.target_user_id,
                score=cached_score,
                dimensions=cached_dimensions,
                signals=enriched_signals,
                interpretation=primary_interpretation,
                best_topics=existing["best_topics"] if isinstance(existing["best_topics"], list) else [],
                conversation_starters=cached_starters,
                data_quality=data_quality,
                deep_analysis=deep_payload,
                engine_version=existing["engine_version"],
                calculated_at=existing["calculated_at"],
            )

        # Cache miss or stale: Load or calculate astro_private placements
        cur.execute(
            "SELECT * FROM public.astro_private WHERE user_id IN (%s, %s);",
            (user_a, user_b),
        )
        astro_rows = {r["user_id"]: r for r in cur.fetchall()}

        if user_a not in astro_rows or astro_rows[user_a] is None or astro_rows[user_a].get("source_birth_data_version") != ver_a:
            recalculate_user_astrology(user_a, db)
            cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (user_a,))
            astro_rows[user_a] = cur.fetchone()

        if user_b not in astro_rows or astro_rows[user_b] is None or astro_rows[user_b].get("source_birth_data_version") != ver_b:
            recalculate_user_astrology(user_b, db)
            cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (user_b,))
            astro_rows[user_b] = cur.fetchone()

        # Run deterministic Synastry V1 Engine
        calc_result = compatibility_engine.calculate(
            person_a_id=user_a,
            person_a_version=ver_a,
            person_a_precision=prec_a,
            person_a_placements=astro_rows[user_a],
            person_b_id=user_b,
            person_b_version=ver_b,
            person_b_precision=prec_b,
            person_b_placements=astro_rows[user_b],
        )

        starters = interpretation_engine.resolve_conversation_starters(
            calc_result.signals, seed=pair_seed
        )

        # Upsert result into public.compatibility_results
        cur.execute(
            """
            INSERT INTO public.compatibility_results (
                user_a_id, user_b_id, user_a_birth_data_version, user_b_birth_data_version,
                engine_version, score, dimensions, signals, best_topics, conversation_starters,
                evidence_trace, calculated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
            ) ON CONFLICT (user_a_id, user_b_id) DO UPDATE SET
                user_a_birth_data_version = EXCLUDED.user_a_birth_data_version,
                user_b_birth_data_version = EXCLUDED.user_b_birth_data_version,
                engine_version = EXCLUDED.engine_version,
                score = EXCLUDED.score,
                dimensions = EXCLUDED.dimensions,
                signals = EXCLUDED.signals,
                best_topics = EXCLUDED.best_topics,
                conversation_starters = EXCLUDED.conversation_starters,
                evidence_trace = EXCLUDED.evidence_trace,
                calculated_at = now()
            RETURNING *;
            """,
            (
                user_a,
                user_b,
                ver_a,
                ver_b,
                calc_result.engine_version,
                calc_result.score,
                Jsonb(calc_result.dimensions),
                Jsonb(calc_result.signals),
                Jsonb(calc_result.best_topics),
                Jsonb(starters),
                Jsonb(calc_result.evidence_trace),
            ),
        )
        saved_row = cur.fetchone()

        enriched_signals = interpretation_engine.resolve_signals(calc_result.signals, seed=pair_seed)
        primary_interpretation = interpretation_engine.get_primary_relationship_interpretation(
            calc_result.score, calc_result.signals, seed=pair_seed
        )
        deep_payload = interpretation_engine.build_deep_analysis_payload(
            score=calc_result.score,
            signals=calc_result.signals,
            evidence_trace=calc_result.evidence_trace,
            confidence=calc_result.data_quality.get("confidence", 1.0),
            seed=pair_seed,
        )

        return StructuredCompatibilityResponse(
            id=saved_row["id"],
            target_user_id=payload.target_user_id,
            score=calc_result.score,
            dimensions=calc_result.dimensions,
            signals=enriched_signals,
            interpretation=primary_interpretation,
            best_topics=calc_result.best_topics,
            conversation_starters=starters,
            data_quality=calc_result.data_quality,
            deep_analysis=deep_payload,
            engine_version=calc_result.engine_version,
            calculated_at=saved_row["calculated_at"],
        )


@router.get("/people/{target_user_id}/why", response_model=StructuredCompatibilityResponse)
async def get_why_this_person(
    target_user_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> StructuredCompatibilityResponse:
    return await compare_users(payload=CompareRequest(target_user_id=target_user_id), current_user=current_user, db=db)
