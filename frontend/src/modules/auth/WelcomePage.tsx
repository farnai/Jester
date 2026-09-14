import React from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../../core/auth/useAuth";
import { Card, Button } from "../../shared/ui";

export const WelcomePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, hasBirthData, isLoading } = useAuth();

  // If user is already logged in, route to appropriate surface
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
        <div style={{ fontSize: "2.8rem", marginBottom: "0.5rem" }}>🃏</div>

        <h1
          style={{
            margin: "0 0 0.5rem 0",
            fontSize: "1.75rem",
            fontWeight: 800,
            color: "#0f172a",
            letterSpacing: "-0.025em",
          }}
        >
          JESTER
        </h1>

        <p
          style={{
            margin: "0 0 2rem 0",
            color: "#64748b",
            fontSize: "0.95rem",
            lineHeight: 1.5,
          }}
        >
          აღმოაჩინეთ ადამიანები და გაიგეთ ურთიერთობების სიღრმისეული დინამიკა
          ასტროლოგიური ინტელექტის დახმარებით.
        </p>

        <div>
          <Button
            variant="brand"
            size="lg"
            fullWidth
            onClick={() => navigate("/auth/choice")}
          >
            Get started / დაწყება
          </Button>
        </div>
      </Card>
    </div>
  );
};
