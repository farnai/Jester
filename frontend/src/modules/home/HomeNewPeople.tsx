import { Link } from 'react-router-dom';
import type { DiscoveryPerson } from '../../core/api/types';

interface HomeNewPeopleProps {
  people: DiscoveryPerson[];
  isLoading: boolean;
  isError: boolean;
  onRetry?: () => void;
}

export function HomeNewPeople({ people, isLoading, isError, onRetry }: HomeNewPeopleProps) {
  if (isLoading) {
    return (
      <section className="home-section home-people-section" aria-label="ახალი ადამიანები">
        <div className="home-section-header">
          <div className="home-skeleton-line title" />
          <div className="home-skeleton-line short" />
        </div>
        <div className="home-people-carousel">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="home-person-card home-skeleton-person">
              <div className="home-skeleton-avatar" />
              <div className="home-skeleton-line title" />
              <div className="home-skeleton-line short" />
            </div>
          ))}
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
          {people.map((person) => {
            const photoUrl = person.photos?.[0]?.url || person.avatar_url;
            const initial = person.display_name?.charAt(0) || 'J';
            const ageDisplay = person.age ? `${person.age} წლის` : null;
            const cityDisplay = person.city_name || person.city || null;
            const interestTags = (person.interests || []).slice(0, 3);

            return (
              <div key={person.id} className="home-person-card" role="listitem">
                <Link to={`/people/${person.id}`} className="home-person-link">
                  <div className="home-person-photo-wrap">
                    {photoUrl ? (
                      <img
                        src={photoUrl}
                        alt={person.display_name}
                        className="home-person-photo"
                        loading="lazy"
                      />
                    ) : (
                      <div className="home-person-photo-fallback" aria-hidden="true">
                        <span className="home-person-initial">{initial}</span>
                        {person.astrology?.sun_sign && (
                          <span className="home-person-sign-tag">
                            {person.astrology.sun_sign}
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="home-person-info">
                    <h3 className="home-person-name">{person.display_name}</h3>

                    <div className="home-person-meta">
                      {ageDisplay && <span className="home-person-age">{ageDisplay}</span>}
                      {ageDisplay && cityDisplay && <span className="home-person-dot">•</span>}
                      {cityDisplay && <span className="home-person-city">{cityDisplay}</span>}
                    </div>

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
          })}
        </div>
      </div>
    </section>
  );
}

