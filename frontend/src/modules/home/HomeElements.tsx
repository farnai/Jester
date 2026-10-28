import { ProfileImage } from '../../shared/ui/ProfileImage';
import { useState, type ReactNode } from 'react';

export type HomeIconKind =
  | 'arrow'
  | 'people'
  | 'message'
  | 'home'
  | 'compass'
  | 'person'
  | 'bell'
  | 'copy'
  | 'exit'
  | 'sparkles'
  | 'quote'
  | 'check'
  | 'pin'
  | 'refresh'
  | 'share';

export function HomeIcon({ kind = 'arrow' }: { kind?: HomeIconKind }) {
  const paths: Record<HomeIconKind, ReactNode> = {
    arrow: <path d="M5 12h14m-6-6 6 6-6 6" />,
    people: (
      <>
        <circle cx="9" cy="8" r="3" />
        <path d="M3 21v-2a6 6 0 0 1 12 0v2M16 5a3 3 0 0 1 0 6m1 4a5 5 0 0 1 4 5" />
      </>
    ),
    message: <path d="M20 14a3 3 0 0 1-3 3H9l-5 4V6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3Z" />,
    home: <path d="m3 10 9-7 9 7v10H3Zm6 10v-7h6v7" />,
    compass: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="m16 8-2 6-6 2 2-6Z" />
      </>
    ),
    person: (
      <>
        <circle cx="12" cy="7" r="4" />
        <path d="M4 22v-2a8 8 0 0 1 16 0v2" />
      </>
    ),
    bell: <path d="M5 17h14l-2-4V8a5 5 0 0 0-10 0v5Zm5 3a2 2 0 0 0 4 0" />,
    copy: (
      <>
        <rect x="8" y="8" width="12" height="13" rx="2" />
        <path d="M16 8V3H3v13h5" />
      </>
    ),
    exit: <path d="M10 4H4v16h6m-1-8h12m-4-4 4 4-4 4" />,
    sparkles: (
      <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z" />
    ),
    quote: (
      <path d="M3 21c3 0 7-1 7-8V5c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v6c0 1.1.9 2 2 2 0 4-2 6-4 8M15 21c3 0 7-1 7-8V5c0-1.1-.9-2-2-2h-4c-1.1 0-2 .9-2 2v6c0 1.1.9 2 2 2 0 4-2 6-4 8" />
    ),
    check: <path d="M20 6 9 17l-5-5" />,
    pin: (
      <>
        <path d="M12 21s-6-5.33-6-10a6 6 0 0 1 12 0c0 4.67-6 10-6 10z" />
        <circle cx="12" cy="11" r="2.5" />
      </>
    ),
    refresh: (
      <>
        <path d="M21 12a9 9 0 1 1-2.64-6.36" />
        <path d="M21 3v6h-6" />
      </>
    ),
    share: (
      <>
        <circle cx="18" cy="5" r="3" />
        <circle cx="6" cy="12" r="3" />
        <circle cx="18" cy="19" r="3" />
        <path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4" />
      </>
    ),
  };

  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[kind]}
    </svg>
  );
}

/** Bespoke JESTER Three-Perspective Spark (Curiosity, Insight, Empathy). */
export function ThreePerspectiveSpark({ className = '' }: { className?: string }) {
  return (
    <svg
      className={`home-motif-spark ${className}`.trim()}
      viewBox="0 0 28 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M11.5 2C11.9 7.4 14.4 9.9 20 10.6C14.5 11.4 12.1 14 11.5 19.8C10.8 14 8.3 11.4 2.8 10.6C8.4 9.9 10.9 7.4 11.5 2Z"
        fill="currentColor"
      />
      <circle cx="21.5" cy="5.5" r="2.6" fill="#FF7A2F" />
      <path
        d="M23 14.2C23.2 16.2 24.1 17.1 26.2 17.4C24.1 17.7 23.2 18.6 23 20.6C22.7 18.6 21.8 17.7 19.8 17.4C21.8 17.1 22.7 16.2 23 14.2Z"
        fill="currentColor"
        opacity="0.72"
      />
    </svg>
  );
}

