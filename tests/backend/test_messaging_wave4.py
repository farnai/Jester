"""UUID-scoped real database integration; no truncation of the primary database."""
import uuid
import time
import psycopg
from concurrent.futures import ThreadPoolExecutor
import pytest
from backend.app.core.database import db_manager
from tests.backend.test_social_profiles import client


@pytest.fixture
def users():
    ids=[uuid.uuid4() for _ in range(3)]
    with db_manager.get_connection() as db:
        for uid in ids:
            db.execute("INSERT INTO auth.users(id,email,raw_user_meta_data,role,aud) VALUES(%s,%s,'{}','authenticated','authenticated')", (uid,f'wave4-{uid}@example.invalid'))
            db.execute("INSERT INTO public.profiles(id,display_name) VALUES(%s,'Wave 4 test') ON CONFLICT(id) DO NOTHING",(uid,))
    try:
        yield ids
    finally:
        with db_manager.get_connection() as db:
            db.execute('DELETE FROM auth.users WHERE id=ANY(%s)',(ids,))


def connected(ids):
    a,b=client(ids[0]),client(ids[1])
    result=a.post('/v1/connections',json={'target_user_id':str(ids[1])})
    assert result.status_code==201,result.text
    cid=result.json()['id']
    assert b.post(f'/v1/connections/{cid}/transition',json={'action':'accept'}).status_code==200
    return a,b,cid


@pytest.mark.parametrize('blocking_index',[0,1])
def test_blocked_state_cannot_be_cleared_or_stolen(users,blocking_index):
    a,b,cid=connected(users)
    blocker,blocked=(a,b) if blocking_index==0 else (b,a)
    route=f'/v1/connections/{cid}/transition'
    assert blocker.post(route,json={'action':'block'}).status_code==200
    assert blocked.post('/v1/connections',json={'target_user_id':str(users[blocking_index])}).status_code==404
    for action in ('remove','block','unblock','accept','decline'):
        assert blocked.post(route,json={'action':action}).status_code==404
    assert blocker.post(route,json={'action':'remove'}).status_code==400
    assert blocker.post(route,json={'action':'block'}).json()['blocked_by']==str(users[blocking_index])
    with db_manager.get_connection() as db:
        row=db.execute('SELECT status,blocked_by FROM public.connections WHERE id=%s',(cid,)).fetchone()
        assert row=={'status':'blocked','blocked_by':users[blocking_index]}
    assert blocker.post(route,json={'action':'unblock'}).json()['status']=='removed'


