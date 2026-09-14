import React, { useState } from "react";
import { Link, useNavigate, Navigate } from "react-router-dom";
import { supabase } from "../../core/realtime/supabase";
import { useAuth } from "../../core/auth/useAuth";
import { Card, Button, Input } from "../../shared/ui";

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, hasBirthData, isLoading: isAuthLoading } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // If already authenticated, redirect appropriately
  if (!isAuthLoading && user) {
    if (hasBirthData === true) {
      return <Navigate to="/" replace />;
    }
    if (hasBirthData === false) {
      return <Navigate to="/onboarding/birth-data" replace />;
    }
  }

  const handleAccountSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanEmail = email.trim();
    if (!cleanEmail.includes("@")) {
      setError("გთხოვთ შეიყვანოთ სწორი ელფოსტა (Valid email address).");
      return;
    }
    if (password.length < 6) {
      setError("პაროლი უნდა შედგებოდეს მინიმუმ 6 სიმბოლოსგან.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let activeUser: any = null;
      let activeSession: any = null;

      // 1. Create account via Supabase Auth
      const { data: authData, error: authErr } = await supabase.auth.signUp({
        email: cleanEmail,
        password,
      });

      if (authErr) {
        const msg = authErr.message.toLowerCase();
        if (msg.includes("already registered") || msg.includes("exists")) {
          // If already registered, attempt direct sign in
          const { data: signInData, error: signInErr } = await supabase.auth.signInWithPassword({
            email: cleanEmail,
            password,
          });
          if (signInErr) {
            throw new Error("ეს მომხმარებელი უკვე რეგისტრირებულია. გთხოვთ შეხვიდეთ თქვენი პაროლით.");
          }
          activeUser = signInData.user;
          activeSession = signInData.session;
        } else {
          throw new Error(authErr.message);
        }
      } else {
        activeUser = authData.user;
        activeSession = authData.session;
      }

      // If session was not directly returned, acquire it via sign in
      if (!activeSession) {
        const { data: signInData, error: signInErr } = await supabase.auth.signInWithPassword({
          email: cleanEmail,
          password,
        });
        if (signInErr) {
          throw new Error(signInErr.message);
        }
        activeUser = signInData.user;
        activeSession = signInData.session;
      }

      if (!activeUser) {
        throw new Error("ანგარიშის შექმნა ვერ მოხერხდა. სცადეთ ხელახლა.");
      }

      if (activeSession) {
        await supabase.auth.setSession({
          access_token: activeSession.access_token,
          refresh_token: activeSession.refresh_token,
        });
      }

      // 2. Canonical user identity established -> proceed straight to onboarding
      setLoading(false);
      navigate("/onboarding/birth-data", { replace: true });
    } catch (err: any) {
      setError(err.message || "ანგარიშის შექმნისას დაფიქსირდა შეცდომა.");
      setLoading(false);
    }
  };

  const isFormValid = email.trim().includes("@") && password.length >= 6;

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
          padding: "2.5rem 2rem",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.25rem" }}>👤</div>
          <h2
            style={{
              margin: "0 0 0.4rem 0",
              fontSize: "1.45rem",
              fontWeight: 800,
              color: "#0f172a",
            }}
          >
            Create Account / ანგარიშის შექმნა
          </h2>
          <p
            style={{
              margin: 0,
              color: "#64748b",
              fontSize: "0.85rem",
            }}
          >
            შეიყვანეთ ელფოსტა და პაროლი JESTER-ში დასარეგისტრირებლად.
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

        <form onSubmit={handleAccountSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
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

          <Input
            label="პაროლი (Password) *"
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="მინიმუმ 6 სიმბოლო"
            helperText="მინიმუმ 6 სიმბოლო"
          />

          <Button
            type="submit"
            variant="brand"
            size="lg"
            fullWidth
            isLoading={loading}
            disabled={!isFormValid || loading}
            style={{ marginTop: "0.5rem" }}
          >
            {loading ? "Creating Account..." : "Continue to Onboarding ➡️"}
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
          უკვე გაქვთ ანგარიში?{" "}
          <Link to="/auth/login" style={{ color: "#6366f1", fontWeight: "bold", textDecoration: "none" }}>
            შესვლა (Log In)
          </Link>
        </div>
      </Card>
    </div>
  );
};
