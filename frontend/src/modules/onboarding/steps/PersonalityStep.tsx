import React, { useEffect, useState } from "react";
import { API } from "../../../core/api/endpoints";
import { PersonalityTraitItem } from "../../../core/api/types";
import { LoadingState } from "../../../shared/StatusState";
import "./interests.css";

export interface PersonalityStepProps {
  selectedIds: string[];
  onNext: (selected: string[]) => void;
  onSkip?: () => void;
  onSkipAll?: () => void;
  onBack: () => void;
}

export const PersonalityStep: React.FC<PersonalityStepProps> = ({
  selectedIds,
  onNext,
  onSkip,
  onSkipAll,
  onBack,
}) => {
  const [traits, setTraits] = useState<PersonalityTraitItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Set<string>>(new Set(selectedIds));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSelected(new Set(selectedIds));
  }, [selectedIds]);

  useEffect(() => {
    let isMounted = true;
    API.personality
      .list()
      .then((res) => {
        if (isMounted) setTraits(res.items);
      })
      .catch((err) => {
        console.error("Failed to load personality traits:", err);
        if (isMounted) setError("თვისებების ჩატვირთვა ვერ მოხერხდა. სცადეთ ხელახლა.");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const toggleTrait = (id: string) => {
    setError(null);
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        if (next.size >= 5) {
          setError("მაქსიმუმ 5 ხასიათის თვისების არჩევაა შესაძლებელი.");
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
    if (count > 5) {
      setError("მაქსიმუმ 5 თვისების არჩევაა შესაძლებელი.");
      return;
    }

    onNext(Array.from(selected));
  };

  if (loading) {
    return <LoadingState message="ხასიათის თვისებების ჩატვირთვა..." />;
  }

  const count = selected.size;
  const isMaxReached = count >= 5;

  return (
    <form onSubmit={handleContinue} className="personality-step-v3">
      {/* Header */}
      <div className="onboarding-v3-stage-header">
        <div className="onboarding-v3-badge-row">
          <span className="onboarding-v3-stage-tag">ნაბიჯი 6.2 • ჩემი ხასიათი</span>
          <span className="onboarding-v3-optional-pill">სურვილისამებრ</span>
        </div>
        <h2>როგორ დაახასიათებ საკუთარ თავს?</h2>
        <p>
          აირჩიე <strong>1-დან 5-მდე</strong> თვისება, რომელიც ყველაზე მეტად გამოგხატავს.
          ეს ინფორმაცია ეხმარება სხვებს შენი ხასიათის უკეთ გაგებაში.
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
            {count} / 5
          </span>
        </div>
        <div className="onboarding-v3-counter-hint">
          {count === 0 && "არცერთი არ არის შერჩეული"}
          {count > 0 && count < 5 && `შეგიძლია დაამატო კიდევ ${5 - count}`}
          {isMaxReached && "მაქსიმალური ლიმიტი (5)"}
        </div>
      </div>

      {/* Direct One-Tap Personality Descriptors Grid */}
      <div className="personality-v3-pills-grid">
        {traits.map((item) => {
          const isSelected = selected.has(item.id);
          const isBlocked = !isSelected && isMaxReached;

          return (
            <button
              key={item.id}
              type="button"
              disabled={isBlocked}
              onClick={() => toggleTrait(item.id)}
              className={`personality-v3-pill ${isSelected ? "selected" : ""} ${
                isBlocked ? "disabled" : ""
              }`}
              aria-pressed={isSelected}
              title={item.name_en ? `${item.name_ka || item.name} (${item.name_en})` : item.name}
            >
              <span className="personality-v3-pill-check" aria-hidden="true">
                {isSelected ? "✓" : "+"}
              </span>
              <span className="personality-v3-pill-text">
                {item.name_ka || item.name}
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

