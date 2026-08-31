import React from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "../core/auth/useAuth";

export const DebugBar: React.FC = () => {
  const { user, session } = useAuth();
  const location = useLocation();

  if (!session) return null;

  return (
    <footer
      style={{
        marginTop: "3rem",
        padding: "0.75rem 1rem",
        backgroundColor: "#f0f2f5",
        borderTop: "1px solid #d9d9d9",
        fontSize: "0.8rem",
        color: "#595959",
        display: "flex",
        flexWrap: "wrap",
        gap: "1.5rem",
        justifyContent: "space-between",
      }}
    >
      <div>
        <strong>Debug Info:</strong> Route: <code>{location.pathname}</code> | User ID:{" "}
        <code>{user?.id || "None"}</code>
      </div>
      <div>
        Engine: <code>synastry-v1.0.0</code> | Environment:{" "}
        <code>development</code>
      </div>
    </footer>
  );
};
