import React from "react";
import { Button, Card } from "../../../shared/ui";
import { BirthTimePrecision } from "./BirthTimeStep";

interface ReviewStepProps {
  displayName: string;
  firstName?: string;
  lastName?: string;
  city: string;
  occupation: string;
  birthDate: string;
  birthTime: string;
  precision: BirthTimePrecision;
  placeLabel: string;
  onConfirm: () => void;
  onBack: () => void;
  onJumpToStep: (step: number) => void;
}

export const ReviewStep: React.FC<ReviewStepProps> = ({
  displayName,
  firstName,
  lastName,
  city,
  occupation,
  birthDate,
  birthTime,
  precision,
  placeLabel,
  onConfirm,
  onBack,
  onJumpToStep,
}) => {
  // Format date nicely: e.g. 1995-11-15 -> 15 November 1995
  const formatDateDisplay = (dStr: string) => {
    if (!dStr) return "";
    try {
      const parts = dStr.split("-");
      if (parts.length === 3) {
        const year = parts[0];
        const monthIndex = parseInt(parts[1], 10) - 1;
        const day = parseInt(parts[2], 10);
        const months = [
          "იანვარი", "თებერვალი", "მარტი", "აპრილი", "მაისი", "ივნისი",
          "ივლისი", "აგვისტო", "სექტემბერი", "ოქტომბერი", "ნოემბერი", "დეკემბერი"
        ];
        return `${day} ${months[monthIndex] || parts[1]} ${year} (${dStr})`;
      }
    } catch {
      // fallback to original
    }
    return dStr;
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      <div>
        <h3 style={{ margin: "0 0 0.4rem 0", fontSize: "1.25rem", fontWeight: 700, color: "#0f172a" }}>
          5. მონაცემების გადამოწმება (Review & Confirm)
        </h3>
        <p style={{ margin: 0, color: "#64748b", fontSize: "0.875rem" }}>
          გადაამოწმეთ შეყვანილი მონაცემები ასტროლოგიური რუკის გამოთვლამდე.
        </p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
        {/* Profile Info */}
        <Card variant="default" style={{ padding: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div>
              <div style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "#64748b", fontWeight: 600 }}>
                სახელი და პროფილი (Profile)
              </div>
              <div style={{ fontSize: "1.05rem", fontWeight: 700, color: "#0f172a", marginTop: "4px" }}>
                {displayName}
                {firstName && lastName ? ` (${firstName} ${lastName})` : ""}
              </div>
              {(city || occupation) && (
                <div style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "2px" }}>
                  {[city, occupation].filter(Boolean).join(" · ")}
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={() => onJumpToStep(1)}
              style={{
                background: "none",
                border: "none",
                color: "#6366f1",
                fontSize: "0.8rem",
                fontWeight: 600,
                cursor: "pointer",
                padding: "2px 6px",
              }}
            >
              რედაქტირება ✏️
            </button>
          </div>
        </Card>

        {/* Birth Date */}
        <Card variant="default" style={{ padding: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div>
              <div style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "#64748b", fontWeight: 600 }}>
                დაბადების თარიღი (Birth Date)
              </div>
              <div style={{ fontSize: "1.05rem", fontWeight: 700, color: "#0f172a", marginTop: "4px" }}>
                📅 {formatDateDisplay(birthDate)}
              </div>
            </div>
            <button
              type="button"
              onClick={() => onJumpToStep(2)}
              style={{
                background: "none",
                border: "none",
                color: "#6366f1",
                fontSize: "0.8rem",
                fontWeight: 600,
                cursor: "pointer",
                padding: "2px 6px",
              }}
            >
              რედაქტირება ✏️
            </button>
          </div>
        </Card>

        {/* Birth Time */}
        <Card variant="default" style={{ padding: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div>
              <div style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "#64748b", fontWeight: 600 }}>
                დაბადების დრო (Birth Time)
              </div>
              <div style={{ fontSize: "1.05rem", fontWeight: 700, color: "#0f172a", marginTop: "4px" }}>
                ⏰{" "}
                {precision === "unknown"
                  ? "Not known / უცნობია"
                  : `${birthTime} (${precision === "exact" ? "Exact / ზუსტი" : "Approximate / მიახლოებითი"})`}
              </div>
            </div>
            <button
              type="button"
              onClick={() => onJumpToStep(3)}
              style={{
                background: "none",
                border: "none",
                color: "#6366f1",
                fontSize: "0.8rem",
                fontWeight: 600,
                cursor: "pointer",
                padding: "2px 6px",
              }}
            >
              რედაქტირება ✏️
            </button>
          </div>
        </Card>

        {/* Birth Place */}
        <Card variant="default" style={{ padding: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div>
              <div style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "#64748b", fontWeight: 600 }}>
                დაბადების ადგილი (Birth Place)
              </div>
              <div style={{ fontSize: "1.05rem", fontWeight: 700, color: "#0f172a", marginTop: "4px" }}>
                📍 {placeLabel}
              </div>
            </div>
            <button
              type="button"
              onClick={() => onJumpToStep(4)}
              style={{
                background: "none",
                border: "none",
                color: "#6366f1",
                fontSize: "0.8rem",
                fontWeight: 600,
                cursor: "pointer",
                padding: "2px 6px",
              }}
            >
              რედაქტირება ✏️
            </button>
          </div>
        </Card>
      </div>

      <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem" }}>
        <Button
          type="button"
          variant="secondary"
          size="lg"
          style={{ flex: 1 }}
          onClick={onBack}
        >
          ⬅️ უკან (Back)
        </Button>
        <Button
          type="button"
          variant="brand"
          size="lg"
          style={{ flex: 2 }}
          onClick={onConfirm}
        >
          Looks right / Continue 🚀
        </Button>
      </div>
    </div>
  );
};
