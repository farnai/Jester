import { useEffect, useRef } from 'react';
import { useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query';
import { useAuth } from '../auth/useAuth';
import { API } from '../api/endpoints';
import { supabase } from './supabase';

export function refreshSocial(cache: QueryClient) {
  for (const key of ['connections', 'conversations', 'conversation', 'messages', 'discovery-deck', 'profile', 'photos', 'person-interests', 'why-starters', 'why-experience', 'compatibility-us']) {
    void cache.invalidateQueries({ queryKey: [key] }, { cancelRefetch: false });
  }
}

// One authenticated subscription per app session. Events are invalidation signals;
// message bodies are always reread through the authorized, bounded HTTP API.
export function SocialSync() {
  const { user } = useAuth();
  const cache = useQueryClient();
  const previous = useRef('');
  const connections = useQuery({ queryKey: ['connections'], queryFn: API.connections.list, enabled: !!user, refetchInterval: 5000 });
  useEffect(() => {
    const signature = JSON.stringify(connections.data?.map(c => [c.id, c.status, c.blocked_by]));
    if (previous.current && previous.current !== signature) refreshSocial(cache);
    previous.current = signature;
  }, [connections.data, cache]);
  useEffect(() => {
    if (!user) return;
    let active = true;
    const refresh = () => { if (active) refreshSocial(cache); };
    const channel = supabase.channel(`social:${user.id}`)
      .on('postgres_changes', { event: '*', schema: 'public', table: 'connections' }, refresh)
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'messages' }, () => {
        if (!active) return;
        void cache.invalidateQueries({ queryKey: ['messages'] }, { cancelRefetch: false });
        void cache.invalidateQueries({ queryKey: ['conversations'] });
      }).subscribe(state => { if (state === 'SUBSCRIBED') refresh(); });
    const visible = () => { if (document.visibilityState === 'visible') refresh(); };
    window.addEventListener('online', refresh);
    document.addEventListener('visibilitychange', visible);
    // A blocked recipient cannot receive the now-invisible connection's event.
    // Authorized HTTP polling also recovers after missed/rejected realtime events.
    const timer = window.setInterval(() => {
      if (document.visibilityState !== 'visible') return;
      void cache.invalidateQueries({ queryKey: ['conversation'] });
      void cache.invalidateQueries({ queryKey: ['conversations'] });
    }, 5000);
    return () => {
      active = false; clearInterval(timer); previous.current = '';
      window.removeEventListener('online', refresh);
      document.removeEventListener('visibilitychange', visible);
      void supabase.removeChannel(channel);
    };
  }, [user?.id, cache]);
  return null;
}
