"""
FastAPI Router for JESTER Stars Wallet, Transaction Ledger, and Unlocks.
"""
from typing import Any
import uuid
from fastapi import APIRouter, Depends, Query, status
import psycopg

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.wallet.models import (
    EntitlementModel,
    EntitlementsListResponse,
    PricingConfigResponse,
    TransactionsListResponse,
    UnlockItemRequest,
    UnlockItemResponse,
    WalletResponse,
    WalletTransactionModel,
)
from backend.app.wallet.service import (
    PRICING_CONFIG,
    get_or_create_wallet,
    get_transactions,
    spend_stars_and_entitle,
)

router = APIRouter(prefix="/wallet", tags=["Wallet & Monetization"])


@router.get("/me", response_model=WalletResponse)
async def get_my_wallet(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> WalletResponse:
    """
    Returns the current authenticated user's Stars wallet balance and lifetime stats.
    """
    data = get_or_create_wallet(current_user.id, db)
    return WalletResponse(**data)


@router.get("/transactions", response_model=TransactionsListResponse)
async def get_my_transactions(
    limit: int = Query(50, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> TransactionsListResponse:
    """
    Returns recent transaction ledger entries for the authenticated user.
    """
    items = get_transactions(current_user.id, db, limit=limit)
    return TransactionsListResponse(
        items=[WalletTransactionModel(**i) for i in items],
        total=len(items),
    )


@router.get("/entitlements", response_model=EntitlementsListResponse)
async def get_my_entitlements(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> EntitlementsListResponse:
    """
    Returns all unlocked entitlements (weekly energy, personal layers) for the user.
    """
    from psycopg.rows import dict_row
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, item_type, item_key, unlocked_at, expires_at
            FROM public.entitlements
            WHERE user_id = %s
            ORDER BY unlocked_at DESC;
            """,
            (current_user.id,),
        )
        rows = cur.fetchall()

    return EntitlementsListResponse(
        items=[
            EntitlementModel(
                id=r["id"],
                item_type=r["item_type"],
                item_key=r["item_key"],
                unlocked_at=r["unlocked_at"].isoformat(),
                expires_at=r["expires_at"].isoformat() if r["expires_at"] else None,
            )
            for r in rows
        ]
    )


@router.get("/pricing", response_model=PricingConfigResponse)
async def get_pricing_config() -> PricingConfigResponse:
    """
    Returns the single authoritative backend source of truth for Stars pricing.
    """
    return PricingConfigResponse(
        weekly_energy_stars=PRICING_CONFIG["weekly_energy"],
        personal_layer_stars=PRICING_CONFIG["personal_layer"],
    )


@router.post("/unlock", response_model=UnlockItemResponse)
async def unlock_item(
    payload: UnlockItemRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> UnlockItemResponse:
    """
    Unlocks a specific product (e.g. personal insight layer or weekly energy) with Stars.
    Enforces atomic database transaction, row-locking, and idempotency.
    """
    result = spend_stars_and_entitle(
        user_id=current_user.id,
        item_type=payload.item_type,
        item_key=payload.item_key,
        db=db,
    )
    return UnlockItemResponse(**result)

