"""Accepted-connection messaging. All mutations serialize on the connection row."""
import uuid
from fastapi import APIRouter, Depends, Query, status
from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.core.errors import ForbiddenException, JesterAPIException, PrivacySafeNotFoundException
from backend.app.conversations.models import (ConversationInboxResponse, ConversationResponse,
    DirectConversationCreate, MessageCreate, MessageResponse, MessagePage, ReadUpdate)

router = APIRouter(prefix="/conversations", tags=["conversations"])


def authorize(db, cid, viewer, lock=False):
    suffix = ' FOR UPDATE OF connection' if lock else ''
    row = db.execute("""SELECT connection.id, connection.status, connection.blocked_by,
        other.user_id AS other_id
        FROM public.conversations c
        JOIN public.conversation_members mine ON mine.conversation_id=c.id AND mine.user_id=%s
        JOIN public.conversation_members other ON other.conversation_id=c.id AND other.user_id<>%s
        JOIN public.connections connection ON connection.user_a_id=least(mine.user_id,other.user_id)
          AND connection.user_b_id=greatest(mine.user_id,other.user_id)
        WHERE c.id=%s AND c.conversation_type='direct'""" + suffix, (viewer,viewer,cid)).fetchone()
    if not row or row['status'] != 'accepted' or row['blocked_by'] is not None:
        raise PrivacySafeNotFoundException('Conversation not found')
    return row['other_id']


def unread(db, cid, viewer):
    return db.execute("""SELECT count(*) AS n FROM public.messages m
        LEFT JOIN public.conversation_reads r ON r.conversation_id=m.conversation_id AND r.user_id=%s
        LEFT JOIN public.messages seen ON seen.id=r.last_read_message_id
        WHERE m.conversation_id=%s AND m.sender_user_id<>%s
          AND (seen.id IS NULL OR (m.created_at,m.id)>(seen.created_at,seen.id))""", (viewer,cid,viewer)).fetchone()['n']


def details(db, cid, viewer):
    row=db.execute("""SELECT c.*, other.user_id AS other_member_id,
        p.display_name AS other_display_name, p.avatar_url AS other_avatar_url
        FROM public.conversations c
        JOIN public.conversation_members other ON other.conversation_id=c.id AND other.user_id<>%s
        LEFT JOIN public.profiles p ON p.id=other.user_id AND p.is_discoverable
        WHERE c.id=%s""", (viewer,cid)).fetchone()
    return ConversationResponse(**row)


@router.get('', response_model=list[ConversationInboxResponse])
def list_my_conversations(current_user: AuthenticatedUser=Depends(get_current_user), db=Depends(get_db)):
    rows=db.execute("""SELECT c.id, other.user_id AS other_member_id, c.updated_at,
        p.display_name AS other_display_name, p.avatar_url AS other_avatar_url,
        to_jsonb(latest) AS last_message, coalesce(latest.created_at,c.updated_at) AS last_activity_at,
        (SELECT count(*) FROM public.messages m WHERE m.conversation_id=c.id AND m.sender_user_id<>%s
          AND (seen.id IS NULL OR (m.created_at,m.id)>(seen.created_at,seen.id))) AS unread_count
        FROM public.conversations c
        JOIN public.conversation_members mine ON mine.conversation_id=c.id AND mine.user_id=%s
        JOIN public.conversation_members other ON other.conversation_id=c.id AND other.user_id<>%s
        LEFT JOIN public.profiles p ON p.id=other.user_id AND p.is_discoverable
        LEFT JOIN public.conversation_reads r ON r.conversation_id=c.id AND r.user_id=%s
        LEFT JOIN public.messages seen ON seen.id=r.last_read_message_id
        LEFT JOIN LATERAL (SELECT id,conversation_id,sender_user_id,body,created_at FROM public.messages
          WHERE conversation_id=c.id ORDER BY created_at DESC,id DESC LIMIT 1) latest ON true
        WHERE c.conversation_type='direct' AND public.is_active_direct_conversation(c.id,%s)
        ORDER BY coalesce(latest.created_at,c.updated_at) DESC,c.id DESC""", (current_user.id,)*5).fetchall()
    return [ConversationInboxResponse(**row) for row in rows]