/** Two independent perspectives meeting across an organic thread (ME · YOU). */
export function ConnectionThreadMotif({ className = '' }: { className?: string }) {
  return (
    <svg
      className={`home-motif-thread ${className}`.trim()}
      viewBox="0 0 116 32"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M10 18C32 4 50 4 58 16C66 28 84 28 106 14"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx="10" cy="18" r="4" fill="currentColor" />
      <circle cx="106" cy="14" r="4" fill="currentColor" />
      <path d="M58 9L62.5 13.5L58 18L53.5 13.5L58 9Z" fill="#FF7A2F" />
    </svg>
  );
}

function extractInitials(name: string) {
  return (
    name
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((word) => Array.from(word)[0])
      .join('') || 'J'
  );
}

export function HomeAvatar({
  name,
  src,
  large = false,
  arch = false,
}: {
  name: string;
  src?: string | null;
  large?: boolean;
  arch?: boolean;
}) {
  const [failed, setFailed] = useState<string | null>(null);
  const initials = extractInitials(name);
  return (
    <span
      className={`home-avatar${large ? ' home-avatar-large' : ''}${arch ? ' home-avatar-arch' : ''}`}
      aria-hidden="true"
    >
      {src && failed !== src ? (
        <ProfileImage src={src} alt="" loading="lazy" onError={() => setFailed(src)} />
      ) : (
        <span>{initials}</span>
      )}
    </span>
  );
}

/**
 * Large natural 4:5 portrait component for People Discovery cards.
 * Uses authenticated card-sized WebP loading via ProfileImage, and renders
 * an intentional JESTER editorial monogram poster when a user has no photo.
 */
export function HomePortrait({
  name,
  src,
  alt,
  occupation,
  city,
  eager = false,
  onReadyChange,
}: {
  name: string;
  src?: string | null;
  alt?: string;
  occupation?: string | null;
  city?: string | null;
  eager?: boolean;
  onReadyChange?: (ready: boolean) => void;
}) {
  const [failed, setFailed] = useState<string | null>(null);
  const initials = extractInitials(name);
  const hasValidPhoto = Boolean(src && failed !== src);

  if (!hasValidPhoto) {
    return (
      <div
        className="home-portrait-poster"
        role="img"
        aria-label={`${name} — ფოტო ჯერ არ არის დამატებული`}
      >
        <div className="home-portrait-poster-arch" aria-hidden="true">
          <ThreePerspectiveSpark className="home-portrait-poster-spark" />
          <span className="home-portrait-poster-monogram">{initials}</span>
          <span className="home-portrait-poster-label">ფოტო ჯერ არ არის</span>
          {(occupation || city) && (
            <span className="home-portrait-poster-sub">
              {[occupation, city].filter(Boolean).join(' · ')}
            </span>
          )}
        </div>
      </div>
    );
  }

  return (
    <ProfileImage
      className="home-portrait-img"
      mediaSize="card"
      draggable={false}
      src={src!}
      alt={alt || `${name} — პროფილის ფოტო`}
      loading={eager ? 'eager' : 'lazy'}
      onLoad={() => onReadyChange?.(true)}
      onError={() => {
        setFailed(src!);
        onReadyChange?.(false);
      }}
    />
  );
}

export function HomeState({
  title,
  children,
  retry,
}: {
  title: string;
  children?: ReactNode;
  retry?: () => void;
}) {
  return (
    <div className="home-state" role={retry ? 'alert' : 'status'}>
      <strong>{title}</strong>
      {children && <p>{children}</p>}
      {retry && (
        <button type="button" className="home-text-button" onClick={retry}>
          ხელახლა ცდა <HomeIcon />
        </button>
      )}
    </div>
  );
}

export function HomeSkeleton({ compact = false }: { compact?: boolean }) {
  return (
    <div
      className={`home-skeleton${compact ? ' is-compact' : ''}`}
      role="status"
      aria-label="იტვირთება"
    >
      <span />
      <span />
      <span />
    </div>
  );
}
