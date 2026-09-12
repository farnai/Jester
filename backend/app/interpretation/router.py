"""
FastAPI Router exposing Interpretation Contract and Content Architecture V2 endpoints.
Supports multi-asset authoring, status transitions, inventory inspection, and deterministic resolution.
"""
import uuid
from datetime import date, datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
import psycopg

from backend.app.astrology.natal import recalculate_user_astrology
from backend.app.astrology.transits import compute_daily_transits, get_daily_guidance
from backend.app.auth.dependencies import get_current_user, get_optional_user, require_copywriter_or_admin
from backend.app.auth.models import AuthenticatedUser
from backend.app.compatibility.engine import CompatibilityEngine
from backend.app.core.database import get_db, db_manager
from backend.app.core.errors import ForbiddenException, JesterAPIException, PrivacySafeNotFoundException
from backend.app.interpretation.engine import interpretation_engine
from backend.app.interpretation.library import content_library
from backend.app.interpretation.models import (
    ContentAsset,
    ContentAssetCreatePayload,
    ContentAssetUpdatePayload,
    ContentInventoryItem,
    ContentRecord,
    ContentStatus,
    ContentUpdatePayload,
    InterpretationContract,
    ResolvedInterpretation,
)

router = APIRouter(prefix="", tags=["interpretations"])


