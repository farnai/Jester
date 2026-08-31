import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { supabase } from "../../core/realtime/supabase";
import { useAuth } from "../../core/auth/useAuth";

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { refreshBirthDataCheck } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const from = (location.state as any)?.from?.pathname || "/self/astrology";

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const { data, error: authError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (authError) {
      setError(authError.message);
      setLoading(false);
      return;
    }

    if (data.user) {
      const hasBirth = await refreshBirthDataCheck();
      setLoading(false);
      if (!hasBirth) {
        navigate("/onboarding/birth-data");
      } else {
        navigate(from, { replace: true });
      }
    }
  };

  return (
    <div
      style={{
        maxWidth: "400px",
        margin: "4rem auto",
        padding: "2rem",
        border: "1px solid #d9d9d9",
        borderRadius: "6px",
        backgroundColor: "#fff",
      }}
    >
      <h2 style={{ marginTop: 0 }}>Log In to JESTER</h2>
      <p style={{ color: "#666", fontSize: "0.9rem" }}>
        Enter your credentials to access your astrological profile and connections.
      </p>

      {error && (
        <div
          style={{
            padding: "0.75rem",
            marginBottom: "1rem",
            background: "#fff1f0",
            border: "1px solid #ff4d4f",
            borderRadius: "4px",
            color: "#cf1322",
            fontSize: "0.85rem",
          }}
        >
          {error}
        </div>
      )}

      <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <div>
          <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
            Email Address
          </label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
            placeholder="user@example.com"
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
            Password
          </label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "0.6rem",
            background: "#1890ff",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            fontWeight: "bold",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Signing In..." : "Sign In"}
        </button>
      </form>

      <div style={{ marginTop: "1.5rem", textAlign: "center", fontSize: "0.85rem" }}>
        Don't have an account? <Link to="/auth/register">Create an account</Link>
      </div>
    </div>
  );
};
