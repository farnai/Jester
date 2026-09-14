import React from "react";
import { Button, Input } from "../../../shared/ui";

interface BasicProfileStepProps {
  displayName: string;
  setDisplayName: (val: string) => void;
  city: string;
  setCity: (val: string) => void;
  occupation: string;
  setOccupation: (val: string) => void;
  onNext: () => void;
}

export const BasicProfileStep: React.FC<BasicProfileStepProps> = ({
  displayName,
  setDisplayName,
  city,
  setCity,
  occupation,
  setOccupation,
  onNext,
}) => {
  const isValid = displayName.trim().length > 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isValid) {
      onNext();
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h3 style={{ margin: "0 0 0.4rem 0", fontSize: "1.2rem", fontWeight: 700, color: "#0f172a" }}>
          1. თქვენი პროფილი (Basic Profile)
        </h3>
        <p style={{ margin: "0 0 1.25rem 0", color: "#64748b", fontSize: "0.875rem" }}>
          როგორ წარმოჩნდეთ JESTER-ის საზოგადოებაში.
        </p>
      </div>

      <Input
        label="თქვენი სახელი / Display Name *"
        type="text"
        required
        value={displayName}
        onChange={(e) => setDisplayName(e.target.value)}
        placeholder="მაგ. ნიკა, ანა, ალექსანდრე"
        helperText="ეს სახელი გამოჩნდება თქვენს პროფილზე."
      />

      <Input
        label="ქალაქი (City) — არასავალდებულო"
        type="text"
        value={city}
        onChange={(e) => setCity(e.target.value)}
        placeholder="მაგ. თბილისი, ბათუმი, ბერლინი"
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
          disabled={!isValid}
        >
          შემდეგი ➡️ (Continue)
        </Button>
      </div>
    </form>
  );
};
