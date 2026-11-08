import React, { useEffect, useState } from "react";
import { API } from "../../../core/api/endpoints";
import { ConnectionIntentionItem } from "../../../core/api/types";
import { LoadingState } from "../../../shared/StatusState";
import "./interests.css";

export interface IntentionsStepProps {
  selectedIds: string[];
  onNext: (selected: string[]) => void;
  onSkip?: () => void;
  onSkipAll?: () => void;
  onBack: () => void;
}

export const IntentionsStep: React.FC<IntentionsStepProps> = ({
  selectedIds,
  onNext,
  onSkip,
  onSkipAll,
  onBack,
}) => {
  const [intentions, setIntentions] = useState<ConnectionIntentionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Set<string>>(new Set(selectedIds));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSelected(new Set(selectedIds));
  }, [selectedIds]);

  useEffect(() => {
    let isMounted = true;
    API.intentions
      .list()
      .then((res) => {
        if (isMounted) setIntentions(res.items);
      })
      .catch((err) => {
        console.error("Failed to load connection intentions:", err);
        if (isMounted) setError("მიზნების ჩატვირთვა ვერ მოხერხდა. სცადეთ ხელახლა.");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const toggleIntention = (id: string) => {
    setError(null);
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        if (next.size >= 3) {
          setError("მაქსიმუმ 3 მიზნის არჩევაა შესაძლებელი.");
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
    if (count > 3) {
      setError("მაქსიმუმ 3 მიზნის არჩევაა შესაძლებელი.");
      return;
    }

    onNext(Array.from(selected));
  };

  if (loading) {
    return <LoadingState message="მიზნების ჩატვირთვა..." />;
  }

  const count = selected.size;
  const isMaxReached = count >= 3;

  return (
    <form onSubmit={handleContinue} className="intentions-step-v3">
      {/* Header */}
      <div className="onboarding-v3-stage-header">
        <div className="onboarding-v3-badge-row">
          <span className="onboarding-v3-stage-tag">ნაბიჯი 6.3 • რას ვეძებ</span>
          <span className="onboarding-v3-optional-pill">სურვილისამებრ</span>
        </div>
        <h2>რისთვის ხარ აქ?</h2>
        <p>
          მონიშნე <strong>1-დან 3-მდე</strong> მიზანი. ეს ეხმარება JESTER-ს დაგაკავშიროს
          მსგავსი განზრახვის მქონე ადამიანებთან.
        </p>
      </div>

      {/* Error Notice */}
      {error && (
        <div className="onboarding-v3-alert" role="alert">
          <span className="onboarding-v3-alert-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Compact Status Counter Bar */}
      <div className="onboarding-v3-compact-counter">
        <div className="onboarding-v3-counter-left">
          <span className="onboarding-v3-counter-title">შერჩეულია:</span>
          <span
            className={`onboarding-v3-counter-number ${
              count === 0 ? "zero" : isMaxReached ? "maxed" : "active"
            }`}
          >
            {count} / 3
          </span>
        </div>
        <div className="onboarding-v3-counter-hint">
          {count === 0 && "არცერთი არ არის შერჩეული"}
          {count > 0 && count < 3 && `შეგიძლია დაამატო კიდევ ${3 - count}`}
          {isMaxReached && "მაქსიმალური ლიმიტი (3)"}
        </div>
      </div>

      {/* Intentions Grid */}
      <div className="intentions-v3-cards-grid">
        {intentions.map((item) => {
          const isSelected = selected.has(item.id);
          const isBlocked = !isSelected && isMaxReached;

          return (
            <button
              key={item.id}
              type="button"
              disabled={isBlocked}
              onClick={() => toggleIntention(item.id)}
              className={`intentions-v3-card ${isSelected ? "selected" : ""} ${
                isBlocked ? "disabled" : ""
              }`}
              aria-pressed={isSelected}
            >
              <span className="intentions-v3-card-icon">{item.icon || "✨"}</span>
              <div className="intentions-v3-card-info">
                <span className="intentions-v3-card-title">
                  {item.name_ka || item.name}
                </span>
                {item.name_en && (
                  <span className="intentions-v3-card-subtitle">{item.name_en}</span>
                )}
              </div>
              <span className="intentions-v3-card-check" aria-hidden="true">
                {isSelected ? "✓" : "+"}
              </span>
            </button>
          );
        })}
      </div>

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

