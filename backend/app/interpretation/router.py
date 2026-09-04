"""
FastAPI Router exposing Interpretation Contract and Content Architecture V2 endpoints.
Supports multi-asset authoring, status transitions, inventory inspection, and deterministic resolution.
"""
from typing import Any
from fastapi import APIRouter, Depends, Query, status

from backend.app.auth.dependencies import get_current_user, require_copywriter_or_admin
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.errors import JesterAPIException, PrivacySafeNotFoundException
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


@router.get("/interpretations/{interpretation_id}", response_model=dict[str, Any])
async def get_interpretation_by_id(
    interpretation_id: str,
    locale: str = "ka",
    tone: str | None = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Retrieves the formal Interpretation Contract and currently resolved text
    for a given locale and tone.
    """
    contract = interpretation_engine.get_contract(interpretation_id)
    if not contract:
        raise PrivacySafeNotFoundException(f"Interpretation contract '{interpretation_id}' not found")

    record = content_library.get_record(interpretation_id)
    resolved = content_library.resolve(
        interpretation_id=interpretation_id,
        locale=locale,
        tone=tone,
        seed=str(current_user.id),
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


# =============================================================================
# Resolution Endpoints
# =============================================================================
@router.post("/interpretations/resolve-signal", response_model=dict[str, Any])
async def resolve_signal_interpretation(
    payload: dict[str, Any],
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Resolves an astrological signal into its human interpretation contract and copy.
    Accepts optional context, locale, tone, and seed.
    """
    context = payload.get("context")
    locale = payload.get("locale", "ka")
    tone = payload.get("tone")
    seed = payload.get("seed") or str(current_user.id)

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
    current_user: AuthenticatedUser = Depends(get_current_user),
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
    seed = payload.get("seed") or str(current_user.id)

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