def test_pagination_unread_nonce_and_privacy(users):
    a,b,cid=connected(users)
    with ThreadPoolExecutor(2) as pool:
        convs=list(pool.map(lambda _:client(users[0]).post('/v1/conversations',json={'target_user_id':str(users[1])}).json()['id'],range(2)))
    assert convs[0]==convs[1]
    conv=convs[0]; route=f'/v1/conversations/{conv}'
    assert client(users[2]).get(route).status_code==404
    assert client(users[2]).post('/v1/conversations',json={'target_user_id':str(users[0])}).status_code==403
    nonce=str(uuid.uuid4())
    with ThreadPoolExecutor(2) as pool:
        sent=list(pool.map(lambda _:client(users[0]).post(route+'/messages',json={'body':'გამარჯობა 👋','client_nonce':nonce}).json(),range(2)))
    assert sent[0]['id']==sent[1]['id']
    assert a.post(route+'/messages',json={'body':'different','client_nonce':nonce}).status_code==409
    for body in ('','   ','x'*2001):
        assert a.post(route+'/messages',json={'body':body}).status_code==400
    for i in range(34):
        assert a.post(route+'/messages',json={'body':f'Page item {i}'}).status_code==201
    inbox=b.get('/v1/conversations').json()[0]
    assert inbox['unread_count']==35 and inbox['other_display_name']=='Wave 4 test'
    assert a.get('/v1/conversations').json()[0]['unread_count']==0
    assert set(inbox['last_message'])=={'id','conversation_id','sender_user_id','body','created_at'}
    assert not {'birth_data','astro_private','birth_date','birth_time','client_nonce'} & inbox.keys()
    with db_manager.get_connection() as db:
        db.execute('UPDATE public.profiles SET is_discoverable=false WHERE id=%s',(users[0],))
    hidden=b.get('/v1/conversations').json()[0]
    assert hidden['other_display_name'] is None and hidden['other_avatar_url'] is None
    assert b.get(route).json()['other_display_name'] is None
    with db_manager.get_connection() as db:
        db.execute('UPDATE public.profiles SET is_discoverable=true WHERE id=%s',(users[0],))
    page=b.get(route+'/messages/page').json()
    assert len(page['items'])==30 and page['next_cursor']
    older=b.get(route+'/messages/page',params={'before':page['next_cursor']}).json()
    assert len(older['items'])==5 and older['next_cursor'] is None
    assert len({m['id'] for m in page['items']+older['items']})==35
    assert len(b.get(route+'/messages').json())==30
    assert b.get(route+'/messages/page?limit=101').status_code==422
    assert b.get(route+'/messages/page?before=bad').status_code==422
    assert b.get(route+'/messages/page?before='+str(uuid.uuid4())).status_code==404
    assert b.patch(route+'/read',json={'last_read_message_id':page['items'][-1]['id']}).json()['unread_count']==0
    a.post(route+'/messages',json={'body':'Arrived after read boundary'})
    assert b.patch(route+'/read',json={'last_read_message_id':older['items'][0]['id']}).json()['unread_count']==1
    assert b.get('/v1/conversations').json()[0]['unread_count']==1
    with db_manager.get_connection() as db:
        with db.transaction():
            db.execute('SET LOCAL ROLE authenticated')
            db.execute("SELECT set_config('request.jwt.claim.sub',%s,true)",(str(users[0]),))
            assert db.execute('SELECT * FROM public.conversation_reads WHERE conversation_id=%s',(conv,)).fetchall()==[]
        with pytest.raises(Exception):
            with db.transaction():
                db.execute('SET LOCAL ROLE authenticated')
                db.execute("SELECT set_config('request.jwt.claim.sub',%s,true)",(str(users[0]),))
                db.execute('UPDATE public.connections SET status=\'removed\' WHERE id=%s',(cid,))
    # Removal preserves storage but denies all future message operations.
    assert a.post(f'/v1/connections/{cid}/transition',json={'action':'remove'}).status_code==200
    for actor in (a,b):
        assert actor.get(route).status_code==404
        assert actor.get(route+'/messages/page').status_code==404
        assert actor.post(route+'/messages',json={'body':'denied','client_nonce':nonce}).status_code==404
        assert actor.patch(route+'/read',json={'last_read_message_id':sent[0]['id']}).status_code==404
        assert actor.get('/v1/conversations').json()==[]
    with db_manager.get_connection() as db:
        with pytest.raises(Exception):
            with db.transaction():
                db.execute('INSERT INTO public.messages(conversation_id,sender_user_id,body) VALUES(%s,%s,\'denied\')',(conv,users[0]))


def test_client_cannot_forge_accepted_connection(users):
    a,b=sorted(users[:2])
    with db_manager.get_connection() as db:
        with pytest.raises(Exception):
            with db.transaction():
                db.execute('SET LOCAL ROLE authenticated')
                db.execute("SELECT set_config('request.jwt.claim.sub',%s,true)",(str(a),))
                db.execute("INSERT INTO public.connections(user_a_id,user_b_id,status,initiated_by) VALUES(%s,%s,'accepted',%s)",(a,b,a))


def test_direct_client_send_waits_for_block_and_is_rejected(users):
    a,b,cid=connected(users)
    conv=a.post('/v1/conversations',json={'target_user_id':str(users[1])}).json()['id']
    tag='wave4-race-'+uuid.uuid4().hex
    def insert_as_recipient():
        with db_manager.get_connection() as writer:
            with writer.transaction():
                writer.execute("SELECT set_config('application_name',%s,true)",(tag,))
                writer.execute('SET LOCAL ROLE authenticated')
                writer.execute("SELECT set_config('request.jwt.claim.sub',%s,true)",(str(users[1]),))
                writer.execute("INSERT INTO public.messages(conversation_id,sender_user_id,body) VALUES(%s,%s,'racing blocked send')",(conv,users[1]))
    with ThreadPoolExecutor(1) as pool:
        with db_manager.get_connection() as db:
            with db.transaction():
                db.execute('SELECT id FROM public.connections WHERE id=%s FOR UPDATE',(cid,))
                pending=pool.submit(insert_as_recipient)
                # Prove that the INSERT is waiting on our connection lock.
                with db_manager.get_connection() as observer:
                    end=time.monotonic()+5
                    while time.monotonic()<end:
                        waiting=observer.execute("SELECT 1 FROM pg_stat_activity WHERE application_name=%s AND wait_event_type='Lock'",(tag,)).fetchone()
                        if waiting:
                            break
                        time.sleep(.02)
                    else:
                        pytest.fail('Direct INSERT did not wait for the connection lock')
                db.execute("UPDATE public.connections SET status='blocked',blocked_by=%s WHERE id=%s",(users[0],cid))
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                pending.result(timeout=5)
            assert db.execute('SELECT count(*) AS n FROM public.messages WHERE conversation_id=%s',(conv,)).fetchone()['n']==0
    assert b.post(f'/v1/conversations/{conv}/messages',json={'body':'after block'}).status_code==404
