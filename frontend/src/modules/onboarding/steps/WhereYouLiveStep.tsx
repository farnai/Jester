import React, { useState } from "react";
import { Button, CitySelector, SelectedCityValue, Card } from "../../../shared/ui";

interface WhereYouLiveStepProps {
  currentCityId: string | null;
  setCurrentCityId: (val: string | null) => void;
  currentCityLabel: string;
  setCurrentCityLabel: (val: string) => void;
  birthCityId: string | null;
  birthCityLabel: string;
  onNext: () => void;
  onBack: () => void;
}

export const WhereYouLiveStep: React.FC<WhereYouLiveStepProps> = ({
  currentCityId,
  setCurrentCityId,
  currentCityLabel,
  setCurrentCityLabel,
  birthCityId,
  birthCityLabel,
  onNext,
  onBack,
}) => {
  const [error, setError] = useState<string | null>(null);

  const handleCitySelect = (selected: SelectedCityValue) => {
    setCurrentCityId(selected.city_id);
    const label = `${selected.display_name}, ${selected.country_name}`;
    setCurrentCityLabel(label);
    setError(null);
  };

  const handleClearCity = () => {
    setCurrentCityId(null);
    setCurrentCityLabel("");
  };

  const handleCopyFromBirthCity = () => {
    if (birthCityId) {
      setCurrentCityId(birthCityId);
      setCurrentCityLabel(birthCityLabel);
      setError(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentCityId) {
      setError("გთხოვთ მიუთითოთ თქვენი ამჟამინდელი საცხოვრებელი ქალაქი.");
      return;
    }
    onNext();
  };

  const isSameAsBirthCity = currentCityId && birthCityId && currentCityId === birthCityId;

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h3 style={{ margin: "0 0 0.4rem 0", fontSize: "1.2rem", fontWeight: 700, color: "#0f172a" }}>
          5. სად ცხოვრობთ? (Where You Live)
        </h3>
        <p style={{ margin: "0 0 1.25rem 0", color: "#64748b", fontSize: "0.875rem" }}>
          მიუთითეთ თქვენი მიმდინარე საცხოვრებელი ქალაქი. ეს ინფორმაცია საჭიროა სიახლოვისა და ადამიანების აღმოჩენისთვის.
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

      {/* Optional Shortcut: "ამჟამადაც აქ ცხოვრობ?" */}
      {birthCityId && birthCityLabel && !isSameAsBirthCity && (
        <Card
          variant="bordered"
          style={{
            padding: "0.875rem",
            backgroundColor: "#f8fafc",
            borderColor: "#cbd5e1",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "0.5rem",
          }}
        >
          <div style={{ fontSize: "0.875rem", color: "#334155" }}>
            ამჟამადაც <strong>{birthCityLabel.split(",")[0]}</strong>-ში ცხოვრობთ?
          </div>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={handleCopyFromBirthCity}
          >
            დიახ, აქ ვცხოვრობ ✓
          </Button>
        </Card>
      )}

      <CitySelector
        value={currentCityId}
        initialDisplayLabel={currentCityLabel}
        onChange={handleCitySelect}
        onClear={handleClearCity}
        label="მიმდინარე საცხოვრებელი ქალაქი (Current City) *"
        placeholder="მოძებნეთ ქალაქი (მაგ. თბილისი, ბათუმი, ბერლინი...)"
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
          disabled={!currentCityId}
        >
          შემდეგი ➡️
        </Button>
      </div>
    </form>
  );
};
