"""Real local DB/Storage fixtures; delete only generated UUIDs, never truncate."""
import io
import uuid
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import db_manager
from backend.app.discovery.router import discovery_page
from tests.backend.test_social_profiles import client, upload, actors


@pytest.fixture
def population():
    ids = sorted(uuid.uuid4() for _ in range(18))
    label = f'Wave3-{uuid.uuid4().hex}'
    with db_manager.get_connection() as db:
        for uid in ids:
            db.execute("INSERT INTO auth.users(id,email,raw_user_meta_data,role,aud) VALUES(%s,%s,'{}','authenticated','authenticated')", (uid, f'wave3-{uid}@example.invalid'))
            db.execute('INSERT INTO public.profiles(id,display_name) VALUES(%s,%s) ON CONFLICT(id) DO UPDATE SET display_name=excluded.display_name', (uid,label))
    try:
        yield ids, label
    finally:
        with db_manager.get_connection() as db:
            db.execute('DELETE FROM auth.users WHERE id=ANY(%s)', (ids,))


def test_stable_bounded_pagination_without_name_dedup_or_calculation(population, monkeypatch):
    from backend.app.interpretation import router as interpretation
    def forbidden(*args, **kwargs):
        pytest.fail('Discovery must not calculate astrology or synastry')
    # Existing computation boundaries used by interpretation/profile comparison.
    monkeypatch.setattr(interpretation, 'recalculate_user_astrology', forbidden)
    monkeypatch.setattr(interpretation.compatibility_engine_instance, 'calculate', forbidden)
    ids, label = population
    ac = client(ids[0])
    first = ac.get('/v1/discovery/people', params={'q':label}).json()
    assert len(first['items']) == 12 and first['next_cursor']
    second = ac.get('/v1/discovery/people', params={'q':label,'after':first['next_cursor']}).json()
    assert len(second['items']) == 5 and second['next_cursor'] is None
    assert [p['id'] for p in first['items'] + second['items']] == [str(i) for i in ids[1:]]
    for person in first['items']:
        assert person['compatibility_score'] is None and person['hook_observation'] is None
        assert not any(key in str(person) for key in ('birth_date','birth_time','latitude','longitude','astro_private','houses'))
    for params in ({'limit':25}, {'limit':0}, {'after':'invalid'}, {'q':'a'*81}, {'city_id':'invalid'}):
        assert ac.get('/v1/discovery/people', params=params).status_code == 422
    assert TestClient(app).get('/v1/discovery/people').status_code == 401
    assert len(ac.get('/v1/interpretations/discovery-people', params={'q':label,'limit':2}).json()) == 2
    # Service cost is exactly three SQL reads, regardless of candidate population.
    with db_manager.get_connection() as db:
        calls = []
        class Cursor:
            def __enter__(self): self.cur = db.cursor(); return self
            def __exit__(self, *args): self.cur.close()
            def execute(self, query, args): calls.append(query); return self.cur.execute(query,args)
            def fetchall(self): return self.cur.fetchall()
        class CountedDB:
            def cursor(self): return Cursor()
        assert len(discovery_page(CountedDB(), ids[0], q=label, limit=2).items) == 2
        assert len(calls) == 3 and all(q.lstrip().upper().startswith('SELECT') for q in calls)


def test_filters_visibility_and_connection_lifecycle(population):
    ids, label = population
    viewer, target, hidden, blocked, blocker = ids[:5]
    ac, other = client(viewer), client(target)
    interests = [r['id'] for r in ac.get('/v1/interests').json()['items'][:3]]
    for user in (ac,other):
        assert user.put('/v1/interests/me',json={'interest_ids':interests}).status_code == 200
    with db_manager.get_connection() as db:
        city = db.execute("SELECT id FROM public.cities WHERE name_ascii='Tbilisi' LIMIT 1").fetchone()['id']
        db.execute('UPDATE public.profiles SET current_city_id=%s WHERE id=ANY(%s)', (city,[viewer,target]))
        db.execute('UPDATE public.profiles SET is_discoverable=false WHERE id=%s', (hidden,))
        for uid,by in ((blocked,viewer),(blocker,blocker)):
            a,b=sorted([viewer,uid])
            db.execute("INSERT INTO public.connections(user_a_id,user_b_id,status,initiated_by,blocked_by) VALUES(%s,%s,'blocked',%s,%s)",(a,b,by,by))
    filters = {'q':label,'city_id':str(city),'shared_only':'true'}
    people = ac.get('/v1/discovery/people',params=filters).json()['items']
    assert [p['id'] for p in people] == [str(target)]
    assert people[0]['same_city'] and set(people[0]['common_interest_ids']) == set(interests)
    all_people = ac.get('/v1/discovery/people',params={'q':label,'limit':24}).json()['items']
    assert not {str(uid) for uid in (viewer,hidden,blocked,blocker)} & {p['id'] for p in all_people}
    assert ac.get('/v1/discovery/people',params={'q':label+'%'}).json()['items'] == []
    def state(user, target_id):
        return next(p['connection_state'] for p in user.get('/v1/discovery/people',params={'q':label,'limit':24}).json()['items'] if p['id']==str(target_id))
    assert state(ac,target) == 'none'
    result = ac.post('/v1/connections',json={'target_user_id':str(target)})
    assert result.status_code == 201, result.text
    cid = result.json()['id']
    assert state(ac,target) == 'pending_out' and state(other,viewer) == 'pending_in'
    assert other.post(f'/v1/connections/{cid}/transition',json={'action':'accept'}).status_code == 200
    assert state(ac,target) == 'accepted'
    assert ac.post(f'/v1/connections/{cid}/transition',json={'action':'block'}).status_code == 200
    assert ac.get('/v1/discovery/people',params=filters).json()['items'] == []
    assert other.get(f'/v1/profiles/{viewer}').status_code == 404


def test_card_media_uses_same_private_boundary(actors):
    owner, viewer = actors
    ac, other = client(owner), client(viewer)
    result = upload(ac)
    assert result.status_code == 201
    url=result.json()[0]['url']
    full, card = other.get(url), other.get(url+'?size=card')
    assert card.status_code == 200 and card.headers['cache-control'] == 'private, no-store'
    image = Image.open(io.BytesIO(card.content))
    assert image.width <= 720 and image.height <= 900
    assert len(card.content) < len(full.content)
    assert TestClient(app).get(url+'?size=card').status_code == 401
    assert other.get(url+'?size=arbitrary').status_code == 422
    ac.patch('/v1/profiles/me',json={'is_discoverable':False})
    assert other.get(url+'?size=card').status_code == 404
    assert ac.get(url+'?size=card').status_code == 200
