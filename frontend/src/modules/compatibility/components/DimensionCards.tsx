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
    accentColor: "#2563eb",
    barColor: "#3b82f6",
  },
  {
    key: "communication",
    title: "კომუნიკაცია & აზროვნება",
    icon: "💡",
    accentColor: "#4f46e5",
    barColor: "#6366f1",
  },
  {
    key: "attraction",
    title: "მიზიდულობა & ქიმია",
    icon: "🔥",
    accentColor: "#db2777",
    barColor: "#ec4899",
  },
  {
    key: "growth_long_term",
    title: "პიროვნული ზრდა",
    icon: "🌱",
    accentColor: "#059669",
    barColor: "#10b981",
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
            color: "#0f172a",
          }}
        >
          ურთიერთობის 4 განზომილება
        </h2>
        <p style={{ margin: 0, fontSize: "0.88rem", color: "#64748b" }}>
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
                backgroundColor: "#ffffff",
                border: "1px solid #f1f5f9",
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
                      color: "#1e293b",
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

                <div style={{ fontSize: "0.78rem", color: "#64748b", lineHeight: 1.4 }}>
                  {qualitative}
                </div>
              </div>

              {/* Progress bar */}
              <div
                style={{
                  height: "6px",
                  backgroundColor: "#f1f5f9",
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
