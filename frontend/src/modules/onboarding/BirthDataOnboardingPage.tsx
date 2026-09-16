import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../../core/auth/useAuth";
import { API } from "../../core/api/endpoints";
import { Card } from "../../shared/ui";
import { LoadingState } from "../../shared/StatusState";

import { BasicProfileStep } from "./steps/BasicProfileStep";
import { BirthDateStep } from "./steps/BirthDateStep";
import { BirthTimeStep, BirthTimePrecision } from "./steps/BirthTimeStep";
import { BirthPlaceStep } from "./steps/BirthPlaceStep";
import { WhereYouLiveStep } from "./steps/WhereYouLiveStep";
import { InterestsStep } from "./steps/InterestsStep";
import { ProfilePhotoStep } from "./steps/ProfilePhotoStep";
import { FinishStep } from "./steps/FinishStep";

export const BirthDataOnboardingPage: React.FC = () => {
  const { user, profile, refreshProfile, onboardingCompleted, signOut } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Active step in onboarding wizard (1 through 8)
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [savingStep, setSavingStep] = useState(false);
  const [stepError, setStepError] = useState<string | null>(null);

  // Step 1: Basic Identity
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [displayName, setDisplayName] = useState<string>("");

  // Step 2: Birth Date
  const [birthDate, setBirthDate] = useState<string>("");

  // Step 3: Birth Time & Precision
  const [precision, setPrecision] = useState<BirthTimePrecision>("exact");
  const [birthTime, setBirthTime] = useState<string>("12:00");

  // Step 4: Birth Place
  const [birthCityId, setBirthCityId] = useState<string | null>(null);
  const [birthCityLabel, setBirthCityLabel] = useState<string>("");
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [birthTimezone, setBirthTimezone] = useState<string>("Asia/Tbilisi");

  // Step 5: Where You Live
  const [currentCityId, setCurrentCityId] = useState<string | null>(null);
  const [currentCityLabel, setCurrentCityLabel] = useState<string>("");

  // Step 6: Interests
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);

  // Step 7: Profile Photo
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);

  // Initial Data Fetch & Deterministic Resume Logic
  useEffect(() => {
    if (!user) {
      setLoadingInitial(false);
      return;
    }

    // If user already completed onboarding, route to /me immediately
    if (onboardingCompleted) {
      navigate("/me", { replace: true });
      return;
    }

    let isMounted = true;

    const profilePromise = profile
      ? Promise.resolve(profile)
      : API.profiles.getMyProfile().catch(async () => {
          try {
            return await API.profiles.initializeProfile();
          } catch {
            return null;
          }
        });

    Promise.all([
      profilePromise,
      API.astrology.getBirthData(user.id).catch(() => null),
      API.interests.getMyInterests().catch(() => ({ interest_ids: [] })),
    ])
      .then(async ([savedProfile, savedBirthData, userInterests]) => {
        if (!isMounted) return;

        // 1. Populate Profile Data
        if (savedProfile) {
          if (savedProfile.first_name) setFirstName(savedProfile.first_name);
          if (savedProfile.last_name) setLastName(savedProfile.last_name);
          if (savedProfile.display_name) setDisplayName(savedProfile.display_name);
          if (savedProfile.avatar_url) setAvatarUrl(savedProfile.avatar_url);
          if (savedProfile.current_city_id) {
            setCurrentCityId(savedProfile.current_city_id);
            if (savedProfile.city) {
              setCurrentCityLabel(savedProfile.city);
            } else {
              API.geo
                .getCity(savedProfile.current_city_id)
                .then((c) => {
                  if (isMounted) setCurrentCityLabel(`${c.display_name}, ${c.country_name}`);
                })
                .catch(() => null);
            }
          }
        }

        // 2. Populate Birth Data
        if (savedBirthData) {
          if (savedBirthData.birth_date) setBirthDate(savedBirthData.birth_date);
          if (savedBirthData.birth_time_precision) setPrecision(savedBirthData.birth_time_precision);
          if (savedBirthData.birth_time) {
            setBirthTime(savedBirthData.birth_time.slice(0, 5));
          } else if (savedBirthData.birth_time_precision === "unknown") {
            setBirthTime("");
          }
          if (savedBirthData.place_label) setBirthCityLabel(savedBirthData.place_label);
          if (savedBirthData.birth_city_id) setBirthCityId(savedBirthData.birth_city_id);
          if (savedBirthData.birth_timezone) setBirthTimezone(savedBirthData.birth_timezone);
          if (savedBirthData.latitude != null) setLatitude(savedBirthData.latitude);
          if (savedBirthData.longitude != null) setLongitude(savedBirthData.longitude);
        }

        // 3. Populate Interests
        if (userInterests?.interest_ids) {
          setSelectedInterests(userInterests.interest_ids);
        }

        // 4. Deterministic Resume Point Calculation
        // Do not blindly trust saved step if earlier required prerequisites are missing
        const persistedStep = savedProfile?.onboarding_step ?? 1;
        let resumeStep = persistedStep;
        if (!savedProfile?.first_name || !savedProfile?.last_name) {
          resumeStep = 1;
        } else if (!savedBirthData?.birth_date) {
          resumeStep = Math.max(2, Math.min(resumeStep, 2));
        } else if (persistedStep <= 3) {
          resumeStep = 3;
        } else if (!savedBirthData?.birth_city_id) {
          resumeStep = 4;
        } else if (!savedProfile?.current_city_id) {
          resumeStep = 5;
        } else {
          // If all required prerequisites are satisfied, respect persisted step or resume at interests
          resumeStep = Math.max(6, Math.min(8, persistedStep));
        }

        setCurrentStep(resumeStep);
      })
      .finally(() => {
        if (isMounted) setLoadingInitial(false);
      });

    return () => {
      isMounted = false;
    };
  }, [user, onboardingCompleted, navigate]);

  // Step 1: Back to Registration
  const handleStep1Back = async () => {
    try {
      await signOut();
    } catch {}
    navigate("/auth/register", { replace: true });
  };

  // Step 1: Advance from Identity
  const handleStep1Next = async () => {
    setStepError(null);
    setSavingStep(true);
    try {
      let updated: any;
      try {
        updated = await API.profiles.updateMyProfile({
          first_name: firstName.trim(),
          last_name: lastName.trim(),
          onboarding_step: 2,
        });
      } catch {
        updated = await API.profiles.initializeProfile({
          first_name: firstName.trim(),
          last_name: lastName.trim(),
        });
        await API.profiles.updateMyProfile({ onboarding_step: 2 });
      }
      if (updated.display_name) {
        setDisplayName(updated.display_name);
      }
      await refreshProfile();
      setCurrentStep(2);
    } catch (err: any) {
      setStepError(err.message || "პროფილის შენახვა ვერ მოხერხდა.");
    } finally {
      setSavingStep(false);
    }
  };

  // Step 2: Advance from Birth Date
  const handleStep2Next = async () => {
    if (!user) return;
    setStepError(null);
    setSavingStep(true);
    try {
      await API.astrology.updateBirthData(user.id, {
        birth_date: birthDate,
        birth_timezone: birthTimezone,
      });
      await API.profiles.updateMyProfile({ onboarding_step: 3 });
      await refreshProfile();
      setCurrentStep(3);
    } catch (err: any) {
      setStepError(err.message || "დაბადების თარიღის შენახვა ვერ მოხერხდა.");
    } finally {
      setSavingStep(false);
    }
  };

  // Step 3: Advance from Birth Time
  const handleStep3Next = async () => {
    if (!user) return;
    setStepError(null);
    setSavingStep(true);
    try {
      const timeVal = precision === "unknown" ? null : birthTime ? `${birthTime}:00` : null;
      await API.astrology.updateBirthData(user.id, {
        birth_time: timeVal,
        birth_time_precision: precision,
      });
      await API.profiles.updateMyProfile({ onboarding_step: 4 });
      await refreshProfile();
      setCurrentStep(4);
    } catch (err: any) {
      setStepError(err.message || "დაბადების დროის შენახვა ვერ მოხერხდა.");
    } finally {
      setSavingStep(false);
    }
  };

  // Step 4: Advance from Birth Place
  const handleStep4Next = async () => {
    if (!user || !birthCityId) return;
    setStepError(null);
    setSavingStep(true);
    try {
      await API.astrology.updateBirthData(user.id, {
        birth_city_id: birthCityId,
        place_label: birthCityLabel,
        latitude: latitude,
        longitude: longitude,
        birth_timezone: birthTimezone,
      });
      // Trigger astrology calculation in background
      API.astrology.recalculate().catch((err) => console.warn("Background astrology recalc note:", err));
      await API.profiles.updateMyProfile({ onboarding_step: 5 });
      await refreshProfile();
      setCurrentStep(5);
    } catch (err: any) {
      setStepError(err.message || "დაბადების ადგილის შენახვა ვერ მოხერხდა.");
    } finally {
      setSavingStep(false);
    }
  };

  // Step 5: Advance from Where You Live
  const handleStep5Next = async () => {
    if (!currentCityId) return;
    setStepError(null);
    setSavingStep(true);
    try {
      await API.profiles.updateMyProfile({
        current_city_id: currentCityId,
        city_id: currentCityId,
        city: currentCityLabel,
        onboarding_step: 6,
      });
      await refreshProfile();
      setCurrentStep(6);
    } catch (err: any) {
      setStepError(err.message || "საცხოვრებელი ადგილის შენახვა ვერ მოხერხდა.");
    } finally {
      setSavingStep(false);
    }
  };

  // Step 6: Advance from Interests
  const handleStep6Next = async (selected: string[]) => {
    setStepError(null);
    setSavingStep(true);
    try {
      await API.interests.setMyInterests(selected);
      setSelectedInterests(selected);
      await API.profiles.updateMyProfile({ onboarding_step: 7 });
      await refreshProfile();
      setCurrentStep(7);
    } catch (err: any) {
      setStepError(err.message || "ინტერესების შენახვა ვერ მოხერხდა.");
    } finally {
      setSavingStep(false);
    }
  };

  const handleStep6Skip = async () => {
    setStepError(null);
    setSavingStep(true);
    try {
      await API.interests.setMyInterests([]);
      setSelectedInterests([]);
      await API.profiles.updateMyProfile({ onboarding_step: 7 });
      await refreshProfile();
      setCurrentStep(7);
    } catch (err: any) {
      setStepError(err.message || "ინტერესების გამოტოვება ვერ მოხერხდა.");
    } finally {
      setSavingStep(false);
    }
  };

  // Step 7: Advance from Photo
  const handleStep7Next = async (uploadedUrl: string | null) => {
    setStepError(null);
    setSavingStep(true);
    try {
      if (uploadedUrl) {
        await API.profiles.updateMyProfile({ avatar_url: uploadedUrl, onboarding_step: 8 });
        setAvatarUrl(uploadedUrl);
      } else {
        await API.profiles.updateMyProfile({ onboarding_step: 8 });
      }
      await refreshProfile();
      setCurrentStep(8);
    } catch (err: any) {
      setStepError(err.message || "ფოტოს შენახვა ვერ მოხერხდა.");
    } finally {
      setSavingStep(false);
    }
  };

  const handleStep7Skip = async () => {
    setStepError(null);
    setSavingStep(true);
    try {
      await API.profiles.updateMyProfile({ onboarding_step: 8 });
      await refreshProfile();
      setCurrentStep(8);
    } catch (err: any) {
      setStepError(err.message || "ეტაპის გამოტოვება ვერ მოხერხდა.");
    } finally {
      setSavingStep(false);
    }
  };

  // Step 8: Complete Onboarding
  const handleStep8Success = async () => {
    await queryClient.invalidateQueries({ queryKey: ["profile"] });
    await queryClient.invalidateQueries({ queryKey: ["birth-data"] });
    await queryClient.invalidateQueries({ queryKey: ["astrology"] });
    await refreshProfile();
    navigate("/me", { replace: true });
  };

  if (loadingInitial) {
    return <LoadingState message="ონბორდინგის მონაცემების ჩატვირთვა..." />;
  }

  const stepTitles: Record<number, string> = {
    1: "სახელი და გვარი (Identity)",
    2: "დაბადების თარიღი (Birth Date)",
    3: "დაბადების დრო (Birth Time)",
    4: "დაბადების ადგილი (Birth Place)",
    5: "საცხოვრებელი ქალაქი (Where You Live)",
    6: "ინტერესები (Interests)",
    7: "პროფილის ფოტო (Photo)",
    8: "გადამოწმება და დასრულება (Finish)",
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "85vh",
        padding: "1.5rem",
        boxSizing: "border-box",
      }}
    >
      <Card
        variant="elevated"
        style={{
          width: "100%",
          maxWidth: "540px",
          padding: "2rem",
        }}
      >
        {/* Progress Bar Header */}
        <div style={{ marginBottom: "1.5rem" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: "0.825rem",
              color: "#64748b",
              marginBottom: "0.4rem",
            }}
          >
            <span>{stepTitles[currentStep]}</span>
            <span>ეტაპი {currentStep} / 8</span>
          </div>
          <div
            style={{
              height: "5px",
              width: "100%",
              background: "#f1f5f9",
              borderRadius: "3px",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${(currentStep / 8) * 100}%`,
                background: "#6366f1",
                transition: "width 0.3s ease",
              }}
            />
          </div>
        </div>

        {/* Global Save Error Banner */}
        {stepError && (
          <div
            style={{
              padding: "0.75rem",
              background: "#fff1f0",
              border: "1px solid #ff4d4f",
              borderRadius: "6px",
              color: "#cf1322",
              fontSize: "0.85rem",
              marginBottom: "1rem",
            }}
          >
            ⚠️ {stepError}
          </div>
        )}

        {/* Loading Spinner for async transition */}
        {savingStep && (
          <div style={{ padding: "0.5rem 0", color: "#6366f1", fontSize: "0.85rem", textAlign: "center" }}>
            მონაცემების შენახვა...
          </div>
        )}

        {/* STEP 1: Basic Identity */}
        {currentStep === 1 && (
          <BasicProfileStep
            firstName={firstName}
            setFirstName={setFirstName}
            lastName={lastName}
            setLastName={setLastName}
            onNext={handleStep1Next}
            onBack={handleStep1Back}
          />
        )}

        {/* STEP 2: Birth Date */}
        {currentStep === 2 && (
          <BirthDateStep
            birthDate={birthDate}
            setBirthDate={setBirthDate}
            onNext={handleStep2Next}
            onBack={() => setCurrentStep(1)}
          />
        )}

        {/* STEP 3: Birth Time */}
        {currentStep === 3 && (
          <BirthTimeStep
            precision={precision}
            setPrecision={setPrecision}
            birthTime={birthTime}
            setBirthTime={setBirthTime}
            onNext={handleStep3Next}
            onBack={() => setCurrentStep(2)}
          />
        )}

        {/* STEP 4: Birth Place */}
        {currentStep === 4 && (
          <BirthPlaceStep
            birthCityId={birthCityId}
            setBirthCityId={setBirthCityId}
            placeLabel={birthCityLabel}
            setPlaceLabel={setBirthCityLabel}
            latitude={latitude}
            setLatitude={setLatitude}
            longitude={longitude}
            setLongitude={setLongitude}
            birthTimezone={birthTimezone}
            setBirthTimezone={setBirthTimezone}
            onNext={handleStep4Next}
            onBack={() => setCurrentStep(3)}
          />
        )}

        {/* STEP 5: Where You Live */}
        {currentStep === 5 && (
          <WhereYouLiveStep
            currentCityId={currentCityId}
            setCurrentCityId={setCurrentCityId}
            currentCityLabel={currentCityLabel}
            setCurrentCityLabel={setCurrentCityLabel}
            birthCityId={birthCityId}
            birthCityLabel={birthCityLabel}
            onNext={handleStep5Next}
            onBack={() => setCurrentStep(4)}
          />
        )}

        {/* STEP 6: Interests */}
        {currentStep === 6 && (
          <InterestsStep
            selectedIds={selectedInterests}
            onNext={handleStep6Next}
            onSkip={handleStep6Skip}
            onBack={() => setCurrentStep(5)}
          />
        )}

        {/* STEP 7: Profile Photo */}
        {currentStep === 7 && user && (
          <ProfilePhotoStep
            userId={user.id}
            avatarUrl={avatarUrl}
            onNext={handleStep7Next}
            onSkip={handleStep7Skip}
            onBack={() => setCurrentStep(6)}
          />
        )}

        {/* STEP 8: Finish & Review */}
        {currentStep === 8 && (
          <FinishStep
            firstName={firstName}
            lastName={lastName}
            displayName={displayName}
            birthDate={birthDate}
            birthTime={birthTime}
            precision={precision}
            birthCityLabel={birthCityLabel}
            currentCityLabel={currentCityLabel}
            interestsCount={selectedInterests.length}
            avatarUrl={avatarUrl}
            onSuccess={handleStep8Success}
            onBack={() => setCurrentStep(7)}
            onJumpToStep={(step) => setCurrentStep(step)}
          />
        )}
      </Card>
    </div>
  );
};
