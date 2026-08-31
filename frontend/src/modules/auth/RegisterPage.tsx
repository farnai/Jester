import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { supabase } from "../../core/realtime/supabase";

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const { data, error: authError } = await supabase.auth.signUp({
      email,
      password,
    });

    if (authError) {
      setError(authError.message);
      setLoading(false);
      return;
    }

    setLoading(false);
    if (data.user) {
      // Direct newly registered user immediately to birth data onboarding
      navigate("/onboarding/birth-data");
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
      <h2 style={{ marginTop: 0 }}>Create JESTER Account</h2>
      <p style={{ color: "#666", fontSize: "0.9rem" }}>
        Sign up to generate your natal astrology profile and discover relationships.
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

      <form onSubmit={handleRegister} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
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
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
            placeholder="At least 6 characters"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "0.6rem",
            background: "#52c41a",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            fontWeight: "bold",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Creating Account..." : "Create Account"}
        </button>
      </form>

      <div style={{ marginTop: "1.5rem", textAlign: "center", fontSize: "0.85rem" }}>
        Already have an account? <Link to="/auth/login">Sign in here</Link>
      </div>
    </div>
  );
};
