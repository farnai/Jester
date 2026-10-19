import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import { useAuth } from '../../core/auth/useAuth';
import { ProfileImage } from '../../shared/ui/ProfileImage';
import '../chat/messaging.css';

export function MessagesPage() {
  const { user } = useAuth();
  const inbox = useQuery({ queryKey: ['conversations', user?.id], queryFn: API.conversations.list, retry: 1, networkMode: 'always' });
  return <div className="messaging-page">
    <header className="messaging-heading"><div><h1>საუბრები</h1><p>გააგრძელე დაწყებული საუბარი.</p></div><Link to="/connections">კავშირები →</Link></header>
    {inbox.isPending ? <p role="status">საუბრები იტვირთება…</p> : inbox.isError ? <div role="alert"><p>საუბრები ვერ ჩაიტვირთა.</p><button onClick={() => inbox.refetch()}>ხელახლა ცდა</button></div> : !inbox.data?.length ? <div className="messaging-empty"><h2>პირველი საუბარი წინ არის</h2><p>საუბრის დასაწყებად გახსენი მიღებული კავშირი.</p><Link to="/connections">ჩემი კავშირები</Link></div> : <div className="inbox-list">
      {inbox.data.map(item => <Link className="inbox-row" key={item.id} to={`/chat/${item.id}`} data-conversation-id={item.id}>
        <span className="messaging-avatar">{item.other_avatar_url ? <ProfileImage src={item.other_avatar_url} mediaSize="card" alt="" /> : <span aria-hidden="true">◎</span>}</span>
        <div className="inbox-copy"><strong>{item.other_display_name || 'მომხმარებელი'}</strong><p>{item.last_message ? `${item.last_message.sender_user_id === user?.id ? 'შენ: ' : ''}${item.last_message.body}` : 'მიმოწერა ჯერ არ დაწყებულა'}</p></div>
        <div className="inbox-meta"><time dateTime={item.last_activity_at}>{new Date(item.last_activity_at).toLocaleString('ka-GE', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</time>{item.unread_count > 0 && <span className="inbox-unread" aria-label={`${item.unread_count} წაუკითხავი შეტყობინება`}>{item.unread_count}</span>}</div>
      </Link>)}
    </div>}
  </div>;
}
