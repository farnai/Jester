import { useState } from 'react';
import { Link } from 'react-router-dom';
import type { DiscoveryPerson } from '../../core/api/types';
import { formatShortName, formatZodiacSign } from '../../shared/utils/profileFormatting';
import { ProfileImage } from '../../shared/ui/ProfileImage';

interface HomeNewPeopleProps {
  people: DiscoveryPerson[];
  isLoading: boolean;
  isError: boolean;
  onRetry?: () => void;
}

function HomePersonCardItem({ person }: { person: DiscoveryPerson }) {
  const [imgError, setImgError] = useState(false);
  const photoUrl = person.photos?.[0]?.url || person.avatar_url;
  const shortName = formatShortName(person.display_name);
  const initial = shortName.charAt(0) || 'J';
  const ageDisplay = person.age != null ? `${person.age}` : null;
  const cityDisplay = person.city_name || person.city || null;
  const zodiacDisplay = formatZodiacSign(person.astrology?.sun_sign);
  // Max 2 interests per specification
  const interestTags = (person.interests || []).slice(0, 2);

  return (
    <div className="home-person-card" role="listitem">
      <Link to={`/people/${person.id}?returnTo=/`} className="home-person-link">
        <div className="home-person-photo-wrap">
          {photoUrl && !imgError ? (
            <ProfileImage
              src={photoUrl}
              alt={shortName}
              className="home-person-photo"
              mediaSize="card"
              loading="lazy"
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="home-person-photo-fallback" aria-hidden="true">
              <div className="home-person-fallback-ring">
                <span className="home-person-initial">{initial}</span>
              </div>
            </div>
          )}

          {/* Top Overlay Badges */}
          <div className="home-person-photo-overlay">
            <span className="home-person-badge-new">ახალი</span>
            {zodiacDisplay && (
              <span className="home-person-zodiac-tag">
                {zodiacDisplay}
              </span>
            )}
          </div>
        </div>

        <div className="home-person-info">
          <div className="home-person-primary-row">
            <h3 className="home-person-name">{shortName}</h3>
            {ageDisplay && (
              <span className="home-person-age">{ageDisplay}</span>
            )}
          </div>

          {cityDisplay && (
            <div className="home-person-meta">
              <span className="home-person-city">{cityDisplay}</span>
            </div>
          )}

          {interestTags.length > 0 && (
            <div className="home-person-interests">
              {interestTags.map((interest) => (
                <span key={interest.id} className="home-person-interest-tag">
                  {interest.name}
                </span>
              ))}
            </div>
          )}
        </div>
      </Link>
    </div>
  );
}

export function HomeNewPeople({ people, isLoading, isError, onRetry }: HomeNewPeopleProps) {
  if (isLoading) {
    return (
      <section className="home-section home-people-section" aria-label="ახალი ადამიანები">
        <div className="home-card home-people-card">
          <div className="home-section-header">
            <div className="home-skeleton-line title" />
            <div className="home-skeleton-line short" />
          </div>
          <div className="home-people-container">
            <div className="home-people-track" role="list">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="home-person-card home-skeleton-person">
                  <div className="home-skeleton-avatar" />
                  <div className="home-skeleton-line title" />
                  <div className="home-skeleton-line short" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (isError) {
    return (
      <section className="home-section home-people-section" aria-label="ახალი ადამიანები">
        <div className="home-card home-error-card">
          <h2 className="home-error-title">ადამიანების სია ვერ ჩაიტვირთა</h2>
          <p className="home-error-desc">
            სერვერთან კავშირი შეფერხდა. სცადე ხელახლა რამდენიმე წამში.
          </p>
          {onRetry && (
            <button type="button" onClick={onRetry} className="home-btn home-btn-outline">
              ხელახლა ცდა
            </button>
          )}
        </div>
      </section>
    );
  }

  if (people.length === 0) {
    return (
      <section className="home-section home-people-section" aria-labelledby="home-people-heading">
        <div className="home-card home-empty-card">
          <h2 id="home-people-heading" className="home-section-title">
            ახალი ადამიანები
          </h2>
          <p className="home-empty-desc">
            ამჟამად ახალი პროფილები არ მოიძებნა. შეამოწმე მოგვიანებით.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="home-section home-people-section" aria-labelledby="home-people-heading">
      <div className="home-card home-people-card">
        <div className="home-section-header">
          <div className="home-section-title-row">
            <h2 id="home-people-heading" className="home-section-title">
              ახალი ადამიანები
            </h2>
            <span className="home-badge home-people-badge">18+ ვერიფიცირებული</span>
          </div>
          <p className="home-section-subtitle">
            პლატფორმის ბოლო დარეგისტრირებული მომხმარებლები
          </p>
        </div>

        <div className="home-people-container">
          <div className="home-people-track" role="list">
            {people.map((person) => (
              <HomePersonCardItem key={person.id} person={person} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

