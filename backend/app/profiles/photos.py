"""Owner-managed gallery, private storage, and an authenticated media proxy."""
import io
import uuid
import warnings

import httpx
from fastapi import APIRouter, Depends, Request, Response
from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.config import get_settings
from backend.app.core.database import get_db, db_manager
from backend.app.core.errors import JesterAPIException, PrivacySafeNotFoundException

router = APIRouter(prefix='/profiles', tags=['profile photos'])
MAX_BYTES = 5 * 1024 * 1024
MIMES = {'image/jpeg': 'JPEG', 'image/png': 'PNG', 'image/webp': 'WEBP', 'image/gif': 'GIF'}


class PhotoResponse(BaseModel):
    id: uuid.UUID
    position: int
    is_primary: bool
    url: str
    is_legacy: bool


def authorize_profile(db, viewer, owner):
    with db.cursor() as cur:
        cur.execute('''SELECT id FROM public.profiles WHERE id = %s
            AND (id = %s OR is_discoverable)
            AND NOT public.is_user_blocked(%s, id)''', (owner, viewer, viewer))
        if not cur.fetchone():
            raise PrivacySafeNotFoundException('Profile not found')


def lock_owner(db, owner):
    with db.cursor() as cur:
        cur.execute('SELECT id FROM public.profiles WHERE id = %s FOR UPDATE', (owner,))
        if not cur.fetchone():
            raise PrivacySafeNotFoundException('Profile not found')


def gallery(db, owner):
    with db.cursor() as cur:
        cur.execute('SELECT * FROM public.profile_photos WHERE user_id = %s ORDER BY position', (owner,))
        return [dict(id=str(r['id']), position=r['position'], is_primary=r['position'] == 0,
                     url=r['legacy_url'] or f"/v1/profiles/{owner}/photos/{r['id']}/content",
                     is_legacy=r['legacy_url'] is not None) for r in cur.fetchall()]


