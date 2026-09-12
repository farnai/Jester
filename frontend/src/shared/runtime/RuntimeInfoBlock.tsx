import React from "react";

export interface InfoItem {
  label: string;
  value: React.ReactNode;
  monospace?: boolean;
}

export interface RuntimeInfoBlockProps {
  title: string;
  badge?: string;
  badgeColor?: string;
  items?: InfoItem[];
  children?: React.ReactNode;
  style?: React.CSSProperties;
}

export const RuntimeInfoBlock: React.FC<RuntimeInfoBlockProps> = ({
  title,
  badge,
  badgeColor = "#6366f1",
  items,
  children,
  style,
}) => {
  return (
    <div
      style={{
        border: "1px solid #e2e8f0",
        borderRadius: "8px",
        backgroundColor: "#f8fafc",
        padding: "0.85rem 1rem",
        fontSize: "0.85rem",
        ...style,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "0.5rem",
        }}
      >
        <div style={{ fontWeight: 700, color: "#1e293b", display: "flex", alignItems: "center", gap: "0.4rem" }}>
          <span>⚙️</span>
          <span>{title}</span>
        </div>
        {badge && (
          <span
            style={{
              fontSize: "0.7rem",
              fontWeight: 700,
              padding: "0.15rem 0.5rem",
              borderRadius: "10px",
              backgroundColor: `${badgeColor}15`,
              color: badgeColor,
              border: `1px solid ${badgeColor}35`,
            }}
          >
            {badge}
          </span>
        )}
      </div>

      {items && items.length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.4rem 0.8rem", marginBottom: children ? "0.5rem" : 0 }}>
          {items.map((item, idx) => (
            <div key={idx} style={{ display: "flex", gap: "0.4rem", alignItems: "baseline" }}>
              <span style={{ color: "#64748b", fontSize: "0.75rem", flexShrink: 0 }}>{item.label}:</span>
              <span
                style={{
                  color: "#0f172a",
                  fontWeight: 600,
                  fontSize: item.monospace ? "0.75rem" : "0.825rem",
                  fontFamily: item.monospace ? "ui-monospace, monospace" : "inherit",
                  wordBreak: "break-all",
                }}
              >
                {item.value}
              </span>
            </div>
          ))}
        </div>
      )}

      {children}
    </div>
  );
};
