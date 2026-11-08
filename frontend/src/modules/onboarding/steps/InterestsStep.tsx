import React, { useEffect, useState, useMemo, useRef } from "react";
import { API } from "../../../core/api/endpoints";
import { InterestItem } from "../../../core/api/types";
import { LoadingState } from "../../../shared/StatusState";
import "./interests.css";

export interface InterestsStepProps {
  selectedIds: string[];
  onNext: (selected: string[]) => void;
  onSkip?: () => void;
  onSkipAll?: () => void;
  onBack: () => void;
}

const CATEGORY_ICONS: Record<string, string> = {
  "music-stage": "🎧",
  "cinema-books-stories": "🎬",
  "art-creativity": "🎨",
  "food-city": "🍽️",
  "travel-nature": "🧭",
  "sports-movement": "🏃",
  "games-tech": "🎮",
  "knowledge-mind": "📖",
  "hobbies-lifestyle": "✨",
};

// 16 curated high-frequency interests across all 9 categories for instant 1-tap selection
const FEATURED_SLUGS = [
  "music",
  "cinema",
  "travel",
  "books",
  "coffee",
  "fitness",
  "photography",
  "gaming",
  "technology",
  "psychology",
  "art",
  "nature",
  "pets",
  "yoga-pilates",
  "home-cooking",
  "tv-series",
];

