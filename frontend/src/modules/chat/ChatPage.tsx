import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import { useAuth } from '../../core/auth/useAuth';
import { ProfileImage } from '../../shared/ui/ProfileImage';
import { chronologicalMessages, isUnavailable, submission } from './messagingModel';
import './messaging.css';

function Unavailable() { return <div className="messaging-empty" role="status"><h1>საუბარი მიუწვდომელია</h1><p>აქტიური კავშირის გარეშე მიმოწერა მიუწვდომელია.</p><Link to="/messages">← საუბრებში დაბრუნება</Link></div>; }
export function ChatPage() {
  const { conversation_id = '' } = useParams();
  const { user } = useAuth();
  return /^[0-9a-f-]{36}$/i.test(conversation_id) ? <Conversation key={`${user?.id}:${conversation_id}`} id={conversation_id} /> : <Unavailable />;
}

function Conversation({ id }: { id: string }) {
  const { user } = useAuth();
  const [params] = useSearchParams();
  const cache = useQueryClient();
  const [text, setText] = useState((params.get('starter') || '').slice(0,2000));
  const [startersOpen, setStartersOpen] = useState(false);
  const [atBottom, setAtBottom] = useState(true);
  const [visible, setVisible] = useState(document.visibilityState === 'visible');
  const [readError, setReadError] = useState(false);
  const root = useRef<HTMLDivElement>(null), stream = useRef<HTMLDivElement>(null), input = useRef<HTMLTextAreaElement>(null);
  const nearBottom = useRef(true), olderAnchor = useRef<{height: number; top: number} | null>(null);
  const attempt = useRef<{body:string;nonce:string} | undefined>(undefined);
  const acknowledged = useRef('');
  const conversation = useQuery({ queryKey: ['conversation', id], queryFn: () => API.conversations.get(id), retry: false, networkMode: 'always' });
  const history = useInfiniteQuery({
    queryKey: ['messages', id], initialPageParam: '',
    queryFn: ({ pageParam, signal }) => API.conversations.messagePage(id, pageParam || undefined, signal),
    getNextPageParam: page => page.next_cursor || undefined,
    enabled: !!conversation.data && !conversation.isError, retry: 1, networkMode: 'always', refetchInterval: 15000,
  });
  const messages = useMemo(() => chronologicalMessages(history.data?.pages), [history.data]);
  const lastId = messages[messages.length - 1]?.id;
  const why = useQuery({ queryKey: ['why-starters', conversation.data?.other_member_id], queryFn: () => API.compatibility.why(conversation.data!.other_member_id!), enabled: startersOpen && !!conversation.data?.other_member_id && !conversation.isError, retry: false });
  const starters = (why.data?.conversation_starters || []).filter((s): s is string => typeof s === 'string' && !!s.trim()).slice(0,3);
  const send = useMutation({
    mutationFn: (item: {body:string;nonce:string}) => API.conversations.sendMessage(id,item.body,item.nonce),
    networkMode: 'always', retry: false,
    onSuccess: () => {
      setText(''); attempt.current = undefined; nearBottom.current = true; setAtBottom(true);
      void cache.invalidateQueries({ queryKey: ['messages',id] }, { cancelRefetch: false });
      void cache.invalidateQueries({ queryKey: ['conversations'] });
      input.current?.focus();
    },
    onError: error => { if (isUnavailable(error)) void conversation.refetch(); },
  });
  const sendText = () => {
    if (!text.trim() || send.isPending) return;
    attempt.current = submission(text,attempt.current);
    send.mutate(attempt.current);
  };
  useEffect(() => {
    const onVisibility = () => setVisible(document.visibilityState === 'visible');
    document.addEventListener('visibilitychange',onVisibility);
    return () => document.removeEventListener('visibilitychange',onVisibility);
  }, []);
  useEffect(() => {
    if (!lastId || !visible || !atBottom || conversation.isError || history.isError || acknowledged.current === lastId) return;
    let active = true;
    void API.conversations.markRead(id,lastId).then(() => {
      if (!active) return;
      acknowledged.current = lastId; setReadError(false);
      void cache.invalidateQueries({ queryKey: ['conversations'] });
    }).catch(() => { if (active) setReadError(true); });
    return () => { active = false; };
  }, [lastId, visible, atBottom, id, conversation.isError, history.isError, history.dataUpdatedAt, cache]);
  useLayoutEffect(() => {
    const el = stream.current; if (!el) return;
    if (olderAnchor.current) {
      el.scrollTop = olderAnchor.current.top + el.scrollHeight - olderAnchor.current.height;
      olderAnchor.current = null;
    } else if (nearBottom.current) el.scrollTop = el.scrollHeight;
  }, [messages.length,lastId]);
  useEffect(() => {
    const resize = () => {
      if (!root.current) return;
      const viewport = window.visualViewport;
      const keyboard = !!viewport && window.innerHeight - viewport.height > 100;
      document.body.classList.toggle('chat-keyboard-open', keyboard);
      const nav = document.querySelector('.home-mobile-navigation');
      const navHeight = !keyboard && nav ? nav.getBoundingClientRect().height : 0;
      const available = (viewport?.height || innerHeight) + (viewport?.offsetTop || 0) - root.current.getBoundingClientRect().top - navHeight - 16;
      root.current.style.setProperty('--chat-height', `${Math.max(180,available)}px`);
      if (nearBottom.current && stream.current) stream.current.scrollTop = stream.current.scrollHeight;
    };
    resize(); window.addEventListener('resize',resize);
    window.visualViewport?.addEventListener('resize',resize); window.visualViewport?.addEventListener('scroll',resize);
    return () => { window.removeEventListener('resize',resize); window.visualViewport?.removeEventListener('resize',resize); window.visualViewport?.removeEventListener('scroll',resize); document.body.classList.remove('chat-keyboard-open'); };
  }, [conversation.isPending,history.isPending]);
  if (isUnavailable(conversation.error) || isUnavailable(history.error) || isUnavailable(send.error)) return <Unavailable />;
  if (conversation.isPending) return <p role="status">საუბარი იტვირთება…</p>;
  if (conversation.isError && !conversation.data) return <div role="alert"><p>საუბარი ვერ ჩაიტვირთა.</p><button onClick={() => conversation.refetch()}>ხელახლა ცდა</button></div>;
  const person = conversation.data!;
  return <div ref={root} className="chat-room">
    <header className="chat-header"><Link className="chat-back" to="/messages" aria-label="საუბრებში დაბრუნება">←</Link><span className="messaging-avatar">{person.other_avatar_url ? <ProfileImage src={person.other_avatar_url} mediaSize="card" alt="" /> : <span aria-hidden="true">◎</span>}</span><Link className="chat-person" to={`/people/${person.other_member_id}`}>{person.other_display_name || 'მომხმარებელი'}</Link><Link className="chat-manage" to="/connections">კავშირი</Link></header>
    {conversation.isError && <p className="chat-notice" role="status">კავშირი ვერ განახლდა. ტექსტი შენარჩუნებულია. <button onClick={() => conversation.refetch()}>ხელახლა ცდა</button></p>}
    <div className="chat-stream" ref={stream} role="log" aria-label="მიმოწერა" aria-live="polite" aria-relevant="additions" onScroll={() => { const el=stream.current!; const bottom=el.scrollHeight-el.scrollTop-el.clientHeight<48; nearBottom.current=bottom; setAtBottom(bottom); }}>
      {history.isPending && <p role="status">შეტყობინებები იტვირთება…</p>}
      {history.isError && <div role="alert"><p>შეტყობინებები ვერ განახლდა.</p><button onClick={() => history.refetch()}>ხელახლა ცდა</button></div>}
      {history.hasNextPage && <button className="chat-older" disabled={history.isFetching} onClick={() => { const el=stream.current!; olderAnchor.current={height:el.scrollHeight,top:el.scrollTop}; nearBottom.current=false; void history.fetchNextPage().then(r => { if (r.isError) olderAnchor.current=null; }); }}>ძველი შეტყობინებები</button>}
      {!history.isPending && !history.isError && !messages.length && <div className="messaging-empty"><h2>საუბარი აქ იწყება</h2><p>მიესალმე ან აირჩიე JESTER-ის სასაუბრო ფრაზა.</p></div>}
      {messages.map(m => <article className={`chat-message${m.sender_user_id===user?.id?' is-mine':''}`} key={m.id} data-message-id={m.id}><p>{m.body}</p><time dateTime={m.created_at}>{new Date(m.created_at).toLocaleString('ka-GE',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})}</time></article>)}
    </div>
    {!atBottom && <button className="chat-latest" onClick={() => { nearBottom.current=true; setAtBottom(true); if(stream.current) stream.current.scrollTop=stream.current.scrollHeight; }}>ბოლო შეტყობინებებზე ↓</button>}
    <details className="chat-starters" open={startersOpen} onToggle={e => setStartersOpen(e.currentTarget.open)}><summary>JESTER · საუბრის დასაწყისი</summary>{startersOpen && <div>{why.isPending ? <p role="status">ფრაზები იტვირთება…</p> : why.isError ? <p>ფრაზები ვერ ჩაიტვირთა. <button onClick={() => why.refetch()}>ხელახლა ცდა</button></p> : starters.length ? starters.map((starter,i) => <button key={i} onClick={() => { setText(starter.slice(0,2000)); setStartersOpen(false); input.current?.focus(); }}>{starter}</button>) : <p>სასაუბრო ფრაზები ამ კავშირისთვის ჯერ მიუწვდომელია.</p>}</div>}</details>
    {readError && <p className="chat-notice" role="status">წაკითხვის მდგომარეობა ჯერ ვერ შეინახა. ხელახლა ვცდით განახლებისას.</p>}
    {send.isError && <div className="chat-send-error" role="alert"><span>ვერ დადასტურდა გაგზავნა. ტექსტი შენარჩუნებულია.</span><button disabled={send.isPending || !text.trim()} onClick={sendText}>ხელახლა გაგზავნა</button></div>}
    <form className="chat-composer" onSubmit={e => { e.preventDefault(); sendText(); }}><label className="chat-input-label"><span className="chat-sr">შეტყობინება</span><textarea ref={input} aria-label="შეტყობინება" rows={2} maxLength={2000} value={text} disabled={send.isPending} onChange={e => setText(e.target.value)} placeholder="დაწერე შეტყობინება…" onKeyDown={e => { if (e.key==='Enter' && (e.ctrlKey || e.metaKey) && !e.nativeEvent.isComposing) { e.preventDefault(); sendText(); } }} /></label><button type="submit" disabled={send.isPending || !text.trim()}>{send.isPending?'იგზავნება…':'გაგზავნა'}</button></form>
  </div>;
}
