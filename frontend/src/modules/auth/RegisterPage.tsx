import React, { useState } from "react";
import { Link, useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../../core/auth/useAuth";
import { Card, Button, Input } from "../../shared/ui";
import { SocialAuthButtons } from "./SocialAuthButtons";

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, onboardingCompleted, isLoading: isAuthLoading, signUp } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [duplicateEmail, setDuplicateEmail] = useState<string | null>(null);

  // If already authenticated, redirect appropriately
  if (!isAuthLoading && user) {
    if (onboardingCompleted) {
      return <Navigate to="/me" replace />;
    }
    return <Navigate to="/onboarding" replace />;
  }

  const handleAccountSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanEmail = email.trim();
    const cleanPassword = password;
    const cleanConfirmPassword = confirmPassword;

    if (!cleanEmail.includes("@")) {
      setError("გთხოვთ შეიყვანოთ სწორი ელფოსტა (Valid email address).");
      return;
    }
    if (cleanPassword.length < 6) {
      setError("პაროლი უნდა შედგებოდეს მინიმუმ 6 სიმბოლოსგან.");
      return;
    }
    if (!cleanConfirmPassword) {
      setError("გთხოვთ გაიმეოროთ პაროლი (Confirm password is required).");
      return;
    }
    if (cleanPassword !== cleanConfirmPassword) {
      setError("პაროლები არ ემთხვევა (Passwords do not match).");
      return;
    }

    setLoading(true);
    setError(null);
    setDuplicateEmail(null);

    try {
      await signUp({
        email: cleanEmail,
        password: cleanPassword,
      });

      setLoading(false);
      navigate("/onboarding", { replace: true });
    } catch (err: any) {
      const msg = err?.message?.toLowerCase() || "";
      if (msg.includes("already registered") || msg.includes("already exists") || msg.includes("unique")) {
        setDuplicateEmail(cleanEmail);
        setError("ეს ელფოსტა უკვე რეგისტრირებულია.");
      } else {
        setError(err?.message || "ანგარიშის შექმნისას დაფიქსირდა შეცდომა.");
      }
      setLoading(false);
    }
  };

  const isFormValid =
    email.trim().includes("@") &&
    password.length >= 6 &&
    confirmPassword.length >= 6 &&
    password === confirmPassword;

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
            შეიყვანეთ თქვენი მონაცემები JESTER-ში დასარეგისტრირებლად.
          </p>
        </div>

        {duplicateEmail ? (
          <div
            style={{
              padding: "1rem",
              marginBottom: "1.2rem",
              background: "#fff1f0",
              border: "1px solid #ff4d4f",
              borderRadius: "8px",
              color: "#cf1322",
            }}
          >
            <p style={{ margin: "0 0 0.75rem 0", fontWeight: 700, fontSize: "0.95rem" }}>
              ⚠️ ეს ელფოსტა უკვე რეგისტრირებულია.
            </p>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <Button
                variant="brand"
                size="sm"
                onClick={() => navigate("/auth/login", { state: { email: duplicateEmail } })}
              >
                შესვლა (Log In)
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => navigate("/auth/reset-password", { state: { email: duplicateEmail } })}
              >
                პაროლის აღდგენა
              </Button>
            </div>
          </div>
        ) : error ? (
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
        ) : null}

        {/* Social Authentication */}
        <SocialAuthButtons onError={(err) => setError(err)} disabled={loading} />

        <div style={{ display: "flex", alignItems: "center", margin: "1.2rem 0", color: "#94a3b8" }}>
          <div style={{ flex: 1, height: "1px", background: "#e2e8f0" }} />
          <span style={{ padding: "0 0.75rem", fontSize: "0.8rem", textTransform: "uppercase" }}>ან ელფოსტით</span>
          <div style={{ flex: 1, height: "1px", background: "#e2e8f0" }} />
        </div>

        <form onSubmit={handleAccountSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <Input
            label="ელფოსტა (Email) *"
            type="email"
            required
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (error) setError(null);
            }}
            placeholder="name@example.com"
            autoComplete="email"
            autoCapitalize="none"
            autoCorrect="off"
          />

          <Input
            label="პაროლი (Password) *"
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              if (error) setError(null);
            }}
            placeholder="მინიმუმ 6 სიმბოლო"
            autoComplete="new-password"
            helperText="მინიმუმ 6 სიმბოლო"
          />

          <Input
            label="გაიმეორეთ პაროლი (Confirm Password) *"
            type="password"
            required
            minLength={6}
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value);
              if (error) setError(null);
            }}
            placeholder="გაიმეორეთ პაროლი"
            autoComplete="new-password"
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
            {loading ? "ანგარიშის შექმნა..." : "ანგარიშის შექმნა →"}
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