export const InterestsStep: React.FC<InterestsStepProps> = ({
  selectedIds,
  onNext,
  onSkip,
  onSkipAll,
  onBack,
}) => {
  const [interests, setInterests] = useState<InterestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Set<string>>(new Set(selectedIds));
  const [showFullCatalog, setShowFullCatalog] = useState(false);
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  const searchInputRef = useRef<HTMLInputElement>(null);

  // Sync with external selectedIds if updated from parent
  useEffect(() => {
    setSelected(new Set(selectedIds));
  }, [selectedIds]);

  // Load catalog from API (database remains single source of truth)
  useEffect(() => {
    let isMounted = true;
    API.interests
      .list()
      .then((res) => {
        if (isMounted) {
          setInterests(res.items);
        }
      })
      .catch((err) => {
        console.error("Failed to load interests catalog:", err);
        if (isMounted) {
          setError("ინტერესების კატალოგის ჩატვირთვა ვერ მოხერხდა. გთხოვთ სცადოთ ხელახლა.");
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // Direct 1-tap featured list resolved from API catalog
  const featuredInterests = useMemo(() => {
    const slugMap = new Map<string, InterestItem>();
    interests.forEach((item) => slugMap.set(item.slug, item));

    const result: InterestItem[] = [];
    FEATURED_SLUGS.forEach((slug) => {
      const match = slugMap.get(slug);
      if (match) result.push(match);
    });

    // Fallback if featured slugs differ
    if (result.length < 12) {
      interests.slice(0, 16).forEach((item) => {
        if (!result.some((r) => r.id === item.id)) {
          result.push(item);
        }
      });
    }

    return result.slice(0, 16);
  }, [interests]);

  // Distinct categories ordered as returned by API
  const categoryTabs = useMemo(() => {
    const map = new Map<string, { slug: string; name: string; icon: string; count: number }>();
    interests.forEach((item) => {
      const slug = item.category_slug || "other";
      if (!map.has(slug)) {
        map.set(slug, {
          slug,
          name: item.category_name_ka || item.category_name || "სხვა",
          icon: CATEGORY_ICONS[slug] || "✨",
          count: 0,
        });
      }
      map.get(slug)!.count += 1;
    });
    return Array.from(map.values());
  }, [interests]);

  // Direct one-tap toggle (0–7 rule)
  const toggleInterest = (id: string) => {
    setError(null);
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        if (next.size >= 7) {
          setError("მაქსიმუმ 7 ინტერესის არჩევაა შესაძლებელი.");
          return prev;
        }
        next.add(id);
      }
      return next;
    });
  };

  const handleContinue = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const count = selected.size;
    if (count > 7) {
      setError("მაქსიმუმ 7 ინტერესის არჩევაა შესაძლებელი.");
      return;
    }

    // 0 to 7 choices are fully valid
    onNext(Array.from(selected));
  };

  // Search filter across Georgian name, English name, and aliases
  const filteredInterests = useMemo(() => {
    const q = searchQuery.toLowerCase().trim();

    return interests.filter((item) => {
      if (activeCategory !== "all" && item.category_slug !== activeCategory) {
        return false;
      }
      if (!q) return true;

      const candidates = [
        item.name,
        item.name_ka || "",
        item.name_en || "",
        ...(item.aliases || []),
        item.category_name || "",
        item.category_name_ka || "",
        item.category_name_en || "",
      ];

      return candidates.some((text) => text.toLowerCase().includes(q));
    });
  }, [interests, activeCategory, searchQuery]);

  // Group filtered results by category
  const groupedCategories = useMemo(() => {
    const map = new Map<string, { slug: string; name: string; icon: string; items: InterestItem[] }>();

    filteredInterests.forEach((item) => {
      const slug = item.category_slug || "other";
      if (!map.has(slug)) {
        map.set(slug, {
          slug,
          name: item.category_name_ka || item.category_name || "სხვა",
          icon: CATEGORY_ICONS[slug] || "✨",
          items: [],
        });
      }
      map.get(slug)!.items.push(item);
    });

    return Array.from(map.values());
  }, [filteredInterests]);

  if (loading) {
    return <LoadingState message="ინტერესების კატალოგი იტვირთება..." />;
  }

  const count = selected.size;
  const isMaxReached = count >= 7;

  return (
    <form onSubmit={handleContinue} className="interests-step-v3">
      {/* Header */}
      <div className="onboarding-v3-stage-header">
        <div className="onboarding-v3-badge-row">
          <span className="onboarding-v3-stage-tag">ნაბიჯი 6.1 • ინტერესები</span>
          <span className="onboarding-v3-optional-pill">სურვილისამებრ</span>
        </div>
        <h2>რა გაინტერესებს?</h2>
        <p>
          მონიშნე პირდაპირ ერთი შეხებით (მაქსიმუმ 7). შეგიძლია აირჩიო თუნდაც 1 ან 2, ან სურვილისამებრ გამოტოვო.
        </p>
      </div>

      {/* Error Notice */}
      {error && (
        <div className="onboarding-v3-alert" role="alert">
          <span className="onboarding-v3-alert-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Compact Status Counter Bar (No repetitive tall trays) */}
      <div className="onboarding-v3-compact-counter">
        <div className="onboarding-v3-counter-left">
          <span className="onboarding-v3-counter-title">შერჩეულია:</span>
          <span
            className={`onboarding-v3-counter-number ${
              count === 0 ? "zero" : isMaxReached ? "maxed" : "active"
            }`}
          >
            {count} / 7
          </span>
        </div>
        <div className="onboarding-v3-counter-hint">
          {count === 0 && "არცერთი არ არის შერჩეული"}
          {count > 0 && count < 7 && `შეგიძლია დაამატო კიდევ ${7 - count}`}
          {isMaxReached && "მაქსიმალური ლიმიტი (7)"}
        </div>
      </div>

      {/* Section 1: One-Tap Direct Discovery Grid (16 curated choices) */}
      <div className="interests-v3-one-tap-section">
        <span className="interests-v3-section-title">პოპულარული ინტერესები:</span>
        <div className="interests-v3-pills-grid">
          {featuredInterests.map((item) => {
            const isSelected = selected.has(item.id);
            const isBlocked = !isSelected && isMaxReached;

            return (
              <button
                key={item.id}
                type="button"
                disabled={isBlocked}
                onClick={() => toggleInterest(item.id)}
                className={`interests-v3-pill ${isSelected ? "selected" : ""} ${
                  isBlocked ? "disabled" : ""
                }`}
                aria-pressed={isSelected}
              >
                <span className="interests-v3-pill-check" aria-hidden="true">
                  {isSelected ? "✓" : "+"}
                </span>
                <span className="interests-v3-pill-text">
                  {item.name_ka || item.name}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Toggle to expand/collapse the full 79 catalog */}
      <div className="interests-v3-expand-wrapper">
        <button
          type="button"
          onClick={() => {
            setShowFullCatalog((prev) => !prev);
            if (!showFullCatalog) {
              setTimeout(() => searchInputRef.current?.focus(), 100);
            }
          }}
          className="interests-v3-btn-toggle-catalog"
          aria-expanded={showFullCatalog}
        >
          <span>
            {showFullCatalog
              ? "▲ სრული კატალოგის დახურვა"
              : "▼ სხვა ინტერესების ნახვა (სრული 79 თემა & ძებნა)"}
          </span>
        </button>
      </div>

      {/* Section 2: Extended Discovery (Full 79 Catalog with Search & Categories) */}
      {showFullCatalog && (
        <div className="interests-v3-full-catalog-panel">
          {/* Search Input */}
          <div className="interests-v3-search-box">
            <svg
              className="interests-v3-search-icon"
              viewBox="0 0 20 20"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              aria-hidden="true"
            >
              <circle cx="8.5" cy="8.5" r="5.5" />
              <path d="M13 13l4 4" strokeLinecap="round" />
            </svg>
            <input
              ref={searchInputRef}
              type="search"
              aria-label="ინტერესების ძებნა"
              placeholder="მოძებნე ნებისმიერი ინტერესი (ქართულად ან ინგლისურად)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                type="button"
                aria-label="ძებნის გასუფთავება"
                onClick={() => {
                  setSearchQuery("");
                  searchInputRef.current?.focus();
                }}
                className="interests-v3-search-clear"
              >
                ✕
              </button>
            )}
          </div>

          {/* Category Chips Bar */}
          <nav className="interests-v3-category-bar" aria-label="კატეგორიების ფილტრი">
            <button
              type="button"
              onClick={() => setActiveCategory("all")}
              className={`interests-v3-cat-btn ${activeCategory === "all" ? "active" : ""}`}
              aria-pressed={activeCategory === "all"}
            >
              <span>ყველა</span>
              <span className="interests-v3-cat-badge">{interests.length}</span>
            </button>
            {categoryTabs.map((cat) => (
              <button
                key={cat.slug}
                type="button"
                onClick={() => setActiveCategory(cat.slug)}
                className={`interests-v3-cat-btn ${activeCategory === cat.slug ? "active" : ""}`}
                aria-pressed={activeCategory === cat.slug}
              >
                <span>{cat.icon}</span>
                <span>{cat.name}</span>
                <span className="interests-v3-cat-badge">{cat.count}</span>
              </button>
            ))}
          </nav>

          {/* Grouped Catalog Items */}
          <div className="interests-v3-catalog-scroll">
            {groupedCategories.length === 0 ? (
              <div className="interests-v3-empty-state">
                <p>ინტერესი ვერ მოიძებნა.</p>
                {searchQuery && (
                  <button
                    type="button"
                    onClick={() => setSearchQuery("")}
                    className="interests-v3-btn-reset"
                  >
                    ძებნის გასუფთავება
                  </button>
                )}
              </div>
            ) : (
              groupedCategories.map((group) => (
                <div key={group.slug} className="interests-v3-group-block">
                  <div className="interests-v3-group-title">
                    <span>{group.icon}</span>
                    <span>{group.name}</span>
                  </div>
                  <div className="interests-v3-pills-grid">
                    {group.items.map((item) => {
                      const isSelected = selected.has(item.id);
                      const isBlocked = !isSelected && isMaxReached;

                      return (
                        <button
                          key={item.id}
                          type="button"
                          disabled={isBlocked}
                          onClick={() => toggleInterest(item.id)}
                          className={`interests-v3-pill ${isSelected ? "selected" : ""} ${
                            isBlocked ? "disabled" : ""
                          }`}
                          aria-pressed={isSelected}
                        >
                          <span className="interests-v3-pill-check" aria-hidden="true">
                            {isSelected ? "✓" : "+"}
                          </span>
                          <span className="interests-v3-pill-text">
                            {item.name_ka || item.name}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Continuation Actions Footer */}
      <div className="onboarding-v3-footer">
        <div className="onboarding-v3-footer-left">
          <button
            type="button"
            className="onboarding-v3-btn-back"
            onClick={onBack}
          >
            ← უკან
          </button>
        </div>

        <div className="onboarding-v3-footer-right">
          {(onSkipAll || onSkip) && (
            <button
              type="button"
              className="onboarding-v3-btn-exit-all"
              onClick={onSkipAll || onSkip}
              title="გადი აპლიკაციაში, პროფილს მოგვიანებით შეავსებ"
            >
              მოგვიანებით შევავსებ
            </button>
          )}

          <button
            type="submit"
            className="onboarding-v3-btn-next"
          >
            <span>შემდეგი</span>
            <span aria-hidden="true">→</span>
          </button>
        </div>
      </div>
    </form>
  );
};
