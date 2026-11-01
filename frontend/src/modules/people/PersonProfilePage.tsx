import { useState } from 'react';
import { useParams, useSearchParams, Link, Navigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import { useAuth } from '../../core/auth/useAuth';
import { Badge, Skeleton, ErrorState, PrivacySafeNotFoundState } from '../../shared/ui';
import { ProfileImage } from '../../shared/ui/ProfileImage';
import { ConnectionActions } from './ConnectionActions';
import { formatShortName, formatZodiacSign } from '../../shared/utils/profileFormatting';
import './person-profile.css';

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function PersonProfilePage() {
  const { id = '' } = useParams<{ id: string }>();
  return UUID_REGEX.test(id) ? <PersonProfile key={id} targetId={id} /> : <Navigate to="/discover" replace />;
}

function PersonProfile({ targetId }: { targetId: string }) {
  const { user } = useAuth();
  const [params] = useSearchParams();
  const [selectedPhotoId, setSelectedPhotoId] = useState<string | null>(null);

  const requestedReturn = params.get('returnTo') || '';
  const returnTo = requestedReturn === '/' || requestedReturn === '/discover' || requestedReturn.startsWith('/discover?') ? requestedReturn : '/';
  const isSelf = user?.id === targetId;

  // 1. Core Profile
  const profile = useQuery({
    queryKey: ['profile', targetId],
    queryFn: () => API.profiles.getProfileById(targetId),
    retry: false,
  });

  // 2. Photos (Wave 2 Gallery System)
  const photos = useQuery({
    queryKey: ['photos', targetId],
    queryFn: () => API.profiles.photos(targetId),
    enabled: !!profile.data && !profile.error,
    retry: false,
  });

  // 3. Interests
  const interests = useQuery({
    queryKey: ['person-interests', targetId],
    queryFn: () => API.interests.forPerson(targetId),
    enabled: !!profile.data && !profile.error,
    retry: false,
  });

  // 4. Safe Derived Astrology (Sun, Moon, Rising, Element, Modality)
  const astro = useQuery({
    queryKey: ['astrology', targetId],
    queryFn: () => API.astrology.getPersonSafeAstro(targetId),
    enabled: !!profile.data && !profile.error,
    retry: false,
  });

  // 5. Connections & Block enforcement
  const connections = useQuery({
    queryKey: ['connections'],
    queryFn: API.connections.list,
    refetchInterval: 15000,
  });
  const blocked = connections.data?.some(
    (c) => c.status === 'blocked' && (c.user_a_id === targetId || c.user_b_id === targetId)
  );

  // 6. Compare Preview (First Sight)
  const preview = useQuery({
    queryKey: ['compare-preview', targetId],
    queryFn: () => API.interpretations.comparePreview({ target_user_id: targetId, locale: 'ka' }),
    enabled: !!profile.data && !profile.error && !isSelf && !blocked,
    retry: false,
  });

  // Security & Privacy Invariants
  if (blocked || (profile.error && [403, 404].includes((profile.error as { statusCode?: number }).statusCode || 0))) {
    return <PrivacySafeNotFoundState message="პროფილი ვერ მოიძებნა ან მიუწვდომელია." />;
  }
  if (profile.error) {
    return <ErrorState error={profile.error} />;
  }
  if (profile.isPending) {
    return (
      <div className="person-profile-container">
        <Skeleton width="100%" height="450px" borderRadius="24px" />
        <Skeleton width="100%" height="200px" borderRadius="20px" style={{ marginTop: '1.5rem' }} />
      </div>
    );
  }
  if (!profile.data) return null;

  const photoItems = photos.data || [];
  const selectedPhoto = photoItems.find((p) => p.id === selectedPhotoId) || photoItems[0];
  const shortName = formatShortName(profile.data.display_name);
  const ageDisplay = profile.data.age != null ? `${profile.data.age} წლის` : null;
  const zodiacDisplay = formatZodiacSign(astro.data?.sun_sign);
  const cityDisplay = profile.data.city || null;
  const occupationDisplay = profile.data.occupation || null;

  const interestItems = interests.data?.items || [];
  const commonInterestIds = interests.data?.common_interest_ids || [];

  const compareScore = preview.data?.score;
  const compareHook = preview.data?.interpretation?.text;

  return (
    <div className="person-profile-container" lang="ka">
      {/* Top Breadcrumb Navigation */}
      <nav className="person-top-nav">
        <Link to={returnTo} className="person-back-link">
          ← აღმოჩენაზე დაბრუნება
        </Link>
        {isSelf && <Badge variant="brand">ეს თქვენი პროფილია</Badge>}
      </nav>

      {/* 1. Photos & Core Identity Card (Hero Section) */}
      <section className="person-card person-identity-card">
        <div className="person-gallery-wrap">
          <div className="person-main-photo-stage">
            {photos.isPending ? (
              <div className="person-photo-loading">
                <Skeleton width="100%" height="100%" borderRadius="18px" />
              </div>
            ) : selectedPhoto ? (
              <ProfileImage
                key={selectedPhoto.id}
                src={selectedPhoto.url}
                alt={`${shortName} — ფოტო ${selectedPhoto.position + 1}`}
              />
            ) : (
              <div className="person-photo-empty-fallback" aria-hidden="true">
                <div className="person-fallback-ring">
                  <span className="person-fallback-initial">{shortName.charAt(0) || 'J'}</span>
                </div>
                {zodiacDisplay && <span className="person-fallback-zodiac">{zodiacDisplay}</span>}
              </div>
            )}

            {selectedPhoto && photoItems.length > 1 && (
              <span className="person-photo-index-pill">
                {selectedPhoto.position + 1} / {photoItems.length}
              </span>
            )}
          </div>

          {/* Thumbnail Track if multiple photos */}
          {photoItems.length > 1 && (
            <div className="person-thumbnails-track" aria-label="ფოტოების გალერეა">
              {photoItems.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={`person-thumb-btn ${selectedPhoto?.id === item.id ? 'is-active' : ''}`}
                  onClick={() => setSelectedPhotoId(item.id)}
                  aria-label={`ფოტო ${item.position + 1}`}
                  aria-pressed={selectedPhoto?.id === item.id}
                >
                  <ProfileImage src={item.url} alt="" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Core Identity Info */}
        <div className="person-identity-body">
          <div className="person-name-row">
            <h1 className="person-display-name">{shortName}</h1>
            {ageDisplay && <span className="person-age-tag">{ageDisplay}</span>}
          </div>

          <div className="person-badges-row">
            {zodiacDisplay && (
              <span className="person-pill person-zodiac-pill" title="ზოდიაქოს ნიშანი">
                {zodiacDisplay}
              </span>
            )}
            {cityDisplay && (
              <span className="person-pill person-city-pill" title="ქალაქი">
                📍 {cityDisplay}
              </span>
            )}
            {occupationDisplay && (
              <span className="person-pill person-work-pill" title="საქმიანობა">
                💼 {occupationDisplay}
              </span>
            )}
          </div>

          {/* Direct Connection Actions */}
          {!isSelf && (
            <div className="person-hero-actions">
              <ConnectionActions target={targetId} name={shortName} />
              <Link to={`/compare/${targetId}`} className="home-btn home-btn-outline person-compare-action">
                შედარება ↗
              </Link>
            </div>
          )}
        </div>
      </section>

      {/* 2. ჩემ შესახებ — About Me */}
      {(profile.data.bio || occupationDisplay || cityDisplay) && (
        <section className="person-card person-about-card">
          <h2 className="person-section-heading">ჩემ შესახებ</h2>

          {profile.data.bio && (
            <blockquote className="person-bio-quote">
              „{profile.data.bio}“
            </blockquote>
          )}

          <div className="person-details-grid">
            {occupationDisplay && (
              <div className="person-detail-item">
                <span className="person-detail-label">საქმიანობა</span>
                <strong className="person-detail-value">{occupationDisplay}</strong>
              </div>
            )}
            {cityDisplay && (
              <div className="person-detail-item">
                <span className="person-detail-label">ქალაქი</span>
                <strong className="person-detail-value">{cityDisplay}</strong>
              </div>
            )}
          </div>
        </section>
      )}

      {/* 3. ჩემი ინტერესები — My Interests */}
      {interestItems.length > 0 && (
        <section className="person-card person-interests-card">
          <div className="person-section-header-row">
            <h2 className="person-section-heading">ჩემი ინტერესები</h2>
            {!isSelf && commonInterestIds.length > 0 && (
              <span className="person-common-badge">
                ↔ {commonInterestIds.length} საერთო ინტერესი
              </span>
            )}
          </div>

          <div className="person-interests-tags">
            {interestItems.map((item) => {
              const isCommon = commonInterestIds.includes(item.id);
              return (
                <span
                  key={item.id}
                  className={`person-interest-chip ${isCommon ? 'is-common' : ''}`}
                >
                  {isCommon && <span className="person-sparkle">✦ </span>}
                  {item.name}
                </span>
              );
            })}
          </div>
        </section>
      )}

      {/* 4. ჩვენი კავშირი — JESTER Compatibility / First Sight */}
      {!isSelf && (
        <section className="person-card person-compatibility-card">
          <div className="person-section-header-row">
            <div>
              <span className="person-sub-eyebrow">JESTER / პირველი ხედვა</span>
              <h2 className="person-section-heading">ჩვენი კავშირი</h2>
            </div>
            {typeof compareScore === 'number' && Number.isFinite(compareScore) && (
              <span className="person-compat-score-pill">
                თანხვედრა <strong>{Math.round(compareScore)}</strong>
              </span>
            )}
          </div>

          {preview.isPending ? (
            <p className="person-compat-status">წინასწარი ხედვა იტვირთება…</p>
          ) : preview.isError ? (
            <p className="person-compat-status">
              წინასწარი ხედვა ვერ ჩაიტვირთა.{' '}
              <button type="button" onClick={() => preview.refetch()} className="person-retry-btn">
                ხელახლა ცდა
              </button>
            </p>
          ) : compareHook ? (
            <p className="person-compat-hook">„{compareHook}“</p>
          ) : (
            <p className="person-compat-status">შედარების წინასწარი ხედვა ამჟამად მიუწვდომელია.</p>
          )}

          <div className="person-compat-footer">
            <p className="person-compat-note">
              ეს საუბრის დასაწყისია. სრული „ჩვენი კავშირი“ იხსნება კავშირის მიღების შემდეგ.
            </p>
            <Link to={`/compare/${targetId}`} className="home-btn home-btn-primary">
              სრული შედარება (Compare) ↗
            </Link>
          </div>
        </section>
      )}

      {/* 5. საჯარო ასტროლოგიური კონტექსტი — Astrological Context */}
      {astro.data && (
        <section className="person-card person-astrology-card">
          <h2 className="person-section-heading">ასტროლოგიური კონტექსტი</h2>
          <p className="person-astro-subtitle">
            ციური კონფიგურაცია დაბადების მომენტში (Swiss Ephemeris-ის უსაფრთხო საჯარო მონაცემები)
          </p>

          <div className="person-astro-grid">
            {astro.data.sun_sign && (
              <div className="person-astro-item">
                <span className="person-astro-label">მზე (Sun)</span>
                <strong className="person-astro-value">
                  {formatZodiacSign(astro.data.sun_sign)}
                </strong>
              </div>
            )}
            {astro.data.moon_sign && (
              <div className="person-astro-item">
                <span className="person-astro-label">მთვარე (Moon)</span>
                <strong className="person-astro-value">
                  {formatZodiacSign(astro.data.moon_sign)}
                </strong>
              </div>
            )}
            {astro.data.ascendant_sign && (
              <div className="person-astro-item">
                <span className="person-astro-label">ასცენდენტი (Rising)</span>
                <strong className="person-astro-value">
                  {formatZodiacSign(astro.data.ascendant_sign)}
                </strong>
              </div>
            )}
            {astro.data.element_primary && (
              <div className="person-astro-item">
                <span className="person-astro-label">დომინანტური სტიქია</span>
                <strong className="person-astro-value">{astro.data.element_primary}</strong>
              </div>
            )}
            {astro.data.modality_primary && (
              <div className="person-astro-item">
                <span className="person-astro-label">მოდალობა</span>
                <strong className="person-astro-value">{astro.data.modality_primary}</strong>
              </div>
            )}
          </div>

          <div className="person-astro-privacy-notice">
            <span>
              ℹ პირადი დაბადების მონაცემები (დრო, ადგილი, კოორდინატები) და პირადი 7-შრიანი ანალიზი
              მკაცრად კონფიდენციალურია და არ საჯაროვდება.
            </span>
          </div>
        </section>
      )}
    </div>
  );
}
