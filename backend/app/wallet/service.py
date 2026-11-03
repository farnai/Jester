"""
Authoritative Server-Owned Wallet & Entitlement Service.
Enforces atomic database transactions, row-level locking, and idempotency.
"""
from datetime import datetime, timezone
import json
from typing import Any
import uuid
import psycopg
from psycopg.rows import dict_row

from backend.app.core.errors import JesterAPIException

PRICING_CONFIG: dict[str, int] = {
    "weekly_energy": 5,
    "personal_layer": 5,
}

PERSONAL_LAYER_LABELS_KA: dict[str, str] = {
    "layer_1": "ვინ ხარ სინამდვილეში",
    "layer_2": "როგორ აზროვნებ",
    "layer_3": "როგორ გიყვარს",
    "layer_4": "როგორ მოქმედებ",
    "layer_5": "შენი ჩრდილოვანი მხარე",
    "layer_6": "შენი შინაგანი კონფიგურაცია",
    "layer_7": "შენი პირადი სახელმძღვანელო",
}


def get_or_create_wallet(user_id: uuid.UUID, db: psycopg.Connection) -> dict[str, Any]:
    """
    Returns the wallet for user_id, initializing it to 0 balance if it does not exist.
    """
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO public.wallets (user_id, balance, created_at, updated_at)
            VALUES (%s, 0, timezone('utc', now()), timezone('utc', now()))
            ON CONFLICT (user_id) DO NOTHING;
            """,
            (user_id,),
        )
        cur.execute(
            """
            SELECT user_id, balance, updated_at
            FROM public.wallets
            WHERE user_id = %s;
            """,
            (user_id,),
        )
        wallet = cur.fetchone()

        # Calculate lifetime totals
        cur.execute(
            """
            SELECT 
                COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) AS total_earned,
                COALESCE(SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END), 0) AS total_spent
            FROM public.wallet_transactions
            WHERE user_id = %s;
            """,
            (user_id,),
        )
        totals = cur.fetchone()

    return {
        "user_id": wallet["user_id"],
        "balance": wallet["balance"],
        "total_earned": totals["total_earned"] if totals else 0,
        "total_spent": totals["total_spent"] if totals else 0,
        "updated_at": wallet["updated_at"].isoformat() if wallet.get("updated_at") else datetime.now(timezone.utc).isoformat(),
    }


def grant_stars(
    user_id: uuid.UUID,
    amount: int,
    transaction_type: str,
    description_ka: str,
    db: psycopg.Connection,
    reference_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Grants stars to a user's wallet. Idempotent when reference_id is provided.
    """
    if amount <= 0:
        raise ValueError("Grant amount must be positive")

    meta_json = json.dumps(metadata or {})

    with db.cursor(row_factory=dict_row) as cur:
        # Check idempotency if reference_id provided
        if reference_id:
            cur.execute(
                """
                SELECT id, balance_after
                FROM public.wallet_transactions
                WHERE user_id = %s AND transaction_type = %s AND reference_id = %s;
                """,
                (user_id, transaction_type, reference_id),
            )
            existing = cur.fetchone()
            if existing:
                cur.execute("SELECT balance, updated_at FROM public.wallets WHERE user_id = %s;", (user_id,))
                w = cur.fetchone()
                return {
                    "transaction_id": existing["id"],
                    "balance": w["balance"],
                    "already_granted": True,
                }

        # Lock wallet row
        cur.execute(
            """
            INSERT INTO public.wallets (user_id, balance, created_at, updated_at)
            VALUES (%s, 0, timezone('utc', now()), timezone('utc', now()))
            ON CONFLICT (user_id) DO NOTHING;
            """,
            (user_id,),
        )
        cur.execute(
            "SELECT balance FROM public.wallets WHERE user_id = %s FOR UPDATE;",
            (user_id,),
        )
        row = cur.fetchone()
        current_balance = row["balance"]
        new_balance = current_balance + amount

        cur.execute(
            """
            UPDATE public.wallets
            SET balance = %s, updated_at = timezone('utc', now())
            WHERE user_id = %s;
            """,
            (new_balance, user_id),
        )

        cur.execute(
            """
            INSERT INTO public.wallet_transactions (
                user_id, amount, balance_after, transaction_type, reference_id, description_ka, metadata, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, timezone('utc', now()))
            RETURNING id;
            """,
            (user_id, amount, new_balance, transaction_type, reference_id, description_ka, meta_json),
        )
        tx_row = cur.fetchone()

    return {
        "transaction_id": tx_row["id"],
        "balance": new_balance,
        "already_granted": False,
    }


