import React from "react";
import { Card, Badge } from "../../../shared/ui";
import { ResolvedInterpretationModel, Signal } from "../../../core/api/types";

interface RelationshipHighlightsProps {
  interpretation?: ResolvedInterpretationModel | null;
  signals?: Signal[];
}

const CATEGORY_MAP: Record<string, { label: string; icon: string; variant: "success" | "brand" | "score" | "default" | "warning" }> = {
  harmony: { label: "ემოციური ჰარმონია", icon: "✨", variant: "success" },
  attraction: { label: "მიზიდულობა & ქიმია", icon: "🔥", variant: "score" },
  communication: { label: "აზროვნება & დიალოგი", icon: "💬", variant: "brand" },
  growth: { label: "პიროვნული ზრდა", icon: "🌱", variant: "success" },
  stability: { label: "სტაბილურობა", icon: "🏛️", variant: "default" },
  notice: { label: "ურთიერთობის დინამიკა", icon: "⚡", variant: "warning" },
};

const STRENGTH_LABELS: Record<string, string> = {
  high: "მთავარი ძალა",
  medium: "გამოხატული",
  low: "ნატიფი დინამიკა",
};

export const RelationshipHighlights: React.FC<RelationshipHighlightsProps> = ({
  interpretation,
  signals = [],
}) => {
  // Select the strongest 2-3 dynamics that have human interpretations
  const highlightedSignals = signals
    .filter((s) => s.interpretation?.text || s.label)
    .slice(0, 3);

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
          რა გამოირჩევა თქვენ შორის?
        </h2>
        <p style={{ margin: 0, fontSize: "0.88rem", color: "#64748b" }}>
          ურთიერთობის ძირითადი მახასიათებლები და ინტუიციური დინამიკა.
        </p>
      </div>

      {/* Primary Relational Narrative */}
      {interpretation?.text && (
        <Card padded style={{ backgroundColor: "#ffffff", border: "1px solid #e2e8f0" }}>
          {interpretation.title && (
            <div
              style={{
                fontSize: "1.05rem",
                fontWeight: 700,
                color: "#1e293b",
                marginBottom: "0.5rem",
              }}
            >
              {interpretation.title}
            </div>
          )}
          <p
            style={{
              margin: 0,
              fontSize: "0.95rem",
              color: "#334155",
              lineHeight: 1.6,
            }}
          >
            {interpretation.text}
          </p>
        </Card>
      )}

      {/* 2-3 Key Interpreted Dynamics */}
      {highlightedSignals.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {highlightedSignals.map((sig, idx) => {
            const cat = CATEGORY_MAP[sig.category] || {
              label: "დინამიკა",
              icon: "✨",
              variant: "default",
            };
            const title = sig.interpretation?.title || sig.label || "კავშირის წერტილი";
            const text = sig.interpretation?.text || null;
            const strengthLabel = STRENGTH_LABELS[sig.strength] || null;

            return (
              <Card
                key={idx}
                padded
                style={{
                  backgroundColor: "#ffffff",
                  border: "1px solid #f1f5f9",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.02)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "0.5rem",
                    marginBottom: "0.4rem",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                    <Badge variant={cat.variant} size="sm">
                      {cat.icon} {cat.label}
                    </Badge>
                    {strengthLabel && (
                      <span style={{ fontSize: "0.75rem", color: "#94a3b8", fontWeight: 500 }}>
                        • {strengthLabel}
                      </span>
                    )}
                  </div>
                </div>

                <div
                  style={{
                    fontSize: "0.98rem",
                    fontWeight: 600,
                    color: "#0f172a",
                    marginBottom: text ? "0.35rem" : 0,
                  }}
                >
                  {title}
                </div>

                {text && (
                  <p
                    style={{
                      margin: 0,
                      fontSize: "0.9rem",
                      color: "#475569",
                      lineHeight: 1.55,
                    }}
                  >
                    {text}
                  </p>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
