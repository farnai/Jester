import { useState } from 'react';
import { Link } from 'react-router-dom';
import { HomeAvatar, HomeIcon } from './HomeElements';
import portrait from '../../assets/registration/hero_portrait.jpg';
import secondPortrait from '../../assets/registration/hero_woman_highres.jpg';

export const GEORGIAN_SIGNS: Record<string, string> = {
  Aries: 'ვერძი',
  Taurus: 'კურო',
  Gemini: 'ტყუპები',
  Cancer: 'კირჩხიბი',
  Leo: 'ლომი',
  Virgo: 'ქალწული',
  Libra: 'სასწორი',
  Scorpio: 'მორიელი',
  Sagittarius: 'მშვილდოსანი',
  Capricorn: 'თხის რქა',
  Aquarius: 'მერწყული',
  Pisces: 'თევზები',
  aries: 'ვერძი',
  taurus: 'კურო',
  gemini: 'ტყუპები',
  cancer: 'კირჩხიბი',
  leo: 'ლომი',
  virgo: 'ქალწული',
  libra: 'სასწორი',
  scorpio: 'მორიელი',
  sagittarius: 'მშვილდოსანი',
  capricorn: 'თხის რქა',
  aquarius: 'მერწყული',
  pisces: 'თევზები',
};

export const GEORGIAN_ELEMENTS: Record<string, string> = {
  Fire: 'ცეცხლი',
  Earth: 'მიწა',
  Air: 'ჰაერი',
  Water: 'წყალი',
  fire: 'ცეცხლი',
  earth: 'მიწა',
  air: 'ჰაერი',
  water: 'წყალი',
};

/** Brand photography is decorative, never presented as a discoverable member. */
export function HomeEditorialHero({
  name,
  avatarUrl,
  connectionCount,
  incomingCount,
}: {
  name: string;
  avatarUrl?: string | null;
  connectionCount?: number;
  incomingCount?: number;
}) {
  return (
    <header className="home-editorial-hero">
      <div className="home-hero-copy">
        <Link to="/me" className="home-hero-greeting" aria-label={`შენი პროფილი - ${name}`}>
          <HomeAvatar name={name} src={avatarUrl} />
          <span>
            <small>შენი სივრცე</small>
            <strong>გამარჯობა, {name}</strong>
          </span>
          <HomeIcon />
        </Link>

        {connectionCount !== undefined && (
          <div className="home-personal-context">
            <Link to="/connections">შენი წრე · {connectionCount} კავშირი</Link>
            {!!incomingCount && (
              <Link to="/connections?tab=incoming" className="home-incoming-badge-pill">
                {incomingCount} ახალი მოთხოვნა <HomeIcon />
              </Link>
            )}
          </div>
        )}

        <h1>
          კარგი საუბარი
          <br />
          შემთხვევით
          <br />
          <em>არ იწყება.</em>
        </h1>
        <p className="home-hero-description">
          გაიცანი საინტერესო ადამიანები.
          <br className="home-desktop-break" /> აღმოაჩინე, რა გაკავშირებთ.
        </p>
        <Link to="/discover" className="home-primary-link">
          აღმოაჩინე ადამიანები <HomeIcon />
        </Link>
      </div>

      <div className="home-hero-art" aria-hidden="true">
        <span className="home-art-blob" />
        <span className="home-art-orbit" />
        <img className="home-hero-portrait" src={portrait} alt="" fetchPriority="high" />
        <img className="home-hero-secondary" src={secondPortrait} alt="" />
        <span className="home-art-note">
          ყველაფერი
          <br />
          ერთი „გამარჯობით“
          <br />
          იწყება.
        </span>
        <span className="home-art-spark">✳</span>
        <span className="home-art-caption">
          ადამიანები. ინსაითები.
          <br />
          <b>ნამდვილი კავშირები.</b>
        </span>
        <ConnectionMotif className="home-art-thread" />
      </div>
    </header>
  );
}

/** Two independent voices meeting on one thread; decorative, not a score. */
export function ConnectionMotif({ className = '' }: { className?: string }) {
  return (
    <svg
      className={`home-connection-motif ${className}`}
      viewBox="0 0 120 80"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M24 49c-24-31 10-55 33-27l13 19c19 27 53 5 30-20"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M21 43c-8 10-5 20 6 22m69-37c11-8 10-18 0-23"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx="26" cy="44" r="6" fill="currentColor" />
      <circle cx="96" cy="26" r="6" fill="currentColor" />
    </svg>
  );
}

