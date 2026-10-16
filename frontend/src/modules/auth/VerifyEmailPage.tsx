import React, { useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import { supabase } from "../../core/realtime/supabase";
import { useAuth } from "../../core/auth/useAuth";
import { Button, Card, Input } from "../../shared/ui";

export const VerifyEmailPage: React.FC = () => {
  const location = useLocation();
  const { user, isLoading, onboardingCompleted } = useAuth();
  const [email, setEmail] = useState<string>(location.state?.email || "");
  const [sending, setSending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isLoading && user) return <Navigate to={onboardingCompleted ? "/" : "/onboarding"} replace />;

  const resend = async (event: React.FormEvent) => {
    event.preventDefault();
    setSending(true);
    setError(null);
    setMessage(null);
    try {
      const { error } = await supabase.auth.resend({
        type: "signup",
        email: email.trim(),
        options: { emailRedirectTo: `${window.location.origin}/auth/callback` },
      });
      if (error) throw error;
      setMessage("დადასტურების წერილი გამოგზავნილია. შეამოწმეთ შემოსული წერილები და სპამის საქაღალდე.");
    } catch (err: any) {
      setError(err?.message || "წერილის გაგზავნა ვერ მოხერხდა. სცადეთ ხელახლა.");
    } finally {
      setSending(false);
    }
  };

  return <Card variant="elevated" style={{ maxWidth: 440, margin: "3rem auto", padding: "2rem" }}>
    <h1>დაადასტურეთ ელფოსტა</h1>
    <p>გასაგრძელებლად გახსენით ელფოსტით მიღებული დადასტურების ბმული. შემდეგ შეძლებთ შესვლას და პროფილის შევსებას.</p>
    {message && <p role="status">{message}</p>}
    {error && <p role="alert">{error}</p>}
    <form onSubmit={resend} aria-busy={sending}>
      <Input label="ელფოსტა" type="email" required autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} />
      <Button type="submit" disabled={sending || !email.trim()}>{sending ? "იგზავნება..." : "წერილის ხელახლა გაგზავნა"}</Button>
    </form>
    <p><Link to="/auth/login" state={{ email }}>შესვლა</Link></p>
  </Card>;
};
