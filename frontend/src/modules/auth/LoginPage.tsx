import React, { useState } from "react";
import { Link, useNavigate, useLocation, Navigate } from "react-router-dom";
import { supabase } from "../../core/realtime/supabase";
import { useAuth } from "../../core/auth/useAuth";
import { Card, Button, Input } from "../../shared/ui";
import { SocialAuthButtons } from "./SocialAuthButtons";

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, onboardingCompleted, isLoading: isAuthLoading } = useAuth();

  const initialEmail = (location.state as any)?.email || "";
  const [email, setEmail] = useState(initialEmail);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const from = (location.state as any)?.from?.pathname || "/";

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

    try {
      const { data, error: authError } = await supabase.auth.signInWithPassword({ email: cleanEmail, password });
      if (authError) {
        if (authError.code === "email_not_confirmed") {
          navigate("/auth/verify-email", { state: { email: cleanEmail } });
          return;
        }
        throw authError;
      }
      if (!data.session) throw new Error("სესიის შექმნა ვერ მოხერხდა. სცადეთ ხელახლა.");
      // AuthProvider hydrates the authoritative profile before the redirect above.
    } catch (err: any) {
      setError(err?.message || "შესვლა ვერ მოხერხდა. სცადეთ ხელახლა.");
    } finally {
      setLoading(false);
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
              color: "var(--jester-text-primary)",
            }}
          >
            Log In to JESTER
          </h2>
          <p style={{ margin: 0, color: "var(--jester-text-secondary)", fontSize: "0.85rem" }}>
            შედით თქვენს ანგარიშში ასტროლოგიური პროფილისა და კავშირების სანახავად.
          </p>
        </div>

        {error && (
          <div
            style={{
              padding: "0.75rem",
              marginBottom: "1.2rem",
              background: "var(--jester-semantic-error-soft)",
              border: "1px solid var(--jester-semantic-error)",
              borderRadius: "6px",
              color: "var(--jester-semantic-error)",
              fontSize: "0.85rem",
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {/* Social Authentication */}
        <SocialAuthButtons onError={(err) => setError(err)} disabled={loading} />

        <div style={{ display: "flex", alignItems: "center", margin: "1.2rem 0", color: "var(--jester-text-secondary)" }}>
          <div style={{ flex: 1, height: "1px", background: "var(--jester-border-soft)" }} />
          <span style={{ padding: "0 0.75rem", fontSize: "0.8rem", textTransform: "uppercase" }}>ან ელფოსტით</span>
          <div style={{ flex: 1, height: "1px", background: "var(--jester-border-soft)" }} />
        </div>

        <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <Input
            label="ელფოსტა (Email) *"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="name@example.com"
            autoComplete="email"
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
              autoComplete="current-password"
            />
            <div style={{ textAlign: "right", marginTop: "0.3rem" }}>
              <Link
                to="/auth/reset-password"
                state={{ email }}
                style={{ fontSize: "0.8rem", color: "var(--jester-brand-orange-800)", textDecoration: "none" }}
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
            borderTop: "1px solid var(--jester-border-soft)",
            paddingTop: "1rem",
            color: "var(--jester-text-secondary)",
          }}
        >
          არ გაქვთ ანგარიში?{" "}
          <Link to="/auth/register" style={{ color: "var(--jester-brand-orange-800)", fontWeight: "bold", textDecoration: "none" }}>
            რეგისტრაცია (Create account)
          </Link>
        </div>
      </Card>
    </div>
  );
};
