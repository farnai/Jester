import { Link, useSearchParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import { useAuth } from '../../core/auth/useAuth';
import { refreshSocial } from '../../core/realtime/SocialSync';
import { ProfileImage } from '../../shared/ui/ProfileImage';
import { ConnectionActions } from '../people/ConnectionActions';
import '../chat/messaging.css';

export function ConnectionsPage() {
  const { user } = useAuth();
  const cache = useQueryClient();
  const [params, setParams] = useSearchParams();
  const tab = params.get('tab') || 'active';
  const connections = useQuery({ queryKey: ['connections'], queryFn: API.connections.list, retry: 1, networkMode: 'always' });
  const mutation = useMutation({ mutationFn: ({ id, action }: { id: string; action: 'block' | 'unblock' | 'remove' }) => API.connections.transition(id,action), onSuccess: () => refreshSocial(cache) });
  const all = connections.data || [];
  const groups = {
    active: all.filter(c => c.status === 'accepted'), incoming: all.filter(c => c.status === 'pending' && c.initiated_by !== user?.id),
    outgoing: all.filter(c => c.status === 'pending' && c.initiated_by === user?.id), blocked: all.filter(c => c.status === 'blocked' && c.blocked_by === user?.id),
  };
  const selected = tab in groups ? tab as keyof typeof groups : 'active';
  return <div className="messaging-page">
    <header className="messaging-heading"><h1>კავშირები</h1><Link to="/discover">აღმოჩენა →</Link></header>
    <nav className="connection-tabs" aria-label="კავშირების ჯგუფები">{([['active','მიღებული'],['incoming','შემოსული'],['outgoing','გაგზავნილი'],['blocked','დაბლოკილი']] as const).map(([key,label]) => <button key={key} aria-pressed={selected === key} onClick={() => setParams({tab:key})}>{label} ({groups[key].length})</button>)}</nav>
    {mutation.error && <p role="alert">{mutation.error.message}</p>}
    {connections.isPending ? <p role="status">კავშირები იტვირთება…</p> : connections.isError ? <div role="alert"><p>კავშირები ვერ ჩაიტვირთა.</p><button onClick={() => connections.refetch()}>ხელახლა ცდა</button></div> : !groups[selected].length ? <div className="messaging-empty"><p>ამ ჯგუფში კავშირები ჯერ არ არის.</p><Link to="/discover">აღმოაჩინე ადამიანები</Link></div> : groups[selected].map(c => {
      const target = c.user_a_id === user?.id ? c.user_b_id : c.user_a_id;
      const name = c.other_display_name || 'მომხმარებელი';
      return <article className="connection-row" key={c.id} data-connection-id={c.id}>
        <div className="connection-identity"><span className="messaging-avatar">{c.other_avatar_url ? <ProfileImage src={c.other_avatar_url} alt="" mediaSize="card" /> : <span aria-hidden="true">◎</span>}</span><div>{selected === 'blocked' ? <strong>დაბლოკილი კავშირი</strong> : <Link to={`/people/${target}`}>{name}</Link>}<p>{selected === 'incoming' ? 'გთავაზობს დაკავშირებას' : selected === 'outgoing' ? 'ელოდება პასუხს' : selected === 'active' ? 'შეგიძლიათ საუბრის დაწყება' : 'ბლოკის მოხსნა კავშირს არ აღადგენს'}</p></div></div>
        <div className="connection-row-actions">{selected !== 'blocked' && <ConnectionActions target={target} name={name} />}
          {selected === 'blocked' ? <button disabled={mutation.isPending} onClick={() => mutation.mutate({id:c.id,action:'unblock'})}>ბლოკის მოხსნა</button> : <>
            {(selected === 'active' || selected === 'outgoing') && <button disabled={mutation.isPending} onClick={() => { if (window.confirm('გაუქმდეს ეს კავშირი? მიმოწერა შეწყდება.')) mutation.mutate({id:c.id,action:'remove'}); }}>{selected === 'outgoing' ? 'მოთხოვნის გაუქმება' : 'კავშირის გაუქმება'}</button>}
            <button disabled={mutation.isPending} onClick={() => { if (window.confirm('დაიბლოკოს მომხმარებელი? მიმოწერა მიუწვდომელი გახდება.')) mutation.mutate({id:c.id,action:'block'}); }}>დაბლოკვა</button>
          </>}
        </div>
      </article>;
    })}
  </div>;
}
