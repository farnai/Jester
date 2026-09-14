import React, { useState } from "react";
import { Button, Input } from "../../../shared/ui";

interface BirthDateStepProps {
  birthDate: string;
  setBirthDate: (val: string) => void;
  onNext: () => void;
  onBack: () => void;
}

export const BirthDateStep: React.FC<BirthDateStepProps> = ({
  birthDate,
  setBirthDate,
  onNext,
  onBack,
}) => {
  const [error, setError] = useState<string | null>(null);

  const today = new Date().toISOString().split("T")[0];

  const validateAndProceed = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!birthDate) {
      setError("დაბადების თარიღის მითითება სავალდებულოა.");
      return;
    }

    if (!/^\d{4}-\d{2}-\d{2}$/.test(birthDate)) {
      setError("თარიღის არასწორი ფორმატი (უნდა იყოს YYYY-MM-DD).");
      return;
    }

    if (birthDate > today) {
      setError("დაბადების თარიღი არ შეიძლება იყოს მომავალში.");
      return;
    }

    if (birthDate < "1900-01-01") {
      setError("დაბადების თარიღი უნდა იყოს 1900 წლის შემდეგ.");
      return;
    }

    onNext();
  };

  return (
    <form onSubmit={validateAndProceed} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h3 style={{ margin: "0 0 0.4rem 0", fontSize: "1.2rem", fontWeight: 700, color: "#0f172a" }}>
          2. დაბადების თარიღი (Birth Date)
        </h3>
        <p style={{ margin: "0 0 1.25rem 0", color: "#64748b", fontSize: "0.875rem" }}>
          დაბადების ზუსტი თარიღი განსაზღვრავს თქვენს მზის, მთვარისა და პლანეტების ნატალურ პოზიციებს.
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

      <Input
        label="დაბადების თარიღი (Birth Date) *"
        type="date"
        required
        value={birthDate}
        max={today}
        min="1900-01-01"
        onChange={(e) => {
          setBirthDate(e.target.value);
          if (error) setError(null);
        }}
        helperText="კალენდარული თარიღი (დღე / თვე / წელი)"
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
          disabled={!birthDate}
        >
          შემდეგი ➡️
        </Button>
      </div>
    </form>
  );
};
