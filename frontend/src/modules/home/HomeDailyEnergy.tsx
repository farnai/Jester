import { useState } from 'react';
import { Link } from 'react-router-dom';
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
  const [whyExpanded, setWhyExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const formattedDate = georgianDate(data?.date) || 'დღევანდელი დღე';
  const archetypeLabel = data?.label || 'დღის ენერგია';
  const observation = data?.interpretation?.text?.trim() || '';
  const isRealTransit = data?.detection_mode === 'real_transit';
  const primaryTransit = data?.primary_transit;

  const handleCopy = async () => {
    if (!observation) return;
    try {
      await navigator.clipboard.writeText(`„${observation}“\n— JESTER (${archetypeLabel})`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  };

  if (isLoading) {
    return (
      <section className="home-section home-daily-section" aria-label="დღის ენერგია">
        <div className="home-card home-skeleton-card">
          <div className="home-skeleton-line short" />
          <div className="home-skeleton-line title" />
          <div className="home-skeleton-line body" />
          <div className="home-skeleton-line body" />
        </div>
      </section>
    );
  }

  if (isError) {
    return (
      <section className="home-section home-daily-section" aria-label="დღის ენერგია">
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
    <section className="home-section home-daily-section" aria-labelledby="home-daily-heading">
      <div className="home-card home-daily-card">
        {/* Missing birth data banner */}
        {!hasBirthData && (
          <div className="home-banner home-missing-banner" role="alert">
            <div className="home-missing-content">
              <strong>პირადი ასტრონომიული მონაცემები არ არის შეყვანილი</strong>
              <p>
                დღის ენერგია ამჟამად ნაჩვენებია ზოგადი ფონით. შენი პირადი ტრანზიტებისა და ზუსტი რუკის
                გასააქტიურებლად შეიყვანე დაბადების თარიღი და დრო.
              </p>
            </div>
            <Link to="/profile" className="home-btn home-btn-sm home-btn-primary">
              მონაცემების შეყვანა
            </Link>
          </div>
        )}

        {/* Section Header */}
        <div className="home-daily-header">
          <div className="home-daily-meta">
            <span className="home-badge home-date-badge">{formattedDate}</span>
            <span className="home-badge home-archetype-badge">{archetypeLabel}</span>
            {isRealTransit ? (
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
            onClick={handleCopy}
            className="home-copy-btn"
            title="ფრაზის კოპირება"
            aria-label="ფრაზის კოპირება"
          >
            {copied ? 'დაკოპირდა ✓' : 'კოპირება ⎘'}
          </button>
        </div>

        {/* Daily Witty Quote & Explanation */}
        <div className="home-daily-body">
          <h2 id="home-daily-heading" className="home-daily-title">
            დღის ენერგია
          </h2>
          <blockquote className="home-daily-quote">
            „{observation || 'დღეს სამყარო შედარებით მშვიდია, მაგრამ საკუთარ თავთან გულწრფელობას ვერ გაექცევი.'}“
          </blockquote>
          <p className="home-daily-explanation">
            ეს გზავნილი ასახავს შენი მიმდინარე კოსმიური ამინდის ხასიათს. გამოიყენე ეს ენერგია
            გაცნობიერებულად — ნუ შეებრძოლები იმას, რაც დღეს ისედაც ზედაპირზე ტივტივებს.
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
              {primaryTransit ? (
                <div className="home-transit-breakdown">
                  <div className="home-transit-row">
                    <span className="home-transit-prop">აქტიური ტრანზიტი:</span>
                    <strong className="home-transit-val">{primaryTransit.context_label_ka}</strong>
                  </div>
                  <div className="home-transit-row">
                    <span className="home-transit-prop">ასპექტი და ორბი:</span>
                    <span className="home-transit-val">
                      {primaryTransit.aspect_type} (ორბი: {primaryTransit.orb_diff.toFixed(2)}°, სიძლიერე:{' '}
                      {(primaryTransit.aspect_strength * 100).toFixed(0)}%)
                    </span>
                  </div>
                  <div className="home-transit-row">
                    <span className="home-transit-prop">სტატუსი:</span>
                    <span className="home-transit-val">
                      {isRealTransit
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

              {/* Strict Epistemic Boundary Notice */}
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
    </section>
  );
}

