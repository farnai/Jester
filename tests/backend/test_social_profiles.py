"""Real DB + Storage integration; only UUID-scoped test accounts are removed.

Failure-injection cases are explicitly distinguished from normal real I/O.
"""
import io
import uuid
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.main import app
from backend.app.core.database import db_manager
from backend.app.core.errors import JesterAPIException
from backend.app.profiles import photos
from tests.backend.test_jwt_verification import generate_test_jwt


@pytest.fixture
def actors():
    ids = [uuid.uuid4(), uuid.uuid4()]
    with db_manager.get_connection() as db:
        for uid in ids:
            db.execute("INSERT INTO auth.users(id, email, raw_user_meta_data, role, aud) VALUES (%s,%s,'{}','authenticated','authenticated')", (uid, f'wave2-{uid}@example.invalid'))
            db.execute("INSERT INTO public.profiles(id, display_name) VALUES (%s,'Wave 2 integration fixture') ON CONFLICT(id) DO NOTHING", (uid,))
    yield ids
    with db_manager.get_connection() as db:
        db.execute('DELETE FROM auth.users WHERE id = ANY(%s)', (ids,))
        photos.drain_cleanup(db)


def client(uid):
    return TestClient(app, headers={'Authorization': f'Bearer {generate_test_jwt(user_id=str(uid))}'})


def picture():
    output = io.BytesIO()
    Image.new('RGB', (1800, 1200), '#788a69').save(output, 'JPEG', exif=b'Exif\x00\x00')
    return output.getvalue()


def upload(ac):
    return ac.post('/v1/profiles/me/photos', content=picture(), headers={'Content-Type': 'image/jpeg'})


def test_gallery_lifecycle_and_authorization(actors):
    owner, viewer = actors
    ac, other = client(owner), client(viewer)
    url = f'/v1/profiles/{owner}/photos'
    assert ac.get(url).json() == []
    for _ in range(6):
        result = upload(ac)
        assert result.status_code == 201, result.text
    items = result.json()
    assert upload(ac).status_code == 409
    assert other.delete(f"/v1/profiles/me/photos/{items[0]['id']}").status_code == 404
    assert other.put('/v1/profiles/me/photos/order', json={'photo_ids': [p['id'] for p in items]}).status_code == 400
    ids = [p['id'] for p in reversed(items)]
    result = ac.put('/v1/profiles/me/photos/order', json={'photo_ids': ids})
    assert result.status_code == 200, result.text
    primary = result.json()[0]
    assert ac.get('/v1/profiles/me').json()['avatar_url'] == primary['url']
    assert ac.patch('/v1/profiles/me', json={'avatar_url': 'https://example.invalid/override.jpg'}).status_code == 409
    assert [p['id'] for p in client(owner).get(url).json()] == ids
    content = other.get(primary['url'])
    assert content.status_code == 200
    assert content.headers['cache-control'] == 'private, no-store'
    image = Image.open(io.BytesIO(content.content))
    assert image.format == 'WEBP' and max(image.size) <= 1600 and not image.getexif()
    assert TestClient(app).get(primary['url']).status_code == 401
    with db_manager.get_connection() as db:
        path = db.execute('SELECT storage_path FROM public.profile_photos WHERE id=%s', (primary['id'],)).fetchone()['storage_path']
    public = httpx.get(f'{db_manager.settings.SUPABASE_URL}/storage/v1/object/public/profile-photos/{path}')
    assert public.status_code != 200
    # Direct client table access is denied, even to the owner.
    with db_manager.get_connection() as db:
        with pytest.raises(Exception):
            with db.transaction():
                db.execute('SET LOCAL ROLE authenticated')
                db.execute('SELECT * FROM public.profile_photos')
    assert ac.patch('/v1/profiles/me', json={'is_discoverable': False}).status_code == 200
    assert other.get(url).status_code == 404
    assert other.get(primary['url']).status_code == 404
    ac.patch('/v1/profiles/me', json={'is_discoverable': True})
    a, b = sorted(actors)
    with db_manager.get_connection() as db:
        db.execute("INSERT INTO public.connections(user_a_id,user_b_id,status,initiated_by,blocked_by) VALUES(%s,%s,'blocked',%s,%s)", (a,b,viewer,viewer))
    assert other.get(url).status_code == 404
    assert other.get(primary['url']).status_code == 404
    assert other.get(f'/v1/interests/people/{owner}').status_code == 404
    for photo_id in ids:
        assert ac.delete(f'/v1/profiles/me/photos/{photo_id}').status_code == 200
    assert ac.get('/v1/profiles/me').json()['avatar_url'] is None
    with db_manager.get_connection() as db:
        assert db.execute("SELECT count(*) AS n FROM storage.objects WHERE bucket_id='profile-photos' AND name LIKE %s", (f'{owner}/%',)).fetchone()['n'] == 0


