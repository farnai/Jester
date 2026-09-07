import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "../core/auth/useAuth";

export const DebugBar: React.FC = () => {
  const { user, session } = useAuth();
  const location = useLocation();
  const [isExpanded, setIsExpanded] = useState(false);

  // Hidden entirely in production builds per AGENTS.md and Phase 2 requirements
  if (!session || !import.meta.env.DEV) return null;

  if (!isExpanded) {
    return (
      <div
        onClick={() => setIsExpanded(true)}
        style={{
          position: "fixed",
          bottom: "4px",
          right: "4px",
          backgroundColor: "#1e293b",
          color: "#94a3b8",
          padding: "0.25rem 0.5rem",
          borderRadius: "4px",
          fontSize: "0.7rem",
          cursor: "pointer",
          zIndex: 999,
          opacity: 0.65,
          fontFamily: "monospace",
        }}
        title="Open Developer Debug Bar"
      >
        🛠️ DEV DEBUG
      </div>
    );
  }

  return (
    <footer
      style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: "#0f172a",
        color: "#cbd5e1",
        borderTop: "1px solid #334155",
        padding: "0.5rem 1rem",
        fontSize: "0.775rem",
        display: "flex",
        flexWrap: "wrap",
        gap: "1rem",
        justifyContent: "space-between",
        alignItems: "center",
        zIndex: 999,
        fontFamily: "monospace",
      }}
    >
      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        <div>
          <span style={{ color: "#94a3b8" }}>Route:</span> <code>{location.pathname}</code>
        </div>
        <div>
          <span style={{ color: "#94a3b8" }}>User:</span> <code>{user?.id ? `${user.id.slice(0, 8)}...` : "None"}</code>
        </div>
        <div>
          <span style={{ color: "#94a3b8" }}>Engine:</span> <code>synastry-v1.0.0</code>
        </div>
      </div>

      <button
        onClick={() => setIsExpanded(false)}
        style={{
          background: "transparent",
          border: "1px solid #475569",
          color: "#94a3b8",
          borderRadius: "4px",
          padding: "0.15rem 0.4rem",
          fontSize: "0.7rem",
          cursor: "pointer",
        }}
      >
        ✕ Close
      </button>
    </footer>
  );
};
