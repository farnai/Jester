import React, { useEffect, useState } from "react";
import { Navigate, Link } from "react-router-dom";
import { useAuth } from "../../core/auth/useAuth";
import { LoadingState } from "../../shared/StatusState";
import { Card } from "../../shared/ui";

export const AuthCallbackPage: React.FC = () => {
  const { user, isLoading, onboardingCompleted, profileError } = useAuth();
  const [linkError] = useState(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    const query = new URLSearchParams(window.location.search);
    return params.get("error_description") || query.get("error_description");
  });
  const [timedOut, setTimedOut] = useState(false);
  useEffect(() => {
    const timer = window.setTimeout(() => setTimedOut(true), 15000);
    return () => window.clearTimeout(timer);
  }, []);
  const error = linkError || profileError || ((!isLoading && !user) || timedOut ? "დადასტურების ბმული არასწორია ან ვადაგასულია. მოითხოვეთ ახალი წერილი." : null);
  if (!error && !isLoading && user) return <Navigate to={onboardingCompleted ? "/" : "/onboarding"} replace />;

  if (error) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "80vh",
          padding: "1.5rem",
        }}
      >
        <Card variant="elevated" style={{ maxWidth: "440px", textAlign: "center", padding: "2rem" }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>⚠️</div>
          <h3 style={{ margin: "0 0 0.5rem 0", color: "#dc2626" }}>ავტორიზაციის შეცდომა</h3>
          <p style={{ color: "#64748b", fontSize: "0.9rem", marginBottom: "1.5rem" }}>{error}</p>
          <p><Link to="/auth/verify-email">დადასტურების წერილის ხელახლა გაგზავნა</Link></p>
          <Link
            to="/auth/login"
            style={{
              display: "inline-block",
              padding: "0.6rem 1.2rem",
              background: "#6366f1",
              color: "#fff",
              borderRadius: "6px",
              textDecoration: "none",
              fontWeight: 600,
            }}
          >
            შესვლის გვერდზე დაბრუნება
          </Link>
        </Card>
      </div>
    );
  }

  return <LoadingState message="ავტორიზაციის დამუშავება... / Processing authentication..." />;
};
