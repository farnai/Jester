import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { supabase } from "../../core/realtime/supabase";
import { Card, Button, Input } from "../../shared/ui";

export const ResetPasswordPage: React.FC = () => {
  const location = useLocation();
  const initialEmail = (location.state as any)?.email || "";

  const [email, setEmail] = useState(initialEmail);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isRecoveryMode, setIsRecoveryMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if arrived via recovery URL hash
    if (window.location.hash.includes("type=recovery")) {
      setIsRecoveryMode(true);
    }

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event) => {
      if (event === "PASSWORD_RECOVERY") {
        setIsRecoveryMode(true);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanEmail = email.trim();
    if (!cleanEmail || !cleanEmail.includes("@")) {
      setError("გთხოვთ შეიყვანოთ სწორი ელფოსტა.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const { error: resetErr } = await supabase.auth.resetPasswordForEmail(cleanEmail, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      });
      if (resetErr) {
        throw new Error(resetErr.message);
      }
      setSuccessMessage("პაროლის აღდგენის ბმული გამოგზავნილია თქვენს ელფოსტაზე. გთხოვთ შეამოწმოთ შემოსული წერილები.");
    } catch (err: any) {
      setError(err?.message || "პაროლის აღდგენის მოთხოვნა ვერ შესრულდა.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword.length < 6) {
      setError("ახალი პაროლი უნდა შეიცავდეს მინიმუმ 6 სიმბოლოს.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("პაროლები ერთმანეთს არ ემთხვევა.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const { error: updateErr } = await supabase.auth.updateUser({
        password: newPassword,
      });
      if (updateErr) {
        throw new Error(updateErr.message);
      }
      setSuccessMessage("თქვენი პაროლი წარმატებით განახლდა!");
    } catch (err: any) {
      setError(err?.message || "პაროლის განახლება ვერ მოხერხდა.");
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
          <div style={{ fontSize: "2.2rem", marginBottom: "0.25rem" }}>🔑</div>
          <h2
            style={{
              margin: "0 0 0.4rem 0",
              fontSize: "1.45rem",
              fontWeight: 800,
              color: "#0f172a",
            }}
          >
            {isRecoveryMode ? "ახალი პაროლის დაყენება" : "პაროლის აღდგენა"}
          </h2>
          <p style={{ margin: 0, color: "#64748b", fontSize: "0.85rem" }}>
            {isRecoveryMode
              ? "შეიყვანეთ თქვენი ახალი პაროლი ანგარიშში შესასვლელად."
              : "შეიყვანეთ თქვენი ელფოსტა და ჩვენ გამოგიგზავნით აღდგენის ბმულს."}
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

        {successMessage ? (
          <div style={{ textAlign: "center" }}>
            <div
              style={{
                padding: "1rem",
                marginBottom: "1.5rem",
                background: "#f6ffed",
                border: "1px solid #b7eb8f",
                borderRadius: "6px",
                color: "#389e0d",
                fontSize: "0.9rem",
              }}
            >
              ✅ {successMessage}
            </div>
            <Link
              to="/auth/login"
              style={{
                display: "inline-block",
                padding: "0.75rem 1.5rem",
                background: "#6366f1",
                color: "#fff",
                borderRadius: "8px",
                textDecoration: "none",
                fontWeight: 600,
              }}
            >
              შესვლის გვერდზე გადასვლა
            </Link>
          </div>
        ) : isRecoveryMode ? (
          <form onSubmit={handleUpdatePassword} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <Input
              label="ახალი პაროლი *"
              type="password"
              required
              minLength={6}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="მინიმუმ 6 სიმბოლო"
            />
            <Input
              label="გაიმეორეთ ახალი პაროლი *"
              type="password"
              required
              minLength={6}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="გაიმეორეთ პაროლი"
            />
            <Button
              type="submit"
              variant="brand"
              size="lg"
              fullWidth
              isLoading={loading}
              disabled={loading || !newPassword || !confirmPassword}
            >
              {loading ? "განახლება..." : "პაროლის შეცვლა"}
            </Button>
          </form>
        ) : (
          <form onSubmit={handleRequestReset} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <Input
              label="ელფოსტა (Email) *"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
            />
            <Button
              type="submit"
              variant="brand"
              size="lg"
              fullWidth
              isLoading={loading}
              disabled={loading || !email.trim()}
            >
              {loading ? "იგზავნება..." : "ბმულის გაგზავნა"}
            </Button>
          </form>
        )}

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
          <Link to="/auth/login" style={{ color: "#6366f1", fontWeight: "bold", textDecoration: "none" }}>
            ⬅️ შესვლის გვერდზე დაბრუნება (Back to Log In)
          </Link>
        </div>
      </Card>
    </div>
  );
};
