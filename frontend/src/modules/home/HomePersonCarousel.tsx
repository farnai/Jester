import {
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type KeyboardEvent,
  type PointerEvent,
  type TouchEvent,
} from 'react';
import { Link } from 'react-router-dom';
import type { ConnectionResponse, DiscoveryPerson, InterestItem, ProfilePhoto } from '../../core/api/types';
import { HomeIcon, HomePortrait, ThreePerspectiveSpark } from './HomeElements';
import { connectionFor, personObservation } from './homeModel';

interface RichDiscoveryPerson extends DiscoveryPerson {
  photos?: ProfilePhoto[];
  interests?: InterestItem[];
  common_interest_ids?: string[];
  same_city?: boolean;
}

export interface HomePersonCarouselProps {
  people: DiscoveryPerson[];
  connections: ConnectionResponse[];
  viewer: string;
  filter: 'insights' | 'all';
  onFilterChange: (filter: 'insights' | 'all') => void;
  observedCount: number;
  totalCount: number;
  onRefresh?: () => void;
  onRequestConnect?: (person: DiscoveryPerson) => void;
}

const DESKTOP_PAGE_SIZE = 3;
const TABLET_PAGE_SIZE = 4;

const GEORGIAN_INTEREST_LABELS: Record<string, string> = {
  travel: 'მოგზაურობა',
  coffee: 'ყავის კულტურა',
  music: 'მუსიკა',
  photography: 'ფოტოგრაფია',
  cinema: 'კინო',
  books: 'წიგნები',
  astrology: 'ასტროლოგია',
  food: 'კულინარია',
  hiking: 'ლაშქრობა',
  art: 'ვიზუალური ხელოვნება',
  fitness: 'ფიტნესი',
  pets: 'ცხოველები',
  technology: 'ტექნოლოგიები',
  gaming: 'გეიმინგი',
  fashion: 'მოდა და სტილი',
  nature: 'ბუნება',
  theatre: 'თეატრი',
  writing: 'წერა',
  psychology: 'ფსიქოლოგია',
  concerts: 'კონცერტები',
  philosophy: 'ფილოსოფია',
};

function formatInterestLabel(interest: InterestItem): string {
  const key = (interest.slug || '').trim().toLowerCase();
  return (key && GEORGIAN_INTEREST_LABELS[key]) || interest.name;
}

/**
 * Formats JESTER's card observation into a complete, grammatically closed
 * Georgian quotation without mid-word clipping, four-dot ellipses, or unclosed „.
 */
function formatCardObservation(raw: string, maxChars = 152): string {
  const clean = raw
    .trim()
    .replace(/^[„"«]+|[“"»]+$/g, '')
    .replace(/\s+/g, ' ')
    .trim();
  if (!clean) return '';
  if (clean.length <= maxChars) return `„${clean}“`;

  const sentenceMatch = clean.match(/^(.+?[.!?])(?:\s+|$)/);
  if (sentenceMatch && sentenceMatch[1].length >= 42 && sentenceMatch[1].length <= maxChars) {
    return `„${sentenceMatch[1]}“`;
  }

  const slice = clean.slice(0, maxChars - 1);
  const wordBoundary = slice.lastIndexOf(' ');
  const stem = (wordBoundary > 56 ? slice.slice(0, wordBoundary) : slice).replace(
    /[.,;:!?…]+$/g,
    ''
  );
  return `„${stem}…“`;
}

