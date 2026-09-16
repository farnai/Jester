import React, { useState } from "react";
import { Button, Input } from "../../../shared/ui";

interface BasicProfileStepProps {
  firstName: string;
  setFirstName: (val: string) => void;
  lastName: string;
  setLastName: (val: string) => void;
  onNext: () => void;
  onBack?: () => void;
}

export const BasicProfileStep: React.FC<BasicProfileStepProps> = ({
  firstName,
  setFirstName,
  lastName,
  setLastName,
  onNext,
  onBack,
}) => {
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const fn = firstName.trim();
    const ln = lastName.trim();

    if (!fn) {
      setError("სახელის მითითება სავალდებულოა (First name is required).");
      return;
    }
    if (!ln) {
      setError("გვარის მითითება სავალდებულოა (Last name is required).");
      return;
    }

    onNext();
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h3 style={{ margin: "0 0 0.4rem 0", fontSize: "1.2rem", fontWeight: 700, color: "#0f172a" }}>
          1. სახელი და გვარი (Basic Identity)
        </h3>
        <p style={{ margin: "0 0 1.25rem 0", color: "#64748b", fontSize: "0.875rem" }}>
          მიუთითეთ თქვენი რეალური სახელი და გვარი. საჯარო სახელი (Display Name) ავტომატურად შედგება: სახელი + გვარის ინიციალი.
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
        label="სახელი (First Name) *"
        type="text"
        required
        value={firstName}
        onChange={(e) => {
          setFirstName(e.target.value);
          if (error) setError(null);
        }}
        placeholder="მაგ. ნიკა"
        autoComplete="given-name"
      />

      <Input
        label="გვარი (Last Name) *"
        type="text"
        required
        value={lastName}
        onChange={(e) => {
          setLastName(e.target.value);
          if (error) setError(null);
        }}
        placeholder="მაგ. იორდანიშვილი"
        autoComplete="family-name"
      />

      <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem" }}>
        {onBack && (
          <Button
            type="button"
            variant="secondary"
            size="lg"
            style={{ flex: 1 }}
            onClick={onBack}
          >
            ⬅️ უკან
          </Button>
        )}
        <Button
          type="submit"
          variant="brand"
          size="lg"
          style={{ flex: onBack ? 2 : 1 }}
          disabled={!firstName.trim() || !lastName.trim()}
        >
          შემდეგი ➡️ (Continue)
        </Button>
      </div>
    </form>
  );
};
