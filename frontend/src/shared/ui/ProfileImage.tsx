import { useEffect, useState, type ImgHTMLAttributes } from 'react';
import { useAuth } from '../../core/auth/useAuth';
import { CONFIG } from '../../core/config';
import { supabase } from '../../core/realtime/supabase';

// Private media never puts bearer tokens or reusable signed URLs in DOM URLs.
export function ProfileImage({ src, alt, ...props }: ImgHTMLAttributes<HTMLImageElement>) {
  const { user } = useAuth();
  const [loaded, setLoaded] = useState<{ key: string; url: string } | null>(null);
  const [failed, setFailed] = useState<string | null>(null);
  const key = `${user?.id}:${src}`;
  const isPrivate = /^\/v1\/profiles\/[0-9a-f-]+\/photos\/[0-9a-f-]+\/content$/i.test(src || '');
  useEffect(() => {
    if (!isPrivate || !user || !src) return;
    const controller = new AbortController();
    let objectUrl: string | undefined;
    void (async () => {
      try {
        const { data } = await supabase.auth.getSession();
        const response = await fetch(`${CONFIG.API_BASE_URL}${src}`, {
          headers: { Authorization: `Bearer ${data.session?.access_token || ''}` },
          cache: 'no-store', signal: controller.signal,
        });
        if (!response.ok) throw new Error('Photo unavailable');
        const blob = await response.blob();
        if (controller.signal.aborted) return;
        objectUrl = URL.createObjectURL(blob);
        setLoaded({ key, url: objectUrl });
      } catch {
        if (!controller.signal.aborted) setFailed(key);
      }
    })();
    return () => { controller.abort(); if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [key, isPrivate, src, user?.id]);
  const resolved = isPrivate ? (loaded?.key === key ? loaded.url : undefined) : src;
  if (!resolved || failed === key) return <span className="profile-image-placeholder" role="img" aria-label={failed === key ? 'ფოტო მიუწვდომელია' : 'ფოტო იტვირთება'} style={props.style}>{failed === key ? 'ფოტო მიუწვდომელია' : '…'}</span>;
  return <img {...props} src={resolved} alt={alt || ''} referrerPolicy="no-referrer" onError={e => { setFailed(key); props.onError?.(e); }} />;
}
