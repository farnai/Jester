import React, { useState } from "react";
import { Link, useNavigate, useLocation, Navigate } from "react-router-dom";
import { supabase } from "../../core/realtime/supabase";
import { useAuth } from "../../core/auth/useAuth";
import { JesterLogo } from "../../shared/ui/JesterLogo";
import { RegistrationIcon } from "./RegistrationScene";
import { SocialAuthButtons } from "./SocialAuthButtons";
import "./login.css";

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, onboardingCompleted, isLoading: isAuthLoading } = useAuth();

  const initialEmail = (location.state as any)?.email || "";
  const [email, setEmail] = useState(initialEmail);
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
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
    if (!password) {
      setError("გთხოვთ შეიყვანოთ პაროლი.");
      setLoading(false);
      return;
    }

    try {
      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email: cleanEmail,
        password,
      });

      if (authError) {
        if (authError.code === "email_not_confirmed") {
          // If unconfirmed, proceed to verify email
          navigate("/auth/verify-email", { state: { email: cleanEmail } });
          return;
        }
        if (authError.message.toLowerCase().includes("invalid login credentials")) {
          throw new Error("არასწორი ელფოსტა ან პაროლი.");
        }
        throw authError;
      }

      if (!data.session) throw new Error("სესიის შექმნა ვერ მოხერხდა. სცადეთ ხელახლა.");
      // AuthProvider handles profile rehydration & route resolution automatically.
    } catch (err: any) {
      setError(err?.message || "შესვლა ვერ მოხერხდა. სცადეთ ხელახლა.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page" lang="ka">
      {/* Background Decorative Scenery */}
      <div className="login-scenery-backdrop" aria-hidden="true">
        <div className="login-cream-arc" />
        <div className="login-orange-glow" />
      </div>

      <main className="login-container">
        <section className="login-card" aria-labelledby="login-title">
          <div className="login-brand-header">
            <Link to="/" aria-label="JESTER — მთავარი">
              <JesterLogo variant="stacked" height={54} />
            </Link>
            <h1 id="login-title">სისტემაში შესვლა</h1>
            <p>დაუბრუნდი შენს ასტროლოგიურ პროფილსა და კავშირებს.</p>
          </div>

          {error && (
            <div className="login-error" role="alert">
              ⚠️ {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="login-form">
            <div className="login-field">
              <label htmlFor="login-email">ელფოსტა</label>
              <div className="login-input">
                <RegistrationIcon kind="email" />
                <input
                  id="login-email"
                  name="email"
                  type="email"
                  required
                  autoComplete="email"
                  autoCapitalize="none"
                  placeholder="example@domain.ge"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setError(null);
                  }}
                  disabled={loading}
                />
              </div>
            </div>

            <div className="login-field">
              <div className="login-field-header">
                <label htmlFor="login-password">პაროლი</label>
                <Link
                  to="/auth/reset-password"
                  state={{ email }}
                  className="login-forgot-link"
                >
                  დაგავიწყდა?
                </Link>
              </div>
              <div className="login-input">
                <RegistrationIcon kind="lock" />
                <input
                  id="login-password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  autoComplete="current-password"
                  placeholder="••••••••••"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setError(null);
                  }}
                  disabled={loading}
                />
                <button
                  type="button"
                  aria-label={showPassword ? "პაროლის დამალვა" : "პაროლის ჩვენება"}
                  aria-pressed={showPassword}
                  onClick={() => setShowPassword(!showPassword)}
                >
                  <RegistrationIcon kind={showPassword ? "eye-off" : "eye"} />
                </button>
              </div>
            </div>

            <button className="login-submit" type="submit" disabled={loading}>
              <span>{loading ? "შესვლა..." : "შესვლა"}</span>
              <span aria-hidden="true">→</span>
            </button>
          </form>

          <div className="login-divider">
            <span>ან</span>
          </div>

          <SocialAuthButtons onError={(err) => setError(err)} disabled={loading} />

          <div className="login-footer-nav">
            არ გაქვს ანგარიში?{" "}
            <Link to="/auth/register">შექმენი ანგარიში</Link>
          </div>

          <div className="login-privacy">
            <RegistrationIcon kind="lock" />
            <span>სრული კონფიდენციალურობა და უსაფრთხოება</span>
          </div>
        </section>
      </main>
    </div>
  );
};
