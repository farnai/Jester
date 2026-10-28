import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import { useAuth } from '../../core/auth/useAuth';
import { HomeAvatar, HomeIcon, HomeSkeleton, HomeState } from './HomeElements';
import {
  calendarKey,
  connectionFor,
  georgianDate,
  guidanceItems,
  personObservation,
  visibleHomePeople,
} from './homeModel';
import {
  HomeEditorialHero,
  HomeQuickActions,
  HomeConversationInvitation,
  HomeInsightArt,
  HomeStage,
} from './HomeEditorial';
import { HomePersonCarousel } from './HomePersonCarousel';
import './home.css';
import './homeEditorial.css';

export function HomePage() {
  const { user } = useAuth();
  const [now, setNow] = useState(() => new Date());
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'failed'>('idle');
  const [expandedInsight, setExpandedInsight] = useState(false);
  const [filter, setFilter] = useState<'insights' | 'all'>('insights');

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
    queryFn: () =>
      API.interpretations?.getDailyEnergy
        ? API.interpretations.getDailyEnergy('auto', 'ka')
        : Promise.resolve({} as any),
    enabled: !!user,
    staleTime: 60_000,
    retry: 1,
  });

  // Safe Astrology Query (Sun, Moon, Ascendant, Mercury, Venus, Mars, Element, Modality)
  const safeAstro = useQuery({
    queryKey: ['safe-astro', user?.id],
    queryFn: () =>
      API.astrology?.getMySafeAstro
        ? API.astrology.getMySafeAstro()
        : Promise.resolve(null as any),
    enabled: !!user,
    staleTime: 300_000,
    retry: 1,
  });

  // Resolved Natal Facets for 4-Facet ME Lens and Core Verdict
  const natalFacets = useQuery({
    queryKey: ['natal-facets', user?.id, safeAstro.data?.sun_sign],
    queryFn: () =>
      API.interpretations?.resolveNatal
        ? API.interpretations.resolveNatal({
            sun_sign: safeAstro.data?.sun_sign || '',
            moon_sign: safeAstro.data?.moon_sign,
            ascendant_sign: safeAstro.data?.ascendant_sign,
            mercury_sign: safeAstro.data?.mercury_sign,
            venus_sign: safeAstro.data?.venus_sign,
            mars_sign: safeAstro.data?.mars_sign,
            element_primary: safeAstro.data?.element_primary,
            modality_primary: safeAstro.data?.modality_primary,
            locale: 'ka',
            tone: 'snarky',
          })
        : Promise.resolve([] as any),
    enabled: !!user && !!safeAstro.data?.sun_sign,
    staleTime: 600_000,
    retry: 1,
  });

  const discovery = useQuery({
    queryKey: ['discovery-people', user?.id],
    queryFn: async () => {
      try {
        if (API.discovery?.people) {
          const res = await API.discovery.people({});
          return res.items || [];
        }
      } catch {
        // fallback
      }
      return API.interpretations?.getDiscoveryPeople
        ? API.interpretations.getDiscoveryPeople()
        : ([] as any);
    },
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
  const observedPeople = people.filter((person) => personObservation(person));
  const selectedPeople = filter === 'insights' ? observedPeople : people;

  const accepted = connectionList.filter((c) => c.status === 'accepted');
  const incoming = connectionList.filter((c) => c.status === 'pending' && c.initiated_by !== viewer);
  const outgoing = connectionList.filter((c) => c.status === 'pending' && c.initiated_by === viewer);

  // Only profiles already authorized by discovery; no speculative profile lookups.
  const familiar = people.find((person) => connectionFor(accepted, viewer, person.id));
  const relationship = useQuery({
    queryKey: ['home-relationship', viewer, familiar?.id],
    queryFn: () => API.compatibility.why(familiar!.id),
    enabled: !!familiar && !connections.isError && !discovery.isError,
    retry: false,
    staleTime: 0,
  });

  const rawName = profile.data?.display_name?.trim();
  const name = !rawName || rawName === 'aaa A.' ? 'მეგობარო' : rawName;
  const observation = daily.data?.interpretation?.text?.trim() || '';
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
      {/* 00 Editorial Hero Greeting */}
      <HomeEditorialHero
        name={name}
        avatarUrl={profile.data?.avatar_url}
        connectionCount={connections.isSuccess ? accepted.length : undefined}
        incomingCount={connections.isSuccess ? incoming.length : undefined}
      />
      <HomeQuickActions />

      {profile.isError && (
        <HomeState title="პროფილი ვერ ჩაიტვირთა" retry={() => void profile.refetch()}>
          შენი სხვა სექციები კვლავ ხელმისაწვდომია.
        </HomeState>
      )}

      {/* Core Asymmetrical Split: 01 Hero Spotlight Stage (ME) vs 02 Relationship Circle (US) */}
      <div className="home-opening">
        {/* 01 Editorial Primary Hero Spotlight Stage (ME) */}
        <section
          id="home-daily"
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
              <HomeInsightArt />
              <HomeStage
                observation={observation}
                realDay={realDay}
                sourceDate={sourceDate}
                dailyLabel={daily.data?.label || 'რას ამჩნევს JESTER'}
                doItems={doItems}
                dontItems={dontItems}
                copyState={copyState}
                onCopy={() => void copyInsight()}
                expandedInsight={expandedInsight}
                onToggleExpand={() => setExpandedInsight(!expandedInsight)}
                safeAstro={safeAstro.data}
                natalFacets={natalFacets.data}
              />
            </>
          ) : (
            <HomeState title="შენი დაკვირვება ჯერ არ არის ხელმისაწვდომი">
              <Link to="/me" className="home-text-link">
                გახსენი შენი პროფილი <HomeIcon />
              </Link>
            </HomeState>
          )}
        </section>

        {/* 02 Contextual Social Circle (US) */}
        <aside className="home-circle" aria-labelledby="home-circle-title">
          <div className="home-section-label">
            <span className="home-chapter">US</span>
            <span>ჩვენი წრე</span>
          </div>

          <div className="home-circle-heading">
            <h2 id="home-circle-title">შენი ახლო კავშირები</h2>
            <Link to="/connections" className="home-text-link">
              ყველა <HomeIcon />
            </Link>
          </div>

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

              {accepted.length > 0 && (
                <ul className="home-active-people">
                  {accepted.slice(0, 3).map((connection) => {
                    const otherId =
                      connection.user_a_id === viewer ? connection.user_b_id : connection.user_a_id;
                    const person = people.find((p) => p.id === otherId);
                    const displayName =
                      connection.other_display_name || person?.display_name || 'შენი კავშირი';
                    return (
                      <li key={connection.id}>
                        <Link to={`/people/${otherId}`}>
                          <HomeAvatar
                            name={displayName}
                            src={connection.other_avatar_url || person?.avatar_url}
                          />
                          <span>
                            <strong>{displayName}</strong>
                            <small>უკვე დაკავშირებული ხართ</small>
                            {person?.occupation && (
                              <span className="home-active-detail">{person.occupation}</span>
                            )}
                          </span>
                          <HomeIcon />
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              )}

              {familiar ? (
                <details className="home-relationship-details" open>
                  <summary>შენ &amp; {familiar.display_name} · თქვენი დინამიკა</summary>
                  <div className="home-pair" aria-label={`${name} და ${familiar.display_name}`}>
                    <HomeAvatar name={name} src={profile.data?.avatar_url} large />
                    <span className="home-pair-thread" aria-hidden="true">
                      <HomeIcon kind="people" />
                    </span>
                    <HomeAvatar name={familiar.display_name} src={familiar.avatar_url} large />
                  </div>
                  <h3 className="home-pair-name">
                    შენ &amp; {familiar.display_name}
                  </h3>
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
                </details>
              ) : accepted.length > 0 ? null : (
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

      {/* 03 Social Discovery Floor (MORE PEOPLE) */}
      <div className="home-lower-grid">
        <section id="home-people" className="home-discovery" aria-labelledby="home-people-title">
          <div className="home-discovery-heading">
            <div>
              <h2 id="home-people-title">გაიცანი ადამიანები</h2>
            </div>
            <Link to="/discover" className="home-outline-link">
              ყველა ადამიანი <HomeIcon />
            </Link>
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
          ) : selectedPeople.length === 0 ? (
            <HomeState
              title={
                filter === 'insights'
                  ? 'დაკვირვებები ჯერ არ ჩანს'
                  : 'ამ ეტაპზე ახალი პროფილები არ ჩანს'
              }
            >
              {filter === 'insights' && people.length > 0 ? (
                <button
                  type="button"
                  className="home-text-button"
                  onClick={() => setFilter('all')}
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
            <HomePersonCarousel
              people={selectedPeople}
              connections={connectionList}
              viewer={viewer}
              filter={filter}
              onFilterChange={setFilter}
              observedCount={observedPeople.length}
              totalCount={people.length}
              onRefresh={() => void discovery.refetch()}
            />
          )}
        </section>

        <HomeConversationInvitation hasConnections={accepted.length > 0} />
      </div>

      {/* 04 Closing Editorial Action */}
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

      {/* 05 Adult-Only Policy Notice */}
      <div className="home-policy-notice">
        <span className="home-policy-badge">18+</span>
        <span>
          JESTER განკუთვნილია სრულწლოვანი მომხმარებლებისთვის · People Discovery &amp; Relationship
          Intelligence
        </span>
      </div>
    </div>
  );
}
