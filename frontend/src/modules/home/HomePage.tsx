import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import { useAuth } from '../../core/auth/useAuth';
import type { ConnectionResponse, DiscoveryPerson } from '../../core/api/types';
import { HomeAvatar, HomeIcon, HomeSkeleton, HomeState } from './HomeElements';
import { calendarKey, connectionFor, georgianDate, guidanceItems, personObservation, visibleHomePeople } from './homeModel';
import './home.css';

function PersonPreview({
  person,
  connection,
  viewer,
  featured = false,
}: {
  person: DiscoveryPerson;
  connection?: ConnectionResponse;
  viewer: string;
  featured?: boolean;
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

  return (
    <article className={`home-person${featured ? ' home-person-featured' : ''}`}>
      <div className="home-person-identity">
        <HomeAvatar name={person.display_name} src={person.avatar_url} large={featured} />
        <div>
          <h3>
            <Link to={`/people/${person.id}`}>{person.display_name}</Link>
          </h3>
          <p className="home-person-meta">
            {[person.occupation, person.city].filter(Boolean).join(' · ') || 'გაიცანი უფრო ახლოს'}
          </p>
          {status && <span className="home-connection-tag">{status}</span>}
        </div>
      </div>

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

export function HomePage() {
  const { user } = useAuth();
  const [now, setNow] = useState(() => new Date());
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'failed'>('idle');
  const [expandedInsight, setExpandedInsight] = useState(false);
  const [filter, setFilter] = useState<'insights' | 'all'>('insights');
  const [page, setPage] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 60_000);
    return () => window.clearInterval(timer);
  }, []);

  const profile = useQuery({
    queryKey: ['profile', 'me'],
    queryFn: API.profiles.getMyProfile,
    enabled: !!user,
    staleTime: 60_000,
  });

  const day = calendarKey(now, profile.data?.timezone);
  const daily = useQuery({
    queryKey: ['daily-energy', user?.id, day],
    queryFn: () => API.interpretations.getDailyEnergy('auto', 'ka'),
    enabled: !!user,
    staleTime: 60_000,
    retry: 1,
  });

  const discovery = useQuery({
    queryKey: ['discovery-people', user?.id],
    queryFn: () => API.interpretations.getDiscoveryPeople(),
    enabled: !!user,
    staleTime: 30_000,
    retry: 1,
  });

  const connections = useQuery({
    queryKey: ['connections'],
    queryFn: API.connections.list,
    enabled: !!user,
    staleTime: 15_000,
    retry: 1,
  });

  const viewer = user?.id || '';
  const connectionList = connections.isError ? [] : connections.data || [];
  const people = discovery.isError ? [] : visibleHomePeople(discovery.data || [], connectionList, viewer);
  const observedPeople = people.filter(person => personObservation(person));
  const selectedPeople = filter === 'insights' ? observedPeople : people;
  const pageCount = Math.max(1, Math.ceil(selectedPeople.length / 4));
  const currentPage = Math.min(page, pageCount - 1);
  const visiblePeople = selectedPeople.slice(currentPage * 4, currentPage * 4 + 4);

  const accepted = connectionList.filter(c => c.status === 'accepted');
  const incoming = connectionList.filter(c => c.status === 'pending' && c.initiated_by !== viewer);
  const outgoing = connectionList.filter(c => c.status === 'pending' && c.initiated_by === viewer);

  // Only profiles already authorized by discovery; no speculative profile lookups.
  const familiar = people.find(person => connectionFor(accepted, viewer, person.id));
  const relationship = useQuery({
    queryKey: ['home-relationship', viewer, familiar?.id],
    queryFn: () => API.compatibility.why(familiar!.id),
    enabled: !!familiar && !connections.isError && !discovery.isError,
    retry: false,
    staleTime: 0,
  });

  const rawName = profile.data?.display_name?.trim();
  const name = !rawName || rawName === 'aaa A.' ? 'მეგობარო' : rawName;
  const observation = daily.data?.interpretation?.text?.trim();
  const realDay = daily.data?.detection_mode === 'real_transit' || daily.data?.detection_mode === 'neutral_baseline';
  const doItems = guidanceItems(daily.data?.do);
  const dontItems = guidanceItems(daily.data?.dont);
  const sourceDate = georgianDate(daily.data?.date);

  useEffect(() => {
    setCopyState('idle');
    setExpandedInsight(false);
  }, [observation]);

  const copyInsight = async () => {
    if (!observation) return;
    try {
      await navigator.clipboard.writeText(`${observation}\n— JESTER`);
      setCopyState('copied');
    } catch {
      setCopyState('failed');
    }
  };

  return (
    <div className="home-experience" lang="ka">
      {/* 0. Entry: Editorial Header & Greeting */}
      <header className="home-heading">
        <div>
          <div className="home-eyebrow-pill">
            <HomeIcon kind="sparkles" />
            <span>შენი სივრცე · {sourceDate || georgianDate(day) || 'დღეს'}</span>
          </div>
          <h1>
            გამარჯობა, <span>{name}</span>
          </h1>
          <p className="home-heading-lead">შენით იწყება. ადამიანებით გრძელდება.</p>
        </div>
        <Link to="/me" className="home-self-link" aria-label="ჩემი პროფილი">
          <HomeAvatar name={name} src={profile.data?.avatar_url} />
          <span>
            ჩემი პროფილი <HomeIcon />
          </span>
        </Link>
      </header>

      {profile.isError && (
        <HomeState title="პროფილი ვერ ჩაიტვირთა" retry={() => void profile.refetch()}>
          შენი სხვა სექციები კვლავ ხელმისაწვდომია.
        </HomeState>
      )}

      {/* Core Asymmetrical Split: 01 Hero Insight (ME) vs 02 Relationship Moment (US) */}
      <div className="home-opening">
        {/* 01 Editorial Primary Hero */}
        <section
          className="home-insight"
          aria-labelledby={observation && !daily.isError ? 'home-insight-title' : undefined}
          aria-label={!observation || daily.isError ? 'პირადი დაკვირვება' : undefined}
        >
          <div className="home-section-label">
            <span className="home-chapter">ME</span>
            <span>პირადი სივრცე</span>
            <span className="home-edition">{realDay ? sourceDate : 'პირადი ხედვა'}</span>
          </div>

          {daily.isLoading ? (
            <HomeSkeleton />
          ) : daily.isError ? (
            <HomeState title="დაკვირვება ვერ ჩაიტვირთა" retry={() => void daily.refetch()}>
              ცოტა ხანში ხელახლა სცადე. ადამიანების გაცნობა უკვე შეგიძლია.
            </HomeState>
          ) : observation ? (
            <>
              <p className="home-eyebrow home-insight-kicker">
                {realDay ? 'დღის დაკვირვება' : 'შენი პროფილის დაკვირვება'}
              </p>
              <h2 id="home-insight-title">{daily.data?.label || 'რას ამჩნევს JESTER'}</h2>
              <blockquote
                id="home-insight-text"
                className={expandedInsight || observation.length <= 180 ? 'is-expanded' : ''}
              >
                {observation}
              </blockquote>
              {observation.length > 180 && (
                <button
                  type="button"
                  className="home-read-more"
                  aria-expanded={expandedInsight}
                  aria-controls="home-insight-text"
                  onClick={() => setExpandedInsight(!expandedInsight)}
                >
                  {expandedInsight ? 'შეამცირე ტექსტი' : 'წაიკითხე სრულად'} <HomeIcon />
                </button>
              )}

              {(doItems.length > 0 || dontItems.length > 0) && (
                <details className="home-guidance-disclosure" open>
                  <summary>
                    დღის პატარა მინიშნებები <span aria-hidden="true">+</span>
                  </summary>
                  <div className="home-guidance">
                    {doItems.length > 0 && (
                      <div>
                        <h3>
                          <span aria-hidden="true">↗</span> სცადე
                        </h3>
                        <ul>
                          {doItems.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {dontItems.length > 0 && (
                      <div>
                        <h3>
                          <span aria-hidden="true">↘</span> ნუ იჩქარებ
                        </h3>
                        <ul>
                          {dontItems.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </details>
              )}

              <div className="home-insight-actions">
                <button
                  type="button"
                  className="home-text-button"
                  onClick={() => void copyInsight()}
                >
                  <HomeIcon kind={copyState === 'copied' ? 'check' : 'copy'} />
                  {copyState === 'copied' ? 'დაკოპირებულია' : 'დააკოპირე აზრი'}
                </button>
                <Link to="/me" className="home-text-link">
                  მეტი ჩემზე <HomeIcon />
                </Link>
              </div>

              <span className="home-copy-status" role="status">
                {copyState === 'copied'
                  ? 'ტექსტი დაკოპირებულია — შეგიძლია გაუზიარო მეგობარს.'
                  : copyState === 'failed'
                  ? 'კოპირება ვერ მოხერხდა. მონიშნე ტექსტი და დააკოპირე.'
                  : ''}
              </span>

              <details className="home-insight-context">
                <summary>რას ეფუძნება ეს დაკვირვება?</summary>
                <p>
                  {realDay
                    ? 'შენს პროფილსა და მითითებული დღის გამოთვლილ სიგნალებს.'
                    : 'შენს პროფილზე დაფუძნებული ზოგადი დაკვირვებაა; დღის პერსონალური გამოთვლა ამ პასუხში არ არის.'}
                </p>
              </details>
            </>
          ) : (
            <HomeState title="შენი დაკვირვება ჯერ არ არის ხელმისაწვდომი">
              <Link to="/me" className="home-text-link">
                გახსენი შენი პროფილი <HomeIcon />
              </Link>
            </HomeState>
          )}
        </section>

        {/* 02 Contextual Social Moment */}
        <aside className="home-circle" aria-labelledby="home-circle-title">
          <div className="home-section-label">
            <span className="home-chapter">US</span>
            <span>ჩვენი წრე</span>
          </div>

          <h2 id="home-circle-title">
            {accepted.length > 0 ? (
              <>
                კავშირი უკვე გაქვს.
                <br />
                <span>ახლა — გაიგე რატომ.</span>
              </>
            ) : (
              <>
                საინტერესოა,
                <br />
                <span>ვისთან გადაიკვეთები?</span>
              </>
            )}
          </h2>

          {connections.isLoading ? (
            <HomeSkeleton compact />
          ) : connections.isError ? (
            <HomeState title="კავშირები ვერ ჩაიტვირთა" retry={() => void connections.refetch()} />
          ) : (
            <>
              {incoming.length > 0 && (
                <Link to="/connections?tab=incoming" className="home-invitation">
                  <span>{incoming.length} ახალი მოთხოვნა</span>
                  <HomeIcon />
                </Link>
              )}

              {familiar ? (
                <>
                  <div className="home-pair" aria-label={`${name} და ${familiar.display_name}`}>
                    <HomeAvatar name={name} src={profile.data?.avatar_url} large />
                    <span className="home-pair-thread" aria-hidden="true">
                      <HomeIcon kind="people" />
                    </span>
                    <HomeAvatar name={familiar.display_name} src={familiar.avatar_url} large />
                  </div>
                  <h3 className="home-pair-name">შენ &amp; {familiar.display_name}</h3>
                  <p className="home-pair-caption">შენი წრიდან</p>

                  {relationship.isLoading ? (
                    <HomeSkeleton compact />
                  ) : relationship.isError ? (
                    <HomeState
                      title="კავშირის ანალიზი ახლა მიუწვდომელია"
                      retry={() => void relationship.refetch()}
                    >
                      პროფილისა და კავშირების გვერდები კვლავ ხელმისაწვდომია.
                    </HomeState>
                  ) : (
                    relationship.data && (
                      <>
                        <p className="home-relationship-copy">
                          {relationship.data.interpretation?.text ||
                            'კავშირის დეტალებში ნახე თქვენი ურთიერთობის დინამიკა.'}
                        </p>
                        {Number.isFinite(relationship.data.score) && (
                          <div className="home-score">
                            <strong>{Math.round(relationship.data.score)}</strong>
                            <span>
                              კავშირის ინდექსი
                              <br />
                              <small>საინტერესო ნაწილი — ახსნაა.</small>
                            </span>
                          </div>
                        )}
                      </>
                    )
                  )}

                  <Link to={`/people/${familiar.id}/why`} className="home-primary-link">
                    ჩვენი კავშირი <HomeIcon />
                  </Link>
                </>
              ) : accepted.length > 0 ? (
                <div className="home-circle-empty">
                  <HomeIcon kind="people" />
                  <p>შენს წრეში {accepted.length} კავშირია. გააგრძელე მათი გაცნობა.</p>
                  <Link to="/connections" className="home-primary-link">
                    ჩემი კავშირები <HomeIcon />
                  </Link>
                </div>
              ) : (
                <div className="home-circle-empty">
                  <HomeIcon kind="people" />
                  <h3>ვისთან დაიწყებ?</h3>
                  <p>ჯერ გაიცანი ადამიანი. ორმხრივი კავშირის შემდეგ თქვენს დინამიკასაც შევხედოთ.</p>
                  <a href="#home-people" className="home-primary-link">
                    გაიცანი ადამიანები <HomeIcon />
                  </a>
                </div>
              )}

              <div className="home-circle-footer">
                <Link to="/connections">{accepted.length} კავშირი</Link>
                <Link to="/messages">
                  საუბრები <HomeIcon kind="message" />
                </Link>
              </div>

              {outgoing.length > 0 && (
                <Link to="/connections?tab=outgoing" className="home-outgoing">
                  {outgoing.length} გაგზავნილი მოთხოვნა
                </Link>
              )}
            </>
          )}
        </aside>
      </div>

      {/* 03 Discover Preview */}
      <section id="home-people" className="home-discovery" aria-labelledby="home-people-title">
        <div className="home-discovery-heading">
          <div>
            <div className="home-eyebrow-pill home-eyebrow-dark">
              <span>ცნობისმოყვარეობა გრძელდება</span>
            </div>
            <h2 id="home-people-title">
              ერთი პროფილის მიღმა —<br />
              <span>მთელი ადამიანია.</span>
            </h2>
          </div>
          <Link to="/discover" className="home-outline-link">
            ყველა ადამიანი <HomeIcon />
          </Link>
        </div>

        <div className="home-discovery-tools">
          <div className="home-filter" role="group" aria-label="ადამიანების ჩვენება">
            <button
              type="button"
              aria-pressed={filter === 'insights'}
              onClick={() => {
                setFilter('insights');
                setPage(0);
              }}
            >
              დაკვირვებით{discovery.isSuccess && ` · ${observedPeople.length}`}
            </button>
            <button
              type="button"
              aria-pressed={filter === 'all'}
              onClick={() => {
                setFilter('all');
                setPage(0);
              }}
            >
              ყველა{discovery.isSuccess && ` · ${people.length}`}
            </button>
          </div>
          <p>სახელის მიხედვით · რეიტინგის გარეშე</p>
        </div>

        {discovery.isLoading ? (
          <div className="home-people-layout">
            <HomeSkeleton />
            <HomeSkeleton />
          </div>
        ) : discovery.isError ? (
          <HomeState
            title="ადამიანების სია ვერ ჩაიტვირთა"
            retry={() => void discovery.refetch()}
          >
            შენი კავშირები და პირადი სივრცე ცალკე რჩება ხელმისაწვდომი.
          </HomeState>
        ) : visiblePeople.length === 0 ? (
          <HomeState
            title={filter === 'insights' ? 'დაკვირვებები ჯერ არ ჩანს' : 'ამ ეტაპზე ახალი პროფილები არ ჩანს'}
          >
            {filter === 'insights' && people.length > 0 ? (
              <button
                type="button"
                className="home-text-button"
                onClick={() => {
                  setFilter('all');
                  setPage(0);
                }}
              >
                ნახე ყველა {people.length} პროფილი <HomeIcon />
              </button>
            ) : (
              <button
                type="button"
                className="home-text-button"
                onClick={() => void discovery.refetch()}
              >
                განაახლე სია <HomeIcon />
              </button>
            )}
          </HomeState>
        ) : (
          <>
            <div className="home-people-layout">
              <PersonPreview
                key={visiblePeople[0].id}
                person={visiblePeople[0]}
                connection={connectionFor(connectionList, viewer, visiblePeople[0].id)}
                viewer={viewer}
                featured
              />
              <div className="home-people-list">
                {visiblePeople.slice(1).map(person => (
                  <PersonPreview
                    key={person.id}
                    person={person}
                    connection={connectionFor(connectionList, viewer, person.id)}
                    viewer={viewer}
                  />
                ))}
              </div>
            </div>

            <div className="home-pagination">
              <span role="status">
                {currentPage * 4 + 1}–{Math.min((currentPage + 1) * 4, selectedPeople.length)} /{' '}
                {selectedPeople.length} პროფილი
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
          </>
        )}
      </section>

      {/* Closing Editorial Action */}
      <footer className="home-closing">
        <div>
          <span className="home-eyebrow">გაცნობა ორივე მხრიდან იწყება</span>
          <h2>
            {profile.data && !profile.data.bio
              ? 'შენზე რას გაიგებენ?'
              : 'შენი პროფილიც ჰყვება ამბავს.'}
          </h2>
          <p>
            {profile.data && !profile.data.bio
              ? 'ორი სიტყვა შენზე ზოგჯერ ათ ფოტოზე მეტს ამბობს.'
              : 'დატოვე ის დეტალები, საიდანაც ნამდვილი საუბარი იწყება.'}
          </p>
        </div>
        <Link to="/me" className="home-outline-link">
          ჩემი პროფილი <HomeIcon />
        </Link>
      </footer>

      {/* Adult-Only Policy Notice */}
      <div className="home-policy-notice">
        <span className="home-policy-badge">18+</span>
        <span>JESTER განკუთვნილია სრულწლოვანი მომხმარებლებისთვის · People Discovery &amp; Relationship Intelligence</span>
      </div>
    </div>
  );
}
