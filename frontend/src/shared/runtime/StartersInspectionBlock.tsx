import React from "react";
import { ConversationStarterDetail } from "../../core/api/types";
import { RuntimeInfoBlock } from "./RuntimeInfoBlock";

export interface StartersInspectionBlockProps {
  starters: string[];
  starterDetails?: ConversationStarterDetail[];
  onSelectStarter?: (text: string) => void;
  title?: string;
}

export const StartersInspectionBlock: React.FC<StartersInspectionBlockProps> = ({
  starters,
  starterDetails = [],
  onSelectStarter,
  title = "Conversation Starters (Relationship Intelligence)",
}) => {
  if ((!starters || starters.length === 0) && starterDetails.length === 0) {
    return null;
  }

  // Combine details or fallback to plain string array
  const items = starterDetails.length > 0
    ? starterDetails
    : starters.map((txt) => ({
        text: txt,
        contract_id: "chat.starter.active_signal",
        category: "relationship",
        source_signal: "synastry_aspect",
        asset_id: "batch_7_chat",
        selection_mode: "deterministic_seed",
      }));

  return (
    <RuntimeInfoBlock
      title={title}
      badge={`${items.length} Curated`}
      badgeColor="#2563eb"
      style={{ marginBottom: "1rem" }}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginTop: "0.5rem" }}>
        {items.map((item, idx) => (
          <div
            key={idx}
            onClick={() => onSelectStarter && onSelectStarter(item.text)}
            style={{
              padding: "0.6rem 0.85rem",
              backgroundColor: "#ffffff",
              border: "1px solid #bfdbfe",
              borderRadius: "8px",
              cursor: onSelectStarter ? "pointer" : "default",
              transition: "border-color 0.15s, background-color 0.15s",
            }}
            title={onSelectStarter ? "Click to use this starter in chat" : undefined}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem", marginBottom: "0.3rem" }}>
              <div style={{ fontSize: "0.875rem", color: "#1e3a8a", fontWeight: 600 }}>
                "{item.text}"
              </div>
              {onSelectStarter && (
                <button
                  type="button"
                  style={{
                    padding: "0.15rem 0.45rem",
                    fontSize: "0.7rem",
                    backgroundColor: "#eff6ff",
                    color: "#1d4ed8",
                    border: "1px solid #93c5fd",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontWeight: 700,
                    flexShrink: 0,
                  }}
                >
                  გამოყენება →
                </button>
              )}
            </div>

            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem", fontSize: "0.7rem", color: "#64748b", borderTop: "1px dashed #e2e8f0", paddingTop: "0.3rem" }}>
              <div>
                <strong>Contract:</strong> <code>{item.contract_id}</code>
              </div>
              <div>
                <strong>Category:</strong> <span style={{ color: "#0284c7", fontWeight: 600 }}>{item.category}</span>
              </div>
              <div>
                <strong>Source Signal:</strong> <code>{item.source_signal}</code>
              </div>
              {item.asset_id && (
                <div>
                  <strong>Asset:</strong> <code>{item.asset_id}</code>
                </div>
              )}
              {item.selection_mode && (
                <div>
                  <strong>Selection:</strong> <span>{item.selection_mode}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </RuntimeInfoBlock>
  );
};
