import { useState } from 'react';
import { Link } from 'react-router-dom';
import type { PersonalCatalogResponse, PersonalCatalogLayer, PersonalCatalogItem } from '../../core/api/types';
import { ShareCardModal } from './ShareCardModal';

interface HomePersonalInsightsProps {
  catalog?: PersonalCatalogResponse | null;
  isLoading: boolean;
  isError: boolean;
  onRetry?: () => void;
}

export function HomePersonalInsights({
  catalog,
  isLoading,
  isError,
  onRetry,
}: HomePersonalInsightsProps) {
  // Outer accordion: collapsed by default
  const [isOuterExpanded, setIsOuterExpanded] = useState(false);

  // Sharing state for individual card export
  const [sharingCard, setSharingCard] = useState<{
    layer: PersonalCatalogLayer;
    item: PersonalCatalogItem;
  } | null>(null);

  // Allow toggling open layers. Open layer 1 by default for discovery when parent opened.
  const [openLayers, setOpenLayers] = useState<Record<string, boolean>>({
    layer_1_core_identity: true,
  });

  const toggleLayer = (layerId: string) => {
    setOpenLayers((prev) => ({
      ...prev,
      [layerId]: !prev[layerId],
    }));
  };

  if (isLoading) {
    return (
      <section className="home-section home-insights-section" aria-label="გაიცანი საკუთარი თავი">
        <div className="home-card home-insights-card">
          <div className="home-skeleton-line title" />
          <div className="home-skeleton-line short" />
        </div>
      </section>
    );
  }

  if (isError) {
    return (
      <section className="home-section home-insights-section" aria-label="გაიცანი საკუთარი თავი">
        <div className="home-card home-error-card">
          <h2 className="home-error-title">პირადი ანალიზი ვერ ჩაიტვირთა</h2>
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

  if (!catalog || !catalog.has_data || catalog.layers.length === 0) {
    return (
      <section className="home-section home-insights-section" aria-labelledby="home-insights-heading">
        <div className="home-card home-insights-empty-card">
          <h2 id="home-insights-heading" className="home-section-title">
            გაიცანი საკუთარი თავი
          </h2>
          <p className="home-section-subtitle">
            შენი ნატალური რუკის 7 შრიანი ანალიზი მოითხოვს დაბადების თარიღსა და ადგილს.
          </p>
          <div className="home-insights-cta-wrap">
            <Link to="/profile" className="home-btn home-btn-primary">
              დაბადების მონაცემების შეყვანა
            </Link>
          </div>
        </div>
      </section>
    );
  }

  const hasExactTime = catalog.data_quality.has_exact_time;

  return (
    <section className="home-section home-insights-section" aria-labelledby="home-insights-heading">
      <div className="home-card home-insights-card">
        {/* Parent Accordion Trigger */}
        <button
          type="button"
          id="home-insights-accordion-toggle"
          className="home-insights-header-toggle"
          onClick={() => setIsOuterExpanded((prev) => !prev)}
          aria-expanded={isOuterExpanded}
          aria-controls="home-insights-body"
        >
          <div className="home-insights-toggle-info">
            <div className="home-section-title-row">
              <h2 id="home-insights-heading" className="home-section-title">
                გაიცანი საკუთარი თავი
              </h2>
              <span className="home-badge home-layer-count-badge">7 ასტროლოგიური შრე</span>
            </div>
            <p className="home-section-subtitle">
              შენი პიროვნების 7 ასტროლოგიური შრე
            </p>
          </div>

          <div className="home-insights-toggle-indicator" aria-hidden="true">
            <span className={`home-chevron ${isOuterExpanded ? 'expanded' : ''}`}>
              ▼
            </span>
          </div>
        </button>

        {/* Parent Accordion Content: 7 Layers */}
        {isOuterExpanded && (
          <div
            id="home-insights-body"
            role="region"
            aria-labelledby="home-insights-accordion-toggle"
            className="home-insights-body"
          >
            {!hasExactTime && (
              <div className="home-banner home-time-notice" role="note">
                <span>ℹ დაბადების ზუსტი დრო უცნობია — ასცენდენტი და სახლები დამალულია. დანარჩენი პლანეტები ზუსტად არის გამოთვლილი.</span>
              </div>
            )}

            <div className="home-insights-accordion">
              {catalog.layers.map((layer) => {
                const isOpen = !!openLayers[layer.layer_id];
                const itemPanelId = `layer-panel-${layer.layer_id}`;
                const itemHeaderId = `layer-header-${layer.layer_id}`;

                return (
                  <div
                    key={layer.layer_id}
                    className={`home-layer-card ${isOpen ? 'is-open' : ''}`}
                  >
                    <button
                      type="button"
                      id={itemHeaderId}
                      className="home-layer-toggle"
                      onClick={() => toggleLayer(layer.layer_id)}
                      aria-expanded={isOpen}
                      aria-controls={itemPanelId}
                    >
                      <div className="home-layer-main-info">
                        <span className="home-layer-num">{layer.number}</span>
                        <div className="home-layer-titles">
                          <h3 className="home-layer-title">{layer.title}</h3>
                          <p className="home-layer-subtitle">{layer.subtitle}</p>
                        </div>
                      </div>

                      <div className="home-layer-meta">
                        <span className={`home-chevron ${isOpen ? 'expanded' : ''}`} aria-hidden="true">
                          ▼
                        </span>
                      </div>
                    </button>

                    {isOpen && (
                      <div
                        id={itemPanelId}
                        role="region"
                        aria-labelledby={itemHeaderId}
                        className="home-layer-body"
                      >
                        <p className="home-layer-summary">{layer.summary}</p>

                        {layer.topics && layer.topics.length > 0 && (
                          <div className="home-topic-chips">
                            {layer.topics.map((t, idx) => (
                              <span key={idx} className="home-topic-chip">
                                #{t}
                              </span>
                            ))}
                          </div>
                        )}

                        <div className="home-layer-items-grid">
                          {layer.items.map((item) => (
                            <div key={item.id} className="home-layer-item-card">
                              <div className="home-item-top">
                                <div className="home-item-label-group">
                                  <span className="home-item-label">{item.label}</span>
                                  {item.sign_badge && (
                                    <span className="home-item-badge">{item.sign_badge}</span>
                                  )}
                                </div>
                                <button
                                  type="button"
                                  className="home-card-share-btn"
                                  onClick={() => setSharingCard({ layer, item })}
                                  title="ბარათის გაზიარება"
                                  aria-label={`ბარათის გაზიარება: ${item.label}`}
                                >
                                  გაზიარება ↗
                                </button>
                              </div>
                              <p className="home-item-text">{item.text}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Individual Card Sharing Modal */}
      <ShareCardModal
        isOpen={!!sharingCard}
        onClose={() => setSharingCard(null)}
        layer={sharingCard?.layer || null}
        item={sharingCard?.item || null}
      />
    </section>
  );
}

