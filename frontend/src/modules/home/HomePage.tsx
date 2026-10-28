import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import type { DiscoveryPerson, ProfilePhoto } from '../../core/api/types';
import { useAuth } from '../../core/auth/useAuth';
import {
  ConnectionThreadMotif,
  HomeAvatar,
  HomeIcon,
  HomeSkeleton,
  HomeState,
  ThreePerspectiveSpark,
} from './HomeElements';
import {
  calendarKey,
  connectionFor,
  georgianDate,
  guidanceItems,
  personObservation,
  visibleHomePeople,
} from './homeModel';
import {
  HomeConversationInvitation,
  HomeMeAtelier,
  HomeSalonMasthead,
  HomeSpotlightStage,
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

  // Explicit connection request confirmation modal state
  const [connectTarget, setConnectTarget] = useState<DiscoveryPerson | null>(null);
  const [connectBusy, setConnectBusy] = useState(false);
  const [connectError, setConnectError] = useState<string | null>(null);
  const connectDialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 60_000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    const dialog = connectDialogRef.current;
    if (!dialog) return;
    if (connectTarget) {
      if (!dialog.open) dialog.showModal();
    } else if (dialog.open) {
      dialog.close();
    }
  }, [connectTarget]);

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
        // Fallback to legacy discovery preview only if deck endpoint fails
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
  const realDay =
    daily.data?.detection_mode === 'real_transit' ||
    daily.data?.detection_mode === 'neutral_baseline';
  const doItems = guidanceItems(daily.data?.do);
  const dontItems = guidanceItems(daily.data?.dont);
  const sourceDate = georgianDate(daily.data?.date);
  const editionDate = sourceDate || georgianDate(day);

  useEffect(() => {
    setCopyState('idle');
    setExpandedInsight(false);
  }, [observation]);

  const copyInsight = async (customText?: string) => {
    const payload = (customText || observation).trim();
    if (!payload) return;
    try {
      await navigator.clipboard.writeText(`„${payload}“\n— JESTER`);
      setCopyState('copied');
    } catch {
      setCopyState('failed');
    }
  };

  const handleOpenConnect = (person: DiscoveryPerson) => {
    setConnectError(null);
    setConnectTarget(person);
  };

  const handleConfirmConnect = async () => {
    if (!connectTarget || !API.connections?.create) return;
    setConnectBusy(true);
    setConnectError(null);
    try {
      await API.connections.create(connectTarget.id);
      await Promise.all([connections.refetch(), discovery.refetch()]);
      setConnectTarget(null);
    } catch (err: any) {
      setConnectError(err?.message || 'მოთხოვნის გაგზავნა ვერ მოხერხდა. სცადე ხელახლა.');
    } finally {
      setConnectBusy(false);
    }
  };

  const familiarPrimaryPhoto =
    ((familiar as { photos?: ProfilePhoto[] } | undefined)?.photos?.[0]?.url) ||
    familiar?.avatar_url;

  return (
    <div className="home-experience home-rebuilt" lang="ka">
      {/* BAND 0: Personal Salon Masthead */}
      <HomeSalonMasthead
        name={name}
        avatarUrl={profile.data?.avatar_url}
        editionDate={editionDate}
        hour={now.getHours()}
        peopleCount={discovery.isSuccess ? people.length : undefined}
        connectionCount={connections.isSuccess ? accepted.length : undefined}
        incomingCount={connections.isSuccess ? incoming.length : undefined}
      />

      {profile.isError && (
        <div className="home-profile-alert-wrap">
          <HomeState title="პროფილი ვერ ჩაიტვირთა" retry={() => void profile.refetch()}>
            შენი სხვა სექციები კვლავ ხელმისაწვდომია.
          </HomeState>
        </div>
      )}

      {/* BAND 1: Opening Asymmetric Stage (Left: Daily JESTER Stage | Right: 4-Facet ME Atelier) */}
      <div className="home-stage-band">
        <section
          id="home-daily"
          className="home-daily-column"
          aria-labelledby={observation && !daily.isError ? 'home-insight-title' : undefined}
          aria-label={!observation || daily.isError ? 'პირადი დაკვირვება' : undefined}
        >
          {daily.isLoading ? (
            <div className="home-stage-placeholder-card">
              <HomeSkeleton />
            </div>
          ) : daily.isError ? (
            <HomeState title="დაკვირვება ვერ ჩაიტვირთა" retry={() => void daily.refetch()}>
              ცოტა ხანში ხელახლა სცადე. ადამიანების გაცნობა უკვე შეგიძლია.
            </HomeState>
          ) : observation ? (
            <HomeSpotlightStage
              observation={observation}
              realDay={realDay}
              sourceDate={sourceDate}
              dailyLabel={daily.data?.label || 'რას ამჩნევს JESTER'}
              doItems={doItems}
              dontItems={dontItems}
              copyState={copyState}
              onCopy={(txt) => void copyInsight(txt)}
              expandedInsight={expandedInsight}
              onToggleExpand={() => setExpandedInsight((prev) => !prev)}
              safeAstro={safeAstro.data}
              natalFacets={natalFacets.data}
            />
          ) : (
            <HomeState title="შენი დაკვირვება ჯერ არ არის ხელმისაწვდომი">
              <Link to="/me" className="home-pill-action">
                <span>გახსენი შენი პროფილი</span>
                <HomeIcon />
              </Link>
            </HomeState>
          )}
        </section>

        <HomeMeAtelier
          safeAstro={safeAstro.data}
          natalFacets={natalFacets.data}
          isLoading={Boolean(
            safeAstro.isLoading || (safeAstro.data?.sun_sign && natalFacets.isLoading)
          )}
        />
      </div>

      {/* BAND 2: Photo-Forward Human Discovery (Full-Width Showcase) */}
      <section
        id="home-people"
        className="home-people-showcase"
        aria-labelledby="home-people-title"
      >
        <div className="home-people-header">
          <div className="home-people-heading-copy">
            <span className="home-section-kicker">
              <ThreePerspectiveSpark />
              <span>YOU · ადამიანების აღმოჩენა</span>
            </span>
            <h2 id="home-people-title">დღეს შენს ჰორიზონტზე</h2>
            <p className="home-people-subtitle">
              რეალური ადამიანები, საერთო ინტერესები და JESTER-ის ზუსტი პირველი შთაბეჭდილება.
            </p>
          </div>

          <Link to="/discover" className="home-pill-action home-discover-all-cta">
            <span>ყველა ადამიანი</span>
            <HomeIcon />
          </Link>
        </div>

        {discovery.isLoading ? (
          <div className="home-desktop-cards-grid">
            <div className="home-stage-placeholder-card">
              <HomeSkeleton />
            </div>
            <div className="home-stage-placeholder-card">
              <HomeSkeleton />
            </div>
            <div className="home-stage-placeholder-card">
              <HomeSkeleton />
            </div>
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
                className="home-pill-action"
                onClick={() => setFilter('all')}
              >
                <span>ნახე ყველა {people.length} პროფილი</span>
                <HomeIcon />
              </button>
            ) : (
              <button
                type="button"
                className="home-pill-action"
                onClick={() => void discovery.refetch()}
              >
                <span>განაახლე სია</span>
                <HomeIcon />
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
            onRequestConnect={handleOpenConnect}
          />
        )}
      </section>

      {/* BAND 3: US Social Circle & Shuffleable Conversation Spark */}
      <div className="home-social-band">
        <aside className="home-circle" aria-labelledby="home-circle-title">
          <div className="home-circle-top">
            <div>
              <span className="home-section-kicker">US · ჩვენი წრე</span>
              <h2 id="home-circle-title">შენი ახლო კავშირები</h2>
            </div>
            <Link to="/connections" className="home-pill-action">
              <span>ყველა</span>
              <HomeIcon />
            </Link>
          </div>

          {connections.isLoading ? (
            <HomeSkeleton compact />
          ) : connections.isError ? (
            <HomeState
              title="კავშირები ვერ ჩაიტვირთა"
              retry={() => void connections.refetch()}
            />
          ) : (
            <>
              {incoming.length > 0 && (
                <Link to="/connections?tab=incoming" className="home-circle-incoming">
                  <span>{incoming.length} ახალი კავშირის მოთხოვნა გელოდება</span>
                  <HomeIcon />
                </Link>
              )}

              {(() => {
                const listedConnections = familiar
                  ? accepted.filter((c) => {
                      const otherId = c.user_a_id === viewer ? c.user_b_id : c.user_a_id;
                      return otherId !== familiar.id;
                    })
                  : accepted;

                return (
                  <>
                    {familiar && (
                      <div className="home-resonance-box">
                        <ul className="home-active-people home-resonance-identity-list">
                          <li>
                            <div
                              className="home-resonance-cameos"
                              aria-label={`${name} და ${familiar.display_name}`}
                            >
                              <HomeAvatar name={name} src={profile.data?.avatar_url} large arch />
                              <ConnectionThreadMotif className="home-resonance-thread" />
                              <Link
                                to={`/people/${familiar.id}`}
                                className="home-resonance-partner-cameo"
                                aria-label={`${familiar.display_name} — პროფილი`}
                              >
                                <HomeAvatar
                                  name={familiar.display_name}
                                  src={familiarPrimaryPhoto}
                                  large
                                  arch
                                />
                              </Link>
                            </div>
                          </li>
                        </ul>

                        <div className="home-resonance-head">
                          <div>
                            <h3>
                              <Link to={`/people/${familiar.id}`}>
                                შენ და {familiar.display_name}
                              </Link>
                            </h3>
                            {(familiar.occupation || familiar.city) && (
                              <p className="home-resonance-sub">
                                {[familiar.occupation, familiar.city].filter(Boolean).join(' · ')}
                              </p>
                            )}
                          </div>
                          {relationship.data && Number.isFinite(relationship.data.score) && (
                            <div className="home-score">
                              <strong>{Math.round(relationship.data.score)}</strong>
                              <span>
                                კავშირის ინდექსი
                                <br />
                                <small>საინტერესო ნაწილი — ახსნაა.</small>
                              </span>
                            </div>
                          )}
                        </div>

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
                            <p className="home-resonance-quote">
                              „
                              {relationship.data.interpretation?.text ||
                                'კავშირის დეტალებში ნახე თქვენი ურთიერთობის სრული დინამიკა.'}
                              “
                            </p>
                          )
                        )}

                        <Link to={`/people/${familiar.id}/why`} className="home-cta-dark">
                          <span>სრული დინამიკა · ჩვენი კავშირი</span>
                          <HomeIcon />
                        </Link>
                      </div>
                    )}

                    {listedConnections.length > 0 && (
                      <ul className="home-active-people">
                        {listedConnections.slice(0, 3).map((connection) => {
                          const otherId =
                            connection.user_a_id === viewer
                              ? connection.user_b_id
                              : connection.user_a_id;
                          const person = people.find((p) => p.id === otherId);
                          const personPhoto = (
                            person as { photos?: ProfilePhoto[] } | undefined
                          )?.photos?.[0]?.url;
                          const displayName =
                            connection.other_display_name ||
                            person?.display_name ||
                            'შენი კავშირი';
                          const avatarSrc =
                            connection.other_avatar_url || personPhoto || person?.avatar_url;

                          return (
                            <li key={connection.id}>
                              <Link to={`/people/${otherId}`} className="home-active-person-row">
                                <HomeAvatar name={displayName} src={avatarSrc} arch />
                                <span className="home-active-person-info">
                                  <strong>{displayName}</strong>
                                  <small>
                                    {person?.occupation
                                      ? `${person.occupation}${person.city ? ` · ${person.city}` : ''}`
                                      : 'უკვე დაკავშირებული ხართ'}
                                  </small>
                                </span>
                                <HomeIcon />
                              </Link>
                            </li>
                          );
                        })}
                      </ul>
                    )}

                    {!familiar && accepted.length === 0 && (
                      <div className="home-circle-empty-stage">
                        <ConnectionThreadMotif className="home-empty-thread" />
                        <h3>შენი წრე ჯერ თავისუფალია</h3>
                        <p>
                          ეს ბევრად სჯობს შემთხვევითი ხალხით სავსე სიას. ჯერ გაიცანი ადამიანი —
                          ორმხრივი კავშირის შემდეგ JESTER თქვენს საერთო დინამიკასაც გახსნის.
                        </p>
                        <a href="#home-people" className="home-cta-orange">
                          <span>გადადი ადამიანებზე</span>
                          <HomeIcon />
                        </a>
                      </div>
                    )}
                  </>
                );
              })()}

              <div className="home-circle-bottom-bar">
                <Link to="/connections">{accepted.length} კავშირი</Link>
                {outgoing.length > 0 && (
                  <Link to="/connections?tab=outgoing">
                    {outgoing.length} გაგზავნილი მოთხოვნა
                  </Link>
                )}
                <Link to="/messages">
                  <span>საუბრები</span>
                  <HomeIcon kind="message" />
                </Link>
              </div>
            </>
          )}
        </aside>

        <HomeConversationInvitation hasConnections={accepted.length > 0} />
      </div>

      {/* BAND 4: Profile Story Nudge & 18+ Privacy Footer */}
      <footer className="home-closing">
        <div className="home-closing-copy">
          <span className="home-section-kicker">გაცნობა ორივე მხრიდან იწყება</span>
          <h2>
            {profile.data && !profile.data.bio
              ? 'შენზე რას შეამჩნევენ პირველს?'
              : 'შენი პროფილიც ჰყვება ამბავს.'}
          </h2>
          <p>
            {profile.data && !profile.data.bio
              ? 'ორი გულწრფელი წინადადება და ნამდვილი ფოტო საუბარს ბევრად უფრო ბუნებრივად იწყებს.'
              : 'განაახლე ფოტოები ან ინტერესები, რომ საერთო გადაკვეთები უფრო ზუსტად გამოჩნდეს.'}
          </p>
        </div>
        <Link to="/me" className="home-pill-action home-closing-cta">
          <span>ჩემი პროფილი</span>
          <HomeIcon />
        </Link>
      </footer>

      <div className="home-policy-notice">
        <div className="home-policy-left">
          <span className="home-policy-badge">18+</span>
          <span>
            JESTER — სრულწლოვანთა ადამიანების აღმოჩენისა და ურთიერთობების ინტელექტის სივრცე.
          </span>
        </div>
        <span className="home-policy-privacy">
          დაბადების ზუსტი დრო და კოორდინატები მხოლოდ შენ გეკუთვნის და სხვებისთვის არასდროს ჩანს.
        </span>
      </div>

      {connectTarget && (
        <dialog
          ref={connectDialogRef}
          className="home-connect-dialog"
          aria-labelledby="home-connect-dialog-title"
          onCancel={() => {
            if (!connectBusy) setConnectTarget(null);
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget && !connectBusy) setConnectTarget(null);
          }}
        >
          <div className="home-connect-dialog-inner">
            <span className="home-section-kicker">კავშირის მოთხოვნა</span>
            <h2 id="home-connect-dialog-title">
              გავუგზავნოთ მოთხოვნა — {connectTarget.display_name}?
            </h2>
            <p>
              {connectTarget.display_name} მიიღებს შენს მოწვევას. პირადი მიმოწერა და საერთო
              დინამიკის გვერდი გაიხსნება მხოლოდ ორმხრივი თანხმობის შემდეგ.
            </p>
            {connectError && (
              <p className="home-connect-dialog-error" role="alert">
                {connectError}
              </p>
            )}
            <div className="home-connect-dialog-actions">
              <button
                type="button"
                className="home-pill-action"
                disabled={connectBusy}
                onClick={() => setConnectTarget(null)}
              >
                ჯერ არა
              </button>
              <button
                type="button"
                className="home-cta-orange"
                disabled={connectBusy}
                onClick={() => void handleConfirmConnect()}
              >
                <span>{connectBusy ? 'იგზავნება…' : 'მოთხოვნის გაგზავნა'}</span>
                <HomeIcon />
              </button>
            </div>
          </div>
        </dialog>
      )}
    </div>
  );
}
