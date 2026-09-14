import React, { useState } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../../core/auth/useAuth";
import { Card, Button } from "../../shared/ui";
import { SocialAuthButtons } from "./SocialAuthButtons";

export const AuthChoicePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, onboardingCompleted, isLoading } = useAuth();
  const [error, setError] = useState<string | null>(null);

  if (!isLoading && user) {
    if (onboardingCompleted) {
      return <Navigate to="/me" replace />;
    }
    return <Navigate to="/onboarding" replace />;
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
            margin: "0 0 1.5rem 0",
            color: "#64748b",
            fontSize: "0.9rem",
            lineHeight: 1.5,
          }}
        >
          აირჩიეთ ახალი ანგარიშის შექმნა ან არსებულში შესვლა:
        </p>

        {error && (
          <div
            style={{
              padding: "0.75rem",
              marginBottom: "1.2rem",
              background: "#fff1f0",
              border: "1px solid #ff4d4f",
              borderRadius: "6px",
              color: "#cf1322",
              fontSize: "0.85rem",
            }}
          >
            ⚠️ {error}
          </div>
        )}

        <div style={{ marginBottom: "1.2rem" }}>
          <SocialAuthButtons onError={(err) => setError(err)} />
        </div>

        <div style={{ display: "flex", alignItems: "center", margin: "1.2rem 0", color: "#94a3b8" }}>
          <div style={{ flex: 1, height: "1px", background: "#e2e8f0" }} />
          <span style={{ padding: "0 0.75rem", fontSize: "0.8rem", textTransform: "uppercase" }}>ან ელფოსტით</span>
          <div style={{ flex: 1, height: "1px", background: "#e2e8f0" }} />
        </div>

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
