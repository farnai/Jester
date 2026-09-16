import React, { useEffect, useState } from "react";
import { API } from "../../../core/api/endpoints";
import { InterestItem } from "../../../core/api/types";
import { Button } from "../../../shared/ui";
import { LoadingState } from "../../../shared/StatusState";

interface InterestsStepProps {
  selectedIds: string[];
  onNext: (selected: string[]) => void;
  onSkip: () => void;
  onBack: () => void;
}

export const InterestsStep: React.FC<InterestsStepProps> = ({
  selectedIds,
  onNext,
  onSkip,
  onBack,
}) => {
  const [interests, setInterests] = useState<InterestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Set<string>>(new Set(selectedIds));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    API.interests
      .list()
      .then((res) => {
        if (isMounted) {
          setInterests(res.items);
        }
      })
      .catch((err) => {
        console.error("Failed to load interests:", err);
        if (isMounted) {
          setError("ინტერესების ჩატვირთვა ვერ მოხერხდა.");
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const toggleInterest = (id: string) => {
    setError(null);
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleContinue = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const count = selected.size;
    if (count === 0) {
      // Zero selected with continue: user can skip or choose
      onSkip();
      return;
    }
    if (count < 3) {
      setError("გთხოვთ აირჩიოთ მინიმუმ 3 ინტერესი, ან დააჭირეთ 'გამოტოვებას' (Must select at least 3 interests or skip).");
      return;
    }

    onNext(Array.from(selected));
  };

  if (loading) {
    return <LoadingState message="ინტერესების სიის ჩატვირთვა..." />;
  }

  const count = selected.size;

  return (
    <form onSubmit={handleContinue} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h3 style={{ margin: "0 0 0.4rem 0", fontSize: "1.2rem", fontWeight: 700, color: "#0f172a" }}>
          6. თქვენი ინტერესები (Interests)
        </h3>
        <p style={{ margin: "0 0 1.25rem 0", color: "#64748b", fontSize: "0.875rem" }}>
          აირჩიეთ მინიმუმ 3 ინტერესი, რათა აღმოაჩინოთ საერთო თემები სხვა ადამიანებთან (არასავალდებულო, შეგიძლიათ გამოტოვოთ).
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

      {/* Selected count badge */}
      <div style={{ fontSize: "0.85rem", color: count >= 3 ? "#16a34a" : "#64748b", fontWeight: 600 }}>
        არჩეულია: {count} {count < 3 && count > 0 && "(საჭიროა კიდევ " + (3 - count) + ")"}
      </div>

      {/* Pill grid of candidate interests */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "0.5rem",
          maxHeight: "280px",
          overflowY: "auto",
          padding: "0.5rem",
          border: "1px solid #e2e8f0",
          borderRadius: "8px",
        }}
      >
        {interests.map((item) => {
          const isSelected = selected.has(item.id);
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => toggleInterest(item.id)}
              style={{
                padding: "0.5rem 0.85rem",
                borderRadius: "20px",
                border: isSelected ? "1px solid #6366f1" : "1px solid #cbd5e1",
                backgroundColor: isSelected ? "#e0e7ff" : "#f8fafc",
                color: isSelected ? "#3730a3" : "#334155",
                fontSize: "0.85rem",
                fontWeight: isSelected ? 600 : 400,
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
            >
              {isSelected ? "✓ " : "+ "}
              {item.name}
            </button>
          );
        })}
      </div>

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
          type="button"
          variant="ghost"
          size="lg"
          style={{ flex: 1 }}
          onClick={onSkip}
        >
          გამოტოვება (Skip)
        </Button>
        <Button
          type="submit"
          variant="brand"
          size="lg"
          style={{ flex: 1.5 }}
          disabled={count > 0 && count < 3}
        >
          შემდეგი ➡️
        </Button>
      </div>
    </form>
  );
};