# =============================================================================
# Interpretation Contract Endpoints
# =============================================================================
@router.get("/interpretations", response_model=list[dict[str, Any]])
async def list_interpretations(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """
    Lists all registered interpretation contracts with summary asset counts
    and legacy approval states.
    """
    inventory = content_library.get_inventory()
    inv_map = {item.interpretation_id: item for item in inventory}

    results: list[dict[str, Any]] = []
    for rec in content_library.list_records():
        inv = inv_map.get(rec.interpretation_id)
        results.append({
            "interpretation_id": rec.interpretation_id,
            "meaning": rec.meaning,
            "draft": rec.draft.model_dump(),
            "final": rec.final.model_dump(),
            "asset_summary": {
                "total_assets": inv.total_assets if inv else 0,
                "approved_assets": inv.approved_assets if inv else 0,
                "available_locales": inv.available_locales if inv else ["ka"],
                "available_tones": inv.available_tones if inv else ["witty"],
            },
        })
    return results




# =============================================================================
# Content Asset Management Endpoints (V2)
# =============================================================================
@router.get("/interpretations/{interpretation_id}/assets", response_model=list[dict[str, Any]])
async def list_interpretation_assets(
    interpretation_id: str,
    locale: str | None = None,
    context: str | None = None,
    tone: str | None = None,
    status_filter: ContentStatus | None = Query(default=None, alias="status"),
    include_archived: bool = False,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """
    Lists content assets for an interpretation contract.
    Non-admin users see public asset fields; copywriters/admins see editorial metadata.
    """
    contract = interpretation_engine.get_contract(interpretation_id)
    if not contract:
        raise PrivacySafeNotFoundException(f"Interpretation contract '{interpretation_id}' not found")

    assets = content_library.list_assets(
        interpretation_id=interpretation_id,
        locale=locale,
        context=context,
        tone=tone,
        status=status_filter,
        include_archived=include_archived,
    )

    is_copywriter = current_user.role in ("copywriter", "admin", "service_role") or (
        current_user.app_metadata.get("role") in ("copywriter", "admin", "service_role")
    )

    clean_results: list[dict[str, Any]] = []
    for a in assets:
        dump = a.model_dump()
        if not is_copywriter:
            # Hide internal editorial metadata from normal consumers
            dump.pop("internal_notes", None)
            dump.pop("author", None)
            dump.pop("experiment_id", None)
            dump.pop("weight", None)
        clean_results.append(dump)

    return clean_results


@router.post(
    "/interpretations/{interpretation_id}/assets",
    response_model=ContentAsset,
    status_code=status.HTTP_201_CREATED,
)
async def create_interpretation_asset(
    interpretation_id: str,
    payload: ContentAssetCreatePayload,
    current_user: AuthenticatedUser = Depends(require_copywriter_or_admin),
) -> ContentAsset:
    """
    Creates a new ContentAsset for an interpretation contract.
    Protected to copywriters and administrators.
    """
    contract = interpretation_engine.get_contract(interpretation_id)
    if not contract:
        raise PrivacySafeNotFoundException(f"Interpretation contract '{interpretation_id}' not found")

    author = payload.author or current_user.email or "copywriter"
    return content_library.create_asset(
        interpretation_id=interpretation_id,
        payload=payload,
        author=author,
    )


@router.get("/content/assets/{asset_id}", response_model=dict[str, Any])
async def get_content_asset(
    asset_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Retrieves a single ContentAsset by its stable asset ID."""
    asset = content_library.get_asset(asset_id)
    if not asset:
        raise PrivacySafeNotFoundException(f"Content asset '{asset_id}' not found")

    dump = asset.model_dump()
    is_copywriter = current_user.role in ("copywriter", "admin", "service_role") or (
        current_user.app_metadata.get("role") in ("copywriter", "admin", "service_role")
    )
    if not is_copywriter:
        dump.pop("internal_notes", None)
        dump.pop("author", None)

    return dump


@router.patch("/content/assets/{asset_id}", response_model=ContentAsset)
async def update_content_asset(
    asset_id: str,
    payload: ContentAssetUpdatePayload,
    current_user: AuthenticatedUser = Depends(require_copywriter_or_admin),
) -> ContentAsset:
    """
    Updates text, status, tone, priority, or tags of a content asset.
    Protected to copywriters and administrators.
    """
    try:
        author = current_user.email or "copywriter"
        return content_library.update_asset(asset_id, payload, author=author)
    except KeyError:
        raise PrivacySafeNotFoundException(f"Content asset '{asset_id}' not found")


@router.post("/content/assets/{asset_id}/approve", response_model=ContentAsset)
async def approve_content_asset(
    asset_id: str,
    current_user: AuthenticatedUser = Depends(require_copywriter_or_admin),
) -> ContentAsset:
    """
    Marks a content asset as approved by copywriter.
    Protected to copywriters and administrators.
    """
    try:
        author = current_user.email or "copywriter"
        return content_library.approve_asset(asset_id, author=author)
    except KeyError:
        raise PrivacySafeNotFoundException(f"Content asset '{asset_id}' not found")


@router.post("/content/assets/{asset_id}/archive", response_model=ContentAsset)
async def archive_content_asset(
    asset_id: str,
    current_user: AuthenticatedUser = Depends(require_copywriter_or_admin),
) -> ContentAsset:
    """
    Archives a content asset, permanently excluding it from user resolution.
    Protected to copywriters and administrators.
    """
    archived = content_library.archive_asset(asset_id)
    if not archived:
        raise PrivacySafeNotFoundException(f"Content asset '{asset_id}' not found")
    return archived


@router.get("/content/inventory", response_model=list[ContentInventoryItem])
async def get_content_inventory(
    current_user: AuthenticatedUser = Depends(require_copywriter_or_admin),
) -> list[ContentInventoryItem]:
    """
    Returns a complete machine-readable inventory matrix across all contracts
    for editorial and copywriter auditing.
    """
    return content_library.get_inventory()


class NatalResolveRequest(BaseModel):
    sun_sign: str
    moon_sign: str | None = None
    ascendant_sign: str | None = None
    mercury_sign: str | None = None
    venus_sign: str | None = None
    mars_sign: str | None = None
    element_primary: str | None = None
    modality_primary: str | None = None
    locale: str = "ka"
    tone: str | None = None


class ComparePreviewRequest(BaseModel):
    target_user_id: uuid.UUID
    source_user_id: uuid.UUID | None = None
    locale: str = "ka"
    tone: str | None = None


DAILY_ENERGY_ARCHETYPES = [
    {"id": "confidence", "label_ka": "თავდაჯერება და მოქმედება", "transit": "sun_mars_transit"},
    {"id": "clarity", "label_ka": "სტრატეგიული სიცხადე", "transit": "mercury_saturn_transit"},
    {"id": "vitality", "label_ka": "ენერგიის მოზღვავება", "transit": "mars_jupiter_transit"},
    {"id": "creativity", "label_ka": "შემოქმედებითი ძიება", "transit": "venus_neptune_transit"},
    {"id": "communication", "label_ka": "პირდაპირი კომუნიკაცია", "transit": "mercury_transit"},
    {"id": "social", "label_ka": "სოციალური მაგნეტიზმი", "transit": "sun_venus_transit"},
    {"id": "introspection", "label_ka": "შინაგანი გადატვირთვა", "transit": "sun_pluto_transit"},
    {"id": "curiosity", "label_ka": "სპონტანური ცნობისმოყვარეობა", "transit": "mercury_uranus_transit"},
    {"id": "discipline", "label_ka": "მყარი დისციპლინა", "transit": "sun_saturn_transit"},
    {"id": "receptivity", "label_ka": "ემოციური პაუზა", "transit": "moon_transit_soft"},
    {"id": "restlessness", "label_ka": "იმპულსური მუხტი", "transit": "mars_uranus_transit"},
    {"id": "focus", "label_ka": "გაფანტული ფოკუსი", "transit": "jupiter_mercury_transit"},
    {"id": "neutral", "label_ka": "სტაბილური ფონი", "transit": "none"},
]

DEFAULT_DEMO_USER_ID = uuid.UUID("26098ac8-f8f0-4cd3-9bbb-78dc8467ba07")
compatibility_engine_instance = CompatibilityEngine()


SIGN_TO_DAILY_ENERGY: dict[str, str] = {
    "Aries": "confidence",        # sun_mars_transit: თავდაჯერება და მოქმედება
    "Taurus": "discipline",       # sun_saturn_transit: მყარი დისციპლინა
    "Gemini": "communication",    # mercury_transit: პირდაპირი კომუნიკაცია
    "Cancer": "receptivity",      # moon_transit_soft: ემოციური პაუზა
    "Leo": "social",              # sun_venus_transit: სოციალური მაგნეტიზმი
    "Virgo": "clarity",           # mercury_saturn_transit: სტრატეგიული სიცხადე
    "Libra": "creativity",        # venus_neptune_transit: შემოქმედებითი ძიება
    "Scorpio": "introspection",   # sun_pluto_transit: შინაგანი გადატვირთვა
    "Sagittarius": "vitality",    # mars_jupiter_transit: ენერგიის მოზღვავება
    "Capricorn": "discipline",    # sun_saturn_transit: მყარი დისციპლინა
    "Aquarius": "curiosity",      # mercury_uranus_transit: სპონტანური ცნობისმოყვარეობა
    "Pisces": "creativity",       # venus_neptune_transit: შემოქმედებითი ძიება
}


# =============================================================================
# Resolution Endpoints
# =============================================================================
@router.get("/interpretations/daily-energy", response_model=dict[str, Any])
async def get_daily_energy_interpretation(
    energy_type: str = "auto",
    locale: str = "ka",
    tone: str | None = None,
    target_date: str | None = None,
    current_user: AuthenticatedUser | None = Depends(get_optional_user),
    db: psycopg.Connection = Depends(get_db),
) -> dict[str, Any]:
    """
    Returns the resolved Daily Energy / Day Vibe interpretation in Georgian,
    personalized to the user's real astrological planetary transits, local timezone day,
    and birth data version.
    """
    calc_date: date
    effective_energy_type = energy_type
    primary_transit: dict[str, Any] | None = None
    supporting_transits: list[dict[str, Any]] = []
    user_tz_str = "UTC"
    seed = ""

    if current_user:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    b.birth_timezone,
                    b.birth_time_precision,
                    b.data_version,
                    p.sun_longitude,
                    p.moon_longitude,
                    p.mercury_longitude,
                    p.venus_longitude,
                    p.mars_longitude,
                    p.jupiter_longitude,
                    p.saturn_longitude,
                    p.uranus_longitude,
                    p.neptune_longitude,
                    p.pluto_longitude,
                    p.ascendant_longitude,
                    s.sun_sign
                FROM public.birth_data b
                LEFT JOIN public.astro_private p ON b.user_id = p.user_id
                LEFT JOIN public.astro_safe_profile s ON b.user_id = s.user_id
                WHERE b.user_id = %s;
                """,
                (current_user.id,),
            )
            row = cur.fetchone()

            if row:
                user_tz_str = row["birth_timezone"] or "UTC"
                if target_date:
                    try:
                        calc_date = date.fromisoformat(target_date)
                    except ValueError:
                        calc_date = datetime.now(ZoneInfo(user_tz_str)).date()
                else:
                    try:
                        calc_date = datetime.now(ZoneInfo(user_tz_str)).date()
                    except Exception:
                        calc_date = datetime.now(timezone.utc).date()

                # If calculated natal planetary positions exist in astro_private, compute real transits
                if row["sun_longitude"] is not None:
                    natal_placements: dict[str, float | None] = {
                        "sun": row["sun_longitude"],
                        "moon": row["moon_longitude"],
                        "mercury": row["mercury_longitude"],
                        "venus": row["venus_longitude"],
                        "mars": row["mars_longitude"],
                        "jupiter": row["jupiter_longitude"],
                        "saturn": row["saturn_longitude"],
                        "uranus": row["uranus_longitude"],
                        "neptune": row["neptune_longitude"],
                        "pluto": row["pluto_longitude"],
                        "ascendant": row["ascendant_longitude"],
                    }
                    precision = row.get("birth_time_precision") or "unknown"

                    transit_result = compute_daily_transits(
                        natal_placements=natal_placements,
                        target_date=calc_date,
                        user_timezone=user_tz_str,
                        birth_time_precision=precision,
                    )

                    if energy_type in [None, "", "auto"]:
                        effective_energy_type = transit_result.active_archetype

                    if transit_result.dominant_transit:
                        primary_transit = transit_result.dominant_transit.to_dict()
                    supporting_transits = [t.to_dict() for t in transit_result.supporting_transits]
                else:
                    # Fallback if astro_private hasn't been calculated yet
                    sun_sign = row["sun_sign"] or ""
                    if energy_type in [None, "", "auto"]:
                        effective_energy_type = SIGN_TO_DAILY_ENERGY.get(sun_sign, "confidence")

                data_ver = row["data_version"] or 1
                seed = f"{current_user.id}:{effective_energy_type}:{data_ver}:{calc_date.isoformat()}"
            else:
                calc_date = datetime.now(timezone.utc).date()
                seed = f"{current_user.id}:{calc_date.isoformat()}"
    else:
        # Unauthenticated / guest session
        if target_date:
            try:
                calc_date = date.fromisoformat(target_date)
            except ValueError:
                calc_date = datetime.now(timezone.utc).date()
        else:
            calc_date = datetime.now(timezone.utc).date()

        seed = f"daily-seed:{calc_date.isoformat()}"

    if effective_energy_type in [None, "", "auto"]:
        effective_energy_type = "confidence"

    resolved = interpretation_engine.resolve_daily_energy(
        energy_type=effective_energy_type,
        locale=locale,
        tone=tone,
        seed=seed,
    )
    if not resolved:
        resolved = interpretation_engine.resolve_daily_energy(
            energy_type="confidence",
            locale=locale,
            tone=tone,
            seed=seed,
        )

    contract = interpretation_engine.get_contract(resolved.id) if resolved else None

    # Find current archetype info
    curr_arch = next((a for a in DAILY_ENERGY_ARCHETYPES if a["id"] == effective_energy_type), DAILY_ENERGY_ARCHETYPES[0])
    guidance = get_daily_guidance(effective_energy_type, locale=locale)

    if primary_transit:
        detection_mode = "real_transit"
    elif effective_energy_type == "neutral":
        detection_mode = "neutral_baseline"
    else:
        detection_mode = "fallback_sun_sign"

    return {
        "date": calc_date.isoformat(),
        "archetype": effective_energy_type,
        "energy_type": effective_energy_type,
        "label": curr_arch["label_ka"],
        "interpretation": resolved.model_dump() if resolved else None,
        "contract": contract.model_dump() if contract else None,
        "available_archetypes": DAILY_ENERGY_ARCHETYPES,
        "primary_transit": primary_transit,
        "supporting_transits": supporting_transits,
        "detection_mode": detection_mode,
        "do": guidance["do"],
        "dont": guidance["dont"],
    }



@router.post("/interpretations/resolve-natal", response_model=list[dict[str, Any]])
async def resolve_natal_profile_interpretations(
    payload: NatalResolveRequest,
    current_user: AuthenticatedUser | None = Depends(get_optional_user),
) -> list[dict[str, Any]]:
    """
    Resolves personal Self/Me profile signals (Sun, Moon, Rising, Element, Modality)
    into resolved Georgian JESTER copy.
    """
    seed = str(current_user.id) if current_user else "natal-seed"
    resolved_list = interpretation_engine.resolve_natal_profile(
        profile=payload.model_dump(),
        locale=payload.locale,
        tone=payload.tone,
        seed=seed,
    )

    results: list[dict[str, Any]] = []
    dimension_titles = {
        "self.identity": "იდენტობა და არსი",
        "self.emotional": "ემოციური სამყარო",
        "self.persona": "სოციალური ნიღაბი და პირველი შთაბეჭდილება",
        "self.cognition": "აზროვნება და კომუნიკაცია (მერკური)",
        "self.relation": "მიზიდულობა და ურთიერთობა (ვენერა)",
        "self.action": "ენერგია და მოქმედება (მარსი)",
        "self.element": "დომინანტური სტიქია",
        "self.modality": "ცხოვრების დინამიკა და მოდალობა",
    }

    for res in resolved_list:
        contract = interpretation_engine.get_contract(res.id)
        # Determine dimension prefix
        dim_key = ".".join(res.id.split(".")[:2])
        title = dimension_titles.get(dim_key, "პირადი დაკვირვება")
        results.append({
            "dimension": dim_key,
            "title": title,
            "interpretation": res.model_dump(),
            "contract": contract.model_dump() if contract else None,
        })

    return results


@router.get("/interpretations/discovery-people", response_model=list[dict[str, Any]])
async def get_discovery_people(
    viewer_id: uuid.UUID | None = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    """
    Returns discoverable profiles with their safe derived astrology and a resolved
    Georgian JESTER hook copy. Also calculates real synastry compatibility score.
    Strictly authenticated: viewer identity is bound to current_user.id.
    Excludes blocked relationships and non-discoverable profiles.
    """
    if viewer_id is not None and viewer_id != current_user.id:
        raise ForbiddenException(
            message="Cannot request discovery results as another user.",
            error_code="forbidden_viewer_impersonation",
        )
    resolved_viewer_id = current_user.id

    with db.cursor() as cur:
        # Check if viewer has birth data for compatibility calculations
        cur.execute("SELECT 1 FROM public.birth_data WHERE user_id = %s;", (resolved_viewer_id,))
        calculation_viewer_id = resolved_viewer_id
        has_bd = cur.fetchone() is not None
        if not has_bd:
            # Check if DEFAULT_DEMO_USER_ID has birth data
            cur.execute("SELECT 1 FROM public.birth_data WHERE user_id = %s;", (DEFAULT_DEMO_USER_ID,))
            if cur.fetchone():
                calculation_viewer_id = DEFAULT_DEMO_USER_ID
                has_bd = True

        viewer_placements = None
        viewer_bd = {"birth_time_precision": "exact", "data_version": 1}
        if has_bd:
            cur.execute("SELECT birth_time_precision, data_version FROM public.birth_data WHERE user_id = %s;", (calculation_viewer_id,))
            row_bd = cur.fetchone()
            if row_bd:
                viewer_bd = row_bd

            cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (calculation_viewer_id,))
            viewer_placements = cur.fetchone()
            if not viewer_placements or viewer_placements.get("source_birth_data_version") != viewer_bd["data_version"]:
                try:
                    recalculate_user_astrology(calculation_viewer_id, db)
                    cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (calculation_viewer_id,))
                    viewer_placements = cur.fetchone()
                except Exception:
                    viewer_placements = None

        # Query all discoverable people except viewer, strictly excluding blocked users
        cur.execute(
            """
            SELECT p.id, p.display_name, p.bio, p.city, p.occupation, p.avatar_url,
                   s.sun_sign, s.moon_sign, s.ascendant_sign, s.element_primary, s.modality_primary
            FROM public.profiles p
            LEFT JOIN public.astro_safe_profile s ON p.id = s.user_id
            WHERE p.is_discoverable = true
              AND p.id != %s
              AND NOT public.is_user_blocked(%s, p.id)
            ORDER BY p.display_name ASC;
            """,
            (resolved_viewer_id, resolved_viewer_id),
        )
        people_rows = cur.fetchall()

        # Batch-fetch placements and birth data for candidates
        candidate_ids = [r["id"] for r in people_rows]
        placements_map: dict[uuid.UUID, Any] = {}
        bd_map: dict[uuid.UUID, Any] = {}
        if candidate_ids:
            cur.execute("SELECT * FROM public.astro_private WHERE user_id = ANY(%s);", (candidate_ids,))
            placements_map = {r["user_id"]: r for r in cur.fetchall()}
            cur.execute("SELECT user_id, birth_time_precision, data_version FROM public.birth_data WHERE user_id = ANY(%s);", (candidate_ids,))
            bd_map = {r["user_id"]: r for r in cur.fetchall()}

    people_list: list[dict[str, Any]] = []
    feed_used_interpretation_ids: set[str] = set()
    feed_used_signal_types: set[str] = set()
    feed_used_asset_ids: set[str] = set()

    for r in people_rows:
        pid = r["id"]
        sun = r["sun_sign"] or "Taurus"

        target_placements = placements_map.get(pid)
        target_bd = bd_map.get(pid, {"birth_time_precision": "exact", "data_version": 1})
        if not target_placements or target_placements.get("source_birth_data_version") != target_bd["data_version"]:
            try:
                recalculate_user_astrology(pid, db)
                with db.cursor() as cur:
                    cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (pid,))
                    target_placements = cur.fetchone()
                    placements_map[pid] = target_placements
            except Exception:
                target_placements = None

        # Calculate real Synastry V1 compatibility
        score = 60.0
        hook_res = None
        if target_placements and viewer_placements:
            try:
                calc = compatibility_engine_instance.calculate(
                    person_a_id=calculation_viewer_id,
                    person_a_version=viewer_bd["data_version"],
                    person_a_precision=viewer_bd["birth_time_precision"],
                    person_a_placements=viewer_placements,
                    person_b_id=pid,
                    person_b_version=target_bd["data_version"],
                    person_b_precision=target_bd["birth_time_precision"],
                    person_b_placements=target_placements,
                )
                score = round(calc.score, 1)
            except Exception:
                score = 60.0

        # Batch 7 Discovery Presence Hook:
        # 1. Candidate Ascendant sign
        # 2. If Ascendant unavailable, candidate Sun sign
        # 3. Fallback to established default sign
        candidate_asc = r.get("ascendant_sign")
        candidate_sun = r.get("sun_sign")
        target_sign = (candidate_asc or candidate_sun or sun or "aries").strip().lower()
        discovery_interp_id = f"discovery.person.presence.{target_sign}.v1"
        hook_res = content_library.resolve(
            interpretation_id=discovery_interp_id,
            context="discovery",
            locale="ka",
            seed=str(pid),
        )

        people_list.append({
            "id": str(pid),
            "display_name": r["display_name"],
            "bio": r["bio"],
            "city": r["city"],
            "occupation": r["occupation"],
            "avatar_url": r["avatar_url"],
            "astrology": {
                "sun_sign": r["sun_sign"],
                "moon_sign": r["moon_sign"],
                "ascendant_sign": r["ascendant_sign"],
                "element_primary": r["element_primary"],
                "modality_primary": r["modality_primary"],
            },
            "compatibility_score": score,
            "hook_observation": hook_res.model_dump() if hook_res else None,
            "presence_sign_source": "ascendant" if candidate_asc else ("sun" if candidate_sun else "fallback"),
            "presence_sign": target_sign,
        })

    return people_list