export function HomeQuickActions() {
  return (
    <nav className="home-quick-actions" aria-label="სწრაფი მოქმედებები">
      <a href="#home-daily">
        <span className="home-quick-icon">
          <HomeIcon kind="sparkles" />
        </span>
        <span>
          <strong>ჩემი ინსაითი</strong>
          <small>შეხედე საკუთარ თავს</small>
        </span>
      </a>
      <Link to="/discover">
        <span className="home-quick-icon">
          <HomeIcon kind="compass" />
        </span>
        <span>
          <strong>ახალი ადამიანები</strong>
          <small>გაიცანი უფრო ახლოს</small>
        </span>
      </Link>
      <Link to="/connections">
        <span className="home-quick-icon">
          <HomeIcon kind="people" />
        </span>
        <span>
          <strong>ჩემი კავშირები</strong>
          <small>აღმოაჩინე თქვენი დინამიკა</small>
        </span>
      </Link>
      <Link to="/messages">
        <span className="home-quick-icon">
          <HomeIcon kind="message" />
        </span>
        <span>
          <strong>საუბრები</strong>
          <small>გააგრძელე ნაცნობი ამბავი</small>
        </span>
      </Link>
    </nav>
  );
}

export function HomeInsightArt() {
  return (
    <div className="home-insight-art" aria-hidden="true">
      <ConnectionMotif />
    </div>
  );
}

export function HomeConversationInvitation({ hasConnections }: { hasConnections: boolean }) {
  return (
    <aside className="home-conversation-invitation">
      <div className="home-invitation-label">
        <HomeIcon kind="message" />
        <span>საუბარი აქ იწყება</span>
      </div>
      <h2>
        „ბოლოს რამ
        <br />
        გაგაკვირვა?“
      </h2>
      <p>
        {hasConnections
          ? 'აირჩიე არსებული საუბარი და გაუზიარე ეს კითხვა შენს თანამოსაუბრეს.'
          : 'გაიცანი ადამიანი. ორმხრივი კავშირი საუბრის დასაწყისია.'}
      </p>
      <Link to={hasConnections ? '/messages' : '/discover'} className="home-primary-link">
        {hasConnections ? 'აირჩიე საუბარი' : 'იპოვე თანამოსაუბრე'} <HomeIcon />
      </Link>
      <span className="home-invitation-doodle" aria-hidden="true">
        ↗
      </span>
    </aside>
  );
}

/** Theatrical Spotlight Stage with Truth-Flip and 4-Facet ME Lens (phkQC Direction) */
export interface HomeStageProps {
  observation: string;
  realDay: boolean;
  sourceDate: string;
  dailyLabel: string;
  doItems: string[];
  dontItems: string[];
  copyState: 'idle' | 'copied' | 'failed';
  onCopy: () => void;
  expandedInsight: boolean;
  onToggleExpand: () => void;
  safeAstro?: {
    sun_sign: string;
    moon_sign: string;
    ascendant_sign?: string | null;
    mercury_sign?: string | null;
    venus_sign?: string | null;
    mars_sign?: string | null;
    element_primary?: string | null;
  } | null;
  natalFacets?: Array<{
    dimension: string;
    title: string;
    interpretation?: { text: string };
  }> | null;
}

