import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { ConnectionResponse, DiscoveryPerson } from '../../core/api/types';
import { HomeAvatar, HomeIcon } from './HomeElements';
import { connectionFor, personObservation } from './homeModel';

interface HomePersonCarouselProps {
  people: DiscoveryPerson[];
  connections: ConnectionResponse[];
  viewer: string;
  filter: 'insights' | 'all';
  onFilterChange: (filter: 'insights' | 'all') => void;
  observedCount: number;
  totalCount: number;
  onRefresh?: () => void;
}

export function PersonCard({
  person,
  connection,
  viewer,
  featured = false,
  isMobileCard = false,
}: {
  person: DiscoveryPerson;
  connection?: ConnectionResponse;
  viewer: string;
  featured?: boolean;
  isMobileCard?: boolean;
}) {
  const observation = personObservation(person);
  const accepted = connection?.status === 'accepted';
  const status = accepted
    ? 'უკვე დაკავშირებული ხართ'
    : connection?.status === 'pending'
    ? connection.initiated_by === viewer
      ? 'მოთხოვნა გაგზავნილია'
      : 'კავშირის მოთხოვნა'
    : null;

  // Photo gallery support for multi-photo candidates
  const photos: Array<{ id?: string; url?: string }> =
    (person as any)?.photos && Array.isArray((person as any).photos) && (person as any).photos.length > 0
      ? (person as any).photos
      : person.avatar_url
      ? [{ url: person.avatar_url }]
      : [];

  const [activePhoto, setActivePhoto] = useState(0);

  // Reset photo index when person changes
  useEffect(() => {
    setActivePhoto(0);
  }, [person.id]);

  const currentPhotoUrl = photos[activePhoto]?.url || person.avatar_url;
  const commonInterests: string[] =
    (person as any)?.common_interest_ids && (person as any)?.interests
      ? (person as any).interests
          .filter((i: any) => (person as any).common_interest_ids.includes(i.id))
          .map((i: any) => i.name)
      : [];

  return (
    <article
      className={`home-person${featured ? ' home-person-featured' : ''}${
        isMobileCard ? ' home-person-carousel-card' : ''
      }`}
      aria-label={`${person.display_name} - პროფილი`}
    >
      <div className="home-person-identity">
        {/* Large Natural Portrait geometry: 3:4/4:5 proportions with rounded-2xl */}
        <div className="home-person-media-wrapper">
          <HomeAvatar
            name={person.display_name}
            src={currentPhotoUrl}
            large={featured || isMobileCard}
          />

          {/* Photo gallery stepping dots if candidate has multiple photos */}
          {photos.length > 1 && (
            <div className="home-person-photo-nav" aria-label="ფოტოების დათვალიერება">
              <button
                type="button"
                className="home-photo-arrow home-photo-prev"
                onClick={(e) => {
                  e.stopPropagation();
                  setActivePhoto((prev) => (prev > 0 ? prev - 1 : photos.length - 1));
                }}
                aria-label="წინა ფოტო"
              >
                ‹
              </button>
              <div className="home-photo-dots">
                {photos.slice(0, 5).map((_, idx) => (
                  <span
                    key={idx}
                    className={`home-photo-dot${idx === activePhoto ? ' is-active' : ''}`}
                    aria-current={idx === activePhoto ? 'true' : undefined}
                  />
                ))}
              </div>
              <button
                type="button"
                className="home-photo-arrow home-photo-next"
                onClick={(e) => {
                  e.stopPropagation();
                  setActivePhoto((prev) => (prev + 1 < photos.length ? prev + 1 : 0));
                }}
                aria-label="შემდეგი ფოტო"
              >
                ›
              </button>
              <span className="home-photo-counter">
                {activePhoto + 1}/{photos.length}
              </span>
            </div>
          )}

          {/* Common interests seal if shared interests exist */}
          {commonInterests.length > 0 && (
            <div className="home-shared-interest-seal" title="საერთო ინტერესები">
              <span>✦</span>
              <strong>{commonInterests.length}</strong>
            </div>
          )}
        </div>

        <div className="home-person-meta-header">
          <h3>
            <Link to={`/people/${person.id}`}>{person.display_name}</Link>
          </h3>
          <p className="home-person-meta">
            {[person.occupation, person.city].filter(Boolean).join(' · ') || 'გაიცანი უფრო ახლოს'}
          </p>
          {status && <span className="home-connection-tag">{status}</span>}
        </div>
      </div>

      {/* Shared interest badges */}
      {commonInterests.length > 0 && (
        <div className="home-person-interests-strip">
          {commonInterests.slice(0, 3).map((name, i) => (
            <span key={i} className="home-interest-chip">
              ✦ {name}
            </span>
          ))}
        </div>
      )}

      <div className="home-person-copy">
        {observation ? (
          <>
            <p className="home-eyebrow">JESTER ამჩნევს</p>
            <p className="home-person-quote">{observation}</p>
          </>
        ) : person.bio ? (
          <>
            <p className="home-eyebrow">თავის შესახებ</p>
            <p className="home-person-quote">{person.bio}</p>
          </>
        ) : (
          <p className="home-muted">აქ ჯერ ცოტა რამ წერია. გაცნობა პროფილიდან შეგიძლია დაიწყო.</p>
        )}
      </div>

      <div className="home-person-actions">
        <Link to={`/people/${person.id}`} className="home-text-link">
          გაიცანი <HomeIcon />
        </Link>
        {accepted && (
          <Link to={`/people/${person.id}/why`} className="home-text-link">
            ჩვენი კავშირი <HomeIcon kind="people" />
          </Link>
        )}
        {connection?.status === 'pending' && connection.initiated_by !== viewer && (
          <Link to="/connections?tab=incoming" className="home-text-link">
            ნახე მოთხოვნა
          </Link>
        )}
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
}: HomePersonCarouselProps) {
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [page, setPage] = useState(0);
  const touchStartX = useRef<number | null>(null);
  const touchEndX = useRef<number | null>(null);

  // Desktop pagination calculation
  const pageCount = Math.max(1, Math.ceil(people.length / 4));
  const currentPage = Math.min(page, pageCount - 1);
  const desktopVisiblePeople = people.slice(currentPage * 4, currentPage * 4 + 4);

  // Active person for mobile single-card carousel
  const activeCandidate = people[carouselIndex] || people[0];

  const handleNextCandidate = () => {
    if (carouselIndex + 1 < people.length) {
      setCarouselIndex((prev) => prev + 1);
    } else {
      setCarouselIndex(0); // Loop or wrap around gracefully
    }
  };

  const handlePrevCandidate = () => {
    if (carouselIndex > 0) {
      setCarouselIndex((prev) => prev - 1);
    } else {
      setCarouselIndex(Math.max(0, people.length - 1));
    }
  };

  // Touch swipe detection for mobile
  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.targetTouches[0].clientX;
    touchEndX.current = null;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    touchEndX.current = e.targetTouches[0].clientX;
  };

  const handleTouchEnd = () => {
    if (touchStartX.current === null || touchEndX.current === null) return;
    const diff = touchStartX.current - touchEndX.current;
    const minSwipeDistance = 45;

    if (diff > minSwipeDistance) {
      // Swiped Left -> Next candidate
      handleNextCandidate();
    } else if (diff < -minSwipeDistance) {
      // Swiped Right -> Previous candidate
      handlePrevCandidate();
    }
    touchStartX.current = null;
    touchEndX.current = null;
  };

  return (
    <div className="home-person-discovery-container">
      {/* Discovery Controls Bar */}
      <div className="home-discovery-tools">
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
        <p>სახელის მიხედვით · რეიტინგის გარეშე</p>
      </div>

      {/* MOBILE VIEW: Touch-friendly single candidate carousel (<768px) */}
      <div
        className="home-person-mobile-deck"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {activeCandidate && (
          <div className="home-mobile-carousel-stage">
            <PersonCard
              person={activeCandidate}
              connection={connectionFor(connections, viewer, activeCandidate.id)}
              viewer={viewer}
              isMobileCard
            />

            {/* Mobile Carousel Controls & Progress */}
            <div className="home-mobile-deck-controls" aria-label="კანდიდატების გადაფურცვლა">
              <button
                type="button"
                className="home-deck-btn home-deck-prev"
                onClick={handlePrevCandidate}
                disabled={people.length <= 1}
                aria-label="წინა ადამიანი"
              >
                ←
              </button>
              <span className="home-deck-indicator" role="status">
                {carouselIndex + 1} / {people.length} ადამიანი
              </span>
              <button
                type="button"
                className="home-deck-btn home-deck-next"
                onClick={handleNextCandidate}
                disabled={people.length <= 1}
                aria-label="შემდეგი ადამიანი"
              >
                →
              </button>
            </div>
            <p className="home-mobile-swipe-hint" aria-hidden="true">
              <span>← გადაფურცლე შემდეგზე</span>
            </p>
          </div>
        )}
      </div>

      {/* DESKTOP & TABLET VIEW: Multi-card layout (>=768px) */}
      <div className="home-people-layout home-desktop-only-layout">
        {desktopVisiblePeople[0] && (
          <PersonCard
            key={desktopVisiblePeople[0].id}
            person={desktopVisiblePeople[0]}
            connection={connectionFor(connections, viewer, desktopVisiblePeople[0].id)}
            viewer={viewer}
            featured
          />
        )}
        <div className="home-people-list">
          {desktopVisiblePeople.slice(1).map((person) => (
            <PersonCard
              key={person.id}
              person={person}
              connection={connectionFor(connections, viewer, person.id)}
              viewer={viewer}
            />
          ))}
        </div>
      </div>

      {/* Desktop Pagination */}
      <div className="home-pagination home-desktop-only-pagination">
        <span role="status">
          {currentPage * 4 + 1}–{Math.min((currentPage + 1) * 4, people.length)} / {people.length}{' '}
          პროფილი
        </span>
        <div>
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
    </div>
  );
}