@router.post("/interpretations/compare-preview", response_model=dict[str, Any])
async def compare_preview(
    payload: ComparePreviewRequest,
    current_user: AuthenticatedUser | None = Depends(get_optional_user),
    db: psycopg.Connection = Depends(get_db),
) -> dict[str, Any]:
    """
    Computes full Synastry V1 compatibility between two users with real Swiss Ephemeris data,
    resolves all signals in Georgian, and builds structured Deep Analysis.
    Strictly prevents viewer impersonation when authenticated, enforces block checks,
    and respects discoverability rules.
    """
    if current_user:
        if payload.source_user_id is not None and payload.source_user_id != current_user.id:
            raise ForbiddenException(
                message="Cannot request comparison preview as another user.",
                error_code="forbidden_viewer_impersonation",
            )
        source_id = current_user.id
    else:
        source_id = payload.source_user_id or DEFAULT_DEMO_USER_ID

    target_id = payload.target_user_id

    if source_id == target_id:
        raise JesterAPIException(
            status_code=400,
            error_code="self_comparison_not_allowed",
            message="Cannot compare a user with themselves.",
        )

    with db.cursor() as cur:
        # Enforce block status in either direction
        cur.execute("SELECT public.is_user_blocked(%s, %s) as is_blocked;", (source_id, target_id))
        block_res = cur.fetchone()
        if block_res and block_res["is_blocked"]:
            raise PrivacySafeNotFoundException("User not found or unavailable.")

        # Check target profile existence and discoverability
        cur.execute("SELECT is_discoverable FROM public.profiles WHERE id = %s;", (target_id,))
        target_prof = cur.fetchone()
        if not target_prof:
            raise PrivacySafeNotFoundException("User not found or unavailable.")

        if not target_prof["is_discoverable"]:
            u_min, u_max = sorted([source_id, target_id])
            cur.execute("SELECT public.has_active_connection(%s, %s) as is_active;", (u_min, u_max))
            conn_res = cur.fetchone()
            if not conn_res or not conn_res["is_active"]:
                raise PrivacySafeNotFoundException("User not found or unavailable.")

        # Validate source birth data existence (fallback to DEFAULT_DEMO_USER_ID for unonboarded demo sessions)
        cur.execute("SELECT 1 FROM public.birth_data WHERE user_id = %s;", (source_id,))
        if not cur.fetchone():
            cur.execute("SELECT 1 FROM public.birth_data WHERE user_id = %s;", (DEFAULT_DEMO_USER_ID,))
            if cur.fetchone():
                source_id = DEFAULT_DEMO_USER_ID
            else:
                raise PrivacySafeNotFoundException("Birth data required for relationship preview.")

        if source_id == target_id:
            raise JesterAPIException(
                status_code=400,
                error_code="self_comparison_not_allowed",
                message="Cannot compare a user with themselves.",
            )

        # Validate target birth data existence
        cur.execute("SELECT 1 FROM public.birth_data WHERE user_id = %s;", (target_id,))
        if not cur.fetchone():
            raise PrivacySafeNotFoundException("Target user birth data unavailable.")

        cur.execute("SELECT * FROM public.astro_private WHERE user_id IN (%s, %s);", (source_id, target_id))
        placements_map = {r["user_id"]: r for r in cur.fetchall()}

        cur.execute("SELECT user_id, data_version, birth_time_precision FROM public.birth_data WHERE user_id IN (%s, %s);", (source_id, target_id))
        bd_map = {r["user_id"]: r for r in cur.fetchall()}

    bd_s = bd_map.get(source_id, {"data_version": 1, "birth_time_precision": "exact"})
    bd_t = bd_map.get(target_id, {"data_version": 1, "birth_time_precision": "exact"})

    if (
        source_id not in placements_map
        or placements_map[source_id] is None
        or placements_map[source_id].get("source_birth_data_version") != bd_s["data_version"]
    ):
        recalculate_user_astrology(source_id, db)
        with db.cursor() as cur:
            cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (source_id,))
            placements_map[source_id] = cur.fetchone()

    if (
        target_id not in placements_map
        or placements_map[target_id] is None
        or placements_map[target_id].get("source_birth_data_version") != bd_t["data_version"]
    ):
        recalculate_user_astrology(target_id, db)
        with db.cursor() as cur:
            cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (target_id,))
            placements_map[target_id] = cur.fetchone()

    calc_result = compatibility_engine_instance.calculate(
        person_a_id=source_id,
        person_a_version=bd_s["data_version"],
        person_a_precision=bd_s["birth_time_precision"],
        person_a_placements=placements_map[source_id],
        person_b_id=target_id,
        person_b_version=bd_t["data_version"],
        person_b_precision=bd_t["birth_time_precision"],
        person_b_placements=placements_map[target_id],
    )

    pair_seed = f"{min(str(source_id), str(target_id))}:{max(str(source_id), str(target_id))}:{bd_s['data_version']}:{bd_t['data_version']}"

    enriched_signals = interpretation_engine.resolve_signals(
        calc_result.signals,
        locale=payload.locale,
        tone=payload.tone,
        seed=pair_seed,
    )

    calc_seed = f"{pair_seed}:{calc_result.score}:{calc_result.signals[0]['type'] if calc_result.signals else 'none'}"

    primary_interp = interpretation_engine.get_primary_relationship_interpretation(
        score=calc_result.score,
        signals=calc_result.signals,
        locale=payload.locale,
        tone=payload.tone,
        seed=calc_seed,
    )

    conn_invitation = interpretation_engine.resolve_connection_invitation(
        signals=calc_result.signals,
        seed=calc_seed,
        locale=payload.locale or "ka",
    )

    conversation_starters = interpretation_engine.resolve_conversation_starters(
        signals=calc_result.signals,
        seed=calc_seed,
        locale=payload.locale or "ka",
    )

    conversation_starter_details = interpretation_engine.resolve_conversation_starter_details(
        signals=calc_result.signals,
        seed=calc_seed,
        locale=payload.locale or "ka",
    )

    deep_payload = interpretation_engine.build_deep_analysis_payload(
        score=calc_result.score,
        signals=calc_result.signals,
        evidence_trace=calc_result.evidence_trace,
        confidence=calc_result.data_quality.get("confidence", 1.0),
        locale=payload.locale,
        tone=payload.tone,
        seed=pair_seed,
    )

    return {
        "source_user_id": str(source_id),
        "target_user_id": str(target_id),
        "score": calc_result.score,
        "dimensions": calc_result.dimensions,
        "signals": enriched_signals,
        "interpretation": primary_interp.model_dump(),
        "connection_invitation": conn_invitation.model_dump() if conn_invitation else None,
        "best_topics": calc_result.best_topics,
        "conversation_starters": conversation_starters,
        "conversation_starter_details": conversation_starter_details,
        "data_quality": calc_result.data_quality,
        "deep_analysis": deep_payload.model_dump(),
        "engine_version": calc_result.engine_version,
        "calculated_at": calc_result.calculated_at,
    }