export function HomeStage({
  observation,
  realDay,
  sourceDate,
  dailyLabel,
  doItems,
  dontItems,
  copyState,
  onCopy,
  expandedInsight,
  onToggleExpand,
  safeAstro,
  natalFacets,
}: HomeStageProps) {
  const [truthFlipMode, setTruthFlipMode] = useState<'daily' | 'verdict'>('daily');
  const [activeFacetKey, setActiveFacetKey] = useState<'identity' | 'voice' | 'spark' | 'rhythm'>('identity');
  const [checkedChips, setCheckedChips] = useState<Record<string, boolean>>({});
  const [chipWhisper, setChipWhisper] = useState<string | null>(null);

  // Extract core verdict from natalFacets if resolved
  const verdictItem = natalFacets?.find(
    (f) => f.dimension === 'self.verdict' || f.dimension === 'self.persona'
  );
  const coreVerdictText =
    verdictItem?.interpretation?.text?.trim() ||
    'შენს ემოციურ მეხსიერებასთან დრო უძლურია: თუ ვინმემ შენს წრეში ნდობა მოიპოვა, ეს სამუდამოა — ოღონდ თუ დაკარგა, უკან დაბრუნების ბილეთი არ არსებობს.';

  // 4-Facet Mapping
  const facetData = {
    identity: {
      key: 'identity',
      label: 'ხასიათი',
      dimension: 'self.identity',
      signTitle: safeAstro?.sun_sign
        ? `მზე ${GEORGIAN_SIGNS[safeAstro.sun_sign] || safeAstro.sun_sign}ში`
        : 'შინაგანი ბირთვი',
      elementTitle: safeAstro?.element_primary
        ? `${GEORGIAN_ELEMENTS[safeAstro.element_primary] || safeAstro.element_primary}ს სტიქია`
        : null,
      fallbackText:
        'შენი შინაგანი სამყარო და გარეგნული მანერა ხშირად სხვებს აბნევს — სანამ გაგიცნობენ, ცოტა გაუგებარი ხარ, მერე კი შეუცვლელი.',
    },
    voice: {
      key: 'voice',
      label: 'საუბარი',
      dimension: 'self.cognition',
      signTitle: safeAstro?.mercury_sign
        ? `მერკური ${GEORGIAN_SIGNS[safeAstro.mercury_sign] || safeAstro.mercury_sign}ში`
        : 'კომუნიკაციის სტილი',
      elementTitle: 'აზროვნება',
      fallbackText:
        'პირდაპირი ხარ მაშინ, როცა სხვები ირიბად ლაპარაკობენ. კითხვას ისე სვამ, რომ პასუხში ადამიანი საკუთარ თავს აწყდება.',
    },
    spark: {
      key: 'spark',
      label: 'მიზიდულობა',
      dimension: 'self.relation',
      signTitle: safeAstro?.venus_sign
        ? `ვენერა ${GEORGIAN_SIGNS[safeAstro.venus_sign] || safeAstro.venus_sign}ში`
        : 'მიზიდულობის ენა',
      elementTitle: 'ურთიერთობა',
      fallbackText:
        'შენთან ურთიერთობაში მთავარია არა დიდი სიტყვები, არამედ წვრილმანი დაკვირვებები. ყალბ ინტერესს წამში გრძნობ.',
    },
    rhythm: {
      key: 'rhythm',
      label: 'რიტმი',
      dimension: 'self.action',
      signTitle: safeAstro?.mars_sign
        ? `მარსი ${GEORGIAN_SIGNS[safeAstro.mars_sign] || safeAstro.mars_sign}ში`
        : 'მოქმედების რიტმი',
      elementTitle: 'ენერგია',
      fallbackText:
        'როცა საქმეს ხელს მოჰკიდებ, შუალედური ტემპი არ იცი: ან სრული ჩართულობა, ან მშვიდი დაკვირვება განზე.',
    },
  };

  const currentFacet = facetData[activeFacetKey];
  const facetResolved = natalFacets?.find((f) => f.dimension === currentFacet.dimension);
  const facetText = facetResolved?.interpretation?.text?.trim() || currentFacet.fallbackText;

  const toggleChip = (tag: string) => {
    setCheckedChips((prev) => {
      const nextState = !prev[tag];
      if (nextState) {
        setChipWhisper('ჩანიშნულია. თუ მაინც შეგეშალა, ჩვენ არავის ვეტყვით.');
      }
      return { ...prev, [tag]: nextState };
    });
  };

  return (
    <div className="home-stage-container">
      {/* Spotlight Stage Card */}
      <div className="home-theatrical-stage">
        {/* Stage Header with Truth-Flip Switcher */}
        <div className="home-stage-header">
          <div className="home-truth-flip-tabs" role="tablist" aria-label="სიმართლის რეჟიმები">
            <button
              type="button"
              role="tab"
              aria-selected={truthFlipMode === 'daily'}
              className={`home-truth-tab${truthFlipMode === 'daily' ? ' is-active' : ''}`}
              onClick={() => setTruthFlipMode('daily')}
            >
              <HomeIcon kind="sparkles" /> დღის სიმართლე
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={truthFlipMode === 'verdict'}
              className={`home-truth-tab${truthFlipMode === 'verdict' ? ' is-active' : ''}`}
              onClick={() => setTruthFlipMode('verdict')}
            >
              <HomeIcon kind="quote" /> შენი ვერდიქტი
            </button>
          </div>

          <span className="home-stage-marquee-badge">JESTER LIVE</span>
        </div>

        {/* Tab Panel 1: დღის სიმართლე */}
        {truthFlipMode === 'daily' ? (
          <div className="home-stage-content" role="tabpanel">
            <div className="home-stage-meta-row">
              <span className="home-eyebrow home-insight-kicker">
                {realDay ? 'დღის დაკვირვება' : 'შენი პროფილის დაკვირვება'}
              </span>
              <span className="home-edition">{realDay ? sourceDate : 'პირადი ხედვა'}</span>
            </div>

            <h2 id="home-insight-title" className="home-stage-title">
              {dailyLabel}
            </h2>

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
                onClick={onToggleExpand}
              >
                {expandedInsight ? 'შეამცირე ტექსტი' : 'წაიკითხე სრულად'} <HomeIcon />
              </button>
            )}

            {/* Open 3 Do / 3 Don't Interactive Chips right on Stage Apron */}
            {(doItems.length > 0 || dontItems.length > 0) && (
              <div className="home-stage-ritual-apron" aria-label="დღის რიტუალი">
                <div className="home-ritual-chips-grid">
                  {doItems.map((item, idx) => {
                    const isChecked = !!checkedChips[item];
                    return (
                      <button
                        type="button"
                        key={`do-${idx}`}
                        className={`home-ritual-chip home-ritual-do${isChecked ? ' is-checked' : ''}`}
                        onClick={() => toggleChip(item)}
                        aria-pressed={isChecked}
                      >
                        <span className="home-chip-icon">{isChecked ? '✓' : '↗'}</span>
                        <span className="home-chip-text">{item}</span>
                      </button>
                    );
                  })}
                  {dontItems.map((item, idx) => {
                    const isChecked = !!checkedChips[item];
                    return (
                      <button
                        type="button"
                        key={`dont-${idx}`}
                        className={`home-ritual-chip home-ritual-dont${isChecked ? ' is-checked' : ''}`}
                        onClick={() => toggleChip(item)}
                        aria-pressed={isChecked}
                      >
                        <span className="home-chip-icon">{isChecked ? '✓' : '↘'}</span>
                        <span className="home-chip-text">{item}</span>
                      </button>
                    );
                  })}
                </div>

                {chipWhisper && (
                  <p className="home-chip-whisper" role="status" aria-live="polite">
                    <em>{chipWhisper}</em>
                  </p>
                )}
              </div>
            )}

            {/* Insight Action Footer */}
            <div className="home-insight-actions">
              <button
                type="button"
                className="home-text-button home-share-btn"
                onClick={onCopy}
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
          </div>
        ) : (
          /* Tab Panel 2: შენი ვერდიქტი (Core Truth) */
          <div className="home-stage-content" role="tabpanel">
            <div className="home-stage-meta-row">
              <span className="home-eyebrow home-insight-kicker">პირადი ვერდიქტი</span>
              <span className="home-edition">ხასიათის ბირთვი</span>
            </div>

            <h2 className="home-stage-title">ვინ ხარ სინამდვილეში?</h2>

            <blockquote className="is-expanded">{coreVerdictText}</blockquote>

            {/* Natal Sign Medallions */}
            <div className="home-verdict-medallions">
              {safeAstro?.sun_sign && (
                <span className="home-medallion-pill">
                  მზე: {GEORGIAN_SIGNS[safeAstro.sun_sign] || safeAstro.sun_sign}
                </span>
              )}
              {safeAstro?.moon_sign && (
                <span className="home-medallion-pill">
                  მთვარე: {GEORGIAN_SIGNS[safeAstro.moon_sign] || safeAstro.moon_sign}
                </span>
              )}
              {safeAstro?.ascendant_sign && (
                <span className="home-medallion-pill">
                  ასცენდენტი: {GEORGIAN_SIGNS[safeAstro.ascendant_sign] || safeAstro.ascendant_sign}
                </span>
              )}
              {safeAstro?.element_primary && (
                <span className="home-medallion-pill">
                  სტიქია: {GEORGIAN_ELEMENTS[safeAstro.element_primary] || safeAstro.element_primary}
                </span>
              )}
            </div>

            <div className="home-insight-actions">
              <button
                type="button"
                className="home-text-button home-share-btn"
                onClick={onCopy}
              >
                <HomeIcon kind={copyState === 'copied' ? 'check' : 'copy'} />
                {copyState === 'copied' ? 'დაკოპირებულია' : 'დააკოპირე ვერდიქტი'}
              </button>
              <Link to="/me" className="home-text-link">
                სრული პროფილი <HomeIcon />
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* 4-Facet ME Lens Card (Theatrical 4-Dimension Mirror) */}
      <aside className="home-me-lens" aria-labelledby="home-lens-heading">
        <div className="home-lens-header">
          <span className="home-eyebrow">ME LENS</span>
          <h3 id="home-lens-heading">4 პირადი წახნაგი</h3>
        </div>

        {/* 4 Facet Selectors */}
        <div className="home-facet-nav" role="tablist" aria-label="პიროვნული წახნაგები">
          {(['identity', 'voice', 'spark', 'rhythm'] as const).map((key) => {
            const f = facetData[key];
            const isActive = activeFacetKey === key;
            return (
              <button
                type="button"
                key={key}
                role="tab"
                aria-selected={isActive}
                className={`home-facet-btn${isActive ? ' is-active' : ''}`}
                onClick={() => setActiveFacetKey(key)}
              >
                {f.label}
              </button>
            );
          })}
        </div>

        {/* Active Facet Display Card */}
        <div className="home-facet-card">
          <div className="home-facet-tags">
            <span className="home-facet-sign-badge">{currentFacet.signTitle}</span>
            {currentFacet.elementTitle && (
              <span className="home-facet-element-badge">{currentFacet.elementTitle}</span>
            )}
          </div>
          <p className="home-facet-quote">{facetText}</p>
          <Link to="/me" className="home-text-link home-facet-link">
            გამოიკვლიე ეს წახნაგი <HomeIcon />
          </Link>
        </div>
      </aside>
    </div>
  );
}