@router.post('', response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_or_get_direct_conversation(payload: DirectConversationCreate,
        current_user: AuthenticatedUser=Depends(get_current_user), db=Depends(get_db)):
    a,b=sorted([current_user.id,payload.target_user_id])
    with db.transaction():
        relation=db.execute('SELECT * FROM public.connections WHERE user_a_id=%s AND user_b_id=%s FOR UPDATE', (a,b)).fetchone()
        if relation and relation['status']=='blocked':
            raise PrivacySafeNotFoundException('Conversation not found')
        if not relation or relation['status']!='accepted':
            raise ForbiddenException('Active connection required to create a direct conversation')
        existing=db.execute("""SELECT c.id FROM public.conversations c
            JOIN public.conversation_members a ON a.conversation_id=c.id AND a.user_id=%s
            JOIN public.conversation_members b ON b.conversation_id=c.id AND b.user_id=%s
            WHERE c.conversation_type='direct' ORDER BY c.created_at,c.id LIMIT 1""", (a,b)).fetchone()
        if existing:
            return details(db,existing['id'],current_user.id)
        cid=uuid.uuid4()
        db.execute("INSERT INTO public.conversations(id,conversation_type,created_by) VALUES(%s,'direct',%s)", (cid,current_user.id))
        db.execute('INSERT INTO public.conversation_members(conversation_id,user_id) VALUES(%s,%s),(%s,%s)', (cid,a,cid,b))
        return details(db,cid,current_user.id)


@router.get('/{conversation_id}', response_model=ConversationResponse)
def get_conversation_details(conversation_id: uuid.UUID, current_user: AuthenticatedUser=Depends(get_current_user), db=Depends(get_db)):
    authorize(db,conversation_id,current_user.id)
    return details(db,conversation_id,current_user.id)


def message_page(db,cid,viewer,limit,before):
    authorize(db,cid,viewer)
    boundary=None
    if before:
        boundary=db.execute('SELECT created_at,id FROM public.messages WHERE id=%s AND conversation_id=%s', (before,cid)).fetchone()
        if not boundary:
            raise PrivacySafeNotFoundException('Message cursor not found')
    rows=db.execute("""SELECT id,conversation_id,sender_user_id,body,created_at FROM public.messages
        WHERE conversation_id=%s AND (%s::timestamptz IS NULL OR (created_at,id)<(%s,%s))
        ORDER BY created_at DESC,id DESC LIMIT %s""", (cid,boundary['created_at'] if boundary else None,
        boundary['created_at'] if boundary else None,before,limit+1)).fetchall()
    more=len(rows)>limit
    rows=rows[:limit]
    return MessagePage(items=[MessageResponse(**row) for row in reversed(rows)],next_cursor=rows[-1]['id'] if more else None)


@router.get('/{conversation_id}/messages/page', response_model=MessagePage)
def paged_messages(conversation_id: uuid.UUID, limit: int=Query(30,ge=1,le=100), before: uuid.UUID|None=None,
        current_user: AuthenticatedUser=Depends(get_current_user), db=Depends(get_db)):
    return message_page(db,conversation_id,current_user.id,limit,before)


@router.get('/{conversation_id}/messages', response_model=list[MessageResponse])
def list_messages(conversation_id: uuid.UUID, limit: int=Query(30,ge=1,le=100), before: uuid.UUID|None=None,
        current_user: AuthenticatedUser=Depends(get_current_user), db=Depends(get_db)):
    # Retain list shape for older consumers, bounded to the latest page.
    return message_page(db,conversation_id,current_user.id,limit,before).items


@router.post('/{conversation_id}/messages', response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(conversation_id: uuid.UUID, payload: MessageCreate,
        current_user: AuthenticatedUser=Depends(get_current_user), db=Depends(get_db)):
    body=payload.body.strip()
    if not body or len(body)>2000:
        raise JesterAPIException(400,'invalid_message_body','Message must contain 1 to 2000 characters')
    with db.transaction():
        authorize(db,conversation_id,current_user.id,lock=True)
        if payload.client_nonce:
            existing=db.execute('SELECT * FROM public.messages WHERE conversation_id=%s AND sender_user_id=%s AND client_nonce=%s',
                (conversation_id,current_user.id,payload.client_nonce)).fetchone()
            if existing:
                if existing['body'] != body:
                    raise JesterAPIException(409,'message_nonce_conflict','Retry identifier already belongs to another message')
                return MessageResponse(**existing)
        row=db.execute("""INSERT INTO public.messages(conversation_id,sender_user_id,body,client_nonce,created_at)
            VALUES(%s,%s,%s,%s,clock_timestamp()) RETURNING *""", (conversation_id,current_user.id,body,payload.client_nonce)).fetchone()
        return MessageResponse(**row)


@router.patch('/{conversation_id}/read')
def mark_read(conversation_id: uuid.UUID, payload: ReadUpdate,
        current_user: AuthenticatedUser=Depends(get_current_user), db=Depends(get_db)):
    with db.transaction():
        authorize(db,conversation_id,current_user.id,lock=True)
        seen=db.execute('SELECT id,created_at FROM public.messages WHERE id=%s AND conversation_id=%s',
            (payload.last_read_message_id,conversation_id)).fetchone()
        if not seen:
            raise PrivacySafeNotFoundException('Message not found')
        old=db.execute("""SELECT m.id,m.created_at FROM public.conversation_reads r
            JOIN public.messages m ON m.id=r.last_read_message_id WHERE r.conversation_id=%s AND r.user_id=%s""", (conversation_id,current_user.id)).fetchone()
        if not old or (seen['created_at'],seen['id'])>(old['created_at'],old['id']):
            db.execute("""INSERT INTO public.conversation_reads(conversation_id,user_id,last_read_message_id) VALUES(%s,%s,%s)
                ON CONFLICT(conversation_id,user_id) DO UPDATE SET last_read_message_id=excluded.last_read_message_id""",
                (conversation_id,current_user.id,seen['id']))
        return {'status':'ok','unread_count':unread(db,conversation_id,current_user.id)}
