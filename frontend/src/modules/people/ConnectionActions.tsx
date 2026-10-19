import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import { useAuth } from '../../core/auth/useAuth';
import './connection-actions.css';
import { refreshSocial } from '../../core/realtime/SocialSync';

export function ConnectionActions({ target, name, confirmSignal = 0, compact = false }: {
  target: string; name: string; confirmSignal?: number; compact?: boolean;
}) {
  const { user } = useAuth();
  const cache = useQueryClient();
  const navigate = useNavigate();
  const dialog = useRef<HTMLDialogElement>(null);
  const previousSignal = useRef(confirmSignal);
  const [confirming, setConfirming] = useState(false);
  const connections = useQuery({ queryKey: ['connections'], queryFn: API.connections.list, refetchInterval: 15000 });
  const connection = connections.data?.find(c => (c.user_a_id === target && c.user_b_id === user?.id) || (c.user_b_id === target && c.user_a_id === user?.id));
  const state = connection?.status === 'blocked' ? 'blocked' : connection?.status === 'accepted' ? 'accepted' : connection?.status === 'pending' ? connection.initiated_by === user?.id ? 'pending_out' : 'pending_in' : 'none';
  const mutation = useMutation({
    mutationFn: async (action: 'request' | 'accept' | 'decline' | 'chat') => {
      if (action === 'chat') { const conversation = await API.conversations.createOrGetDirect(target); navigate(`/chat/${conversation.id}`); return; }
      if (action === 'request') return API.connections.create(target);
      if (!connection) throw new Error('კავშირი მიუწვდომელია.');
      return API.connections.transition(connection.id, action);
    },
    onSuccess: () => {
      setConfirming(false);
      refreshSocial(cache);
      cache.invalidateQueries({ queryKey: ['connections'] });
      cache.invalidateQueries({ queryKey: ['discovery-deck'] });
      cache.invalidateQueries({ queryKey: ['why-experience', target] });
      cache.invalidateQueries({ queryKey: ['compatibility-us', target] });
    },
  });
  useEffect(() => {
    if (confirmSignal !== previousSignal.current) {
      previousSignal.current = confirmSignal;
      if (state === 'none' && connections.data) { mutation.reset(); setConfirming(true); }
    }
  }, [confirmSignal, state, connections.data]);
  useEffect(() => {
    if (confirming && state === 'none') dialog.current?.showModal();
    else dialog.current?.close();
  }, [confirming, state]);
  if (target === user?.id) return null;
  return <div className={`connection-actions${compact ? ' is-compact' : ''}`} data-state={state}>
    {connections.isPending ? <span role="status">იტვირთება…</span> : connections.isError ? <button onClick={() => connections.refetch()}>კავშირის ხელახლა შემოწმება</button> : <>
      {state === 'none' && <button className="connect-primary" onClick={() => { mutation.reset(); setConfirming(true); }}>დაკავშირება</button>}
      {state === 'pending_out' && <span className="connection-pending" role="status">მოთხოვნა გაგზავნილია</span>}
      {state === 'pending_in' && <><button className="connect-primary" disabled={mutation.isPending} onClick={() => mutation.mutate('accept')}>მოთხოვნის მიღება</button><button disabled={mutation.isPending} onClick={() => mutation.mutate('decline')}>უარყოფა</button></>}
      {state === 'accepted' && <><button className="connect-primary" disabled={mutation.isPending} onClick={() => mutation.mutate('chat')}>საუბარი</button>{!compact && <Link to={`/people/${target}/why`}>ჩვენი კავშირი · Why</Link>}</>}
      {state === 'blocked' && <span role="status">პროფილი მიუწვდომელია</span>}
    </>}
    {!confirming && mutation.error && <p role="alert">{mutation.error.message}</p>}
    <dialog ref={dialog} className="connection-dialog" aria-labelledby={`connect-title-${target}`} onCancel={() => setConfirming(false)} onClick={e => { if (e.target === e.currentTarget && !mutation.isPending) setConfirming(false); }}>
      <h2 id={`connect-title-${target}`}>გავუგზავნოთ კავშირის მოთხოვნა?</h2>
      <p>{name} მიიღებს შენს მოთხოვნას. მიმოწერა გაიხსნება მხოლოდ მიღების შემდეგ.</p>
      <div><button autoFocus disabled={mutation.isPending} onClick={() => setConfirming(false)}>ჯერ არა</button><button className="connect-primary" disabled={mutation.isPending} onClick={() => mutation.mutate('request')}>{mutation.isPending ? 'იგზავნება…' : 'მოთხოვნის გაგზავნა'}</button></div>
      {mutation.error && <p role="alert">{mutation.error.message}</p>}
    </dialog>
  </div>;
}
