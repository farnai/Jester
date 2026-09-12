import React from "react";
import { DailyEnergyResponse } from "../../core/api/types";
import { RuntimeInfoBlock } from "./RuntimeInfoBlock";
import { RuntimeJson } from "./RuntimeJson";

export interface TransitEvidenceBlockProps {
  daily: DailyEnergyResponse;
}

export const TransitEvidenceBlock: React.FC<TransitEvidenceBlockProps> = ({ daily }) => {
  const primary = daily.primary_transit;
  const supporting = daily.supporting_transits || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginTop: "1rem" }}>
      {/* 1. Energy Evidence / Debug Summary */}
      <RuntimeInfoBlock
        title="Energy Evidence & Archetype Mapping"
        badge={daily.detection_mode || (primary ? "real_transit" : "fallback")}
        badgeColor="#9333ea"
        items={[
          {
            label: "Detected Primary",
            value: primary ? `${primary.transit_planet} ${primary.aspect_type} natal ${primary.natal_point}` : "None (Quiet Sky)",
            monospace: true,
          },
          {
            label: "Primary Archetype",
            value: daily.energy_type || daily.archetype || "neutral",
            monospace: true,
          },
          {
            label: "Interpretation Asset",
            value: daily.interpretation?.content_asset_id || daily.interpretation?.id || "N/A",
            monospace: true,
          },
          {
            label: "DO/DON'T Source",
            value: `daily_energy_tags[${daily.energy_type || "neutral"}]`,
            monospace: true,
          },
          {
            label: "Detection Mode",
            value: daily.detection_mode || (primary ? "real_transit" : "neutral_baseline"),
            monospace: true,
          },
          {
            label: "Date / Version",
            value: `${daily.date || "today"} (Data v1)`,
            monospace: true,
          },
        ]}
      />

      {/* 2. Primary Transit Deep Signal */}
      {primary && (
        <RuntimeInfoBlock
          title={`Primary Transit: ${primary.context_label_ka}`}
          badge={`Score: ${primary.ranking_score?.toFixed(1) ?? "N/A"}`}
          badgeColor="#059669"
          items={[
            { label: "Transit Body", value: primary.transit_planet },
            { label: "Natal Body", value: primary.natal_point },
            { label: "Aspect", value: primary.aspect_type },
            { label: "Orb Difference", value: `${primary.orb_diff}° (max: ${primary.max_orb}°)` },
            { label: "Motion", value: primary.is_applying ? "Applying (უახლოვდება)" : "Separating (შორდება)" },
            { label: "Aspect Strength", value: `${Math.round(primary.aspect_strength * 100)}%` },
            { label: "Ranking Score", value: primary.ranking_score?.toFixed(2) || "N/A", monospace: true },
            { label: "Retrograde", value: primary.transit_retrograde ? "Yes (რეტროგრადული)" : "Direct (პირდაპირი)" },
          ]}
        />
      )}

      {/* 3. Supporting Transits */}
      {supporting.length > 0 && (
        <RuntimeInfoBlock
          title={`Supporting Transits (${supporting.length} Active)`}
          badge="Secondary Influences"
          badgeColor="#3b82f6"
        >
          <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", marginTop: "0.4rem" }}>
            {supporting.map((t, idx) => (
              <div
                key={idx}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "0.35rem 0.6rem",
                  backgroundColor: "#ffffff",
                  borderRadius: "6px",
                  border: "1px solid #e2e8f0",
                  fontSize: "0.775rem",
                }}
              >
                <div>
                  <strong style={{ color: "#1e293b" }}>{t.context_label_ka}</strong>
                  <span style={{ color: "#64748b", marginLeft: "0.4rem" }}>
                    ({t.transit_planet} {t.aspect_type} {t.natal_point})
                  </span>
                </div>
                <div style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}>
                  <span style={{ color: "#059669", fontWeight: 600 }}>orb: {t.orb_diff}°</span>
                  <span style={{ color: "#6366f1", fontSize: "0.7rem", padding: "0.1rem 0.35rem", backgroundColor: "#e0e7ff", borderRadius: "4px" }}>
                    {t.archetype_id}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </RuntimeInfoBlock>
      )}

      <RuntimeJson data={daily} label="Daily Energy Raw API Payload" />
    </div>
  );
};