def optimize_image(content, mime):
    if mime not in MIMES:
        raise JesterAPIException(415, 'unsupported_image', 'გამოიყენეთ JPEG, PNG, WebP ან GIF.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(content)) as source:
                if source.format != MIMES[mime] or source.width * source.height > 25_000_000:
                    raise ValueError('Invalid format or dimensions')
                source.seek(0)  # Animated formats become a still portrait.
                picture = ImageOps.exif_transpose(source).convert('RGB')
                picture.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
                # Fresh pixel image removes EXIF, GPS, comments and color metadata.
                clean = Image.new('RGB', picture.size)
                clean.paste(picture)
                result = io.BytesIO()
                clean.save(result, 'WEBP', quality=85, method=4)
                return result.getvalue()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise JesterAPIException(400, 'invalid_image', 'ფაილი დაზიანებულია ან ზომები ზედმეტად დიდია.')


def storage_request(method, path='', **kwargs):
    url = f"{get_settings().SUPABASE_URL}/storage/v1/object/profile-photos"
    if path:
        url += '/' + path
    try:
        with httpx.Client(timeout=30) as client:
            response = client.request(method, url, headers={**db_manager.get_admin_headers(),
                                      **kwargs.pop('headers', {})}, **kwargs)
            response.raise_for_status()
            return response
    except httpx.HTTPError:
        raise JesterAPIException(503, 'photo_storage_unavailable', 'ფოტოს საცავი დროებით მიუწვდომელია. სცადეთ ხელახლა.')


def drain_cleanup(db, path=None):
    """Retryable Storage API deletion. Never delete a referenced or active upload."""
    with db.cursor() as cur:
        cur.execute('''SELECT storage_path FROM public.profile_photo_cleanup q
            WHERE not_before <= now() AND (%s::text IS NULL OR storage_path = %s)
            AND NOT EXISTS (SELECT 1 FROM public.profile_photos p WHERE p.storage_path = q.storage_path)
            ORDER BY created_at LIMIT 100''', (path, path))
        paths = [r['storage_path'] for r in cur.fetchall()]
    for key in paths:
        storage_request('DELETE', json={'prefixes': [key]})
        with db.cursor() as cur:
            cur.execute('DELETE FROM public.profile_photo_cleanup WHERE storage_path = %s', (key,))
    return len(paths)


@router.get('/{owner}/photos', response_model=list[PhotoResponse])
def list_photos(owner: uuid.UUID, current_user: AuthenticatedUser = Depends(get_current_user), db=Depends(get_db)):
    authorize_profile(db, current_user.id, owner)
    return gallery(db, owner)


@router.post('/me/photos', status_code=201, response_model=list[PhotoResponse])
async def upload_photo(request: Request, current_user: AuthenticatedUser = Depends(get_current_user), db=Depends(get_db)):
    content = bytearray()
    async for chunk in request.stream():
        if len(content) + len(chunk) > MAX_BYTES:
            raise JesterAPIException(413, 'image_too_large', 'ფოტო არ უნდა აღემატებოდეს 5 MB-ს.')
        content.extend(chunk)
    return await run_in_threadpool(save_photo, db, current_user.id, content,
                                   request.headers.get('content-type', '').split(';')[0])


def save_photo(db, owner, content, mime):
    optimized = optimize_image(content, mime)
    photo_id = uuid.uuid4()
    path = f'{owner}/{photo_id}.webp'
    # Persist compensation BEFORE network I/O, surviving upload or DB failures.
    with db.cursor() as cur:
        cur.execute("INSERT INTO public.profile_photo_cleanup(storage_path, not_before) VALUES (%s, now() + interval '1 hour')", (path,))
    try:
        with db.transaction():
            lock_owner(db, owner)
            items = gallery(db, owner)
            if len(items) >= 6:
                raise JesterAPIException(409, 'photo_limit_reached', 'შეგიძლიათ დაამატოთ მაქსიმუმ 6 ფოტო.')
            storage_request('POST', path, content=optimized, headers={'Content-Type': 'image/webp', 'Cache-Control': 'no-store'})
            with db.cursor() as cur:
                cur.execute('INSERT INTO public.profile_photos(id, user_id, position, storage_path) VALUES (%s, %s, %s, %s)',
                            (photo_id, owner, len(items), path))
                cur.execute('DELETE FROM public.profile_photo_cleanup WHERE storage_path = %s', (path,))
    except Exception:
        with db.cursor() as cur:
            cur.execute('UPDATE public.profile_photo_cleanup SET not_before = now() WHERE storage_path = %s', (path,))
        try:
            drain_cleanup(db, path)
        except JesterAPIException:
            pass  # Durable queue retained; operator retry is safe.
        raise
    return gallery(db, owner)


class PhotoOrder(BaseModel):
    photo_ids: list[uuid.UUID] = Field(max_length=6)


@router.put('/me/photos/order', response_model=list[PhotoResponse])
def reorder_photos(payload: PhotoOrder, current_user: AuthenticatedUser = Depends(get_current_user), db=Depends(get_db)):
    with db.transaction():
        lock_owner(db, current_user.id)
        existing = gallery(db, current_user.id)
        supplied = [str(i) for i in payload.photo_ids]
        if len(set(supplied)) != len(supplied) or set(supplied) != {p['id'] for p in existing}:
            raise JesterAPIException(400, 'invalid_photo_order', 'გადატვირთეთ გალერეა და სცადეთ ხელახლა.')
        with db.cursor() as cur:
            for position, photo_id in enumerate(payload.photo_ids):
                cur.execute('UPDATE public.profile_photos SET position = %s WHERE id = %s AND user_id = %s',
                            (position, photo_id, current_user.id))
    return gallery(db, current_user.id)


@router.delete('/me/photos/{photo_id}', response_model=list[PhotoResponse])
def delete_photo(photo_id: uuid.UUID, current_user: AuthenticatedUser = Depends(get_current_user), db=Depends(get_db)):
    with db.transaction():
        lock_owner(db, current_user.id)
        with db.cursor() as cur:
            cur.execute('DELETE FROM public.profile_photos WHERE id = %s AND user_id = %s RETURNING storage_path', (photo_id, current_user.id))
            removed = cur.fetchone()
            if not removed:
                raise PrivacySafeNotFoundException('Photo not found')
            for position, item in enumerate(gallery(db, current_user.id)):
                cur.execute('UPDATE public.profile_photos SET position = %s WHERE id = %s', (position, item['id']))
    # Logical deletion commits first. Private bytes can no longer be served.
    if removed['storage_path']:
        try:
            drain_cleanup(db, removed['storage_path'])
        except JesterAPIException:
            pass
    return gallery(db, current_user.id)


@router.get('/{owner}/photos/{photo_id}/content')
def photo_content(owner: uuid.UUID, photo_id: uuid.UUID,
                  current_user: AuthenticatedUser = Depends(get_current_user), db=Depends(get_db)):
    authorize_profile(db, current_user.id, owner)
    with db.cursor() as cur:
        cur.execute('SELECT storage_path FROM public.profile_photos WHERE id = %s AND user_id = %s', (photo_id, owner))
        row = cur.fetchone()
    if not row or not row['storage_path']:
        raise PrivacySafeNotFoundException('Photo not found')
    data = storage_request('GET', row['storage_path']).content
    return Response(data, media_type='image/webp', headers={'Cache-Control': 'private, no-store', 'Vary': 'Authorization', 'X-Content-Type-Options': 'nosniff'})
