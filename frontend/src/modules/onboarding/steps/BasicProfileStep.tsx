import React from "react";
import { Button, Input, CitySelector, SelectedCityValue } from "../../../shared/ui";

interface BasicProfileStepProps {
  city: string;
  setCity: (val: string) => void;
  cityId?: string | null;
  setCityId?: (val: string | null) => void;
  occupation: string;
  setOccupation: (val: string) => void;
  onNext: () => void;
}

export const BasicProfileStep: React.FC<BasicProfileStepProps> = ({
  city,
  setCity,
  cityId,
  setCityId,
  occupation,
  setOccupation,
  onNext,
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext();
  };

  const handleCitySelect = (selected: SelectedCityValue) => {
    const formatted = `${selected.display_name}, ${selected.country_name}`;
    setCity(formatted);
    if (setCityId) {
      setCityId(selected.city_id);
    }
  };

  const handleClearCity = () => {
    setCity("");
    if (setCityId) {
      setCityId(null);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h3 style={{ margin: "0 0 0.4rem 0", fontSize: "1.2rem", fontWeight: 700, color: "#0f172a" }}>
          1. დამატებითი ინფორმაცია (Additional Details)
        </h3>
        <p style={{ margin: "0 0 1.25rem 0", color: "#64748b", fontSize: "0.875rem" }}>
          მიუთითეთ თქვენი საცხოვრებელი ქალაქი და საქმიანობა (არასავალდებულო).
        </p>
      </div>

      <CitySelector
        value={cityId || null}
        initialDisplayLabel={city}
        onChange={handleCitySelect}
        onClear={handleClearCity}
        label="საცხოვრებელი ქალაქი (Current City) — არასავალდებულო"
        placeholder="მაგ. თბილისი, ბათუმი, ბერლინი..."
        helperText="ქალაქი, სადაც ამჟამად ცხოვრობთ."
      />

      <Input
        label="საქმიანობა (Occupation) — არასავალდებულო"
        type="text"
        value={occupation}
        onChange={(e) => setOccupation(e.target.value)}
        placeholder="მაგ. არქიტექტორი, დეველოპერი, მხატვარი"
      />

      <div style={{ marginTop: "1rem" }}>
        <Button
          type="submit"
          variant="brand"
          size="lg"
          fullWidth
        >
          შემდეგი ➡️ (Continue)
        </Button>
      </div>
    </form>
  );
};
