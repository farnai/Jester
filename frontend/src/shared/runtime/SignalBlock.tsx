import React from "react";
import { Signal } from "../../core/api/types";
import { RuntimeInfoBlock } from "./RuntimeInfoBlock";

export interface SignalBlockProps {
  signals: Signal[];
  title?: string;
}

export const SignalBlock: React.FC<SignalBlockProps> = ({
  signals,
  title = "Active Relationship Signals (Synastry V1 Engine)",
}) => {
  if (!signals || signals.length === 0) {
    return (
      <RuntimeInfoBlock title={title} badge="0 Signals" badgeColor="#94a3b8">
        <div style={{ color: "#64748b", fontSize: "0.8rem", fontStyle: "italic" }}>
          No active synastry aspects meeting the orb threshold.
        </div>
      </RuntimeInfoBlock>
    );
  }

  return (
    <RuntimeInfoBlock
      title={title}
      badge={`${signals.length} Active`}
      badgeColor="#9333ea"
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginTop: "0.5rem" }}>
        {signals.map((sig, idx) => {
          const s = sig as any;
          const interpText = s.interpretation?.text || s.description || s.label;
          const assetId = s.interpretation?.content_asset_id || s.interpretation_id;
          return (
            <div
              key={idx}
              style={{
                backgroundColor: "#ffffff",
                border: "1px solid #e2e8f0",
                borderRadius: "6px",
                padding: "0.6rem 0.85rem",
                fontSize: "0.8rem",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem", flexWrap: "wrap", gap: "0.3rem" }}>
                <div style={{ fontWeight: 700, color: "#0f172a" }}>
                  <span style={{ color: "#6366f1", marginRight: "0.35rem" }}>#{idx + 1}</span>
                  {s.label || s.type}
                </div>
                <div style={{ display: "flex", gap: "0.35rem", alignItems: "center" }}>
                  <span style={{ fontSize: "0.7rem", padding: "0.1rem 0.4rem", borderRadius: "10px", backgroundColor: "#f1f5f9", color: "#475569" }}>
                    {s.category || "general"}
                  </span>
                  <span style={{ fontSize: "0.7rem", fontWeight: 700, padding: "0.1rem 0.4rem", borderRadius: "10px", backgroundColor: "#fef3c7", color: "#92400e" }}>
                    strength: {s.strength}
                  </span>
                </div>
              </div>

              {interpText && (
                <div style={{ color: "#334155", lineHeight: 1.5, margin: "0.25rem 0" }}>
                  {interpText}
                </div>
              )}

              <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", fontSize: "0.725rem", color: "#64748b", marginTop: "0.35rem", paddingTop: "0.35rem", borderTop: "1px dashed #f1f5f9" }}>
                {s.source_aspects && s.source_aspects.length > 0 && (
                  <div>
                    <strong>Aspects:</strong>{" "}
                    <code>{Array.isArray(s.source_aspects) ? s.source_aspects.join(", ") : String(s.source_aspects)}</code>
                  </div>
                )}
                {assetId && (
                  <div>
                    <strong>Asset ID:</strong> <code>{assetId}</code>
                  </div>
                )}
                {s.type && (
                  <div>
                    <strong>Signal Type:</strong> <code>{s.type}</code>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </RuntimeInfoBlock>
  );
};