def test_legacy_avatar_and_interests(actors):
    owner, viewer = actors
    ac, other = client(owner), client(viewer)
    legacy = 'https://example.invalid/legacy-avatar.jpg'
    assert ac.patch('/v1/profiles/me', json={'avatar_url': legacy}).status_code == 200
    first = ac.get(f'/v1/profiles/{owner}/photos').json()[0]
    assert first['is_legacy'] and first['url'] == legacy
    assert len(upload(ac).json()) == 2
    assert ac.get('/v1/profiles/me').json()['avatar_url'] == legacy
    ids = [r['id'] for r in ac.get('/v1/interests').json()['items'][:4]]
    assert len(ids) == 4
    assert ac.put('/v1/interests/me', json={'interest_ids': ids[:2]}).status_code == 400
    assert ac.put('/v1/interests/me', json={'interest_ids': ids[:3]}).status_code == 200
    assert other.put('/v1/interests/me', json={'interest_ids': ids[1:]}).status_code == 200
    shared = other.get(f'/v1/interests/people/{owner}').json()
    assert set(shared['common_interest_ids']) == set(ids[1:3])
    assert set(client(owner).get('/v1/interests/me').json()['interest_ids']) == set(ids[:3])
    assert ac.put('/v1/interests/me', json={'interest_ids': []}).status_code == 200


def test_validation_and_concurrent_limit(actors):
    ac = client(actors[0])
    assert ac.post('/v1/profiles/me/photos', content=b'fake', headers={'Content-Type': 'image/jpeg'}).status_code == 400
    assert ac.post('/v1/profiles/me/photos', content=picture(), headers={'Content-Type': 'image/png'}).status_code == 400
    assert ac.post('/v1/profiles/me/photos', content=b'x', headers={'Content-Type': 'image/svg+xml'}).status_code == 415
    assert ac.post('/v1/profiles/me/photos', content=b'x' * (photos.MAX_BYTES+1), headers={'Content-Type': 'image/jpeg'}).status_code == 413
    for _ in range(5):
        assert upload(ac).status_code == 201
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(lambda _: upload(client(actors[0])).status_code, range(2)))
    assert sorted(results) == [201, 409]


def test_injected_storage_failure_retains_cleanup_and_hides_deleted_bytes(actors, monkeypatch):
    ac = client(actors[0])
    item = upload(ac).json()[0]
    original = photos.storage_request
    def fail_delete(method, *args, **kwargs):
        if method == 'DELETE':
            raise JesterAPIException(503, 'injected_failure')
        return original(method, *args, **kwargs)
    monkeypatch.setattr(photos, 'storage_request', fail_delete)
    assert ac.delete(f"/v1/profiles/me/photos/{item['id']}").status_code == 200
    assert ac.get(item['url']).status_code == 404
    with db_manager.get_connection() as db:
        assert db.execute('SELECT count(*) AS n FROM public.profile_photo_cleanup WHERE storage_path LIKE %s', (f'{actors[0]}/%',)).fetchone()['n'] == 1
        monkeypatch.setattr(photos, 'storage_request', original)
        assert photos.drain_cleanup(db) >= 1


def test_injected_upload_failure_is_compensated(actors, monkeypatch):
    original = photos.storage_request
    def upload_then_fail(method, *args, **kwargs):
        response = original(method, *args, **kwargs)
        if method == 'POST':
            raise JesterAPIException(503, 'injected_after_upload')
        return response
    monkeypatch.setattr(photos, 'storage_request', upload_then_fail)
    assert upload(client(actors[0])).status_code == 503
    with db_manager.get_connection() as db:
        assert photos.gallery(db, actors[0]) == []
        assert db.execute("SELECT count(*) AS n FROM storage.objects WHERE bucket_id='profile-photos' AND name LIKE %s", (f'{actors[0]}/%',)).fetchone()['n'] == 0


def test_deleted_gallery_does_not_resurrect_oauth_avatar(actors):
    ac = client(actors[0])
    with db_manager.get_connection() as db:
        db.execute('''UPDATE auth.users SET raw_user_meta_data =
            '{"picture":"https://example.invalid/old-avatar.jpg"}' WHERE id=%s''', (actors[0],))
    ac.post('/v1/profiles/initialize')
    items = ac.get(f'/v1/profiles/{actors[0]}/photos').json()
    assert len(items) == 1 and items[0]['is_legacy']
    ac.delete(f"/v1/profiles/me/photos/{items[0]['id']}")
    assert ac.post('/v1/profiles/initialize').json()['avatar_url'] is None
    assert ac.patch('/v1/profiles/me', json={'avatar_url': 'https://example.invalid/replacement.jpg'}).status_code == 409


def test_interest_rls_hidden_and_blocked(actors):
    ac = client(actors[0])
    ids = [i['id'] for i in ac.get('/v1/interests').json()['items'][:3]]
    ac.put('/v1/interests/me', json={'interest_ids': ids})
    def visible_count():
        with db_manager.get_connection() as db, db.transaction():
            db.execute('SET LOCAL ROLE authenticated')
            db.execute("SELECT set_config('request.jwt.claim.sub', %s, true)", (str(actors[1]),))
            return db.execute('SELECT count(*) AS n FROM public.user_interests WHERE user_id=%s', (actors[0],)).fetchone()['n']
    assert visible_count() == 3
    ac.patch('/v1/profiles/me', json={'is_discoverable': False})
    assert visible_count() == 0
    ac.patch('/v1/profiles/me', json={'is_discoverable': True})
    a, b = sorted(actors)
    with db_manager.get_connection() as db:
        db.execute("INSERT INTO public.connections(user_a_id,user_b_id,status,initiated_by,blocked_by) VALUES(%s,%s,'blocked',%s,%s)", (a,b,actors[1],actors[1]))
    assert visible_count() == 0
