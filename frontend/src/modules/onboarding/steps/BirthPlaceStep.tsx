import React, { useState } from "react";
import { Button, CitySelector, SelectedCityValue } from "../../../shared/ui";
import { API } from "../../../core/api/endpoints";

interface BirthPlaceStepProps {
  birthCityId: string | null;
  setBirthCityId: (val: string | null) => void;
  placeLabel: string;
  setPlaceLabel: (val: string) => void;
  latitude: number | null;
  setLatitude: (val: number | null) => void;
  longitude: number | null;
  setLongitude: (val: number | null) => void;
  birthTimezone: string;
  setBirthTimezone: (val: string) => void;
  onNext: () => void;
  onBack: () => void;
}

export const BirthPlaceStep: React.FC<BirthPlaceStepProps> = ({
  birthCityId,
  setBirthCityId,
  placeLabel,
  setPlaceLabel,
  setLatitude,
  setLongitude,
  setBirthTimezone,
  onNext,
  onBack,
}) => {
  const [error, setError] = useState<string | null>(null);

  const handleCitySelect = async (selected: SelectedCityValue) => {
    setBirthCityId(selected.city_id);
    const label = `${selected.display_name}, ${selected.country_name}`;
    setPlaceLabel(label);
    setError(null);

    // Fetch canonical coordinates & timezone for immediate client review
    try {
      const canonical = await API.geo.getCity(selected.city_id);
      setLatitude(canonical.latitude);
      setLongitude(canonical.longitude);
      setBirthTimezone(canonical.timezone);
    } catch {
      // Backend remains authoritative fallback
    }
  };

  const handleClearCity = () => {
    setBirthCityId(null);
    setPlaceLabel("");
    setLatitude(null);
    setLongitude(null);
  };

  const validateAndProceed = (e: React.FormEvent) => {
    e.preventDefault();
    if (!birthCityId) {
      setError("გთხოვთ აირჩიოთ დაბადების ადგილი ჩამონათვალიდან.");
      return;
    }
    onNext();
  };

  return (
    <form onSubmit={validateAndProceed} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h3 style={{ margin: "0 0 0.4rem 0", fontSize: "1.2rem", fontWeight: 700, color: "#0f172a" }}>
          4. დაბადების ადგილი (Birth Place)
        </h3>
        <p style={{ margin: "0 0 1.25rem 0", color: "#64748b", fontSize: "0.875rem" }}>
          დაბადების გეოგრაფიული ადგილი საჭიროა ასცენდენტისა და სახლების ზუსტი გამოთვლისთვის.
        </p>
      </div>

      {error && (
        <div
          style={{
            padding: "0.75rem",
            background: "#fff1f0",
            border: "1px solid #ff4d4f",
            borderRadius: "6px",
            color: "#cf1322",
            fontSize: "0.85rem",
          }}
        >
          ⚠️ {error}
        </div>
      )}

      {/* Production-grade CitySelector Component */}
      <CitySelector
        value={birthCityId}
        initialDisplayLabel={placeLabel}
        onChange={handleCitySelect}
        onClear={handleClearCity}
        label="დაბადების ქალაქი (Birth City)"
        placeholder="მოძებნეთ ქალაქი (მაგ. თბილისი, Batumi, London...)"
        required
        error={error}
      />

      <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem" }}>
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
          type="submit"
          variant="brand"
          size="lg"
          style={{ flex: 2 }}
          disabled={!birthCityId}
        >
          შემდეგი ➡️
        </Button>
      </div>
    </form>
  );
};
