import React, { useState } from "react";
import { Link, useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../../core/auth/useAuth";
import { JesterHatIcon } from "../../shared/ui/JesterLogo";
import heroPortraitImg from "../../assets/registration/hero_portrait.jpg";
import scenicSunsetImg from "../../assets/registration/scenic_sunset.jpg";

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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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
    <div className="min-h-screen bg-[#FAF7F2] text-[#222630] font-sans flex flex-col justify-between selection:bg-[#FFD0B2] selection:text-[#713111]">
      {/* 1. Global Navigation Header */}
      <header className="w-full max-w-7xl mx-auto px-4 sm:px-8 lg:px-12 pt-5 pb-4 flex items-center justify-between z-20">
        {/* Brand Logo */}
        <Link to="/" className="inline-flex items-center gap-3 group focus:outline-none focus-visible:ring-2 focus-visible:ring-[#FF7A2F] rounded-lg">
          <JesterHatIcon size={34} className="transition-transform group-hover:scale-105" />
          <span
            style={{
              fontFamily: "'GFS Didot', 'Didot', 'Bodoni MT', 'Cinzel', 'Georgia', serif",
              fontWeight: 700,
              fontSize: "1.45rem",
              letterSpacing: "0.18em",
              color: "#3A2A22",
            }}
          >
            JESTER
          </span>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-[#222630]/80">
          <button
            type="button"
            onClick={() => {}}
            className="hover:text-[#FF7A2F] transition-colors cursor-pointer bg-transparent border-0 p-0"
          >
            როგორ მუშაობს
          </button>
          <button
            type="button"
            onClick={() => {}}
            className="hover:text-[#FF7A2F] transition-colors cursor-pointer bg-transparent border-0 p-0"
          >
            ჩვენ შესახებ
          </button>
          <button
            type="button"
            onClick={() => {}}
            className="hover:text-[#FF7A2F] transition-colors cursor-pointer bg-transparent border-0 p-0"
          >
            ბლოგი
          </button>
        </nav>

        {/* Right Action: Log In Button (Desktop) & Hamburger (Mobile) */}
        <div className="flex items-center gap-3">
          <Link
            to="/auth/login"
            className="hidden sm:inline-flex items-center justify-center px-6 py-2 rounded-full border border-[#222630]/30 hover:border-[#222630] text-sm font-semibold text-[#222630] hover:bg-[#222630]/5 transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[#FF7A2F]"
          >
            შესვლა
          </Link>

          {/* Mobile Hamburger Button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="sm:hidden p-2 rounded-lg text-[#222630] hover:bg-[#E6E0D7]/40 focus:outline-none"
            aria-label="მენიუ"
          >
            {mobileMenuOpen ? (
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>
      </header>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="sm:hidden w-full bg-white border-b border-[#E6E0D7] px-6 py-4 flex flex-col gap-3 shadow-md z-30 animate-fadeIn">
          <div className="flex flex-col gap-2.5 text-sm font-medium text-[#222630]">
            <span className="py-1.5 hover:text-[#FF7A2F]">როგორ მუშაობს</span>
            <span className="py-1.5 hover:text-[#FF7A2F]">ჩვენ შესახებ</span>
            <span className="py-1.5 hover:text-[#FF7A2F]">ბლოგი</span>
          </div>
          <Link
            to="/auth/login"
            className="mt-2 w-full text-center py-2.5 rounded-full border border-[#222630] text-sm font-semibold text-[#222630]"
          >
            შესვლა
          </Link>
        </div>
      )}

      {/* 2. Main Hero Composition & Registration Card */}
      <main className="w-full max-w-7xl mx-auto px-4 sm:px-8 lg:px-12 py-3 sm:py-6 flex-1 flex flex-col justify-center">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-start relative">

          {/* LEFT & CENTER HERO SECTION (7 COLS ON DESKTOP) */}
          <div className="lg:col-span-7 flex flex-col justify-between relative">
            
            {/* Top Row: Headline + Feature Bullets on Left, Portrait Arch on Right */}
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6 relative">
              {/* Left Editorial Copy (Text Content) */}
              <div className="w-full md:max-w-[320px] lg:max-w-[340px] shrink-0 z-10">
                {/* Mobile: Row with Headline on Left, Compact Arch Portrait on Right */}
                <div className="flex items-start justify-between gap-3 md:block">
                  <h1 className="text-3xl sm:text-4xl lg:text-[40px] leading-[1.16] font-extrabold tracking-tight text-[#222630]">
                    შექმენი თავი. <br />
                    შექმენი სხვა. <br />
                    <span className="text-[#FF7A2F]">შეიგრძენი კავშირი.</span>
                  </h1>

                  {/* Compact Portrait Thumbnail on Mobile */}
                  <div className="md:hidden shrink-0 w-24 h-32 rounded-t-full overflow-hidden shadow-md relative mt-1 bg-gradient-to-b from-[#FF7A2F] to-[#C7614B]">
                    <img
                      src={heroPortraitImg}
                      alt="JESTER Portrait"
                      className="w-full h-full object-cover object-top"
                    />
                  </div>
                </div>

                <p className="mt-4 text-[14px] sm:text-[15px] text-[#6A716F] leading-relaxed">
                  JESTER გეხმარება გაიგო შენი თავი, აღმოაჩინო სხვა ადამიანები და უკეთ გაიგო ნამდვილი, ღრმა კავშირები.
                </p>

                {/* Three Feature Bullets with Circular Orange Icons */}
                <div className="mt-6 sm:mt-7 flex flex-col gap-4 sm:gap-5">
                  {/* Feature 1 */}
                  <div className="flex items-start gap-3.5">
                    <div className="w-11 h-11 rounded-full bg-[#FBEEE7] text-[#FF7A2F] border border-[#FFD0B2]/60 flex items-center justify-center shrink-0 shadow-sm">
                      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z" />
                        <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-[14px] font-bold text-[#222630] leading-snug">
                        გაიცანი შენი თავი
                      </h2>
                      <p className="text-xs text-[#6A716F] mt-0.5 leading-relaxed">
                        შეისწავლე შენი ღირებულებები, ემოციები და კომუნიკაციის სტილი.
                      </p>
                    </div>
                  </div>

                  {/* Feature 2 */}
                  <div className="flex items-start gap-3.5">
                    <div className="w-11 h-11 rounded-full bg-[#FBEEE7] text-[#FF7A2F] border border-[#FFD0B2]/60 flex items-center justify-center shrink-0 shadow-sm">
                      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-[14px] font-bold text-[#222630] leading-snug">
                        აღმოაჩინე შესაფერისი ადამიანები
                      </h2>
                      <p className="text-xs text-[#6A716F] mt-0.5 leading-relaxed">
                        იპოვე ადამიანები, რომლებიც იზიარებენ შენს ღირებულებებსა და ინტერესებს.
                      </p>
                    </div>
                  </div>

                  {/* Feature 3 */}
                  <div className="flex items-start gap-3.5">
                    <div className="w-11 h-11 rounded-full bg-[#FBEEE7] text-[#FF7A2F] border border-[#FFD0B2]/60 flex items-center justify-center shrink-0 shadow-sm">
                      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-[14px] font-bold text-[#222630] leading-snug">
                        შეიგრძენი უფრო ღრმა კავშირები
                      </h2>
                      <p className="text-xs text-[#6A716F] mt-0.5 leading-relaxed">
                        მიიღე პერსონალური ანალიზი და ინსაიტები ურთიერთობების შესახებ.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Desktop Portrait Arch (Flex sibling on the right of editorial copy) */}
              <div className="hidden md:flex flex-col items-center justify-end w-64 lg:w-[290px] h-[370px] lg:h-[410px] shrink-0 relative mt-1">
                <div
                  className="w-full h-full rounded-t-full overflow-hidden shadow-sm relative"
                  style={{
                    background: "linear-gradient(175deg, #FF7A2F 0%, #E9681F 50%, #C7614B 100%)",
                  }}
                >
                  <img
                    src={heroPortraitImg}
                    alt="JESTER Portrait"
                    className="w-full h-full object-cover object-center"
                    style={{
                      maskImage: "linear-gradient(to bottom, black 82%, transparent 100%)",
                      WebkitMaskImage: "linear-gradient(to bottom, black 82%, transparent 100%)",
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Lower Scenic Sunset Photograph (Desktop & Tablet) */}
            <div className="hidden sm:block mt-8 relative rounded-2xl overflow-hidden shadow-sm border border-[#E6E0D7]/60 group z-10">
              <div className="w-full h-44 sm:h-52 lg:h-56 relative overflow-hidden bg-[#FAF7F2]">
                <img
                  src={scenicSunsetImg}
                  alt="Couple looking at sunset over city"
                  className="w-full h-full object-cover object-center transition-transform duration-700 group-hover:scale-102"
                />
                {/* Sunset Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/45 via-transparent to-transparent pointer-events-none" />

                {/* Georgian Script Quote on the bottom right */}
                <div className="absolute bottom-3 right-4 sm:bottom-4 sm:right-6 text-right pointer-events-none drop-shadow-md">
                  <p
                    className="text-white text-xs sm:text-sm italic font-medium tracking-wide"
                    style={{
                      fontFamily: "'Noto Sans Georgian', Georgia, serif",
                      textShadow: "0 2px 4px rgba(0,0,0,0.6)",
                    }}
                  >
                    უფრო მეტი ვიდრე დამთხვევა <br />
                    <span className="font-semibold text-[#FFE7D7]">უფრო ნამდვილი კავშირი</span>
                  </p>
                  <svg
                    className="w-24 h-2 mt-1 ml-auto text-[#FF7A2F]"
                    viewBox="0 0 100 10"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                  >
                    <path d="M 5 5 Q 50 10 95 3" />
                  </svg>
                </div>
              </div>
            </div>

          </div>

          {/* RIGHT REGISTRATION CARD (5 COLS ON DESKTOP) */}
          <div className="lg:col-span-5 flex flex-col items-center lg:items-end w-full">
            <div className="w-full max-w-[440px] bg-white rounded-3xl p-6 sm:p-8 shadow-[0_20px_50px_rgba(34,38,48,0.08)] border border-[#E6E0D7]/80 relative z-20 transition-shadow hover:shadow-[0_24px_60px_rgba(34,38,48,0.12)]">

              {/* Step indicator */}
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-[#FF7A2F] tracking-wide">
                  ნაბიჯი 1 / 2
                </span>
                <span className="text-[11px] text-[#6A716F]">
                  ანგარიში → დაბადების მონაცემები
                </span>
              </div>

              {/* Card Headline & Subtitle */}
              <h2 className="text-2xl sm:text-[26px] font-extrabold text-[#222630] tracking-tight leading-tight">
                შექმენი ანგარიში
              </h2>
              <p className="text-xs sm:text-sm text-[#6A716F] mt-1 mb-5 leading-normal">
                დაიწყე შენი მოგზაურობა უფრო ღრმა კავშირებისკენ.
              </p>

              {/* Duplicate Email Notice */}
              {duplicateEmail ? (
                <div className="mb-4 p-3.5 bg-[#FBE9E8] border border-[#AE3534]/30 rounded-xl text-xs text-[#AE3534]">
                  <p className="font-bold mb-2">⚠️ ეს ელფოსტა უკვე რეგისტრირებულია.</p>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => navigate("/auth/login", { state: { email: duplicateEmail } })}
                      className="px-3 py-1.5 bg-[#FF7A2F] text-[#222630] font-bold rounded-lg text-xs hover:bg-[#E9681F]"
                    >
                      შესვლა
                    </button>
                    <button
                      type="button"
                      onClick={() => navigate("/auth/reset-password", { state: { email: duplicateEmail } })}
                      className="px-3 py-1.5 bg-white border border-[#AE3534]/40 text-[#AE3534] font-semibold rounded-lg text-xs hover:bg-[#FAF7F2]"
                    >
                      პაროლის აღდგენა
                    </button>
                  </div>
                </div>
              ) : error ? (
                <div className="mb-4 p-3 bg-[#FBE9E8] border border-[#AE3534]/30 rounded-xl text-xs text-[#AE3534] flex items-start gap-2">
                  <span className="shrink-0">⚠️</span>
                  <span>{error}</span>
                </div>
              ) : null}

              {/* Registration Form */}
              <form onSubmit={handleAccountSubmit} className="flex flex-col gap-4">
                {/* 1. Email Field */}
                <div>
                  <label htmlFor="reg-email" className="block text-xs font-semibold text-[#222630] mb-1.5">
                    ელფოსტა
                  </label>
                  <div className="relative rounded-xl border border-[#D8D1C7] focus-within:border-[#9E4215] focus-within:ring-2 focus-within:ring-[#FF7A2F]/20 bg-[#FCFBF9] transition-all">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#8F8A83]">
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect width="20" height="16" x="2" y="4" rx="2" />
                        <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                      </svg>
                    </div>
                    <input
                      id="reg-email"
                      type="email"
                      required
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value);
                        if (error) setError(null);
                      }}
                      placeholder="example@domain.ge"
                      autoComplete="email"
                      autoCapitalize="none"
                      autoCorrect="off"
                      className="w-full pl-10 pr-3 py-2.5 text-sm text-[#222630] placeholder-[#8F8A83] bg-transparent focus:outline-none"
                    />
                  </div>
                </div>

                {/* 2. Password Field */}
                <div>
                  <label htmlFor="reg-password" className="block text-xs font-semibold text-[#222630] mb-1.5">
                    პაროლი
                  </label>
                  <div className="relative rounded-xl border border-[#D8D1C7] focus-within:border-[#9E4215] focus-within:ring-2 focus-within:ring-[#FF7A2F]/20 bg-[#FCFBF9] transition-all">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#8F8A83]">
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                      </svg>
                    </div>
                    <input
                      id="reg-password"
                      type={showPassword ? "text" : "password"}
                      required
                      minLength={6}
                      value={password}
                      onChange={(e) => {
                        setPassword(e.target.value);
                        if (error) setError(null);
                      }}
                      placeholder="••••••••"
                      autoComplete="new-password"
                      className="w-full pl-10 pr-10 py-2.5 text-sm text-[#222630] placeholder-[#8F8A83] bg-transparent focus:outline-none"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-[#8F8A83] hover:text-[#222630] transition-colors focus:outline-none"
                      aria-label={showPassword ? "პაროლის დამალვა" : "პაროლის ჩვენება"}
                    >
                      {showPassword ? (
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
                          <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
                          <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
                          <line x1="2" x2="22" y1="2" y2="22" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                          <circle cx="12" cy="12" r="3" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>

                {/* 3. Confirm Password Field */}
                <div>
                  <label htmlFor="reg-confirm-password" className="block text-xs font-semibold text-[#222630] mb-1.5">
                    გაიმეორე პაროლი
                  </label>
                  <div className="relative rounded-xl border border-[#D8D1C7] focus-within:border-[#9E4215] focus-within:ring-2 focus-within:ring-[#FF7A2F]/20 bg-[#FCFBF9] transition-all">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#8F8A83]">
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                      </svg>
                    </div>
                    <input
                      id="reg-confirm-password"
                      type={showConfirmPassword ? "text" : "password"}
                      required
                      minLength={6}
                      value={confirmPassword}
                      onChange={(e) => {
                        setConfirmPassword(e.target.value);
                        if (error) setError(null);
                      }}
                      placeholder="••••••••"
                      autoComplete="new-password"
                      className="w-full pl-10 pr-10 py-2.5 text-sm text-[#222630] placeholder-[#8F8A83] bg-transparent focus:outline-none"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-[#8F8A83] hover:text-[#222630] transition-colors focus:outline-none"
                      aria-label={showConfirmPassword ? "პაროლის დამალვა" : "პაროლის ჩვენება"}
                    >
                      {showConfirmPassword ? (
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
                          <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
                          <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
                          <line x1="2" x2="22" y1="2" y2="22" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                          <circle cx="12" cy="12" r="3" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>

                {/* Submit CTA Button */}
                <button
                  type="submit"
                  disabled={!isFormValid || loading}
                  className={`mt-2 w-full h-12 rounded-xl font-bold text-sm sm:text-base flex items-center justify-center gap-2 transition-all shadow-sm ${
                    isFormValid && !loading
                      ? "bg-[#FF7A2F] text-[#222630] hover:bg-[#E9681F] hover:shadow-md cursor-pointer active:scale-[0.99]"
                      : "bg-[#FF7A2F]/80 text-[#222630] cursor-pointer hover:bg-[#E9681F]"
                  }`}
                  style={{
                    backgroundColor: "#FF7A2F",
                    color: "#222630",
                  }}
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin h-5 w-5 text-[#222630]" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                      </svg>
                      <span>ანგარიშის შექმნა...</span>
                    </>
                  ) : (
                    <>
                      <span>ანგარიშის შექმნა</span>
                      <span className="text-lg">→</span>
                    </>
                  )}
                </button>
              </form>

              {/* Login link */}
              <div className="mt-4 text-center text-xs text-[#6A716F]">
                უკვე გაქვს ანგარიში?{" "}
                <Link
                  to="/auth/login"
                  className="font-bold text-[#C95618] hover:text-[#9E4215] underline-offset-2 hover:underline transition-colors"
                >
                  შესვლა
                </Link>
              </div>

              {/* Privacy / Security Notice */}
              <div className="mt-5 pt-4 border-t border-[#E6E0D7]/60 flex items-start gap-2.5 text-[11px] text-[#6A716F] leading-tight">
                <div className="w-4 h-4 rounded text-[#FF7A2F] shrink-0 mt-0.5">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                </div>
                <span>
                  შენი მონაცემები დაცულია და არ გადაეცემა მესამე პირებს. სრული კონფიდენციალურობა.
                </span>
              </div>

            </div>

            {/* Mobile Scenic Sunset Photograph (displayed below card on mobile) */}
            <div className="sm:hidden mt-6 w-full max-w-[440px] rounded-2xl overflow-hidden shadow-sm border border-[#E6E0D7]/60 relative">
              <div className="w-full h-36 relative overflow-hidden bg-[#FAF7F2]">
                <img
                  src={scenicSunsetImg}
                  alt="Couple looking at sunset over city"
                  className="w-full h-full object-cover object-center"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent pointer-events-none" />
                <div className="absolute bottom-2.5 right-3 text-right pointer-events-none">
                  <p
                    className="text-white text-[11px] italic font-medium leading-tight"
                    style={{
                      fontFamily: "'Noto Sans Georgian', Georgia, serif",
                      textShadow: "0 2px 4px rgba(0,0,0,0.6)",
                    }}
                  >
                    უფრო მეტი ვიდრე დამთხვევა <br />
                    <span className="font-semibold text-[#FFE7D7]">უფრო ნამდვილი კავშირი</span>
                  </p>
                </div>
              </div>
            </div>

          </div>

        </div>
      </main>
      {/* 3. Subtle Footer Spacing */}
      <footer className="w-full py-4 text-center text-xs text-[#6A716F]/70">
        JESTER • People Discovery & Relationship Intelligence
      </footer>
    </div>
  );
};

