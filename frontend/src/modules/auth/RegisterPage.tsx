import React, { useState } from "react";
import { Link, useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../../core/auth/useAuth";
import { RegistrationHeader, RegistrationScenery, RegistrationStory, RegistrationIcon } from "./RegistrationScene";
import "./registration.css";

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, onboardingCompleted, isLoading: isAuthLoading, signUp } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [duplicateEmail, setDuplicateEmail] = useState<string | null>(null);

  // If already authenticated, redirect appropriately
  if (!isAuthLoading && user) {
    if (onboardingCompleted) {
      return <Navigate to="/" replace />;
    }
    return <Navigate to="/onboarding" replace />;
  }

  const handleAccountSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanEmail = email.trim();
    const cleanPassword = password;
    const cleanConfirmPassword = confirmPassword;

    if (!cleanEmail.includes("@")) {
      setError("გთხოვთ შეიყვანოთ სწორი ელფოსტა.");
      return;
    }
    if (cleanPassword.length < 6) {
      setError("პაროლი უნდა შედგებოდეს მინიმუმ 6 სიმბოლოსგან.");
      return;
    }
    if (!cleanConfirmPassword) {
      setError("გთხოვთ გაიმეოროთ პაროლი.");
      return;
    }
    if (cleanPassword !== cleanConfirmPassword) {
      setError("პაროლები არ ემთხვევა.");
      return;
    }

    setLoading(true);
    setError(null);
    setDuplicateEmail(null);

    try {
      const result = await signUp({
        email: cleanEmail,
        password: cleanPassword,
      });

      setLoading(false);
      navigate(result.confirmationRequired ? "/auth/verify-email" : "/onboarding", { replace: true, state: { email: cleanEmail } });
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

  return (
    <div className="registration-page" lang="ka">
      <RegistrationHeader />
      <main className="registration-composition">
        <RegistrationScenery />
        <RegistrationStory />
        <section className="registration-card" aria-labelledby="registration-card-title">
          <p className="registration-step">ნაბიჯი 1 / 2</p>
          <h2 id="registration-card-title">შექმენი ანგარიში</h2>
          <p className="registration-card-intro">დაიწყე შენი მოგზაურობა<br />უფრო ღრმა კავშირებისკენ.</p>
          {error && <div className="registration-error" id="registration-error" role="alert">
            <p>{error}</p>
            {duplicateEmail && <div className="registration-error-actions">
              <button type="button" onClick={() => navigate("/auth/login", { state: { email: duplicateEmail } })}>შესვლა</button>
              <button type="button" onClick={() => navigate("/auth/reset-password", { state: { email: duplicateEmail } })}>პაროლის აღდგენა</button>
            </div>}
          </div>}
          <form onSubmit={handleAccountSubmit} aria-busy={loading} aria-describedby={error ? "registration-error" : undefined}>
            <div className="registration-field">
              <label htmlFor="registration-email">ელფოსტა</label>
              <div className="registration-input">
                <RegistrationIcon kind="email" />
                <input id="registration-email" name="email" type="email" required autoComplete="email" placeholder="example@domain.ge" value={email} onChange={(e) => { setEmail(e.target.value); setError(null); setDuplicateEmail(null); }} />
              </div>
            </div>
            <div className="registration-field">
              <label htmlFor="registration-password">პაროლი</label>
              <div className="registration-input">
                <RegistrationIcon kind="lock" />
                <input id="registration-password" name="password" type={showPassword ? "text" : "password"} required minLength={6} autoComplete="new-password" placeholder="••••••••••" value={password} onChange={(e) => { setPassword(e.target.value); setError(null); }} />
                <button type="button" aria-label={showPassword ? "პაროლის დამალვა" : "პაროლის ჩვენება"} aria-pressed={showPassword} onClick={() => setShowPassword(!showPassword)}><RegistrationIcon kind={showPassword ? "eye-off" : "eye"} /></button>
              </div>
            </div>
            {/* Confirm Password shares the same form at every viewport. */}
            <div className="registration-field">
              <label htmlFor="registration-confirm-password">გაიმეორე პაროლი</label>
              <div className="registration-input">
                <RegistrationIcon kind="lock" />
                <input id="registration-confirm-password" name="confirmPassword" type={showConfirmPassword ? "text" : "password"} required minLength={6} autoComplete="new-password" placeholder="••••••••••" value={confirmPassword} onChange={(e) => { setConfirmPassword(e.target.value); setError(null); }} />
                <button type="button" aria-label={showConfirmPassword ? "გამეორებული პაროლის დამალვა" : "გამეორებული პაროლის ჩვენება"} aria-pressed={showConfirmPassword} onClick={() => setShowConfirmPassword(!showConfirmPassword)}><RegistrationIcon kind={showConfirmPassword ? "eye-off" : "eye"} /></button>
              </div>
            </div>
            <button className="registration-submit" type="submit" disabled={loading}>
              <span role="status">{loading ? "ანგარიშის შექმნა..." : "ანგარიშის შექმნა"}</span><span aria-hidden="true">→</span>
            </button>
          </form>
          <p className="registration-login">უკვე გაქვს ანგარიში? <Link to="/auth/login">შესვლა</Link></p>
          <p className="registration-privacy"><RegistrationIcon kind="lock" /><span>შენი მონაცემები დაცულია და არ გადაეცემა მესამე პირებს. სრული კონფიდენციალურობა.</span></p>
        </section>
        <p className="registration-annotation">შეიგრძენი უფრო<br />ღრმა კავშირები.</p>
      </main>
      <footer className="registration-footer">JESTER · People Discovery &amp; Relationship Intelligence</footer>
    </div>
  );
};