export function PersonCard({
  person,
  connection,
  viewer,
  eager = false,
  isMobileCard = false,
  onRequestConnect,
}: {
  person: DiscoveryPerson;
  connection?: ConnectionResponse;
  viewer: string;
  eager?: boolean;
  isMobileCard?: boolean;
  onRequestConnect?: (person: DiscoveryPerson) => void;
}) {
  const rich = person as RichDiscoveryPerson;
  const observation = personObservation(person);
  const accepted = connection?.status === 'accepted';
  const pendingOut = connection?.status === 'pending' && connection.initiated_by === viewer;
  const pendingIn = connection?.status === 'pending' && connection.initiated_by !== viewer;

  const statusLabel = accepted
    ? 'უკვე დაკავშირებული ხართ'
    : pendingOut
    ? 'მოთხოვნა გაგზავნილია'
    : pendingIn
    ? 'კავშირის მოთხოვნა'
    : null;

  const photos: Array<{ id?: string; url: string }> =
    Array.isArray(rich.photos) && rich.photos.length > 0
      ? rich.photos.filter((p) => Boolean(p?.url)).map((p) => ({ id: p.id, url: p.url }))
      : person.avatar_url
      ? [{ id: 'avatar', url: person.avatar_url }]
      : [];

  const [activePhoto, setActivePhoto] = useState(0);
  const [readyPhotoUrl, setReadyPhotoUrl] = useState<string | null>(null);

  useEffect(() => {
    setActivePhoto(0);
  }, [person.id]);

  const safePhotoIndex = photos.length > 0 ? Math.min(activePhoto, photos.length - 1) : 0;
  const currentPhotoUrl = photos[safePhotoIndex]?.url || person.avatar_url || null;
  const isPhotoReady = Boolean(currentPhotoUrl && readyPhotoUrl === currentPhotoUrl);

  const commonIds = Array.isArray(rich.common_interest_ids) ? rich.common_interest_ids : [];
  const allInterests = Array.isArray(rich.interests) ? rich.interests : [];
  const sortedInterests = [...allInterests]
    .sort((a, b) => Number(commonIds.includes(b.id)) - Number(commonIds.includes(a.id)))
    .slice(0, 3);
  const commonCount = commonIds.length;

  const metaParts: string[] = [];
  if (person.occupation) metaParts.push(person.occupation);
  if (person.city) {
    metaParts.push(rich.same_city ? `შენს ქალაქში · ${person.city}` : person.city);
  }
  const metaLine = metaParts.join(' · ') || 'პირადი პროფილი';

  const stepPhoto = (delta: number) => {
    if (photos.length <= 1) return;
    setActivePhoto((prev) => (prev + delta + photos.length) % photos.length);
  };

  return (
    <article
      className={`home-candidate-card${isMobileCard ? ' is-mobile-card' : ''}`}
      data-person-id={person.id}
      aria-label={`${person.display_name} — პროფილი`}
    >
      {/* Primary Visual Anchor: Natural 4:5 Portrait */}
      <div className="home-candidate-media">
        <HomePortrait
          name={person.display_name}
          src={currentPhotoUrl}
          alt={`${person.display_name} — ფოტო ${safePhotoIndex + 1}`}
          occupation={person.occupation}
          city={person.city}
          eager={eager}
          onReadyChange={(ready) => setReadyPhotoUrl(ready ? currentPhotoUrl : null)}
        />

        {isPhotoReady && photos.length > 1 && (
          <div className="home-photo-progress-rail" aria-hidden="true">
            {photos.slice(0, 6).map((item, idx) => (
              <span
                key={item.id || idx}
                className={`home-photo-progress-bar${idx === safePhotoIndex ? ' is-active' : ''}`}
              />
            ))}
          </div>
        )}

        {isPhotoReady && photos.length > 0 && (
          <span className="home-photo-count-pill">
            {safePhotoIndex + 1} / {photos.length} ფოტო
          </span>
        )}

        {isPhotoReady && photos.length > 1 && (
          <div
            className="home-photo-stepper"
            onPointerDown={(e) => e.stopPropagation()}
            onTouchStart={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              className="home-photo-step-btn"
              aria-label="წინა ფოტო"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                stepPhoto(-1);
              }}
            >
              ‹
            </button>
            <button
              type="button"
              className="home-photo-step-btn"
              aria-label="შემდეგი ფოტო"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                stepPhoto(1);
              }}
            >
              ›
            </button>
          </div>
        )}

        {commonCount > 0 && (
          <span className="home-common-seal" title={`${commonCount} საერთო ინტერესი`}>
            <span aria-hidden="true">✦</span>
            <strong>{commonCount} საერთო</strong>
          </span>
        )}
      </div>

      {/* Card Content */}
      <div className="home-candidate-body">
        <div className="home-candidate-header">
          <div className="home-candidate-title-row">
            <h3 className="home-candidate-name">
              <Link to={`/people/${person.id}`}>{person.display_name}</Link>
            </h3>
            {statusLabel && <span className="home-candidate-status-badge">{statusLabel}</span>}
          </div>
          <p className="home-candidate-meta">{metaLine}</p>
        </div>

        {sortedInterests.length > 0 && (
          <div className="home-candidate-interests" aria-label="ინტერესები">
            {sortedInterests.map((interest) => {
              const isShared = commonIds.includes(interest.id);
              return (
                <span
                  key={interest.id}
                  className={`home-interest-pill${isShared ? ' is-shared' : ''}`}
                >
                  {isShared ? '✦ ' : ''}
                  {formatInterestLabel(interest)}
                </span>
              );
            })}
          </div>
        )}

        <div className="home-candidate-excerpt">
          {observation ? (
            <>
              <span className="home-candidate-kicker">
                <ThreePerspectiveSpark />
                <span>JESTER ამჩნევს</span>
              </span>
              <p className="home-candidate-quote">{formatCardObservation(observation)}</p>
            </>
          ) : person.bio ? (
            <>
              <span className="home-candidate-kicker">თავის შესახებ</span>
              <p className="home-candidate-quote">{person.bio}</p>
            </>
          ) : (
            <p className="home-candidate-muted">
              დეტალები და ინტერესები სრულ პროფილში დაგხვდება.
            </p>
          )}
        </div>

        <div className="home-candidate-actions">
          <Link to={`/people/${person.id}`} className="home-candidate-primary-cta">
            <span>გაიცანი ახლოს</span>
            <HomeIcon />
          </Link>

          {accepted ? (
            <Link to={`/people/${person.id}/why`} className="home-candidate-secondary-cta">
              <span>ჩვენი კავშირი</span>
            </Link>
          ) : pendingIn ? (
            <Link to="/connections?tab=incoming" className="home-candidate-secondary-cta">
              <span>ნახე მოთხოვნა</span>
            </Link>
          ) : !connection && onRequestConnect ? (
            <button
              type="button"
              className="home-candidate-secondary-cta"
              onClick={() => onRequestConnect(person)}
            >
              <span>დაკავშირება</span>
            </button>
          ) : null}
        </div>
      </div>
    </article>
  );
}

