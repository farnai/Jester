import uuid
from fastapi import APIRouter, Depends
import psycopg
from psycopg.rows import dict_row

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.core.errors import JesterAPIException, PrivacySafeNotFoundException
from backend.app.profiles.photos import authorize_profile, lock_owner
from backend.app.enrichment.models import (
    PersonalityTraitItem,
    PersonalityTraitsListResponse,
    UserPersonalityTraitsResponse,
    UserPersonalityTraitsUpdateRequest,
    ConnectionIntentionItem,
    ConnectionIntentionsListResponse,
    UserConnectionIntentionsResponse,
    UserConnectionIntentionsUpdateRequest,
    PersonPersonalityResponse,
    PersonIntentionsResponse,
)

router = APIRouter(tags=["enrichment"])


# ---------------------------------------------------------------------------
# Personality Descriptors (ხასიათი)
# ---------------------------------------------------------------------------

@router.get("/personality-traits", response_model=PersonalityTraitsListResponse)
async def list_personality_traits(
    db: psycopg.Connection = Depends(get_db),
) -> PersonalityTraitsListResponse:
    """Returns all active personality descriptors sorted canonically."""
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, slug, name, name_ka, name_en, sort_order
            FROM public.personality_traits
            WHERE status = 'active'
            ORDER BY sort_order ASC, name_ka ASC;
            """
        )
        rows = cur.fetchall()
        return PersonalityTraitsListResponse(items=[PersonalityTraitItem.model_validate(r) for r in rows])


@router.get("/personality-traits/me", response_model=UserPersonalityTraitsResponse)
async def get_my_personality_traits(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> UserPersonalityTraitsResponse:
    """Returns the authenticated user's selected personality trait IDs."""
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT trait_id FROM public.user_personality_traits WHERE user_id = %s;",
            (current_user.id,),
        )
        rows = cur.fetchall()
        return UserPersonalityTraitsResponse(trait_ids=[r["trait_id"] for r in rows])


