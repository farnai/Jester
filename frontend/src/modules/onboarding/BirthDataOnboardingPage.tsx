import React, { useState, useEffect } from "react";
import { useAuth } from "../../core/auth/useAuth";
import { API } from "../../core/api/endpoints";
import { Card } from "../../shared/ui";
import { LoadingState } from "../../shared/StatusState";
import { BasicProfileStep } from "./steps/BasicProfileStep";
import { BirthDateStep } from "./steps/BirthDateStep";
import { BirthTimeStep, BirthTimePrecision } from "./steps/BirthTimeStep";
import { BirthPlaceStep } from "./steps/BirthPlaceStep";
import { ReviewStep } from "./steps/ReviewStep";
import { CreateSelfStep } from "./steps/CreateSelfStep";

export const BirthDataOnboardingPage: React.FC = () => {
  const { user } = useAuth();

  // Active step in onboarding wizard (1 through 6)
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [loadingInitial, setLoadingInitial] = useState(true);

  // Step 1: Basic Profile
  const [displayName, setDisplayName] = useState<string>("");
  const [city, setCity] = useState<string>("");
  const [occupation, setOccupation] = useState<string>("");

  // Step 2: Birth Date
  const [birthDate, setBirthDate] = useState<string>("");

  // Step 3: Birth Time & Precision
  const [precision, setPrecision] = useState<BirthTimePrecision>("exact");
  const [birthTime, setBirthTime] = useState<string>("12:00");

  // Step 4: Birth Place & Coordinates
  const [placeLabel, setPlaceLabel] = useState<string>("Tbilisi, Georgia");
  const [latitude, setLatitude] = useState<number | null>(41.7151);
  const [longitude, setLongitude] = useState<number | null>(44.8271);
  const [birthTimezone, setBirthTimezone] = useState<string>("Asia/Tbilisi");

  // Load existing profile & birth data if available (e.g., editing flow)
  useEffect(() => {
    if (!user) {
      setLoadingInitial(false);
      return;
    }

    let isMounted = true;

    Promise.all([
      API.profiles.getMyProfile().catch(() => null),
      API.astrology.getBirthData(user.id).catch(() => null),
    ])
      .then(([savedProfile, savedBirthData]) => {
        if (!isMounted) return;

        // Populate profile fields
        if (savedProfile) {
          if (savedProfile.display_name) setDisplayName(savedProfile.display_name);
          if (savedProfile.city) setCity(savedProfile.city);
          if (savedProfile.occupation) setOccupation(savedProfile.occupation);
        } else if (user.email) {
          setDisplayName(user.email.split("@")[0]);
        }

        // Populate birth data fields if already exist
        if (savedBirthData) {
          if (savedBirthData.birth_date) setBirthDate(savedBirthData.birth_date);
          if (savedBirthData.birth_time_precision) setPrecision(savedBirthData.birth_time_precision);
          if (savedBirthData.birth_time) setBirthTime(savedBirthData.birth_time.slice(0, 5));
          if (savedBirthData.place_label) setPlaceLabel(savedBirthData.place_label);
          if (savedBirthData.birth_timezone) setBirthTimezone(savedBirthData.birth_timezone);
          if (savedBirthData.latitude != null) setLatitude(savedBirthData.latitude);
          if (savedBirthData.longitude != null) setLongitude(savedBirthData.longitude);
        }
      })
      .finally(() => {
        if (isMounted) setLoadingInitial(false);
      });

    return () => {
      isMounted = false;
    };
  }, [user]);

  if (loadingInitial) {
    return <LoadingState message="მონაცემების შემოწმება (Loading profile)..." />;
  }

  const stepTitles: Record<number, string> = {
    1: "პროფილი",
    2: "დაბადების თარიღი",
    3: "დაბადების დრო",
    4: "დაბადების ადგილი",
    5: "გადამოწმება",
    6: "რუკის გამოთვლა",
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
          maxWidth: "520px",
          padding: "2rem",
        }}
      >
        {/* Progress Bar Header (Steps 1 to 5) */}
        {currentStep <= 5 && (
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
              <span>ეტაპი {currentStep} / 5</span>
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
                  width: `${(currentStep / 5) * 100}%`,
                  background: "#6366f1",
                  transition: "width 0.3s ease",
                }}
              />
            </div>
          </div>
        )}

        {/* STEP 1: Basic Profile */}
        {currentStep === 1 && (
          <BasicProfileStep
            displayName={displayName}
            setDisplayName={setDisplayName}
            city={city}
            setCity={setCity}
            occupation={occupation}
            setOccupation={setOccupation}
            onNext={() => setCurrentStep(2)}
          />
        )}

        {/* STEP 2: Birth Date */}
        {currentStep === 2 && (
          <BirthDateStep
            birthDate={birthDate}
            setBirthDate={setBirthDate}
            onNext={() => setCurrentStep(3)}
            onBack={() => setCurrentStep(1)}
          />
        )}

        {/* STEP 3: Birth Time & Precision */}
        {currentStep === 3 && (
          <BirthTimeStep
            precision={precision}
            setPrecision={setPrecision}
            birthTime={birthTime}
            setBirthTime={setBirthTime}
            onNext={() => setCurrentStep(4)}
            onBack={() => setCurrentStep(2)}
          />
        )}

        {/* STEP 4: Birth Place */}
        {currentStep === 4 && (
          <BirthPlaceStep
            placeLabel={placeLabel}
            setPlaceLabel={setPlaceLabel}
            latitude={latitude}
            setLatitude={setLatitude}
            longitude={longitude}
            setLongitude={setLongitude}
            birthTimezone={birthTimezone}
            setBirthTimezone={setBirthTimezone}
            onNext={() => setCurrentStep(5)}
            onBack={() => setCurrentStep(3)}
          />
        )}

        {/* STEP 5: Review & Confirm */}
        {currentStep === 5 && (
          <ReviewStep
            displayName={displayName}
            city={city}
            occupation={occupation}
            birthDate={birthDate}
            birthTime={birthTime}
            precision={precision}
            placeLabel={placeLabel}
            onConfirm={() => setCurrentStep(6)}
            onBack={() => setCurrentStep(4)}
            onJumpToStep={(step) => setCurrentStep(step)}
          />
        )}

        {/* STEP 6: Persistence, Swiss Ephemeris Calculation, and Success Highlights */}
        {currentStep === 6 && (
          <CreateSelfStep
            displayName={displayName}
            city={city}
            occupation={occupation}
            birthDate={birthDate}
            birthTime={birthTime}
            precision={precision}
            placeLabel={placeLabel}
            latitude={latitude}
            longitude={longitude}
            birthTimezone={birthTimezone}
            onBack={() => setCurrentStep(5)}
          />
        )}
      </Card>
    </div>
  );
};
