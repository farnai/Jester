import { ProfileImage } from "../../shared/ui/ProfileImage";
import { useState, type ReactNode } from 'react';

export function HomeIcon({ kind = 'arrow' }: { kind?: 'arrow' | 'people' | 'message' | 'home' | 'compass' | 'person' | 'bell' | 'copy' | 'exit' | 'sparkles' | 'quote' | 'check' | 'pin' }) {
  const paths = {
    arrow: <path d="M5 12h14m-6-6 6 6-6 6" />,
    people: <><circle cx="9" cy="8" r="3" /><path d="M3 21v-2a6 6 0 0 1 12 0v2M16 5a3 3 0 0 1 0 6m1 4a5 5 0 0 1 4 5" /></>,
    message: <path d="M20 14a3 3 0 0 1-3 3H9l-5 4V6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3Z" />,
    home: <path d="m3 10 9-7 9 7v10H3Zm6 10v-7h6v7" />,
    compass: <><circle cx="12" cy="12" r="9" /><path d="m16 8-2 6-6 2 2-6Z" /></>,
    person: <><circle cx="12" cy="7" r="4" /><path d="M4 22v-2a8 8 0 0 1 16 0v2" /></>,
    bell: <path d="M5 17h14l-2-4V8a5 5 0 0 0-10 0v5Zm5 3a2 2 0 0 0 4 0" />,
    copy: <><rect x="8" y="8" width="12" height="13" rx="2" /><path d="M16 8V3H3v13h5" /></>,
    exit: <path d="M10 4H4v16h6m-1-8h12m-4-4 4 4-4 4" />,
    sparkles: <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z" />,
    quote: <path d="M3 21c3 0 7-1 7-8V5c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v6c0 1.1.9 2 2 2 0 4-2 6-4 8M15 21c3 0 7-1 7-8V5c0-1.1-.9-2-2-2h-4c-1.1 0-2 .9-2 2v6c0 1.1.9 2 2 2 0 4-2 6-4 8" />,
    check: <path d="M20 6 9 17l-5-5" />,
    pin: <><path d="M12 21s-6-5.33-6-10a6 6 0 0 1 12 0c0 4.67-6 10-6 10z" /><circle cx="12" cy="11" r="2.5" /></>,
  };
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[kind]}</svg>;
}

export function HomeAvatar({ name, src, large = false }: { name: string; src?: string | null; large?: boolean }) {
  const [failed, setFailed] = useState<string | null>(null);
  const initials = name.trim().split(/\s+/).slice(0, 2).map(word => Array.from(word)[0]).join('') || 'J';
  return <span className={`home-avatar${large ? ' home-avatar-large' : ''}`} aria-hidden="true">
    {src && failed !== src ? <ProfileImage src={src} alt="" loading="lazy" onError={() => setFailed(src)} /> : <span>{initials}</span>}
  </span>;
}

export function HomeState({ title, children, retry }: { title: string; children?: ReactNode; retry?: () => void }) {
  return <div className="home-state" role={retry ? 'alert' : 'status'}><strong>{title}</strong>{children && <p>{children}</p>}{retry && <button className="home-text-button" onClick={retry}>ხელახლა ცდა <HomeIcon /></button>}</div>;
}

export function HomeSkeleton({ compact = false }: { compact?: boolean }) {
  return <div className={`home-skeleton${compact ? ' is-compact' : ''}`} role="status" aria-label="იტვირთება"><span /><span /><span /></div>;
}