def spend_stars_and_entitle(
    user_id: uuid.UUID,
    item_type: str,
    item_key: str,
    db: psycopg.Connection,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Atomically verifies balance, locks wallet row, deducts stars, and records entitlement.
    Guarantees no double spend and idempotent repeat calls.
    """
    cost = PRICING_CONFIG.get(item_type)
    if cost is None:
        raise JesterAPIException(
            status_code=400,
            error_code="invalid_item_type",
            message=f"უცნობი პროდუქტის ტიპი: {item_type}",
        )

    # Human-readable Georgian description
    if item_type == "weekly_energy":
        desc_ka = f"კვირის ენერგიის განბლოკვა ({item_key})"
    elif item_type == "personal_layer":
        layer_label = PERSONAL_LAYER_LABELS_KA.get(item_key, item_key)
        desc_ka = f"პირადი შრის განბლოკვა: {layer_label}"
    else:
        desc_ka = f"{item_type} განბლოკვა ({item_key})"

    ref_id = f"{item_type}:{item_key}"
    meta_json = json.dumps(metadata or {})

    with db.cursor(row_factory=dict_row) as cur:
        # 1. Lock wallet row FIRST for atomic check-and-decrement across all concurrent requests
        cur.execute(
            """
            INSERT INTO public.wallets (user_id, balance, created_at, updated_at)
            VALUES (%s, 0, timezone('utc', now()), timezone('utc', now()))
            ON CONFLICT (user_id) DO NOTHING;
            """,
            (user_id,),
        )
        cur.execute(
            "SELECT balance FROM public.wallets WHERE user_id = %s FOR UPDATE;",
            (user_id,),
        )
        wallet = cur.fetchone()
        current_balance = wallet["balance"]

        # 2. Idempotency Check INSIDE the lock: Already unlocked?
        cur.execute(
            """
            SELECT id, unlocked_at
            FROM public.entitlements
            WHERE user_id = %s AND item_type = %s AND item_key = %s;
            """,
            (user_id, item_type, item_key),
        )
        existing_ent = cur.fetchone()
        if existing_ent:
            return {
                "success": True,
                "already_unlocked": True,
                "item_type": item_type,
                "item_key": item_key,
                "stars_spent": 0,
                "balance_after": current_balance,
                "message": "კონტენტი უკვე განბლოკილია.",
            }

        # 3. Balance verification
        if current_balance < cost:
            raise JesterAPIException(
                status_code=400,
                error_code="insufficient_stars",
                message=f"არასაკმარისი ვარსკვლავები. საჭიროა {cost} ✦, შენ გაქვს {current_balance} ✦.",
            )

        new_balance = current_balance - cost

        # 4. Decrement wallet
        cur.execute(
            """
            UPDATE public.wallets
            SET balance = %s, updated_at = timezone('utc', now())
            WHERE user_id = %s;
            """,
            (new_balance, user_id),
        )

        # 5. Insert transaction ledger row
        cur.execute(
            """
            INSERT INTO public.wallet_transactions (
                user_id, amount, balance_after, transaction_type, reference_id, description_ka, metadata, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, timezone('utc', now()))
            RETURNING id;
            """,
            (user_id, -cost, new_balance, f"{item_type}_unlock", ref_id, desc_ka, meta_json),
        )
        tx_row = cur.fetchone()
        tx_id = tx_row["id"]

        # 6. Insert Entitlement row
        cur.execute(
            """
            INSERT INTO public.entitlements (
                user_id, item_type, item_key, transaction_id, metadata, unlocked_at
            )
            VALUES (%s, %s, %s, %s, %s, timezone('utc', now()))
            ON CONFLICT (user_id, item_type, item_key) DO NOTHING;
            """,
            (user_id, item_type, item_key, tx_id, meta_json),
        )

    return {
        "success": True,
        "already_unlocked": False,
        "item_type": item_type,
        "item_key": item_key,
        "stars_spent": cost,
        "balance_after": new_balance,
        "message": f"კონტენტი წარმატებით განბლოკილია ({cost} ✦).",
    }


def has_entitlement(user_id: uuid.UUID, item_type: str, item_key: str, db: psycopg.Connection) -> bool:
    """
    Checks if a user currently has access to a specific entitlement item.
    """
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT 1 FROM public.entitlements
            WHERE user_id = %s AND item_type = %s AND item_key = %s;
            """,
            (user_id, item_type, item_key),
        )
        return cur.fetchone() is not None


def get_user_entitlements_map(user_id: uuid.UUID, db: psycopg.Connection) -> dict[str, set[str]]:
    """
    Returns a fast lookup dict of {item_type: set(item_keys)} for all active entitlements.
    """
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT item_type, item_key
            FROM public.entitlements
            WHERE user_id = %s;
            """,
            (user_id,),
        )
        rows = cur.fetchall()

    res: dict[str, set[str]] = {}
    for r in rows:
        t = r["item_type"]
        k = r["item_key"]
        if t not in res:
            res[t] = set()
        res[t].add(k)
    return res


def get_transactions(user_id: uuid.UUID, db: psycopg.Connection, limit: int = 50) -> list[dict[str, Any]]:
    """
    Returns the recent transaction history for the user from the immutable ledger.
    """
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, amount, balance_after, transaction_type, reference_id, description_ka, metadata, created_at
            FROM public.wallet_transactions
            WHERE user_id = %s
            ORDER BY created_at DESC, id DESC
            LIMIT %s;
            """,
            (user_id, limit),
        )
        rows = cur.fetchall()

    return [
        {
            "id": r["id"],
            "amount": r["amount"],
            "balance_after": r["balance_after"],
            "transaction_type": r["transaction_type"],
            "reference_id": r["reference_id"],
            "description_ka": r["description_ka"],
            "metadata": r["metadata"] or {},
            "created_at": r["created_at"].isoformat(),
        }
        for r in rows
    ]

