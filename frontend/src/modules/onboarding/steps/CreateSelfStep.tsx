import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { supabase } from "../../../core/realtime/supabase";
import { API } from "../../../core/api/endpoints";
import { useAuth } from "../../../core/auth/useAuth";
import { BirthDataPayload, SafeDerivedAstrologyResponse } from "../../../core/api/types";
import { Card, Button, Badge } from "../../../shared/ui";
import { BirthTimePrecision } from "./BirthTimeStep";

interface CreateSelfStepProps {
  displayName: string;
  city: string;
  occupation: string;
  birthDate: string;
  birthTime: string;
  precision: BirthTimePrecision;
  placeLabel: string;
  latitude: number | null;
  longitude: number | null;
  birthTimezone: string;
  onBack: () => void;
}

const ZODIAC_NAMES_KA: Record<string, string> = {
  aries: "ვერძი",
  taurus: "კურო",
  gemini: "ტყუპები",
  cancer: "კირჩხიბი",
  leo: "ლომი",
  virgo: "ქალწული",
  libra: "სასწორი",
  scorpio: "მორიელი",
  sagittarius: "მშვილდოსანი",
  capricorn: "თხის რქა",
  aquarius: "მერწყული",
  pisces: "თევზები",
};

export const CreateSelfStep: React.FC<CreateSelfStepProps> = ({
  displayName,
  city,
  occupation,
  birthDate,
  birthTime,
  precision,
  placeLabel,
  latitude,
  longitude,
  birthTimezone,
  onBack,
}) => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user, setHasBirthData, refreshBirthDataCheck } = useAuth();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [safeAstro, setSafeAstro] = useState<SafeDerivedAstrologyResponse | null>(null);

  const executePersistenceAndCalculation = async () => {
    if (!user) {
      setError("მომხმარებელი ავტორიზებული არ არის. გთხოვთ შეხვიდეთ თავიდან.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1. Persist user profile to public.profiles
      const { error: profileErr } = await supabase.from("profiles").upsert({
        id: user.id,
        display_name: displayName.trim() || user.email?.split("@")[0] || "User",
        city: city.trim() || null,
        occupation: occupation.trim() || null,
        timezone: birthTimezone || "UTC",
        is_discoverable: true,
        updated_at: new Date().toISOString(),
      });

      if (profileErr) {
        console.warn("Direct profile upsert note:", profileErr.message);
      }

      // Also call PATCH /v1/profiles/me if backend API is reachable
      try {
        await API.profiles.updateMyProfile({
          display_name: displayName.trim(),
          city: city.trim() || undefined,
          occupation: occupation.trim() || undefined,
          timezone: birthTimezone || "UTC",
          is_discoverable: true,
        });
      } catch (patchErr) {
        console.warn("Backend PATCH /v1/profiles/me notification:", patchErr);
      }

      // 2. Format BirthDataPayload conforming strictly to repository contract
      const birthPayload: BirthDataPayload = {
        birth_date: birthDate,
        birth_time: precision === "unknown" ? null : (birthTime ? `${birthTime}:00` : null),
        birth_time_precision: precision,
        birth_timezone: birthTimezone,
        latitude: latitude,
        longitude: longitude,
        place_label: placeLabel || null,
      };

      // 3. Save birth data and trigger Swiss Ephemeris calculation
      const astroResult = await API.astrology.saveBirthData(user.id, birthPayload);
      setSafeAstro(astroResult);

      // Invalidate relevant caches immediately
      await queryClient.invalidateQueries({ queryKey: ["astrology"] });
      await queryClient.invalidateQueries({ queryKey: ["birth-data"] });
      await queryClient.invalidateQueries({ queryKey: ["profile"] });
      await queryClient.invalidateQueries({ queryKey: ["daily-energy"] });
      await queryClient.invalidateQueries({ queryKey: ["discovery-people"] });

      // Mark birth data as complete in auth state
      setHasBirthData(true);
      await refreshBirthDataCheck(user.id);

      setLoading(false);
    } catch (err: any) {
      console.error("Persistence/Calculation failed:", err);
      setError(err.message || "ასტროლოგიური მონაცემების შენახვა და გამოთვლა ვერ მოხერხდა.");
      setLoading(false);
    }
  };

  useEffect(() => {
    executePersistenceAndCalculation();
  }, []);

  const handleFinishOnboarding = () => {
    navigate("/", { replace: true });
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "3rem 1rem" }}>
        <div style={{ fontSize: "3rem", marginBottom: "1rem", animation: "spin 2s linear infinite" }}>
          🪐
        </div>
        <h3 style={{ fontSize: "1.3rem", fontWeight: 700, color: "#0f172a", margin: "0 0 0.5rem 0" }}>
          ასტროლოგიური რუკის გამოთვლა...
        </h3>
        <p style={{ color: "#64748b", fontSize: "0.9rem", margin: 0 }}>
          Swiss Ephemeris-ის საშუალებით ითვლება თქვენი ნატალური პლანეტები და ასტროლოგიური პარამეტრები.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem", padding: "1rem 0" }}>
        <div
          style={{
            padding: "1rem",
            background: "#fff1f0",
            border: "1px solid #ff4d4f",
            borderRadius: "8px",
            color: "#cf1322",
            fontSize: "0.9rem",
          }}
        >
          <div style={{ fontWeight: 700, marginBottom: "0.3rem" }}>⚠️ დაფიქსირდა შეცდომა</div>
          {error}
        </div>

        <div style={{ display: "flex", gap: "0.75rem" }}>
          <Button
            type="button"
            variant="secondary"
            size="lg"
            style={{ flex: 1 }}
            onClick={onBack}
          >
            ⬅️ უკან
          </Button>
          <Button
            type="button"
            variant="brand"
            size="lg"
            style={{ flex: 2 }}
            onClick={executePersistenceAndCalculation}
          >
            🔄 ხელახლა ცდა (Retry)
          </Button>
        </div>
      </div>
    );
  }

  // STEP 10 — SUCCESS STATE
  const sunSignKa = safeAstro?.sun_sign ? ZODIAC_NAMES_KA[safeAstro.sun_sign.toLowerCase()] || safeAstro.sun_sign : "—";
  const moonSignKa = safeAstro?.moon_sign ? ZODIAC_NAMES_KA[safeAstro.moon_sign.toLowerCase()] || safeAstro.moon_sign : "—";
  const ascendantSignKa = safeAstro?.ascendant_sign
    ? ZODIAC_NAMES_KA[safeAstro.ascendant_sign.toLowerCase()] || safeAstro.ascendant_sign
    : null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", textAlign: "center" }}>
      <div>
        <div style={{ fontSize: "2.8rem", marginBottom: "0.5rem" }}>🎉</div>
        <h2 style={{ margin: "0 0 0.4rem 0", fontSize: "1.5rem", fontWeight: 800, color: "#0f172a" }}>
          კეთილი იყოს თქვენი მობრძანება JESTER-ში!
        </h2>
        <p style={{ margin: 0, color: "#64748b", fontSize: "0.9rem" }}>
          თქვენი პროფილი და ნატალური რუკა წარმატებით შეიქმნა.
        </p>
      </div>

      {/* Highlights Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem", textAlign: "left" }}>
        {/* Sun Sign */}
        <Card variant="default" style={{ padding: "1rem" }}>
          <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#f59e0b", textTransform: "uppercase" }}>
            ☀️ მზე (Sun Sign)
          </div>
          <div style={{ fontSize: "1.15rem", fontWeight: 800, color: "#0f172a", marginTop: "4px" }}>
            {sunSignKa}
          </div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "capitalize" }}>
            {safeAstro?.sun_sign}
          </div>
        </Card>

        {/* Moon Sign */}
        <Card variant="default" style={{ padding: "1rem" }}>
          <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#6366f1", textTransform: "uppercase" }}>
            🌙 მთვარე (Moon Sign)
          </div>
          <div style={{ fontSize: "1.15rem", fontWeight: 800, color: "#0f172a", marginTop: "4px" }}>
            {moonSignKa}
          </div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "capitalize" }}>
            {safeAstro?.moon_sign}
          </div>
        </Card>

        {/* Ascendant */}
        <Card variant="default" style={{ padding: "1rem", gridColumn: "span 2" }}>
          <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#ec4899", textTransform: "uppercase" }}>
            🌅 ასცენდენტი (Rising / Ascendant)
          </div>
          <div style={{ fontSize: "1.15rem", fontWeight: 800, color: "#0f172a", marginTop: "4px" }}>
            {ascendantSignKa ? (
              <span>{ascendantSignKa} ({safeAstro?.ascendant_sign})</span>
            ) : (
              <span style={{ color: "#94a3b8", fontSize: "0.95rem", fontWeight: 500 }}>
                არ არის გამოთვლილი (დაბადების დრო უცნობია)
              </span>
            )}
          </div>
        </Card>
      </div>

      {(safeAstro?.element_primary || safeAstro?.modality_primary) && (
        <div style={{ display: "flex", justifyContent: "center", gap: "0.5rem" }}>
          {safeAstro?.element_primary && (
            <Badge variant="brand">
              სტიქია: {safeAstro.element_primary}
            </Badge>
          )}
          {safeAstro?.modality_primary && (
            <Badge variant="outline">
              მოდალობა: {safeAstro.modality_primary}
            </Badge>
          )}
        </div>
      )}

      <Button
        type="button"
        variant="brand"
        size="lg"
        fullWidth
        onClick={handleFinishOnboarding}
        style={{ marginTop: "0.5rem" }}
      >
        Enter JESTER / აპლიკაციაში შესვლა 🚀
      </Button>
    </div>
  );
};
