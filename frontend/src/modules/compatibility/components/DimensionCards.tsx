import React from "react";
import { Card } from "../../../shared/ui";
import { Dimensions } from "../../../core/api/types";

interface DimensionCardsProps {
  dimensions?: Dimensions | null;
}

interface DimensionConfig {
  key: keyof Dimensions;
  title: string;
  icon: string;
  accentColor: string;
  barColor: string;
}

const DIMENSIONS_CONFIG: DimensionConfig[] = [
  {
    key: "emotional_harmony",
    title: "ემოციური კავშირი",
    icon: "🌊",
    accentColor: "var(--jester-brand-orange-800)",
    barColor: "var(--jester-brand-orange-500)",
  },
  {
    key: "communication",
    title: "კომუნიკაცია & აზროვნება",
    icon: "💡",
    accentColor: "var(--jester-brand-orange-800)",
    barColor: "var(--jester-brand-orange-500)",
  },
  {
    key: "attraction",
    title: "მიზიდულობა & ქიმია",
    icon: "🔥",
    accentColor: "var(--jester-brand-orange-800)",
    barColor: "var(--jester-brand-orange-500)",
  },
  {
    key: "growth_long_term",
    title: "პიროვნული ზრდა",
    icon: "🌱",
    accentColor: "var(--jester-support-sage-ink)",
    barColor: "var(--jester-support-sage-500)",
  },
];

const getQualitativeDescription = (value: number): string => {
  if (value >= 80) return "ბუნებრივი და ძლიერი თანხვედრა";
  if (value >= 65) return "კარგი ბალანსი და ურთიერთგაგება";
  if (value >= 50) return "საინტერესო დინამიკური განსხვავებები";
  return "ინდივიდუალური მიდგომები და განსხვავებული ტემპი";
};

export const DimensionCards: React.FC<DimensionCardsProps> = ({ dimensions }) => {
  if (!dimensions || Object.keys(dimensions).length === 0) {
    return null;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h2
          style={{
            margin: "0 0 0.25rem 0",
            fontSize: "1.15rem",
            fontWeight: 700,
            color: "var(--jester-text-primary)",
          }}
        >
          ურთიერთობის 4 განზომილება
        </h2>
        <p style={{ margin: 0, fontSize: "0.88rem", color: "var(--jester-text-secondary)" }}>
          სინასტრიული ბალანსი ოთხ ძირითად მიმართულებაში.
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "0.85rem",
        }}
      >
        {DIMENSIONS_CONFIG.map((dim) => {
          const value = dimensions[dim.key] ?? 50;
          const rounded = Math.round(value);
          const qualitative = getQualitativeDescription(value);

          return (
            <Card
              key={dim.key}
              padded
              style={{
                backgroundColor: "var(--jester-surface-card)",
                border: "1px solid var(--jester-border-soft)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                gap: "0.75rem",
              }}
            >
              {/* Header with icon, title, and score */}
              <div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "0.25rem",
                  }}
                >
                  <span
                    style={{
                      fontSize: "0.92rem",
                      fontWeight: 600,
                      color: "var(--jester-text-primary)",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.35rem",
                    }}
                  >
                    <span>{dim.icon}</span> {dim.title}
                  </span>
                  <span
                    style={{
                      fontSize: "0.95rem",
                      fontWeight: 700,
                      color: dim.accentColor,
                    }}
                  >
                    {rounded}%
                  </span>
                </div>

                <div style={{ fontSize: "0.78rem", color: "var(--jester-text-secondary)", lineHeight: 1.4 }}>
                  {qualitative}
                </div>
              </div>

              {/* Progress bar */}
              <div
                style={{
                  height: "6px",
                  backgroundColor: "var(--jester-surface-alt)",
                  borderRadius: "9999px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${Math.min(100, Math.max(0, rounded))}%`,
                    backgroundColor: dim.barColor,
                    borderRadius: "9999px",
                    transition: "width 0.4s ease",
                  }}
                />
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
