import React, { useState } from "react";
import { API } from "../../../core/api/endpoints";
import { Button, Card } from "../../../shared/ui";

interface FinishStepProps {
  firstName: string;
  lastName: string;
  displayName: string;
  birthDate: string;
  birthTime: string;
  precision: string;
  birthCityLabel: string;
  currentCityLabel: string;
  interestsCount: number;
  avatarUrl: string | null;
  onSuccess: () => void;
  onBack: () => void;
  onJumpToStep: (step: number) => void;
}

export const FinishStep: React.FC<FinishStepProps> = ({
  firstName,
  lastName,
  displayName,
  birthDate,
  birthTime,
  precision,
  birthCityLabel,
  currentCityLabel,
  interestsCount,
  avatarUrl,
  onSuccess,
  onBack,
  onJumpToStep,
}) => {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleComplete = async () => {
    setSubmitting(true);
    setError(null);

    try {
      // Authoritative backend validation and completion
      await API.profiles.completeOnboarding();
      onSuccess();
    } catch (err: any) {
      console.error("Completion error:", err);
      const msg = err.message || "ონბორდინგის დასრულება ვერ მოხერხდა.";
      setError(msg);

      // Determine if a specific step is missing and can jump to it
      if (msg.includes("first_name") || msg.includes("last_name")) {
        onJumpToStep(1);
      } else if (msg.includes("birth_date")) {
        onJumpToStep(2);
      } else if (msg.includes("birth_city_id")) {
        onJumpToStep(4);
      } else if (msg.includes("current_city_id")) {
        onJumpToStep(5);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const formattedTime =
    precision === "unknown" || !birthTime ? "უცნობია (Unknown)" : `${birthTime} (${precision === "exact" ? "ზუსტი" : "მიახლოებითი"})`;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      <div>
        <h3 style={{ margin: "0 0 0.4rem 0", fontSize: "1.25rem", fontWeight: 700, color: "#0f172a" }}>
          8. გადამოწმება და დასრულება (Finish)
        </h3>
        <p style={{ margin: "0 0 1rem 0", color: "#64748b", fontSize: "0.875rem" }}>
          შეამოწმეთ შეყვანილი მონაცემები JESTER-ში შესვლამდე:
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

      {/* Summary Review Card */}
      <Card variant="bordered" style={{ padding: "1.25rem", display: "flex", flexDirection: "column", gap: "0.85rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ color: "#64748b", fontSize: "0.85rem" }}>სახელი / გვარი:</span>
          <span style={{ fontWeight: 600, color: "#0f172a" }}>
            {firstName} {lastName} {displayName ? `(${displayName})` : ""}
          </span>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ color: "#64748b", fontSize: "0.85rem" }}>დაბადების თარიღი:</span>
          <span style={{ fontWeight: 600, color: "#0f172a" }}>{birthDate || "—"}</span>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ color: "#64748b", fontSize: "0.85rem" }}>დაბადების დრო:</span>
          <span style={{ fontWeight: 600, color: "#0f172a" }}>{formattedTime}</span>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ color: "#64748b", fontSize: "0.85rem" }}>დაბადების ადგილი:</span>
          <span style={{ fontWeight: 600, color: "#0f172a", textAlign: "right", maxWidth: "60%" }}>
            {birthCityLabel || "—"}
          </span>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ color: "#64748b", fontSize: "0.85rem" }}>საცხოვრებელი ქალაქი:</span>
          <span style={{ fontWeight: 600, color: "#0f172a", textAlign: "right", maxWidth: "60%" }}>
            {currentCityLabel || "—"}
          </span>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ color: "#64748b", fontSize: "0.85rem" }}>ინტერესები:</span>
          <span style={{ fontWeight: 600, color: "#0f172a" }}>
            {interestsCount > 0 ? `${interestsCount} არჩეული` : "გამოტოვებული"}
          </span>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ color: "#64748b", fontSize: "0.85rem" }}>პროფილის ფოტო:</span>
          <span style={{ fontWeight: 600, color: "#0f172a" }}>
            {avatarUrl ? "ატვირთულია ✓" : "არ არის არჩეული"}
          </span>
        </div>
      </Card>

      <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem" }}>
        <Button
          type="button"
          variant="secondary"
          size="lg"
          style={{ flex: 1 }}
          onClick={onBack}
          disabled={submitting}
        >
          ⬅️ უკან
        </Button>
        <Button
          type="button"
          variant="brand"
          size="lg"
          style={{ flex: 2 }}
          onClick={handleComplete}
          disabled={submitting}
        >
          {submitting ? "დასრულება..." : "დასრულება და შესვლა 🚀"}
        </Button>
      </div>
    </div>
  );
};
