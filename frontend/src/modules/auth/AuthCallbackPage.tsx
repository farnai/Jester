import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { supabase } from "../../core/realtime/supabase";
import { API } from "../../core/api/endpoints";
import { useAuth } from "../../core/auth/useAuth";
import { LoadingState } from "../../shared/StatusState";
import { Card } from "../../shared/ui";

export const AuthCallbackPage: React.FC = () => {
  const navigate = useNavigate();
  const { refreshProfile } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // 1. Get authenticated session
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        if (sessionError || !session) {
          // Wait briefly in case session exchange is pending
          const { data: authListener } = supabase.auth.onAuthStateChange(async (_event, newSession) => {
            if (newSession) {
              authListener.subscription.unsubscribe();
              await processSession();
            }
          });
          return;
        }

        await processSession();
      } catch (err: any) {
        setError(err?.message || "ავტორიზაციის დამუშავებისას დაფიქსირდა შეცდომა.");
      }
    };

    const processSession = async () => {
      try {
        // 2. Explicitly initialize/verify profile via backend API
        const profile = await API.profiles.initializeProfile();
        await refreshProfile();

        // 3. Route according to authoritative onboarding completion status
        if (profile.onboarding_completed) {
          navigate("/me", { replace: true });
        } else {
          navigate("/onboarding", { replace: true });
        }
      } catch (err: any) {
        setError(err?.message || "პროფილის ინიციალიზაციისას დაფიქსირდა შეცდომა.");
      }
    };

    handleAuthCallback();
  }, [navigate, refreshProfile]);

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
