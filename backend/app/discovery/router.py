"""Bounded social discovery: no astrology recalculation or compatibility scoring."""
import uuid
from typing import Any, Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.interpretation.library import content_library
from backend.app.interests.models import InterestItem
from backend.app.profiles.photos import PhotoResponse

router = APIRouter(prefix='/discovery', tags=['discovery'])


class DiscoveryPerson(BaseModel):
    id: uuid.UUID
    display_name: str
    city: str | None
    bio: str | None
    occupation: str | None
    avatar_url: str | None
    photos: list[PhotoResponse]
    interests: list[InterestItem]
    common_interest_ids: list[uuid.UUID]
    same_city: bool
    connection_id: uuid.UUID | None
    connection_state: Literal['none', 'pending_out', 'pending_in', 'accepted']
    astrology: dict[str, str | None]
    compatibility_score: None = None
    hook_observation: dict[str, Any] | None
    presence_sign_source: str | None
    presence_sign: str | None


class DiscoveryPage(BaseModel):
    items: list[DiscoveryPerson]
    next_cursor: uuid.UUID | None


def discovery_page(db, viewer, limit=12, after=None, city_id=None, shared_only=False, q=''):
    # Keyset pagination uses immutable UUIDs, independent of names or edits.
    with db.cursor() as cur:
        cur.execute('''SELECT p.id, p.display_name, p.bio, p.city, p.occupation, p.avatar_url,
            coalesce(p.current_city_id = me.current_city_id, false) AS same_city,
            s.sun_sign, s.moon_sign, s.ascendant_sign, s.element_primary, s.modality_primary,
            c.id AS connection_id, c.status AS connection_status, c.initiated_by
            FROM public.profiles p
            LEFT JOIN public.profiles me ON me.id = %s
            LEFT JOIN public.birth_data bd ON bd.user_id = p.id
            LEFT JOIN public.astro_safe_profile s ON s.user_id = p.id
                AND (bd.user_id IS NULL OR s.source_birth_data_version = bd.data_version)
            LEFT JOIN public.connections c ON c.user_a_id = least(p.id, %s)
                AND c.user_b_id = greatest(p.id, %s)
            WHERE p.is_discoverable AND p.id <> %s
                AND NOT public.is_user_blocked(%s, p.id)
                AND (%s::uuid IS NULL OR p.id > %s)
                AND (%s::uuid IS NULL OR p.current_city_id = %s)
                AND (%s = '' OR position(lower(%s) in lower(p.display_name)) > 0)
                AND (NOT %s OR EXISTS (
                    SELECT 1 FROM public.user_interests theirs
                    JOIN public.user_interests mine ON mine.interest_id = theirs.interest_id AND mine.user_id = %s
                    JOIN public.interests i ON i.id = theirs.interest_id AND i.status = 'active'
                    JOIN public.interest_categories cat ON cat.id = i.category_id AND cat.status = 'active'
                    WHERE theirs.user_id = p.id))
            ORDER BY p.id LIMIT %s''',
            (viewer, viewer, viewer, viewer, viewer, after, after, city_id, city_id, q, q, shared_only, viewer, limit + 1))
        rows = cur.fetchall()
        more = len(rows) > limit
        rows = rows[:limit]
        ids = [r['id'] for r in rows]
        photo_map = {uid: [] for uid in ids}
        interest_map = {uid: [] for uid in ids}
        common_map = {uid: [] for uid in ids}
        if ids:
            cur.execute('SELECT id, user_id, position, legacy_url FROM public.profile_photos WHERE user_id = ANY(%s) ORDER BY user_id, position', (ids,))
            for photo in cur.fetchall():
                photo_map[photo['user_id']].append(dict(id=photo['id'], position=photo['position'],
                    is_primary=photo['position'] == 0, is_legacy=photo['legacy_url'] is not None,
                    url=photo['legacy_url'] or f"/v1/profiles/{photo['user_id']}/photos/{photo['id']}/content"))
            cur.execute('''SELECT ui.user_id, i.id, i.category_id, i.name, i.slug, i.sort_order,
                c.name AS category_name, c.slug AS category_slug, c.icon AS category_icon,
                EXISTS(SELECT 1 FROM public.user_interests mine WHERE mine.user_id = %s AND mine.interest_id = i.id) AS shared
                FROM public.user_interests ui JOIN public.interests i ON ui.interest_id = i.id
                JOIN public.interest_categories c ON i.category_id = c.id
                WHERE ui.user_id = ANY(%s) AND i.status = 'active' AND c.status = 'active'
                ORDER BY c.sort_order, i.sort_order, i.id''', (viewer, ids))
            for interest in cur.fetchall():
                interest_map[interest['user_id']].append(InterestItem.model_validate(interest))
                if interest['shared']:
                    common_map[interest['user_id']].append(interest['id'])
    items = []
    for row in rows:
        uid = row['id']
        source = 'ascendant' if row['ascendant_sign'] else 'sun' if row['sun_sign'] else None
        sign = (row['ascendant_sign'] or row['sun_sign'] or '').strip().lower() or None
        hook = content_library.resolve(interpretation_id=f'discovery.person.presence.{sign}.v1',
            context='discovery', locale='ka', seed=str(uid)) if sign else None
        state = 'none'
        if row['connection_status'] == 'accepted':
            state = 'accepted'
        elif row['connection_status'] == 'pending':
            state = 'pending_out' if row['initiated_by'] == viewer else 'pending_in'
        items.append(DiscoveryPerson(
            **{key: row[key] for key in ('id','display_name','city','bio','occupation','avatar_url','same_city','connection_id')},
            photos=photo_map[uid], interests=interest_map[uid], common_interest_ids=common_map[uid],
            connection_state=state, astrology={key: row[key] for key in ('sun_sign','moon_sign','ascendant_sign','element_primary','modality_primary')},
            hook_observation=hook.model_dump() if hook else None, presence_sign=sign, presence_sign_source=source))
    return DiscoveryPage(items=items, next_cursor=rows[-1]['id'] if more else None)


@router.get('/people', response_model=DiscoveryPage)
def people(limit: int = Query(12, ge=1, le=24), after: uuid.UUID | None = None,
           city_id: uuid.UUID | None = None, shared_only: bool = False,
           q: str = Query('', max_length=80),
           current_user: AuthenticatedUser = Depends(get_current_user), db=Depends(get_db)):
    return discovery_page(db, current_user.id, limit, after, city_id, shared_only, q.strip())
