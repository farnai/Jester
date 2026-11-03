import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import { useAuth } from '../../core/auth/useAuth';
import type { DailyEnergyResponse } from '../../core/api/types';
import { georgianDate } from './homeModel';

interface HomeDailyEnergyProps {
  data?: DailyEnergyResponse | null;
  isLoading: boolean;
  isError: boolean;
  hasBirthData: boolean;
  onRetry?: () => void;
}

export function HomeDailyEnergy({
  data,
  isLoading,
  isError,
  hasBirthData,
  onRetry,
}: HomeDailyEnergyProps) {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'daily' | 'weekly'>('daily');
  const [whyExpanded, setWhyExpanded] = useState(false);
  const [weeklyWhyExpanded, setWeeklyWhyExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const [weeklyCopied, setWeeklyCopied] = useState(false);
  const [isUnlocking, setIsUnlocking] = useState(false);
  const [unlockError, setUnlockError] = useState<string | null>(null);

  // Weekly Energy Query (fetched on demand or cached for the ISO calendar week)
  const weekly = useQuery({
    queryKey: ['weekly-energy', user?.id],
    queryFn: () => API.interpretations.getWeeklyEnergy(undefined, 'ka'),
    enabled: activeTab === 'weekly',
    staleTime: 120_000,
  });

  // Daily formatting
  const formattedDailyDate = georgianDate(data?.date) || 'დღევანდელი დღე';
  const dailyArchetypeLabel = data?.label || 'დღის ენერგია';
  const dailyObservation = data?.interpretation?.text?.trim() || '';
  const dailyExplanation =
    data?.explanation ||
    'ეს გზავნილი ასახავს შენი მიმდინარე კოსმიური ამინდის ხასიათს. გამოიყენე ეს ენერგია გაცნობიერებულად — ნუ შეებრძოლები იმას, რაც დღეს ისედაც ზედაპირზე ტივტივებს.';
  const isDailyRealTransit = data?.detection_mode === 'real_transit';
  const primaryDailyTransit = data?.primary_transit;

  // Weekly formatting
  const weeklyData = weekly.data;
  const weeklyPeriod = weeklyData?.period || 'მიმდინარე კვირა';
  const weeklyArchetypeLabel =
    weeklyData?.interpretation?.label || weeklyData?.preview?.archetype_label || 'კვირის ენერგია';
  const weeklyQuote = weeklyData?.interpretation?.quote?.trim() || '';
  const isWeeklyRealTransit = weeklyData?.astrological_basis?.detection_mode === 'real_transit';
  const primaryWeeklyTransit = weeklyData?.astrological_basis?.primary_transit;

  const handleCopyDaily = async () => {
    if (!dailyObservation) return;
    try {
      await navigator.clipboard.writeText(`„${dailyObservation}“\n— JESTER (${dailyArchetypeLabel})`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  };

  const handleCopyWeekly = async () => {
    if (!weeklyQuote) return;
    try {
      await navigator.clipboard.writeText(`„${weeklyQuote}“\n— JESTER (${weeklyArchetypeLabel})`);
      setWeeklyCopied(true);
      setTimeout(() => setWeeklyCopied(false), 2000);
    } catch {
      // ignore
    }
  };

  const handleTabKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>) => {
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
      e.preventDefault();
      setActiveTab((prev) => (prev === 'daily' ? 'weekly' : 'daily'));
    }
  };

  const handleUnlockWeekly = async () => {
    setIsUnlocking(true);
    setUnlockError(null);
    try {
      await API.interpretations.unlockWeeklyEnergy();
      await Promise.all([
        weekly.refetch(),
        queryClient.invalidateQueries({ queryKey: ['wallet-me'] }),
        queryClient.invalidateQueries({ queryKey: ['wallet-transactions'] }),
      ]);
    } catch (err: any) {
      console.error('Failed to unlock weekly energy:', err);
      const msg = err?.message || 'განბლოკვა ვერ მოხერხდა. გადაამოწმე ვარსკვლავების ბალანსი.';
      setUnlockError(msg);
    } finally {
      setIsUnlocking(false);
    }
  };

  if (isLoading) {
    return (
      <section className="home-section home-daily-section" aria-label="დღის და კვირის ენერგია">
        <div className="home-card home-skeleton-card">
          <div className="home-skeleton-line short" />
          <div className="home-skeleton-line title" />
          <div className="home-skeleton-line body" />
          <div className="home-skeleton-line body" />
        </div>
      </section>
    );
  }

  if (isError && activeTab === 'daily') {
    return (
      <section className="home-section home-daily-section" aria-label="დღის და კვირის ენერგია">
        <div className="home-card home-error-card">
          <h2 className="home-error-title">დღის ენერგია ვერ ჩაიტვირთა</h2>
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

  return (
    <section className="home-section home-daily-section" aria-labelledby="home-energy-heading">
      <div className="home-card home-daily-card">
        {/* Missing birth data banner */}
        {!hasBirthData && (
          <div className="home-banner home-missing-banner" role="alert">
            <div className="home-missing-content">
              <strong>პირადი ასტრონომიული მონაცემები არ არის შეყვანილი</strong>
              <p>
                ენერგია ამჟამად ნაჩვენებია ზოგადი ფონით. შენი პირადი ტრანზიტებისა და ზუსტი რუკის
                გასააქტიურებლად შეიყვანე დაბადების თარიღი და დრო.
              </p>
            </div>
            <Link to="/profile" className="home-btn home-btn-sm home-btn-primary">
              მონაცემების შეყვანა
            </Link>
          </div>
        )}

        {/* TAB NAVIGATION: Daily vs Weekly */}
        <div className="home-energy-tabs-nav" role="tablist" aria-label="ენერგიის პერიოდის არჩევა">
          <button
            type="button"
            role="tab"
            id="tab-daily-energy"
            aria-selected={activeTab === 'daily'}
            aria-controls="panel-daily-energy"
            tabIndex={activeTab === 'daily' ? 0 : -1}
            className={`home-energy-tab-btn ${activeTab === 'daily' ? 'active' : ''}`}
            onClick={() => setActiveTab('daily')}
            onKeyDown={handleTabKeyDown}
          >
            <span>დღის ენერგია</span>
          </button>
          <button
            type="button"
            role="tab"
            id="tab-weekly-energy"
            aria-selected={activeTab === 'weekly'}
            aria-controls="panel-weekly-energy"
            tabIndex={activeTab === 'weekly' ? 0 : -1}
            className={`home-energy-tab-btn ${activeTab === 'weekly' ? 'active' : ''}`}
            onClick={() => setActiveTab('weekly')}
            onKeyDown={handleTabKeyDown}
          >
            <span>კვირის ენერგია</span>
            <span className="home-tab-star-badge" aria-label="პრემიუმ ვარსკვლავები">
              ✦
            </span>
          </button>
        </div>

        {/* ========================================================================= */}
        {/* TAB 1: DAILY ENERGY (100% PRESERVED FREE CURRENT FUNCTIONALITY) */}
        {/* ========================================================================= */}
        {activeTab === 'daily' && (
          <div
            id="panel-daily-energy"
            role="tabpanel"
            aria-labelledby="tab-daily-energy"
            tabIndex={0}
            className="home-tab-panel"
          >
            {/* Section Header */}
            <div className="home-daily-header">
              <div className="home-daily-meta">
                <span className="home-badge home-date-badge">{formattedDailyDate}</span>
                <span className="home-badge home-archetype-badge">{dailyArchetypeLabel}</span>
                {isDailyRealTransit ? (
                  <span className="home-badge home-real-badge" title="Swiss Ephemeris-ის რეალური გამოთვლა">
                    ● რეალური ტრანზიტი
                  </span>
                ) : (
                  <span className="home-badge home-neutral-badge" title="კოსმიური ბაზური ფონი">
                    ○ კოსმიური ფონი
                  </span>
                )}
              </div>
              <button
                type="button"
                onClick={handleCopyDaily}
                className="home-copy-btn"
                title="ფრაზის კოპირება"
                aria-label="ფრაზის კოპირება"
              >
                {copied ? 'დაკოპირდა ✓' : 'კოპირება ⎘'}
              </button>
            </div>

            {/* Daily Witty Quote & Explanation */}
            <div className="home-daily-body">
              <h2 id="home-energy-heading" className="home-daily-title">
                დღის ენერგია
              </h2>
              <blockquote className="home-daily-quote">
                „{dailyObservation || 'დღეს სამყარო შედარებით მშვიდია, მაგრამ საკუთარ თავთან გულწრფელობას ვერ გაექცევი.'}“
              </blockquote>
              <p className="home-daily-explanation">
                {dailyExplanation}
              </p>
            </div>

            {/* "რატომ / რის საფუძველზე?" Expandable Drawer */}
            <div className="home-why-drawer">
              <button
                type="button"
                className="home-why-toggle-btn"
                onClick={() => setWhyExpanded(!whyExpanded)}
                aria-expanded={whyExpanded}
                aria-controls="home-why-details"
              >
                <span>რატომ? (ასტრონომიული საფუძველი)</span>
                <span className={`home-chevron ${whyExpanded ? 'expanded' : ''}`} aria-hidden="true">
                  ▼
                </span>
              </button>

              {whyExpanded && (
                <div id="home-why-details" className="home-why-content">
                  {primaryDailyTransit ? (
                    <div className="home-transit-breakdown">
                      <div className="home-transit-row">
                        <span className="home-transit-prop">აქტიური ტრანზიტი:</span>
                        <strong className="home-transit-val">{primaryDailyTransit.context_label_ka}</strong>
                      </div>
                      <div className="home-transit-row">
                        <span className="home-transit-prop">ასპექტი და ორბი:</span>
                        <span className="home-transit-val">
                          {primaryDailyTransit.aspect_type} (ორბი: {primaryDailyTransit.orb_diff.toFixed(2)}°, სიძლიერე:{' '}
                          {(primaryDailyTransit.aspect_strength * 100).toFixed(0)}%)
                        </span>
                      </div>
                      <div className="home-transit-row">
                        <span className="home-transit-prop">სტატუსი:</span>
                        <span className="home-transit-val">
                          {isDailyRealTransit
                            ? '✓ შვეიცარიული ეფემერიდებით (Swiss Ephemeris) დადასტურებული რეალური ტრანზიტი'
                            : '○ ნეიტრალური კოსმიური ფონი'}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="home-transit-breakdown">
                      <p className="home-transit-muted">
                        ამ მომენტში შენს ნატალურ პლანეტებთან მჭიდრო ორბიანი ტრანზიტი არ ფიქსირდება. ნაჩვენებია დღის
                        ზოგადი კოსმიური ფონი.
                      </p>
                    </div>
                  )}

                  {/* Epistemic Boundary Notice */}
                  <div className="home-epistemic-notice">
                    <p>
                      <strong>ასტრონომიული ფაქტი:</strong> პლანეტების ზუსტი ციური კოორდინატები, ასპექტები და ორბები
                      გამოთვლილია მაღალი სიზუსტის Swiss Ephemeris ძრავით.
                    </p>
                    <p>
                      <strong>JESTER-ის ინტერპრეტაცია:</strong> ტექსტი, ფსიქოლოგიური შეფასება და ირონიული ტონი
                      წარმოადგენს JESTER-ის საავტორო მოდელს და არა დოგმატურ წინასწარმეტყველებას.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: WEEKLY ENERGY ✦ (LOCKED PREVIEW OR UNLOCKED 3-POINT BREAKDOWN) */}
        {/* ========================================================================= */}
        {activeTab === 'weekly' && (
          <div
            id="panel-weekly-energy"
            role="tabpanel"
            aria-labelledby="tab-weekly-energy"
            tabIndex={0}
            className="home-tab-panel"
          >
            {/* Loading state for Weekly Tab */}
            {weekly.isLoading && (
              <div className="home-tab-loading">
                <div className="home-skeleton-line short" />
                <div className="home-skeleton-line title" />
                <div className="home-skeleton-line body" />
              </div>
            )}

            {/* Error state for Weekly Tab */}
            {weekly.isError && (
              <div className="home-error-inline">
                <p>კვირის ენერგიის მონაცემების ჩატვირთვა ვერ მოხერხდა.</p>
                <button
                  type="button"
                  onClick={() => void weekly.refetch()}
                  className="home-btn home-btn-sm home-btn-outline"
                >
                  ხელახლა ცდა
                </button>
              </div>
            )}

            {weeklyData && (
              <>
                {/* Weekly Meta Header */}
                <div className="home-daily-header">
                  <div className="home-daily-meta">
                    <span className="home-badge home-date-badge">{weeklyPeriod}</span>
                    <span className="home-badge home-archetype-badge">{weeklyArchetypeLabel}</span>
                    {weeklyData.star_cost ? (
                      <span className="home-badge home-star-cost-badge">
                        ✦ {weeklyData.star_cost} ვარსკვლავი
                      </span>
                    ) : (
                      <span className="home-badge home-star-cost-badge">
                        ✦ ვარსკვლავებით
                      </span>
                    )}
                    {weeklyData.is_unlocked && isWeeklyRealTransit && (
                      <span className="home-badge home-real-badge" title="7-დღიანი რეალური ასტრონომიული ტრანზიტები">
                        ● რეალური ტრანზიტები
                      </span>
                    )}
                  </div>
                  {weeklyData.is_unlocked && (
                    <button
                      type="button"
                      onClick={handleCopyWeekly}
                      className="home-copy-btn"
                      title="ფრაზის კოპირება"
                      aria-label="ფრაზის კოპირება"
                    >
                      {weeklyCopied ? 'დაკოპირდა ✓' : 'კოპირება ⎘'}
                    </button>
                  )}
                </div>

                {/* --- A. LOCKED STATE (PREVIEW TEASER & STATUS NOTICE) --- */}
                {!weeklyData.is_unlocked && (
                  <div className="home-weekly-locked-card">
                    <div className="home-weekly-locked-header">
                      <span className="home-weekly-lock-icon" aria-hidden="true">
                        🔒
                      </span>
                      <h2 className="home-daily-title">კვირის ენერგია (დახურული Preview)</h2>
                    </div>

                    <blockquote className="home-weekly-teaser-quote">
                      „{weeklyData.preview?.teaser || 'კვირის ასტრონომიული მოძრაობა განსაკუთრებულ ყურადღებას მოითხოვს.'}“
                    </blockquote>

                    {/* Status Banner */}
                    <div className="home-weekly-status-notice" role="status">
                      <div className="home-notice-badge">✦ ვარსკვლავებით განბლოკვა</div>
                      <p className="home-notice-text">
                        {weeklyData.notice ||
                          'კვირის სრული ენერგია და 3-პუნქტიანი რეფლექსია იხსნება 5 ვარსკვლავით.'}
                      </p>
                    </div>

                    <div className="home-weekly-locked-actions">
                      <button
                        type="button"
                        onClick={handleUnlockWeekly}
                        disabled={isUnlocking}
                        className="home-btn home-btn-primary"
                        title="კვირის ენერგიის განბლოკვა 5 ვარსკვლავით"
                      >
                        {isUnlocking ? 'იხსნება…' : `განბლოკვა (${weeklyData.star_cost ?? 5} ✦ ვარსკვლავი)`}
                      </button>
                      {unlockError && (
                        <p role="alert" className="home-unlock-error" style={{ color: '#B91C1C', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                          {unlockError}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* --- B. UNLOCKED STATE (FULL 3-POINT INTERPRETATION & SIGNIFICANT PERIODS) --- */}
                {weeklyData.is_unlocked && weeklyData.interpretation && (
                  <div className="home-weekly-unlocked-body">
                    <div className="home-daily-body">
                      <h2 className="home-daily-title">კვირის ენერგია</h2>
                      <blockquote className="home-daily-quote">
                        „{weeklyData.interpretation.quote}“
                      </blockquote>
                    </div>

                    {/* 3-Point Weekly Structured Interpretation */}
                    <div className="home-weekly-points-grid">
                      <div className="home-weekly-point-card">
                        <div className="home-point-header">
                          <span className="home-point-num">01</span>
                          <strong className="home-point-title">კვირის ძირითადი თემა</strong>
                        </div>
                        <p className="home-point-text">{weeklyData.interpretation.theme}</p>
                      </div>

                      <div className="home-weekly-point-card">
                        <div className="home-point-header">
                          <span className="home-point-num">02</span>
                          <strong className="home-point-title">თვითრეფლექსია</strong>
                        </div>
                        <p className="home-point-text">{weeklyData.interpretation.reflection}</p>
                      </div>

                      <div className="home-weekly-point-card">
                        <div className="home-point-header">
                          <span className="home-point-num">03</span>
                          <strong className="home-point-title">სად მიმართო ფოკუსი</strong>
                        </div>
                        <p className="home-point-text">{weeklyData.interpretation.focus}</p>
                      </div>
                    </div>

                    {/* Significant Periods / Peak Days */}
                    {weeklyData.significant_periods && weeklyData.significant_periods.length > 0 && (
                      <div className="home-weekly-periods-block">
                        <h3 className="home-periods-title">
                          <span>მნიშვნელოვანი პერიოდები (პიკური დღეები)</span>
                        </h3>
                        <div className="home-periods-list">
                          {weeklyData.significant_periods.map((sp, idx) => (
                            <div key={idx} className="home-period-item">
                              <div className="home-period-top">
                                <span className="home-period-day-badge">{sp.day_name_ka}</span>
                                <span className="home-period-transit">{sp.transit_label_ka}</span>
                              </div>
                              <p className="home-period-desc">{sp.significance_description_ka}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* "რატომ? — ასტრონომიული საფუძველი" Expandable Drawer */}
                    <div className="home-why-drawer">
                      <button
                        type="button"
                        className="home-why-toggle-btn"
                        onClick={() => setWeeklyWhyExpanded(!weeklyWhyExpanded)}
                        aria-expanded={weeklyWhyExpanded}
                        aria-controls="home-weekly-why-details"
                      >
                        <span>რატომ? (დეტალური ასტრონომიული საფუძველი)</span>
                        <span
                          className={`home-chevron ${weeklyWhyExpanded ? 'expanded' : ''}`}
                          aria-hidden="true"
                        >
                          ▼
                        </span>
                      </button>

                      {weeklyWhyExpanded && (
                        <div id="home-weekly-why-details" className="home-why-content">
                          {primaryWeeklyTransit ? (
                            <div className="home-transit-breakdown">
                              <div className="home-transit-row">
                                <span className="home-transit-prop">დომინანტური ტრანზიტი:</span>
                                <strong className="home-transit-val">
                                  {primaryWeeklyTransit.context_label_ka}
                                </strong>
                              </div>
                              <div className="home-transit-row">
                                <span className="home-transit-prop">პიკური სიზუსტე:</span>
                                <span className="home-transit-val">
                                  {primaryWeeklyTransit.peak_day_ka} (მინიმალური ორბი:{' '}
                                  {primaryWeeklyTransit.min_orb_diff.toFixed(2)}°)
                                </span>
                              </div>
                              <div className="home-transit-row">
                                <span className="home-transit-prop">აქტიურობის ხანგრძლივობა:</span>
                                <span className="home-transit-val">
                                  ~{primaryWeeklyTransit.duration_days} დღე (ხანგრძლივობის კოეფიციენტი:{' '}
                                  {primaryWeeklyTransit.duration_factor})
                                </span>
                              </div>
                            </div>
                          ) : (
                            <div className="home-transit-breakdown">
                              <p className="home-transit-muted">
                                მიმდინარე კვირაში შენს ნატალურ პლანეტებთან მკვეთრი ასპექტები არ ფიქსირდება.
                                ნაჩვენებია სტაბილური ბაზური ფონი.
                              </p>
                            </div>
                          )}

                          {/* Epistemic Boundary Notice */}
                          <div className="home-epistemic-notice">
                            <p>
                              <strong>ასტრონომიული ფაქტი:</strong>{' '}
                              {weeklyData.astrological_basis?.epistemic_astronomy}
                            </p>
                            <p>
                              <strong>JESTER-ის ინტერპრეტაცია:</strong>{' '}
                              {weeklyData.astrological_basis?.epistemic_interpretation}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
