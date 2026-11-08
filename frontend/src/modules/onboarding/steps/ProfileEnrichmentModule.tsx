import React, { useState, useEffect } from "react";
import { API } from "../../../core/api/endpoints";
import { InterestsStep } from "./InterestsStep";
import { PersonalityStep } from "./PersonalityStep";
import { IntentionsStep } from "./IntentionsStep";
import "./interests.css";

export interface ProfileEnrichmentModuleProps {
  onComplete: () => void;
  onBackToStep5: () => void;
}

export const ProfileEnrichmentModule: React.FC<ProfileEnrichmentModuleProps> = ({
  onComplete,
  onBackToStep5,
}) => {
  const [subStage, setSubStage] = useState<1 | 2 | 3>(1);
  const [savedInterests, setSavedInterests] = useState<string[]>([]);
  const [savedTraits, setSavedTraits] = useState<string[]>([]);
  const [savedIntentions, setSavedIntentions] = useState<string[]>([]);
  const [moduleError, setModuleError] = useState<string | null>(null);

  // Pre-load existing selections if any exist
  useEffect(() => {
    let isMounted = true;
    Promise.all([
      API.interests.getMyInterests().catch(() => ({ interest_ids: [] })),
      API.personality.getMyTraits().catch(() => ({ trait_ids: [] })),
      API.intentions.getMyIntentions().catch(() => ({ intention_ids: [] })),
    ]).then(([intRes, traitRes, intentRes]) => {
      if (isMounted) {
        setSavedInterests(intRes.interest_ids || []);
        setSavedTraits(traitRes.trait_ids || []);
        setSavedIntentions(intentRes.intention_ids || []);
      }
    });

    return () => {
      isMounted = false;
    };
  }, []);

  // 1. Interests Handlers
  const handleInterestsNext = async (selected: string[]) => {
    setModuleError(null);
    try {
      await API.interests.setMyInterests(selected);
      setSavedInterests(selected);
      setSubStage(2);
    } catch (err: any) {
      setModuleError(err.message || "ინტერესების შენახვა ვერ მოხერხდა.");
    }
  };

  // 2. Personality Handlers
  const handlePersonalityNext = async (selected: string[]) => {
    setModuleError(null);
    try {
      await API.personality.setMyTraits(selected);
      setSavedTraits(selected);
      setSubStage(3);
    } catch (err: any) {
      setModuleError(err.message || "ხასიათის თვისებების შენახვა ვერ მოხერხდა.");
    }
  };

  // 3. Intentions Handlers
  const handleIntentionsNext = async (selected: string[]) => {
    setModuleError(null);
    try {
      await API.intentions.setMyIntentions(selected);
      setSavedIntentions(selected);
      onComplete();
    } catch (err: any) {
      setModuleError(err.message || "მიზნების შენახვა ვერ მოხერხდა.");
    }
  };

  // Exit all remaining optional stages immediately
  const handleSkipAll = () => {
    setModuleError(null);
    onComplete();
  };

  return (
    <div className="onboarding-v3-enrichment-container">
      {moduleError && (
        <div className="onboarding-v3-alert" role="alert">
          <span className="onboarding-v3-alert-icon">⚠️</span>
          <span>{moduleError}</span>
        </div>
      )}

      {/* Sub-stage Indicator Pills */}
      <div className="onboarding-v3-substeps-indicator" aria-label="პროფილის შევსების ქვესაფეხურები">
        <button
          type="button"
          onClick={() => setSubStage(1)}
          className={`onboarding-v3-substep-tab ${subStage === 1 ? "active" : "done"}`}
        >
          <span>1. ინტერესები</span>
          {savedInterests.length > 0 && <span className="substep-badge">{savedInterests.length}</span>}
        </button>

        <button
          type="button"
          onClick={() => setSubStage(2)}
          className={`onboarding-v3-substep-tab ${subStage === 2 ? "active" : subStage > 2 ? "done" : ""}`}
        >
          <span>2. ხასიათი</span>
          {savedTraits.length > 0 && <span className="substep-badge">{savedTraits.length}</span>}
        </button>

        <button
          type="button"
          onClick={() => setSubStage(3)}
          className={`onboarding-v3-substep-tab ${subStage === 3 ? "active" : ""}`}
        >
          <span>3. რას ვეძებ</span>
          {savedIntentions.length > 0 && <span className="substep-badge">{savedIntentions.length}</span>}
        </button>
      </div>

      {subStage === 1 && (
        <InterestsStep
          selectedIds={savedInterests}
          onNext={handleInterestsNext}
          onSkipAll={handleSkipAll}
          onBack={onBackToStep5}
        />
      )}

      {subStage === 2 && (
        <PersonalityStep
          selectedIds={savedTraits}
          onNext={handlePersonalityNext}
          onSkipAll={handleSkipAll}
          onBack={() => setSubStage(1)}
        />
      )}

      {subStage === 3 && (
        <IntentionsStep
          selectedIds={savedIntentions}
          onNext={handleIntentionsNext}
          onSkipAll={handleSkipAll}
          onBack={() => setSubStage(2)}
        />
      )}
    </div>
  );
};