@router.post("/interpretations/resolve-signal", response_model=dict[str, Any])
async def resolve_signal_interpretation(
    payload: dict[str, Any],
    current_user: AuthenticatedUser | None = Depends(get_optional_user),
) -> dict[str, Any]:
    """
    Resolves an astrological signal into its human interpretation contract and copy.
    Accepts optional context, locale, tone, and seed.
    """
    context = payload.get("context")
    locale = payload.get("locale", "ka")
    tone = payload.get("tone")
    seed = payload.get("seed") or (str(current_user.id) if current_user else "signal-seed")

    resolved = interpretation_engine.resolve_signal(
        signal=payload,
        context=context,
        locale=locale,
        tone=tone,
        seed=seed,
    )
    if not resolved:
        raise JesterAPIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="signal_interpretation_not_found",
            message="No interpretation registered for this signal type",
        )

    contract = interpretation_engine.get_contract(resolved.id)
    return {
        "interpretation": resolved.model_dump(),
        "contract": contract.model_dump() if contract else None,
    }


@router.post("/interpretations/deep-analysis", response_model=dict[str, Any])
async def generate_deep_analysis(
    payload: dict[str, Any],
    current_user: AuthenticatedUser | None = Depends(get_optional_user),
) -> dict[str, Any]:
    """
    Generates a structured Deep Analysis payload from synastry evidence and ranked signals.
    Supports optional locale, tone, and seed.
    """
    score = float(payload.get("score", 70.0))
    signals = payload.get("signals", [])
    evidence = payload.get("evidence_trace", [])
    confidence = float(payload.get("data_confidence", 1.0))
    locale = payload.get("locale", "ka")
    tone = payload.get("tone")
    seed = payload.get("seed") or (str(current_user.id) if current_user else "deep-seed")

    deep_payload = interpretation_engine.build_deep_analysis_payload(
        score=score,
        signals=signals,
        evidence_trace=evidence,
        confidence=confidence,
        locale=locale,
        tone=tone,
        seed=seed,
    )
    return deep_payload.model_dump()