@router.put("/personality-traits/me", response_model=UserPersonalityTraitsResponse)
async def set_my_personality_traits(
    payload: UserPersonalityTraitsUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> UserPersonalityTraitsResponse:
    """
    Sets the current user's personality descriptors.
    Enforces maximum 5 selections. 0 selections (clearing/skipping) is valid.
    """
    raw_ids = payload.trait_ids
    unique_ids: list[uuid.UUID] = list(dict.fromkeys(raw_ids))

    if len(unique_ids) > 5:
        raise JesterAPIException(
            status_code=400,
            error_code="max_five_traits_exceeded",
            message="მაქსიმუმ 5 ხასიათის თვისების არჩევაა შესაძლებელი (Maximum 5 personality descriptors allowed).",
        )

    with db.transaction(), db.cursor(row_factory=dict_row) as cur:
        lock_owner(db, current_user.id)
        if unique_ids:
            cur.execute(
                """
                SELECT id FROM public.personality_traits
                WHERE id = ANY(%s) AND status = 'active';
                """,
                (unique_ids,),
            )
            found_ids = {r["id"] for r in cur.fetchall()}
            invalid = [str(i) for i in unique_ids if i not in found_ids]
            if invalid:
                raise JesterAPIException(
                    status_code=400,
                    error_code="invalid_trait_id",
                    message=f"One or more specified trait IDs do not exist: {', '.join(invalid)}",
                )

        cur.execute("DELETE FROM public.user_personality_traits WHERE user_id = %s;", (current_user.id,))
        if unique_ids:
            records = [(current_user.id, tid) for tid in unique_ids]
            cur.executemany(
                """
                INSERT INTO public.user_personality_traits (user_id, trait_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, trait_id) DO NOTHING;
                """,
                records,
            )

    return UserPersonalityTraitsResponse(trait_ids=unique_ids)


@router.get("/personality-traits/people/{profile_id}", response_model=PersonPersonalityResponse)
def get_person_personality_traits(
    profile_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> PersonPersonalityResponse:
    """Retrieves another person's personality descriptors respecting visibility policy."""
    authorize_profile(db, current_user.id, profile_id)
    with db.cursor(row_factory=dict_row) as cur:
        # Check target visibility
        cur.execute("SELECT personality_visibility FROM public.profiles WHERE id = %s;", (profile_id,))
        p_row = cur.fetchone()
        if not p_row:
            raise PrivacySafeNotFoundException("Profile not found")

        vis = p_row["personality_visibility"]
        if profile_id != current_user.id:
            if vis == "private":
                return PersonPersonalityResponse(items=[], visibility="private")
            if vis == "connections_only":
                cur.execute(
                    """
                    SELECT 1 FROM public.connections
                    WHERE status = 'accepted'
                      AND ((user_a_id = %s AND user_b_id = %s) OR (user_b_id = %s AND user_a_id = %s));
                    """,
                    (current_user.id, profile_id, current_user.id, profile_id),
                )
                if not cur.fetchone():
                    return PersonPersonalityResponse(items=[], visibility="connections_only")

        cur.execute(
            """
            SELECT pt.id, pt.slug, pt.name, pt.name_ka, pt.name_en, pt.sort_order
            FROM public.user_personality_traits upt
            JOIN public.personality_traits pt ON pt.id = upt.trait_id
            WHERE upt.user_id = %s AND pt.status = 'active'
            ORDER BY pt.sort_order ASC;
            """,
            (profile_id,),
        )
        rows = cur.fetchall()
        return PersonPersonalityResponse(
            items=[PersonalityTraitItem.model_validate(r) for r in rows],
            visibility=vis,
        )


# ---------------------------------------------------------------------------
# Connection Intentions (რას ვეძებ / მიზნები)
# ---------------------------------------------------------------------------

@router.get("/connection-intentions", response_model=ConnectionIntentionsListResponse)
async def list_connection_intentions(
    db: psycopg.Connection = Depends(get_db),
) -> ConnectionIntentionsListResponse:
    """Returns all active connection intentions sorted canonically."""
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, slug, name, name_ka, name_en, icon, sort_order
            FROM public.connection_intentions
            WHERE status = 'active'
            ORDER BY sort_order ASC, name_ka ASC;
            """
        )
        rows = cur.fetchall()
        return ConnectionIntentionsListResponse(items=[ConnectionIntentionItem.model_validate(r) for r in rows])


@router.get("/connection-intentions/me", response_model=UserConnectionIntentionsResponse)
async def get_my_connection_intentions(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> UserConnectionIntentionsResponse:
    """Returns the authenticated user's selected connection intention IDs."""
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT intention_id FROM public.user_connection_intentions WHERE user_id = %s;",
            (current_user.id,),
        )
        rows = cur.fetchall()
        return UserConnectionIntentionsResponse(intention_ids=[r["intention_id"] for r in rows])


@router.put("/connection-intentions/me", response_model=UserConnectionIntentionsResponse)
async def set_my_connection_intentions(
    payload: UserConnectionIntentionsUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> UserConnectionIntentionsResponse:
    """
    Sets the current user's connection intentions.
    Enforces maximum 3 selections. 0 selections (clearing/skipping) is valid.
    """
    raw_ids = payload.intention_ids
    unique_ids: list[uuid.UUID] = list(dict.fromkeys(raw_ids))

    if len(unique_ids) > 3:
        raise JesterAPIException(
            status_code=400,
            error_code="max_three_intentions_exceeded",
            message="მაქსიმუმ 3 მიზნის არჩევაა შესაძლებელი (Maximum 3 connection intentions allowed).",
        )

    with db.transaction(), db.cursor(row_factory=dict_row) as cur:
        lock_owner(db, current_user.id)
        if unique_ids:
            cur.execute(
                """
                SELECT id FROM public.connection_intentions
                WHERE id = ANY(%s) AND status = 'active';
                """,
                (unique_ids,),
            )
            found_ids = {r["id"] for r in cur.fetchall()}
            invalid = [str(i) for i in unique_ids if i not in found_ids]
            if invalid:
                raise JesterAPIException(
                    status_code=400,
                    error_code="invalid_intention_id",
                    message=f"One or more specified intention IDs do not exist: {', '.join(invalid)}",
                )

        cur.execute("DELETE FROM public.user_connection_intentions WHERE user_id = %s;", (current_user.id,))
        if unique_ids:
            records = [(current_user.id, iid) for iid in unique_ids]
            cur.executemany(
                """
                INSERT INTO public.user_connection_intentions (user_id, intention_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, intention_id) DO NOTHING;
                """,
                records,
            )

    return UserConnectionIntentionsResponse(intention_ids=unique_ids)


@router.get("/connection-intentions/people/{profile_id}", response_model=PersonIntentionsResponse)
def get_person_connection_intentions(
    profile_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> PersonIntentionsResponse:
    """Retrieves another person's connection intentions respecting visibility policy."""
    authorize_profile(db, current_user.id, profile_id)
    with db.cursor(row_factory=dict_row) as cur:
        # Check target visibility
        cur.execute("SELECT intentions_visibility FROM public.profiles WHERE id = %s;", (profile_id,))
        p_row = cur.fetchone()
        if not p_row:
            raise PrivacySafeNotFoundException("Profile not found")

        vis = p_row["intentions_visibility"]
        if profile_id != current_user.id:
            if vis == "private":
                return PersonIntentionsResponse(items=[], visibility="private")
            if vis == "connections_only":
                cur.execute(
                    """
                    SELECT 1 FROM public.connections
                    WHERE status = 'accepted'
                      AND ((user_a_id = %s AND user_b_id = %s) OR (user_b_id = %s AND user_a_id = %s));
                    """,
                    (current_user.id, profile_id, current_user.id, profile_id),
                )
                if not cur.fetchone():
                    return PersonIntentionsResponse(items=[], visibility="connections_only")

        cur.execute(
            """
            SELECT ci.id, ci.slug, ci.name, ci.name_ka, ci.name_en, ci.icon, ci.sort_order
            FROM public.user_connection_intentions uci
            JOIN public.connection_intentions ci ON ci.id = uci.intention_id
            WHERE uci.user_id = %s AND ci.status = 'active'
            ORDER BY ci.sort_order ASC;
            """,
            (profile_id,),
        )
        rows = cur.fetchall()
        return PersonIntentionsResponse(
            items=[ConnectionIntentionItem.model_validate(r) for r in rows],
            visibility=vis,
        )

