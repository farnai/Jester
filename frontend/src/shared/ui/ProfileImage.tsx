import { useEffect, useRef, useState, type ImgHTMLAttributes, type SyntheticEvent } from 'react';
import { useAuth } from '../../core/auth/useAuth';
import { CONFIG } from '../../core/config';
import { supabase } from '../../core/realtime/supabase';

const MAX_BLOB_CACHE_ENTRIES = 64;
const privateBlobCache = new Map<string, string>();
const inflightPrivateFetches = new Map<string, Promise<string>>();
let activeCacheUserId: string | null = null;

function clearPrivateBlobCache() {
  const urls = [...privateBlobCache.values()];
  privateBlobCache.clear();
  inflightPrivateFetches.clear();
  activeCacheUserId = null;
  window.setTimeout(() => {
    for (const objectUrl of urls) {
      URL.revokeObjectURL(objectUrl);
    }
  }, 300);
}

function syncBlobCacheOwner(userId: string | null) {
  if (!userId) return;
  if (activeCacheUserId && activeCacheUserId !== userId) {
    clearPrivateBlobCache();
  }
  activeCacheUserId = userId;
}

if (typeof window !== 'undefined' && supabase?.auth?.onAuthStateChange) {
  supabase.auth.onAuthStateChange((event) => {
    if (event === 'SIGNED_OUT') {
      clearPrivateBlobCache();
    }
  });
}

function rememberPrivateBlob(key: string, candidateUrl: string): string {
  const existing = privateBlobCache.get(key);
  if (existing) {
    if (existing !== candidateUrl) {
      URL.revokeObjectURL(candidateUrl);
    }
    return existing;
  }
  if (privateBlobCache.size >= MAX_BLOB_CACHE_ENTRIES) {
    const oldestKey = privateBlobCache.keys().next().value;
    if (oldestKey) {
      const oldestUrl = privateBlobCache.get(oldestKey);
      privateBlobCache.delete(oldestKey);
      if (oldestUrl) {
        window.setTimeout(() => URL.revokeObjectURL(oldestUrl), 300);
      }
    }
  }
  privateBlobCache.set(key, candidateUrl);
  return candidateUrl;
}

function fetchPrivateBlobOnce(
  key: string,
  src: string,
  mediaSize: 'full' | 'card'
): Promise<string> {
  const hit = privateBlobCache.get(key);
  if (hit) return Promise.resolve(hit);

  const inflight = inflightPrivateFetches.get(key);
  if (inflight) return inflight;

  const task = (async () => {
    const { data } = await supabase.auth.getSession();
    const response = await fetch(
      `${CONFIG.API_BASE_URL}${src}${mediaSize === 'card' ? '?size=card' : ''}`,
      {
        headers: { Authorization: `Bearer ${data.session?.access_token || ''}` },
        cache: 'no-store',
      }
    );
    if (!response.ok) throw new Error('Photo unavailable');
    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    return rememberPrivateBlob(key, objectUrl);
  })().finally(() => {
    inflightPrivateFetches.delete(key);
  });

  inflightPrivateFetches.set(key, task);
  return task;
}

// Private media never puts bearer tokens or reusable signed URLs in DOM URLs.
export function ProfileImage({
  src,
  alt,
  mediaSize = 'full',
  onError,
  onLoad,
  ...props
}: ImgHTMLAttributes<HTMLImageElement> & { mediaSize?: 'full' | 'card' }) {
  const { user } = useAuth();
  syncBlobCacheOwner(user?.id ?? null);

  const key = `${user?.id}:${src}:${mediaSize}`;
  const isPrivate = /^\/v1\/profiles\/[0-9a-f-]+\/photos\/[0-9a-f-]+\/content$/i.test(src || '');
  const cachedUrl = isPrivate && user?.id ? privateBlobCache.get(key) : undefined;

  const [loaded, setLoaded] = useState<{ key: string; url: string } | null>(() =>
    cachedUrl ? { key, url: cachedUrl } : null
  );
  const [failed, setFailed] = useState<string | null>(null);
  const onErrorRef = useRef(onError);
  onErrorRef.current = onError;
  const onLoadRef = useRef(onLoad);
  onLoadRef.current = onLoad;
  const notifiedKeyRef = useRef<string | null>(null);

  useEffect(() => {
    if (!isPrivate || !user || !src) return;
    const hit = privateBlobCache.get(key);
    if (hit) {
      setLoaded((prev) => (prev?.key === key && prev.url === hit ? prev : { key, url: hit }));
      return;
    }

    let cancelled = false;
    void fetchPrivateBlobOnce(key, src, mediaSize)
      .then((objectUrl) => {
        if (!cancelled) {
          setLoaded({ key, url: objectUrl });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setFailed(key);
          onErrorRef.current?.(new Event('error') as unknown as SyntheticEvent<HTMLImageElement>);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [key, isPrivate, src, user, mediaSize]);

  const resolved = isPrivate
    ? cachedUrl || (loaded?.key === key ? loaded.url : undefined)
    : src;

  if (!resolved || failed === key) {
    const isFailed = failed === key;
    return (
      <span
        className={`profile-image-placeholder${isFailed ? ' is-failed' : ' is-loading'}`}
        role="img"
        aria-label={isFailed ? 'ფოტო მიუწვდომელია' : 'ფოტო იტვირთება'}
        style={props.style}
      >
        {isFailed ? 'ფოტო მიუწვდომელია' : ''}
      </span>
    );
  }

  return (
    <img
      {...props}
      ref={(el) => {
        if (el && el.complete && el.naturalWidth > 0 && notifiedKeyRef.current !== key) {
          notifiedKeyRef.current = key;
          onLoadRef.current?.({ currentTarget: el } as unknown as SyntheticEvent<HTMLImageElement>);
        }
      }}
      src={resolved}
      alt={alt || ''}
      referrerPolicy="no-referrer"
      onLoad={(e) => {
        notifiedKeyRef.current = key;
        onLoad?.(e);
      }}
      onError={(e) => {
        privateBlobCache.delete(key);
        setFailed(key);
        onError?.(e);
      }}
    />
  );
}
