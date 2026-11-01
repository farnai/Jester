import { useState, type KeyboardEvent } from 'react';
import { Link } from 'react-router-dom';
import heroPortrait from '../../assets/registration/hero_woman_highres.jpg';
import portraitDetail from '../../assets/registration/hero_portrait.jpg';
import {
  ConnectionThreadMotif,
  HomeAvatar,
  HomeIcon,
  HomeSkeleton,
  ThreePerspectiveSpark,
} from './HomeElements';

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

export const GEORGIAN_SIGNS_LOCATIVE: Record<string, string> = {
  Aries: 'ვერძში',
  Taurus: 'კუროში',
  Gemini: 'ტყუპებში',
  Cancer: 'კირჩხიბში',
  Leo: 'ლომში',
  Virgo: 'ქალწულში',
  Libra: 'სასწორში',
  Scorpio: 'მორიელში',
  Sagittarius: 'მშვილდოსანში',
  Capricorn: 'თხის რქაში',
  Aquarius: 'მერწყულში',
  Pisces: 'თევზებში',
  aries: 'ვერძში',
  taurus: 'კუროში',
  gemini: 'ტყუპებში',
  cancer: 'კირჩხიბში',
  leo: 'ლომში',
  virgo: 'ქალწულში',
  libra: 'სასწორში',
  scorpio: 'მორიელში',
  sagittarius: 'მშვილდოსანში',
  capricorn: 'თხის რქაში',
  aquarius: 'მერწყულში',
  pisces: 'თევზებში',
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

export const GEORGIAN_ELEMENTS_LABEL: Record<string, string> = {
  Fire: 'ცეცხლის სტიქია',
  Earth: 'მიწის სტიქია',
  Air: 'ჰაერის სტიქია',
  Water: 'წყლის სტიქია',
  fire: 'ცეცხლის სტიქია',
  earth: 'მიწის სტიქია',
  air: 'ჰაერის სტიქია',
  water: 'წყლის სტიქია',
};

function greetingByHour(hour: number) {
  if (hour >= 5 && hour < 12) return 'დილა მშვიდობისა';
  if (hour >= 12 && hour < 18) return 'შუადღე მშვიდობისა';
  return 'საღამო მშვიდობისა';
}

function navigateTabs(event: KeyboardEvent<HTMLDivElement>) {
  if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
  const tabs = Array.from(event.currentTarget.querySelectorAll<HTMLButtonElement>('[role="tab"]'));
  const index = tabs.indexOf(document.activeElement as HTMLButtonElement);
  if (index < 0) return;
  event.preventDefault();
  const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1
    : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
  tabs[next].focus();
  tabs[next].click();
}

export interface SafeAstroSummary {
  sun_sign: string;
  moon_sign: string;
  ascendant_sign?: string | null;
  mercury_sign?: string | null;
  venus_sign?: string | null;
  mars_sign?: string | null;
  element_primary?: string | null;
}

export interface NatalFacetItem {
  dimension: string;
  title: string;
  interpretation?: { text: string };
}

/** Decorative geometry: independent perspectives meeting on a common axis. */
function ConnectionGeometry() {
  return (
    <svg className="home-connection-geometry" viewBox="0 0 600 600" fill="none" aria-hidden="true">
      <g stroke="currentColor" strokeWidth="0.8">
        <circle cx="310" cy="282" r="248" />
        <circle cx="398" cy="370" r="160" />
        <path d="M18 282H580M310 8V582M62 100H558V530H62Z" />
        <path d="M558 370a160 160 0 0 1-160 160 99 99 0 0 1-99-99 61 61 0 0 1 61-61 38 38 0 0 1 38 38 23 23 0 0 1-23 23" />
      </g>
      <g fill="currentColor">
        <circle cx="62" cy="282" r="4" /><circle cx="310" cy="530" r="4" />
        <circle cx="558" cy="100" r="4" /><circle cx="558" cy="282" r="4" />
      </g>
    </svg>
  );
}

/** Authenticated editorial opening. Brand portraits are never member evidence. */
export function HomeSalonMasthead({
  name,
  avatarUrl,
  editionDate,
  hour,
  connectionCount,
  incomingCount,
}: {
  name: string;
  avatarUrl?: string | null;
  editionDate?: string;
  hour: number;
  connectionCount?: number;
  incomingCount?: number;
}) {
  const greeting = greetingByHour(hour);

  return (
    <header className="home-salon-masthead">
      <div className="home-welcome-bar">
        <Link to="/me" className="home-welcome-person">
          <HomeAvatar name={name} src={avatarUrl} />
          <span>{greeting}, <strong>{name}.</strong></span>
        </Link>
        <div className="home-salon-pills">
        {!!incomingCount && incomingCount > 0 && (
          <Link to="/connections?tab=incoming" className="home-pill-incoming">
            <span>{incomingCount} ახალი მოთხოვნა</span>
            <HomeIcon />
          </Link>
        )}

        {connectionCount !== undefined && (
          <Link to="/connections" className="home-pill-neutral">
            <HomeIcon kind="people" />
            <span>ჩემი წრე · {connectionCount}</span>
          </Link>
        )}

          {editionDate && <span className="home-edition-date">{editionDate}</span>}
        </div>
      </div>
      <div className="home-humanism-hero">
        <div className="home-hero-copy">
          <span className="home-section-kicker"><ThreePerspectiveSpark />ადამიანები ახალ სამყაროს გვიხსნიან</span>
          <h1>აღმოაჩინე ადამიანი.<br /><span>იგრძენი კავშირი.</span></h1>
          <p className="home-hero-description">საერთო ინტერესები, განსხვავებული ხასიათები და საუბრები, რომლებიც გაცნობას ნამდვილ კავშირად აქცევს.</p>
          <div className="home-hero-actions">
            <Link to="/discover" className="home-cta-orange"><span>აღმოაჩინე ადამიანები</span><HomeIcon /></Link>
            <a href="#home-daily" className="home-pill-action"><HomeIcon kind="sparkles" /><span>რას ამჩნევს JESTER?</span></a>
          </div>
          <p className="home-hero-note"><span aria-hidden="true" />მეგობრობისთვის. იდეებისთვის. რაღაც ახლისთვის.</p>
        </div>
        <div className="home-hero-art" aria-hidden="true">
          <div className="home-hero-photo"><img src={heroPortrait} alt="" fetchPriority="high" width="896" height="1200" /></div>
          <ConnectionGeometry />
          <div className="home-hero-cameo"><img src={portraitDetail} alt="" width="896" height="1200" /></div>
          <div className="home-hero-coordinate"><span>ხასიათი</span><span>ინტერესები</span><span>კავშირი</span></div>
          <div className="home-hero-caption"><ThreePerspectiveSpark /><span>ყოველი ადამიანი —<br />ახალი პერსპექტივა.</span></div>
        </div>
      </div>
    </header>
  );
}

const CONNECTION_BENEFITS = [
  { icon: 'people', title: 'კავშირს თავისი ხასიათი აქვს', text: 'ორმხრივი კავშირის შემდეგ გაეცანი თქვენს საერთო დინამიკას — რა გაერთიანებთ და სად განსხვავდებით.', to: '/connections', action: 'ჩემი კავშირები' },
  { icon: 'compass', title: 'საერთო ინტერესი — კარგი დასაწყისი', text: 'მუსიკა, მოგზაურობა თუ დიდი იდეები. აღმოაჩინე ადამიანი, რომელსაც შენი ცნობისმოყვარეობა ესმის.', to: '/discover', action: 'აღმოაჩინე მეტი' },
  { icon: 'sparkles', title: 'გაცნობა საკუთარი თავით იწყება', text: 'შეხედე შენს ხასიათსა და ურთიერთობის სტილს ახალი კუთხით. საინტერესო საუბარი აქაც იწყება.', to: '/me', action: 'ჩემი პორტრეტი' },
] as const;

export function HomeConnectionBenefits() {
  return (
    <section id="home-benefits" className="home-benefits" aria-labelledby="home-benefits-title">
      <div className="home-benefits-heading">
        <span className="home-section-kicker">მეტი, ვიდრე პირველი შთაბეჭდილება</span>
        <h2 id="home-benefits-title">გაცნობას სიღრმე აქვს.</h2>
      </div>
      <div className="home-benefits-grid">
        {CONNECTION_BENEFITS.map(({ icon, title, text, to, action }) => (
          <Link key={icon} to={to} className={`home-benefit home-benefit-${icon}`}>
            <div className="home-benefit-drawing" aria-hidden="true"><span /><span /><HomeIcon kind={icon} /></div>
            <h3>{title}</h3><p>{text}</p>
            <span className="home-benefit-action">{action}<HomeIcon /></span>
          </Link>
        ))}
      </div>
    </section>
  );
}

/** Contained Theatrical Spotlight Stage (Left column of Opening Band). */
export interface HomeSpotlightStageProps {
  observation: string;
  realDay: boolean;
  sourceDate: string;
  dailyLabel: string;
  doItems: string[];
  dontItems: string[];
  copyState: 'idle' | 'copied' | 'failed';
  onCopy: (text?: string) => void;
  expandedInsight: boolean;
  onToggleExpand: () => void;
  safeAstro?: SafeAstroSummary | null;
  natalFacets?: NatalFacetItem[] | null;
}

export function HomeSpotlightStage({
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
}: HomeSpotlightStageProps) {
  const [mode, setMode] = useState<'daily' | 'verdict'>('daily');
  const [checkedChips, setCheckedChips] = useState<Record<string, boolean>>({});
  const [lastStamped, setLastStamped] = useState<string | null>(null);

  const verdictFacet =
    natalFacets?.find((f) => f.dimension === 'self.verdict' || f.dimension === 'self.persona') ||
    natalFacets?.find((f) => f.dimension === 'self.identity');
  const coreVerdictText = verdictFacet?.interpretation?.text?.trim() || '';

  const toggleChip = (item: string) => {
    setCheckedChips((prev) => {
      const next = !prev[item];
      if (next) {
        setLastStamped(item);
      } else if (lastStamped === item) {
        setLastStamped(null);
      }
      return { ...prev, [item]: next };
    });
  };

  const isLong = observation.length > 260;

  return (
    <div className="home-spotlight-stage">
      {/* Stage Top Bar: Honest Provenance Pill + Truth-Flip Switcher */}
      <div className="home-spotlight-topbar">
        <span className="home-spotlight-marquee">
          <ThreePerspectiveSpark />
          <span>
            {mode === 'daily'
              ? realDay
                ? `დღის დაკვირვება${sourceDate ? ` · ${sourceDate}` : ''}`
                : 'შენი პროფილის დაკვირვება'
              : 'შენი ხასიათის ვერდიქტი'}
          </span>
        </span>

        <div className="home-truth-switcher" role="tablist" aria-label="JESTER-ის ხედვის რეჟიმი" onKeyDown={navigateTabs}>
          <button
            type="button"
            role="tab"
            id="home-daily-tab"
            aria-controls="home-insight-panel"
            tabIndex={mode === 'daily' ? 0 : -1}
            aria-selected={mode === 'daily'}
            className={`home-truth-pill${mode === 'daily' ? ' is-active' : ''}`}
            onClick={() => setMode('daily')}
          >
            დღის სიმართლე
          </button>
          <button
            type="button"
            role="tab"
            id="home-verdict-tab"
            aria-controls="home-insight-panel"
            tabIndex={mode === 'verdict' ? 0 : -1}
            aria-selected={mode === 'verdict'}
            className={`home-truth-pill${mode === 'verdict' ? ' is-active' : ''}`}
            onClick={() => setMode('verdict')}
          >
            შენი ვერდიქტი
          </button>
        </div>
      </div>

      {mode === 'daily' ? (
        <div className="home-spotlight-body" role="tabpanel" id="home-insight-panel" aria-labelledby="home-daily-tab">
          <h2 id="home-insight-title" className="home-spotlight-headline">
            {dailyLabel}
          </h2>

          <div className="home-truth-frame">
            <span className="home-truth-corner" aria-hidden="true" />
            <blockquote
              id="home-insight-text"
              className={`home-spotlight-quote${
                expandedInsight || !isLong ? ' is-expanded' : ' is-clamped'
              }`}
            >
              „{observation}“
            </blockquote>
          </div>

          {isLong && (
            <button
              type="button"
              className="home-spotlight-expand"
              aria-expanded={expandedInsight}
              aria-controls="home-insight-text"
              onClick={onToggleExpand}
            >
              {expandedInsight ? 'შეამცირე ტექსტი' : 'წაიკითხე სრულად'} <HomeIcon />
            </button>
          )}

          {/* Integrated 3 Do / 3 Don't Ritual Apron */}
          {(doItems.length > 0 || dontItems.length > 0) && (
            <details className="home-guidance">
              <summary>პატარა ნაბიჯები დღისთვის <HomeIcon /></summary>
            <div className="home-ritual-ledger" aria-label="დღის რიტუალი — 3 გაბედე და 3 მოერიდე">
              {doItems.length > 0 && (
                <div className="home-ritual-row">
                  <span className="home-ritual-label">გაბედე:</span>
                  <div className="home-ritual-chips">
                    {doItems.slice(0, 3).map((item, idx) => {
                      const active = !!checkedChips[item];
                      return (
                        <button
                          type="button"
                          key={`do-${idx}`}
                          className={`home-ritual-move is-do${active ? ' is-stamped' : ''}`}
                          aria-pressed={active}
                          onClick={() => toggleChip(item)}
                        >
                          <span className="home-ritual-glyph" aria-hidden="true">
                            {active ? '✓' : '+'}
                          </span>
                          <span>{item}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {dontItems.length > 0 && (
                <div className="home-ritual-row">
                  <span className="home-ritual-label">მოერიდე:</span>
                  <div className="home-ritual-chips">
                    {dontItems.slice(0, 3).map((item, idx) => {
                      const active = !!checkedChips[item];
                      return (
                        <button
                          type="button"
                          key={`dont-${idx}`}
                          className={`home-ritual-move is-dont${active ? ' is-stamped' : ''}`}
                          aria-pressed={active}
                          onClick={() => toggleChip(item)}
                        >
                          <span className="home-ritual-glyph" aria-hidden="true">
                            {active ? '✓' : '−'}
                          </span>
                          <span>{item}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
            </details>
          )}

          {lastStamped && (
            <p className="home-spotlight-whisper" role="status" aria-live="polite">
              ჩანიშნულია: „{lastStamped}“. თუ მაინც შეგეშალა, ჩვენ არავის ვეტყვით.
            </p>
          )}

          <div className="home-spotlight-footer">
            <div className="home-spotlight-cta-group">
              <button
                type="button"
                className="home-cta-orange"
                onClick={() => onCopy(observation)}
              >
                <HomeIcon kind={copyState === 'copied' ? 'check' : 'share'} />
                <span>
                  {copyState === 'copied' ? 'დაკოპირებულია' : 'გაუზიარე დაკვირვება'}
                </span>
              </button>

              <details className="home-insight-context">
                <summary>რას ეფუძნება ეს დაკვირვება?</summary>
                <p>
                  {realDay
                    ? 'ეფუძნება შენს პირად ასტროლოგიურ პროფილსა და დღევანდელ დეტერმინისტულ სიგნალებს — ეს არის დაკვირვებისა და თვითრეფლექსიის ხელსაწყო და არა სამეცნიერო დიაგნოზი.'
                    : 'ეფუძნება შენი პროფილის საბაზისო ნიშანს; ამ პასუხში დღის ინდივიდუალური ტრანზიტი გამოყენებული არ არის.'}
                </p>
              </details>
            </div>

            {copyState !== 'idle' && (
              <span className="home-spotlight-copy-note" role="status">
                {copyState === 'copied'
                  ? 'ტექსტი დაკოპირებულია — გაუგზავნე მეგობარს ან ჩატში.'
                  : 'კოპირება ვერ მოხერხდა.'}
              </span>
            )}
          </div>
        </div>
      ) : (
        <div className="home-spotlight-body" role="tabpanel" id="home-insight-panel" aria-labelledby="home-verdict-tab">
          <h2 id="home-insight-title" className="home-spotlight-headline">ვინ ხარ, როცა არავის არაფერს უმტკიცებ?</h2>

          {coreVerdictText ? (
            <div className="home-truth-frame">
              <span className="home-truth-corner" aria-hidden="true" />
              <blockquote className="home-spotlight-quote is-expanded">
                „{coreVerdictText}“
              </blockquote>
            </div>
          ) : (
            <p className="home-spotlight-empty-verdict">
              სრული პირადი ვერდიქტის სანახავად შეავსე ან გადაამოწმე შენი მონაცემები პირად გვერდზე.
            </p>
          )}

          {safeAstro && (
            <div className="home-verdict-badges" aria-label="პირადი პროფილის ნიშნები">
              {safeAstro.sun_sign && (
                <span className="home-verdict-badge">
                  მზე: {GEORGIAN_SIGNS[safeAstro.sun_sign] || safeAstro.sun_sign}
                </span>
              )}
              {safeAstro.moon_sign && (
                <span className="home-verdict-badge">
                  მთვარე: {GEORGIAN_SIGNS[safeAstro.moon_sign] || safeAstro.moon_sign}
                </span>
              )}
              {safeAstro.ascendant_sign && (
                <span className="home-verdict-badge">
                  ასცენდენტი: {GEORGIAN_SIGNS[safeAstro.ascendant_sign] || safeAstro.ascendant_sign}
                </span>
              )}
              {safeAstro.element_primary && (
                <span className="home-verdict-badge">
                  {GEORGIAN_ELEMENTS_LABEL[safeAstro.element_primary] || safeAstro.element_primary}
                </span>
              )}
            </div>
          )}

          <div className="home-spotlight-footer">
            <div className="home-spotlight-cta-group">
              {coreVerdictText && (
                <button
                  type="button"
                  className="home-cta-orange"
                  onClick={() => onCopy(coreVerdictText)}
                >
                  <HomeIcon kind={copyState === 'copied' ? 'check' : 'copy'} />
                  <span>{copyState === 'copied' ? 'დაკოპირებულია' : 'დააკოპირე ვერდიქტი'}</span>
                </button>
              )}
              <Link to="/me" className="home-spotlight-secondary-link">
                <span>სრული პირადი პორტრეტი</span>
                <HomeIcon />
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/** 4-Facet ME Self-Discovery Atelier (Right column of Opening Band). */
export function HomeMeAtelier({
  safeAstro,
  natalFacets,
  isLoading = false,
}: {
  safeAstro?: SafeAstroSummary | null;
  natalFacets?: NatalFacetItem[] | null;
  isLoading?: boolean;
}) {
  const [activeKey, setActiveKey] = useState<'identity' | 'voice' | 'spark' | 'rhythm'>('identity');

  const facets = {
    identity: {
      key: 'identity' as const,
      label: 'ხასიათი',
      subtitle: 'შინაგანი ღერძი',
      dimension: 'self.identity',
      signPill: safeAstro?.sun_sign
        ? `მზე ${GEORGIAN_SIGNS_LOCATIVE[safeAstro.sun_sign] || safeAstro.sun_sign}`
        : null,
      contextPill: safeAstro?.element_primary
        ? `წამყვანი: ${GEORGIAN_ELEMENTS_LABEL[safeAstro.element_primary] || safeAstro.element_primary}`
        : null,
    },
    voice: {
      key: 'voice' as const,
      label: 'საუბარი',
      subtitle: 'კომუნიკაციის მანერა',
      dimension: 'self.cognition',
      signPill: safeAstro?.mercury_sign
        ? `მერკური ${GEORGIAN_SIGNS_LOCATIVE[safeAstro.mercury_sign] || safeAstro.mercury_sign}`
        : null,
      contextPill: 'დიალოგი და აზროვნება',
    },
    spark: {
      key: 'spark' as const,
      label: 'მიზიდულობა',
      subtitle: 'სიახლოვის ენა',
      dimension: 'self.relation',
      signPill: safeAstro?.venus_sign
        ? `ვენერა ${GEORGIAN_SIGNS_LOCATIVE[safeAstro.venus_sign] || safeAstro.venus_sign}`
        : null,
      contextPill: 'სიმპათია და არჩევანი',
    },
    rhythm: {
      key: 'rhythm' as const,
      label: 'რიტმი',
      subtitle: 'მოქმედების იმპულსი',
      dimension: 'self.action',
      signPill: safeAstro?.mars_sign
        ? `მარსი ${GEORGIAN_SIGNS_LOCATIVE[safeAstro.mars_sign] || safeAstro.mars_sign}`
        : null,
      contextPill: 'ტემპი და საზღვრები',
    },
  };

  const current = facets[activeKey];
  const resolved = natalFacets?.find((item) => item.dimension === current.dimension);
  const insightText = resolved?.interpretation?.text?.trim() || '';

  return (
    <aside className="home-me-atelier" aria-labelledby="home-me-atelier-title">
      <div className="home-me-header">
        <span className="home-section-kicker">შენი ხასიათის ოთხი მხარე</span>
        <h2 id="home-me-atelier-title">რა იმალება შენი ჩვევების უკან?</h2>
      </div>

      <div className="home-me-tabs" role="tablist" aria-label="პიროვნული წახნაგები" onKeyDown={navigateTabs}>
        {(['identity', 'voice', 'spark', 'rhythm'] as const).map((key) => {
          const item = facets[key];
          const isSelected = activeKey === key;
          return (
            <button
              type="button"
              key={key}
              role="tab"
              id={`home-facet-${key}`}
              aria-controls="home-facet-panel"
              tabIndex={isSelected ? 0 : -1}
              aria-selected={isSelected}
              className={`home-me-tab${isSelected ? ' is-active' : ''}`}
              onClick={() => setActiveKey(key)}
            >
              {isSelected && <span aria-hidden="true">✓ </span>}
              {item.label}
            </button>
          );
        })}
      </div>

      <div className="home-me-callout" role="tabpanel" id="home-facet-panel" aria-labelledby={`home-facet-${activeKey}`}>
        <span className="home-me-corner" aria-hidden="true" />
        <div className="home-me-meta">
          <span className="home-me-subtitle">არჩეული შტრიხი: {current.subtitle}</span>
          <div className="home-me-pills">
            {current.signPill && <span className="home-me-pill-sign">{current.signPill}</span>}
            {current.contextPill && (
              <span className="home-me-pill-context">{current.contextPill}</span>
            )}
          </div>
        </div>

        {isLoading ? (
          <HomeSkeleton compact />
        ) : insightText ? (
          <p className="home-me-insight-copy">„{insightText}“</p>
        ) : (
          <p className="home-me-insight-empty">
            გახსენი შენი სრული პროფილი, რომ JESTER-მა ამ წახნაგის დეტალური დაკვირვება გაჩვენოს.
          </p>
        )}
      </div>

      <div className="home-me-footer">
        <span className="home-me-footnote">ყველა შტრიხი და სრული პორტრეტი პირად გვერდზე</span>
        <Link to="/me" className="home-pill-action">
          <span>ჩემი სრული პორტრეტი</span>
          <HomeIcon />
        </Link>
      </div>
    </aside>
  );
}

const CONVERSATION_SPARKS = [
  'ბოლოს რამ გაგაკვირვა ისე, რომ პასუხი ეგრევე ვერ მოიფიქრე?',
  'რა არის ის წვრილმანი, რაც ადამიანში პირველივე ხუთ წუთში განდობს თავს?',
  'რომელ თემაზე შეგიძლია ილაპარაკო საათობით ისე, რომ დრო საერთოდ დაგავიწყდეს?',
  'ბოლოს რომელმა ადგილმა ან სიმღერამ შეგიცვალა განწყობა სრულიად მოულოდნელად?',
  'რაში ხარ იმაზე ბევრად ჯიუტი, ვიდრე ერთი შეხედვით ჩანხარ?',
];

/** Shuffleable Conversation Spark Card (Right column of Social Band). */
export function HomeConversationInvitation({ hasConnections }: { hasConnections: boolean }) {
  const [questionIndex, setQuestionIndex] = useState(0);
  const [copied, setCopied] = useState(false);
  const [copyFailed, setCopyFailed] = useState(false);

  const currentQuestion = CONVERSATION_SPARKS[questionIndex];

  const handleNextQuestion = () => {
    setQuestionIndex((prev) => (prev + 1) % CONVERSATION_SPARKS.length);
    setCopied(false);
    setCopyFailed(false);
  };

  const handleCopyQuestion = async () => {
    setCopyFailed(false);
    try {
      await navigator.clipboard.writeText(`„${currentQuestion}“`);
      setCopied(true);
    } catch {
      setCopied(false);
      setCopyFailed(true);
    }
  };

  return (
    <aside className="home-conversation-invitation" aria-labelledby="home-spark-title">
      <div className="home-spark-header">
        <span className="home-section-kicker">
          <ThreePerspectiveSpark />
          <span>საუბრის ნაპერწკალი</span>
        </span>
        <h2 id="home-spark-title">დაივიწყე „როგორ ხარ?“</h2>
        <p className="home-spark-lead">
          {hasConnections
            ? 'აიღე ერთი წესიერი კითხვა და გაუგზავნე ადამიანს შენი წრიდან.'
            : 'ჯერ იპოვე საინტერესო ადამიანი — ორმხრივი კავშირის შემდეგ საუბარი აქედან იწყება.'}
        </p>
      </div>

      <div className="home-spark-question-box">
        <div className="home-spark-counter">
          <span>
            კითხვა {questionIndex + 1} / {CONVERSATION_SPARKS.length}
          </span>
          <ConnectionThreadMotif className="home-spark-thread" />
        </div>
        <blockquote className="home-spark-quote">„{currentQuestion}“</blockquote>
      </div>

      <div className="home-spark-actions">
        <div className="home-spark-utility-row">
          <button type="button" className="home-spark-btn" onClick={handleNextQuestion}>
            <HomeIcon kind="refresh" />
            <span>სხვა კითხვა</span>
          </button>
          <button type="button" className="home-spark-btn" onClick={() => void handleCopyQuestion()}>
            <HomeIcon kind={copied ? 'check' : 'copy'} />
            <span>{copied ? 'დაკოპირდა' : 'დააკოპირე'}</span>
          </button>
        </div>

        {copyFailed && <p className="home-spark-copy-feedback" role="status">კოპირება ვერ მოხერხდა. შეგიძლია კითხვა მონიშნო და დააკოპირო.</p>}
        <Link to={hasConnections ? '/messages' : '/discover'} className="home-primary-link">
          <span>{hasConnections ? 'აირჩიე საუბარი' : 'იპოვე თანამოსაუბრე'}</span>
          <HomeIcon />
        </Link>
      </div>
    </aside>
  );
}
