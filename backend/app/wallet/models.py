"""
Pydantic Models for JESTER Stars Economy, Wallet, Ledger, and Entitlements.
"""
from datetime import datetime
from typing import Any
import uuid
from pydantic import BaseModel, Field


class WalletResponse(BaseModel):
    user_id: uuid.UUID
    balance: int = Field(ge=0, description="Current Stars balance")
    total_earned: int = Field(ge=0, description="Lifetime Stars received")
    total_spent: int = Field(ge=0, description="Lifetime Stars spent")
    updated_at: str


class WalletTransactionModel(BaseModel):
    id: uuid.UUID
    amount: int = Field(description="Positive for grants/earnings, negative for spends")
    balance_after: int = Field(ge=0)
    transaction_type: str
    reference_id: str | None = None
    description_ka: str
    created_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class TransactionsListResponse(BaseModel):
    items: list[WalletTransactionModel]
    total: int


class EntitlementModel(BaseModel):
    id: uuid.UUID
    item_type: str
    item_key: str
    unlocked_at: str
    expires_at: str | None = None


class EntitlementsListResponse(BaseModel):
    items: list[EntitlementModel]


class UnlockItemRequest(BaseModel):
    item_type: str = Field(description="'weekly_energy' or 'personal_layer'")
    item_key: str = Field(description="Identifier (e.g. '2026-W45' or 'layer_2')")


class UnlockItemResponse(BaseModel):
    success: bool
    already_unlocked: bool
    item_type: str
    item_key: str
    stars_spent: int
    balance_after: int
    message: str


class PricingConfigResponse(BaseModel):
    weekly_energy_stars: int = 5
    personal_layer_stars: int = 5
    free_features: list[str] = [
        "daily_energy",
        "do_and_dont",
        "discovery",
        "public_profiles",
        "layer_titles_and_summaries",
    ]

