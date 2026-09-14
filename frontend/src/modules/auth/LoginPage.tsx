import React, { useState } from "react";
import { Link, useNavigate, useLocation, Navigate } from "react-router-dom";
import { supabase } from "../../core/realtime/supabase";
import { useAuth } from "../../core/auth/useAuth";
import { Card, Button, Input } from "../../shared/ui";
import { SocialAuthButtons } from "./SocialAuthButtons";

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, onboardingCompleted, isLoading: isAuthLoading, refreshProfile } = useAuth();

  const initialEmail = (location.state as any)?.email || "";
  const [email, setEmail] = useState(initialEmail);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const from = (location.state as any)?.from?.pathname || "/me";

  // If already authenticated, redirect
  if (!isAuthLoading && user) {
    if (onboardingCompleted) {
      return <Navigate to={from} replace />;
    }
    return <Navigate to="/onboarding" replace />;
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const cleanEmail = email.trim();
    if (!cleanEmail.includes("@")) {
      setError("გთხოვთ შეიყვანოთ სწორი ელფოსტა.");
      setLoading(false);
      return;
    }

    const { data, error: authError } = await supabase.auth.signInWithPassword({
      email: cleanEmail,
      password,
    });

    if (authError) {
      setError(authError.message);
      setLoading(false);
      return;
    }

    if (data.user) {
      const p = await refreshProfile();
      setLoading(false);
      if (p?.onboarding_completed) {
        navigate(from, { replace: true });
      } else {
        navigate("/onboarding", { replace: true });
      }
    }
  };

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
          maxWidth: "440px",
          padding: "2.5rem 2rem",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <div style={{ fontSize: "2.2rem", marginBottom: "0.25rem" }}>🃏</div>
          <h2
            style={{
              margin: "0 0 0.4rem 0",
              fontSize: "1.45rem",
              fontWeight: 800,
              color: "#0f172a",
            }}
          >
            Log In to JESTER
          </h2>
          <p style={{ margin: 0, color: "#64748b", fontSize: "0.85rem" }}>
            შედით თქვენს ანგარიშში ასტროლოგიური პროფილისა და კავშირების სანახავად.
          </p>
        </div>

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

        {/* Social Authentication */}
        <SocialAuthButtons onError={(err) => setError(err)} disabled={loading} />

        <div style={{ display: "flex", alignItems: "center", margin: "1.2rem 0", color: "#94a3b8" }}>
          <div style={{ flex: 1, height: "1px", background: "#e2e8f0" }} />
          <span style={{ padding: "0 0.75rem", fontSize: "0.8rem", textTransform: "uppercase" }}>ან ელფოსტით</span>
          <div style={{ flex: 1, height: "1px", background: "#e2e8f0" }} />
        </div>

        <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <Input
            label="ელფოსტა (Email) *"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="name@example.com"
            autoCapitalize="none"
            autoCorrect="off"
          />

          <div>
            <Input
              label="პაროლი (Password) *"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="თქვენი პაროლი"
            />
            <div style={{ textAlign: "right", marginTop: "0.3rem" }}>
              <Link
                to="/auth/reset-password"
                state={{ email }}
                style={{ fontSize: "0.8rem", color: "#6366f1", textDecoration: "none" }}
              >
                დაგავიწყდათ პაროლი?
              </Link>
            </div>
          </div>

          <Button
            type="submit"
            variant="brand"
            size="lg"
            fullWidth
            isLoading={loading}
            disabled={loading || !email.trim() || !password}
            style={{ marginTop: "0.5rem" }}
          >
            {loading ? "Signing In..." : "Sign In / შესვლა"}
          </Button>
        </form>

        <div
          style={{
            marginTop: "1.5rem",
            textAlign: "center",
            fontSize: "0.85rem",
            borderTop: "1px solid #f1f5f9",
            paddingTop: "1rem",
            color: "#64748b",
          }}
        >
          არ გაქვთ ანგარიში?{" "}
          <Link to="/auth/register" style={{ color: "#6366f1", fontWeight: "bold", textDecoration: "none" }}>
            რეგისტრაცია (Create account)
          </Link>
        </div>
      </Card>
    </div>
  );
};