export function HomePersonCarousel({
  people,
  connections,
  viewer,
  filter,
  onFilterChange,
  observedCount,
  totalCount,
  onRequestConnect,
}: HomePersonCarouselProps) {
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [page, setPage] = useState(0);
  const [dragOffset, setDragOffset] = useState(0);
  const [pageSize, setPageSize] = useState(DESKTOP_PAGE_SIZE);

  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return;
    const mq = window.matchMedia('(min-width: 768px) and (max-width: 1080px)');
    const sync = () => setPageSize(mq.matches ? TABLET_PAGE_SIZE : DESKTOP_PAGE_SIZE);
    sync();
    mq.addEventListener('change', sync);
    return () => mq.removeEventListener('change', sync);
  }, []);

  const gestureRef = useRef<{
    startX: number;
    startY: number;
    lockedHorizontal: boolean;
    cancelled: boolean;
  } | null>(null);

  const pageCount = Math.max(1, Math.ceil(people.length / pageSize));
  const currentPage = Math.min(page, pageCount - 1);
  const desktopVisiblePeople = people.slice(
    currentPage * pageSize,
    currentPage * pageSize + pageSize
  );

  const safeCarouselIndex = people.length > 0 ? Math.min(carouselIndex, people.length - 1) : 0;
  const activeCandidate = people[safeCarouselIndex] || people[0];

  const goNextCandidate = () => {
    if (people.length <= 1) return;
    setCarouselIndex((prev) => (prev + 1 < people.length ? prev + 1 : 0));
  };

  const goPrevCandidate = () => {
    if (people.length <= 1) return;
    setCarouselIndex((prev) => (prev > 0 ? prev - 1 : people.length - 1));
  };

  // Pointer gesture handlers (unified mouse/pen/touch where PointerEvents apply)
  const handlePointerDown = (e: PointerEvent<HTMLDivElement>) => {
    if (!e.isPrimary || (e.pointerType === 'mouse' && e.button !== 0)) return;
    gestureRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      lockedHorizontal: false,
      cancelled: false,
    };
  };

  const handlePointerMove = (e: PointerEvent<HTMLDivElement>) => {
    const g = gestureRef.current;
    if (!g || g.cancelled || people.length <= 1) return;
    const dx = e.clientX - g.startX;
    const dy = e.clientY - g.startY;

    if (!g.lockedHorizontal && Math.abs(dy) > 14 && Math.abs(dy) >= Math.abs(dx)) {
      g.cancelled = true;
      setDragOffset(0);
      return;
    }

    if (Math.abs(dx) > 14 && Math.abs(dx) > Math.abs(dy) * 1.45) {
      g.lockedHorizontal = true;
      setDragOffset(Math.max(-72, Math.min(72, dx)));
    }
  };

  const handlePointerUp = (e: PointerEvent<HTMLDivElement>) => {
    const g = gestureRef.current;
    gestureRef.current = null;
    setDragOffset(0);
    if (!g || g.cancelled || people.length <= 1) return;
    const dx = e.clientX - g.startX;
    const dy = e.clientY - g.startY;
    if (Math.abs(dx) >= 52 && Math.abs(dx) > Math.abs(dy) * 1.45) {
      if (dx < 0) goNextCandidate();
      else goPrevCandidate();
    }
  };

  // Fallback TouchEvents for environments dispatching synthetic TouchEvents
  const touchOrigin = useRef<{ x: number; y: number } | null>(null);
  const handleTouchStart = (e: TouchEvent<HTMLDivElement>) => {
    if (e.targetTouches.length !== 1) return;
    touchOrigin.current = {
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    };
  };

  const handleTouchEnd = (e: TouchEvent<HTMLDivElement>) => {
    if (!touchOrigin.current || e.changedTouches.length === 0 || people.length <= 1) return;
    // Skip if PointerUp already handled this gesture
    if (gestureRef.current === null && 'PointerEvent' in globalThis && e.nativeEvent.isTrusted) {
      touchOrigin.current = null;
      return;
    }
    const dx = e.changedTouches[0].clientX - touchOrigin.current.x;
    const dy = e.changedTouches[0].clientY - touchOrigin.current.y;
    touchOrigin.current = null;
    if (Math.abs(dx) >= 48 && Math.abs(dx) > Math.abs(dy) * 1.4) {
      if (dx < 0) goNextCandidate();
      else goPrevCandidate();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      goNextCandidate();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      goPrevCandidate();
    }
  };

  return (
    <div className="home-people-deck-wrapper">
      {/* Filter & Provenance Subbar */}
      <div className="home-people-toolbar">
        <div className="home-filter" role="group" aria-label="ადამიანების ჩვენება">
          <button
            type="button"
            aria-pressed={filter === 'insights'}
            onClick={() => {
              onFilterChange('insights');
              setPage(0);
              setCarouselIndex(0);
            }}
          >
            დაკვირვებით · {observedCount}
          </button>
          <button
            type="button"
            aria-pressed={filter === 'all'}
            onClick={() => {
              onFilterChange('all');
              setPage(0);
              setCarouselIndex(0);
            }}
          >
            ყველა · {totalCount}
          </button>
        </div>

        <p className="home-people-provenance">
          ავთენტური პროფილები · ქულებისა და ხელოვნური რეიტინგის გარეშე
        </p>
      </div>

      {/* MOBILE (<768px): Single Active Candidate Horizontal Carousel */}
      <div className="home-mobile-deck">
        {activeCandidate && (
          <div
            className="home-mobile-deck-stage"
            tabIndex={0}
            role="region"
            aria-roledescription="კარუსელი"
            aria-label={`ადამიანების კარუსელი — ${safeCarouselIndex + 1} / ${people.length}`}
            onKeyDown={handleKeyDown}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerCancel={() => {
              gestureRef.current = null;
              setDragOffset(0);
            }}
            onTouchStart={handleTouchStart}
            onTouchEnd={handleTouchEnd}
            style={{ '--deck-drag-x': `${dragOffset}px` } as CSSProperties}
          >
            <div className="home-mobile-card-track">
              <PersonCard
                key={activeCandidate.id}
                person={activeCandidate}
                connection={connectionFor(connections, viewer, activeCandidate.id)}
                viewer={viewer}
                eager
                isMobileCard
                onRequestConnect={onRequestConnect}
              />
            </div>

            <div className="home-mobile-deck-bar" aria-label="კანდიდატების ნავიგაცია">
              <button
                type="button"
                className="home-deck-nav-btn"
                onClick={goPrevCandidate}
                disabled={people.length <= 1}
                aria-label="წინა ადამიანი"
              >
                ←
              </button>

              <div className="home-deck-progress">
                <span className="home-deck-count" role="status">
                  {safeCarouselIndex + 1} / {people.length} ადამიანი
                </span>
                {people.length > 1 && (
                  <div className="home-deck-dots" aria-hidden="true">
                    {people.slice(0, 8).map((p, idx) => (
                      <span
                        key={p.id}
                        className={`home-deck-dot${idx === safeCarouselIndex ? ' is-active' : ''}`}
                      />
                    ))}
                  </div>
                )}
              </div>

              <button
                type="button"
                className="home-deck-nav-btn"
                onClick={goNextCandidate}
                disabled={people.length <= 1}
                aria-label="შემდეგი ადამიანი"
              >
                →
              </button>
            </div>
          </div>
        )}
      </div>

      {/* DESKTOP & TABLET (>=768px): 3 Substantial Photo-Led Cards (2-up on Tablet) */}
      <div className="home-desktop-cards-grid">
        {desktopVisiblePeople.map((person, idx) => (
          <PersonCard
            key={person.id}
            person={person}
            connection={connectionFor(connections, viewer, person.id)}
            viewer={viewer}
            eager={idx < 4}
            onRequestConnect={onRequestConnect}
          />
        ))}
      </div>

      {people.length > pageSize && (
        <div className="home-desktop-pagination">
          <span role="status">
            ნაჩვენებია {currentPage * pageSize + 1}–
            {Math.min((currentPage + 1) * pageSize, people.length)} / {people.length}{' '}
            ადამიანი
          </span>
          <div className="home-desktop-page-controls">
            <button
              type="button"
              disabled={currentPage === 0}
              onClick={() => setPage(currentPage - 1)}
              aria-label="წინა პროფილები"
            >
              ←
            </button>
            <button
              type="button"
              disabled={currentPage + 1 >= pageCount}
              onClick={() => setPage(currentPage + 1)}
              aria-label="შემდეგი პროფილები"
            >
              →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
