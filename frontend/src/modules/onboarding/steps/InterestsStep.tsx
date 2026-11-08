import React, { useEffect, useState, useMemo, useRef } from "react";
import { API } from "../../../core/api/endpoints";
import { InterestItem } from "../../../core/api/types";
import { LoadingState } from "../../../shared/StatusState";
import "./interests.css";

interface InterestsStepProps {
  selectedIds: string[];
  onNext: (selected: string[]) => void;
  onSkip: () => void;
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

export const InterestsStep: React.FC<InterestsStepProps> = ({
  selectedIds,
  onNext,
  onSkip,
  onBack,
}) => {
  const [interests, setInterests] = useState<InterestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Set<string>>(new Set(selectedIds));
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  const searchInputRef = useRef<HTMLInputElement>(null);
  const categoryScrollRef = useRef<HTMLDivElement>(null);

  // Load catalog from API
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

  // Map of interest by ID for rapid lookup (e.g. for selected tray)
  const interestMap = useMemo(() => {
    const map = new Map<string, InterestItem>();
    interests.forEach((item) => map.set(item.id, item));
    return map;
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

  // Toggle selection with strict 3..7 constraint enforcement
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

  const removeSelectedInterest = (id: string) => {
    setError(null);
    setSelected((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  };

  const handleContinue = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const count = selected.size;
    if (count === 0) {
      onSkip();
      return;
    }
    if (count < 3) {
      setError("გთხოვთ აირჩიოთ მინიმუმ 3 ინტერესი, ან გამოიყენეთ 'გამოტოვება'.");
      return;
    }
    if (count > 7) {
      setError("მაქსიმუმ 7 ინტერესის არჩევაა შესაძლებელი.");
      return;
    }

    onNext(Array.from(selected));
  };

  // Search filter across Georgian name, English name, and aliases
  const filteredInterests = useMemo(() => {
    const q = searchQuery.toLowerCase().trim();

    return interests.filter((item) => {
      // 1. Category filter
      if (activeCategory !== "all" && item.category_slug !== activeCategory) {
        return false;
      }

      // 2. Query search
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

  // Group filtered results by category for clear hierarchical presentation
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

  // Selected items array for the overview tray
  const selectedItems = Array.from(selected)
    .map((id) => interestMap.get(id))
    .filter((item): item is InterestItem => Boolean(item));

  return (
    <form onSubmit={handleContinue} className="interests-step-v2">
      {/* Header */}
      <div className="interests-v2-header">
        <span className="interests-v2-step-tag">ნაბიჯი 6 / 7</span>
        <h2>რა გაინტერესებს?</h2>
        <p>
          აირჩიე <strong>3-დან 7-მდე</strong> ინტერესი, რათა JESTER-მა შეძლოს შენთან
          რეზონანსული ადამიანების პოვნა და საუბრის დაწყება.
        </p>
      </div>

      {/* Error Notice */}
      {error && (
        <div className="interests-v2-alert" role="alert">
          <span className="interests-v2-alert-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Selected Items Tray & Status Counter */}
      <section className="interests-v2-tray-card" aria-label="შერჩეული ინტერესები">
        <div className="interests-v2-tray-header">
          <div className="interests-v2-counter-group">
            <span className="interests-v2-counter-label">შერჩეულია</span>
            <span
              className={`interests-v2-counter-pill ${
                count === 0
                  ? "empty"
                  : count < 3
                  ? "need-more"
                  : isMaxReached
                  ? "maxed"
                  : "ready"
              }`}
            >
              {count} / 7
            </span>
          </div>

          <div className="interests-v2-counter-hint">
            {count === 0 && "აირჩიეთ მინიმუმ 3 თემა"}
            {count > 0 && count < 3 && `დარჩა კიდევ ${3 - count} ინტერესი`}
            {count >= 3 && count < 7 && "მზადაა გასაგრძელებლად (შეგიძლიათ კიდევ დაამატოთ)"}
            {isMaxReached && "მიღწეულია მაქსიმალური ლიმიტი (7)"}
          </div>
        </div>

        {selectedItems.length > 0 && (
          <div className="interests-v2-tray-chips">
            {selectedItems.map((item) => (
              <span key={item.id} className="interests-v2-tray-chip">
                <span>{item.name_ka || item.name}</span>
                <button
                  type="button"
                  aria-label={`წაშლა: ${item.name_ka || item.name}`}
                  onClick={() => removeSelectedInterest(item.id)}
                  className="interests-v2-tray-chip-remove"
                >
                  ✕
                </button>
              </span>
            ))}
          </div>
        )}
      </section>

      {/* Search Input Bar */}
      <div className="interests-v2-search-container">
        <div className="interests-v2-search-box">
          <svg
            className="interests-v2-search-icon"
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
            placeholder="ძებნა (მაგ. როკი, კინო, იოგა, anime, tech)..."
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
              className="interests-v2-search-clear"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Horizontal Category Quick-Filter Bar */}
      <nav
        ref={categoryScrollRef}
        className="interests-v2-categories-nav"
        aria-label="კატეგორიების ფილტრი"
      >
        <button
          type="button"
          onClick={() => setActiveCategory("all")}
          className={`interests-v2-cat-btn ${activeCategory === "all" ? "active" : ""}`}
          aria-pressed={activeCategory === "all"}
        >
          <span className="interests-v2-cat-icon">✨</span>
          <span>ყველა</span>
          <span className="interests-v2-cat-count">{interests.length}</span>
        </button>

        {categoryTabs.map((cat) => {
          const isActive = activeCategory === cat.slug;
          return (
            <button
              key={cat.slug}
              type="button"
              onClick={() => setActiveCategory(cat.slug)}
              className={`interests-v2-cat-btn ${isActive ? "active" : ""}`}
              aria-pressed={isActive}
            >
              <span className="interests-v2-cat-icon">{cat.icon}</span>
              <span>{cat.name}</span>
              <span className="interests-v2-cat-count">{cat.count}</span>
            </button>
          );
        })}
      </nav>

      {/* Grouped Interest Pills */}
      <div className="interests-v2-grid-scroll">
        {groupedCategories.length === 0 ? (
          <div className="interests-v2-empty-state">
            <span className="interests-v2-empty-icon">🔍</span>
            <h3>ინტერესი ვერ მოიძებნა</h3>
            <p>
              სცადეთ სხვა საძიებო სიტყვა (ქართულად ან ინგლისურად), ან აირჩიეთ კატეგორია „ყველა“.
            </p>
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="interests-v2-btn-reset-search"
              >
                ძებნის გასუფთავება
              </button>
            )}
          </div>
        ) : (
          groupedCategories.map((group) => (
            <div key={group.slug} className="interests-v2-group-card">
              <div className="interests-v2-group-title">
                <span className="interests-v2-group-icon">{group.icon}</span>
                <h4>{group.name}</h4>
              </div>

              <div className="interests-v2-pills">
                {group.items.map((item) => {
                  const isSelected = selected.has(item.id);
                  const isBlocked = !isSelected && isMaxReached;

                  return (
                    <button
                      key={item.id}
                      type="button"
                      disabled={isBlocked}
                      onClick={() => toggleInterest(item.id)}
                      className={`interests-v2-pill ${isSelected ? "selected" : ""} ${
                        isBlocked ? "disabled" : ""
                      }`}
                      aria-pressed={isSelected}
                      title={
                        isBlocked
                          ? "მაქსიმუმ 7 ინტერესია ნებადართული"
                          : item.name_en
                          ? `${item.name_ka || item.name} (${item.name_en})`
                          : item.name_ka || item.name
                      }
                    >
                      <span className="interests-v2-pill-check" aria-hidden="true">
                        {isSelected ? "✓" : "+"}
                      </span>
                      <span className="interests-v2-pill-text">
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

      {/* Continuation Actions Footer */}
      <div className="interests-v2-footer">
        <button
          type="button"
          className="interests-v2-btn-back"
          onClick={onBack}
        >
          ← უკან
        </button>

        <button
          type="button"
          className="interests-v2-btn-skip"
          onClick={onSkip}
        >
          გამოტოვება
        </button>

        <button
          type="submit"
          className="interests-v2-btn-submit"
          disabled={count > 0 && count < 3}
        >
          <span>შემდეგი</span>
          <span aria-hidden="true">→</span>
        </button>
      </div>
    </form>
  );
};
