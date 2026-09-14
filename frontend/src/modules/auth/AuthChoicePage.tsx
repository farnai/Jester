import React from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../../core/auth/useAuth";
import { Card, Button } from "../../shared/ui";

export const AuthChoicePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, hasBirthData, isLoading } = useAuth();

  if (!isLoading && user) {
    if (hasBirthData === true) {
      return <Navigate to="/" replace />;
    }
    if (hasBirthData === false) {
      return <Navigate to="/onboarding/birth-data" replace />;
    }
  }

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "85vh",
        padding: "1.5rem",
        boxSizing: "border-box",
      }}
    >
      <Card
        variant="elevated"
        style={{
          width: "100%",
          maxWidth: "460px",
          textAlign: "center",
          padding: "2.5rem 2rem",
        }}
      >
        <div style={{ fontSize: "2.2rem", marginBottom: "0.5rem" }}>✨</div>

        <h2
          style={{
            margin: "0 0 0.5rem 0",
            fontSize: "1.45rem",
            fontWeight: 800,
            color: "#0f172a",
          }}
        >
          შემოუერთდით JESTER-ს
        </h2>

        <p
          style={{
            margin: "0 0 2rem 0",
            color: "#64748b",
            fontSize: "0.9rem",
            lineHeight: 1.5,
          }}
        >
          აირჩიეთ ახალი ანგარიშის შექმნა ან არსებულში შესვლა:
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <Button
            variant="brand"
            size="lg"
            fullWidth
            onClick={() => navigate("/auth/register")}
          >
            Create account / ანგარიშის შექმნა
          </Button>

          <Button
            variant="secondary"
            size="lg"
            fullWidth
            onClick={() => navigate("/auth/login")}
          >
            Log in / სისტემაში შესვლა
          </Button>

          <div style={{ marginTop: "1rem" }}>
            <button
              type="button"
              onClick={() => navigate("/welcome")}
              style={{
                background: "none",
                border: "none",
                color: "#64748b",
                fontSize: "0.85rem",
                cursor: "pointer",
                padding: "0.4rem",
              }}
            >
              ⬅️ უკან დაბრუნება (Back)
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
};
