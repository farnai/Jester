import React, { useState } from "react";
import { Button, Input, Card } from "../../../shared/ui";

export type BirthTimePrecision = "exact" | "approximate" | "unknown";

interface BirthTimeStepProps {
  precision: BirthTimePrecision;
  setPrecision: (val: BirthTimePrecision) => void;
  birthTime: string;
  setBirthTime: (val: string) => void;
  onNext: () => void;
  onBack: () => void;
}

export const BirthTimeStep: React.FC<BirthTimeStepProps> = ({
  precision,
  setPrecision,
  birthTime,
  setBirthTime,
  onNext,
  onBack,
}) => {
  const [error, setError] = useState<string | null>(null);

  const handlePrecisionChange = (newPrecision: BirthTimePrecision) => {
    setPrecision(newPrecision);
    setError(null);
    if (newPrecision === "unknown") {
      setBirthTime("");
    } else if (!birthTime) {
      setBirthTime("12:00");
    }
  };

  const validateAndProceed = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (precision !== "unknown") {
      if (!birthTime || !/^\d{2}:\d{2}$/.test(birthTime)) {
        setError("გთხოვთ მიუთითოთ დაბადების დრო (ფორმატით სთ:წთ).");
        return;
      }
    }

    onNext();
  };

  return (
    <form onSubmit={validateAndProceed} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h3 style={{ margin: "0 0 0.4rem 0", fontSize: "1.2rem", fontWeight: 700, color: "#0f172a" }}>
          3. დაბადების დრო (Birth Time)
        </h3>
        <p style={{ margin: "0 0 1.25rem 0", color: "#64748b", fontSize: "0.875rem" }}>
          იცით თქვენი დაბადების დრო?
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

      {/* 3 Precision Choices */}
      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {/* Choice 1: Exact */}
        <Card
          variant={precision === "exact" ? "bordered" : "default"}
          interactive
          onClick={() => handlePrecisionChange("exact")}
          style={{
            padding: "1rem",
            borderColor: precision === "exact" ? "#6366f1" : "#e2e8f0",
            backgroundColor: precision === "exact" ? "#f5f3ff" : "#ffffff",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <input
              type="radio"
              name="precision"
              checked={precision === "exact"}
              onChange={() => handlePrecisionChange("exact")}
              style={{ accentColor: "#6366f1", width: "18px", height: "18px", cursor: "pointer" }}
            />
            <div>
              <div style={{ fontWeight: 700, color: "#0f172a", fontSize: "0.95rem" }}>
                1. ზუსტი დრო (Exact)
              </div>
              <div style={{ fontSize: "0.8rem", color: "#64748b" }}>
                ზუსტად ვიცი დაბადების საათი და წუთი
              </div>
            </div>
          </div>
        </Card>

        {/* Choice 2: Approximate */}
        <Card
          variant={precision === "approximate" ? "bordered" : "default"}
          interactive
          onClick={() => handlePrecisionChange("approximate")}
          style={{
            padding: "1rem",
            borderColor: precision === "approximate" ? "#6366f1" : "#e2e8f0",
            backgroundColor: precision === "approximate" ? "#f5f3ff" : "#ffffff",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <input
              type="radio"
              name="precision"
              checked={precision === "approximate"}
              onChange={() => handlePrecisionChange("approximate")}
              style={{ accentColor: "#6366f1", width: "18px", height: "18px", cursor: "pointer" }}
            />
            <div>
              <div style={{ fontWeight: 700, color: "#0f172a", fontSize: "0.95rem" }}>
                2. მიახლოებითი დრო (Approximate)
              </div>
              <div style={{ fontSize: "0.8rem", color: "#64748b" }}>
                ვიცი მიახლოებითი საათი (შენარჩუნდება როგორც მიახლოებითი)
              </div>
            </div>
          </div>
        </Card>

        {/* Choice 3: Unknown */}
        <Card
          variant={precision === "unknown" ? "bordered" : "default"}
          interactive
          onClick={() => handlePrecisionChange("unknown")}
          style={{
            padding: "1rem",
            borderColor: precision === "unknown" ? "#6366f1" : "#e2e8f0",
            backgroundColor: precision === "unknown" ? "#f5f3ff" : "#ffffff",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <input
              type="radio"
              name="precision"
              checked={precision === "unknown"}
              onChange={() => handlePrecisionChange("unknown")}
              style={{ accentColor: "#6366f1", width: "18px", height: "18px", cursor: "pointer" }}
            />
            <div>
              <div style={{ fontWeight: 700, color: "#0f172a", fontSize: "0.95rem" }}>
                3. არ ვიცი (I don't know)
              </div>
              <div style={{ fontSize: "0.8rem", color: "#64748b" }}>
                დრო უცნობია — შეგიძლიათ გააგრძელოთ დროის გარეშე
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Time Input for Exact & Approximate */}
      {precision !== "unknown" && (
        <div style={{ marginTop: "0.5rem" }}>
          <Input
            label={precision === "exact" ? "დაბადების ზუსტი დრო *" : "დაბადების მიახლოებითი დრო *"}
            type="time"
            required
            value={birthTime}
            onChange={(e) => {
              setBirthTime(e.target.value);
              if (error) setError(null);
            }}
            helperText="24-საათიანი ფორმატი (მაგ. 18:30 ან 09:15)"
          />
        </div>
      )}

      {/* Informative banner for Unknown */}
      {precision === "unknown" && (
        <div
          style={{
            padding: "0.85rem",
            background: "#eff6ff",
            border: "1px solid #bfdbfe",
            borderRadius: "6px",
            fontSize: "0.825rem",
            color: "#1e40af",
            lineHeight: 1.5,
          }}
        >
          ℹ️ <strong>დრო არ არის სავალდებულო:</strong> თქვენი მზის, მთვარისა და სხვა პლანეტების ნიშნები
          დაითვლება სრული სიზუსტით. მხოლოდ ასცენდენტი (Rising Sign) და ასტროლოგიური სახლები დარჩება
          გამოუთვლელი, სანამ ზუსტ დროს არ მიუთითებთ.
        </div>
      )}

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
        >
          შემდეგი ➡️
        </Button>
      </div>
    </form>
  );
};
