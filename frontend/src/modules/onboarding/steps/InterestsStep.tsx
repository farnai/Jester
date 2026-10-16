import React, { useEffect, useState, useMemo } from "react";
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

const ICON_MAP: Record<string, string> = {
  compass: "🧭",
  utensils: "🍽️",
  music: "🎧",
  film: "🎬",
  "book-open": "📖",
  palette: "🎨",
  dumbbell: "🏃",
  laptop: "💻",
  code: "💻",
  atom: "🔬",
  heart: "❤️",
  coffee: "☕",
  sparkles: "✨",
  globe: "🌍",
  plane: "✈️",
  camera: "📷",
  tv: "📺",
  gamepad: "🎮",
  activity: "⚡",
  smile: "😊",
  sun: "☀️",
  moon: "🌙",
};

const resolveCategoryIcon = (iconName?: string | null, slug?: string): string => {
  if (iconName && ICON_MAP[iconName.toLowerCase()]) {
    return ICON_MAP[iconName.toLowerCase()];
  }
  if (slug && ICON_MAP[slug.toLowerCase()]) {
    return ICON_MAP[slug.toLowerCase()];
  }
  return "✨";
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
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

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
        console.error("Failed to load interests:", err);
        if (isMounted) {
          setError("ინტერესების ჩატვირთვა ვერ მოხერხდა.");
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const toggleInterest = (id: string) => {
    setError(null);
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
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

    onNext(Array.from(selected));
  };

  // Group interests by category
  const filteredInterests = useMemo(() => {
    if (!searchQuery.trim()) return interests;
    const query = searchQuery.toLowerCase().trim();
    return interests.filter(
      (item) =>
        item.name.toLowerCase().includes(query) ||
        item.category_name.toLowerCase().includes(query)
    );
  }, [interests, searchQuery]);

  const categories = useMemo(() => {
    const map = new Map<string, { name: string; slug: string; icon?: string | null; items: InterestItem[] }>();

    filteredInterests.forEach((item) => {
      const catKey = item.category_slug || item.category_name || "other";
      if (!map.has(catKey)) {
        map.set(catKey, {
          name: item.category_name || "სხვა",
          slug: item.category_slug || "other",
          icon: item.category_icon,
          items: [],
        });
      }
      map.get(catKey)!.items.push(item);
    });

    return Array.from(map.values());
  }, [filteredInterests]);

  if (loading) {
    return <LoadingState message="ინტერესების სიის ჩატვირთვა..." />;
  }

  const count = selected.size;
  const isReady = count >= 3;

  return (
    <form onSubmit={handleContinue} className="interests-step-container">
      <div className="interests-step-header">
        <h2>6. რა გაინტერესებს?</h2>
        <p>აირჩიე მინიმუმ 3 თემა, რათა JESTER-მა შეძლოს შენთან რეზონანსული ადამიანების პოვნა.</p>
      </div>

      {error && (
        <div style={{ padding: "10px 14px", background: "#fef2f2", border: "1px solid #fecaca", borderRadius: "10px", color: "#dc2626", fontSize: "12px" }}>
          ⚠️ {error}
        </div>
      )}

      {/* Status Bar with Counter & Search */}
      <div className="interests-status-bar">
        <div className={`interests-counter-badge ${isReady ? "ready" : "pending"}`}>
          <span>{isReady ? "✓" : "●"}</span>
          <span>
            არჩეულია: {count} {count > 0 && count < 3 && `(კიდევ ${3 - count})`}
          </span>
        </div>

        <div className="interests-search-box">
          <svg viewBox="0 0 20 20" fill="none" stroke="#9c978f" strokeWidth="1.8" width="14" height="14" aria-hidden="true">
            <circle cx="8.5" cy="8.5" r="5.5" />
            <path d="M13 13l4 4" strokeLinecap="round" />
          </svg>
          <input
            type="text"
            placeholder="ძებნა..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              style={{ border: 0, background: "transparent", color: "#9c978f", cursor: "pointer", fontSize: "12px", padding: 0 }}
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Categorized Pills Grid */}
      <div className="interests-categories-wrapper">
        {categories.length === 0 ? (
          <div style={{ textAlign: "center", padding: "30px", color: "#8c8880", fontSize: "13px" }}>
            ინტერესები ვერ მოიძებნა.
          </div>
        ) : (
          categories.map((cat) => {
            const catIcon = resolveCategoryIcon(cat.icon, cat.slug);
            return (
              <div key={cat.slug} className="interests-category-group">
                <div className="interests-category-title">
                  <span>{catIcon}</span>
                  <span>{cat.name}</span>
                </div>
                <div className="interests-pills-grid">
                  {cat.items.map((item) => {
                    const isSelected = selected.has(item.id);
                    return (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => toggleInterest(item.id)}
                        className={`interest-pill ${isSelected ? "is-selected" : ""}`}
                        aria-pressed={isSelected}
                      >
                        <span className="interest-pill-check">{isSelected ? "✓" : "+"}</span>
                        <span>{item.name}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Actions */}
      <div className="interests-actions">
        <button type="button" className="interests-btn-back" onClick={onBack}>
          ⬅️ უკან
        </button>
        <button type="button" className="interests-btn-skip" onClick={onSkip}>
          გამოტოვება
        </button>
        <button
          type="submit"
          className="interests-btn-next"
          disabled={count > 0 && count < 3}
        >
          <span>შემდეგი</span>
          <span aria-hidden="true">→</span>
        </button>
      </div>
    </form>
  );
};