@router.get("/interpretations/{interpretation_id}", response_model=dict[str, Any])
async def get_interpretation_by_id(
    interpretation_id: str,
    locale: str = "ka",
    tone: str | None = None,
    current_user: AuthenticatedUser | None = Depends(get_optional_user),
) -> dict[str, Any]:
    """
    Retrieves the formal Interpretation Contract and currently resolved text
    for a given locale and tone.
    """
    contract = interpretation_engine.get_contract(interpretation_id)
    if not contract:
        raise PrivacySafeNotFoundException(f"Interpretation contract '{interpretation_id}' not found")

    seed = str(current_user.id) if current_user else "interp-seed"
    record = content_library.get_record(interpretation_id)
    resolved = content_library.resolve(
        interpretation_id=interpretation_id,
        locale=locale,
        tone=tone,
        seed=seed,
    ) or content_library.resolve_text(interpretation_id)

    # Asset counts
    assets = content_library.list_assets(interpretation_id=interpretation_id)

    return {
        "contract": contract.model_dump(),
        "record": record.model_dump() if record else None,
        "resolved": resolved.model_dump() if resolved else None,
        "asset_count": len(assets),
    }




# =============================================================================
# Legacy Endpoints (Maintained for Backward Compatibility)
# =============================================================================
@router.patch("/interpretations/{interpretation_id}/copy", response_model=ContentRecord)
async def update_copywriter_text(
    interpretation_id: str,
    payload: ContentUpdatePayload,
    current_user: AuthenticatedUser = Depends(require_copywriter_or_admin),
) -> ContentRecord:
    """Legacy endpoint for updating copy."""
    contract = interpretation_engine.get_contract(interpretation_id)
    if not contract:
        raise PrivacySafeNotFoundException(f"Interpretation contract '{interpretation_id}' not found")

    author = payload.author or current_user.email or "copywriter"
    return content_library.update_approved_copy(
        interpretation_id=interpretation_id,
        text=payload.text,
        author=author,
    )


@router.post("/interpretations/{interpretation_id}/reset", response_model=ContentRecord)
async def reset_interpretation_copy(
    interpretation_id: str,
    current_user: AuthenticatedUser = Depends(require_copywriter_or_admin),
) -> ContentRecord:
    """Legacy endpoint for resetting copy to draft."""
    rec = content_library.get_record(interpretation_id)
    if not rec:
        raise PrivacySafeNotFoundException(f"Interpretation record '{interpretation_id}' not found")

    return content_library.reset_to_draft(interpretation_id)


