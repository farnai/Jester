import React from "react";

export interface RuntimeJsonProps {
  data: any;
  label?: string;
  defaultOpen?: boolean;
}

export const RuntimeJson: React.FC<RuntimeJsonProps> = ({
  data,
  label = "Runtime Data (Raw JSON)",
  defaultOpen = false,
}) => {
  if (data === undefined || data === null) return null;

  return (
    <details
      open={defaultOpen}
      style={{
        marginTop: "0.75rem",
        fontSize: "0.8rem",
        color: "#64748b",
        borderTop: "1px dashed #e2e8f0",
        paddingTop: "0.5rem",
      }}
    >
      <summary style={{ cursor: "pointer", fontWeight: 600, userSelect: "none" }}>
        🔍 {label}
      </summary>
      <pre
        style={{
          marginTop: "0.5rem",
          background: "#0f172a",
          color: "#f8fafc",
          padding: "0.75rem",
          borderRadius: "6px",
          overflowX: "auto",
          fontSize: "0.75rem",
          lineHeight: 1.4,
          maxHeight: "320px",
        }}
      >
        {JSON.stringify(data, null, 2)}
      </pre>
    </details>
  );
};
