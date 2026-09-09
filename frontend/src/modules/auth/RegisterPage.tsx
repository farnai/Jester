import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { supabase } from "../../core/realtime/supabase";
import { useAuth } from "../../core/auth/useAuth";
import { API } from "../../core/api/endpoints";
import { BirthDataPayload } from "../../core/api/types";

interface CityPreset {
  label: string;
  place: string;
  lat: string;
  lon: string;
  tz: string;
}

const CITY_PRESETS: CityPreset[] = [
  { label: "თბილისი", place: "Tbilisi, Georgia", lat: "41.7151", lon: "44.8271", tz: "Asia/Tbilisi" },
  { label: "ბათუმი", place: "Batumi, Georgia", lat: "41.6168", lon: "41.6367", tz: "Asia/Tbilisi" },
  { label: "ქუთაისი", place: "Kutaisi, Georgia", lat: "42.2662", lon: "42.7180", tz: "Asia/Tbilisi" },
  { label: "რუსთავი", place: "Rustavi, Georgia", lat: "41.5495", lon: "45.0031", tz: "Asia/Tbilisi" },
  { label: "თელავი", place: "Telavi, Georgia", lat: "41.9198", lon: "45.4731", tz: "Asia/Tbilisi" },
  { label: "ზუგდიდი", place: "Zugdidi, Georgia", lat: "42.5088", lon: "41.8709", tz: "Asia/Tbilisi" },
];

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { setHasBirthData, refreshBirthDataCheck } = useAuth();

  // Current wizard step: 1 to 5
  const [step, setStep] = useState<number>(1);

  // Step 1: Account
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // Step 2: Profile
  const [displayName, setDisplayName] = useState("");
  const [city, setCity] = useState("");
  const [occupation, setOccupation] = useState("");

  // Step 3: Birth Date & Time
  const [birthDate, setBirthDate] = useState("1996-04-12");
  const [precision, setPrecision] = useState<"exact" | "approximate" | "unknown">("exact");
  const [birthTime, setBirthTime] = useState("14:30");

  // Step 4: Location & Timezone
  const [placeLabel, setPlaceLabel] = useState("Tbilisi, Georgia");
  const [latitude, setLatitude] = useState("41.7151");
  const [longitude, setLongitude] = useState("44.8271");
  const [timezone, setTimezone] = useState("Asia/Tbilisi");

  // Submission / Loading state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Quick preset selector
  const handleSelectPreset = (preset: CityPreset) => {
    setPlaceLabel(preset.place);
    setLatitude(preset.lat);
    setLongitude(preset.lon);
    setTimezone(preset.tz);
    if (!city) {
      setCity(preset.label);
    }
  };

  // Step 1 Validation
  const canGoToStep2 = email.trim().includes("@") && password.length >= 6;

  // Step 2 Validation
  const canGoToStep3 = displayName.trim().length > 0;

  // Step 3 Validation
  const canGoToStep4 =
    birthDate.trim().length > 0 &&
    (precision === "unknown" || birthTime.trim().length > 0);

  // Final Registration & Persistence Handler
  const handleFinalSubmit = async () => {
    setLoading(true);
    setError(null);

    try {
      // 1. Create account via Supabase Auth
      let activeUser: any = null;
      let activeSession: any = null;

      const { data: authData, error: authError } = await supabase.auth.signUp({
        email: email.trim(),
        password,
      });

      if (authError) {
        // If user was already registered in a previous attempt, sign in directly
        const errMsg = authError.message.toLowerCase();
        if (errMsg.includes("already registered") || errMsg.includes("exists")) {
          const { data: signInData, error: signInErr } = await supabase.auth.signInWithPassword({
            email: email.trim(),
            password,
          });
          if (signInErr) {
            throw new Error(signInErr.message);
          }
          activeUser = signInData.user;
          activeSession = signInData.session;
        } else {
          throw new Error(authError.message);
        }
      } else {
        activeUser = authData.user;
        activeSession = authData.session;
      }

      // If session wasn't returned directly, sign in to acquire access token
      if (!activeSession) {
        const { data: signInData, error: signInErr } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        });
        if (signInErr) {
          throw new Error(signInErr.message);
        }
        activeUser = signInData.user;
        activeSession = signInData.session;
      }

      if (!activeUser) {
        throw new Error("მომხმარებლის შექმნა ვერ მოხერხდა.");
      }

      // Explicitly set session on Supabase client to ensure storage is populated
      if (activeSession) {
        await supabase.auth.setSession({
          access_token: activeSession.access_token,
          refresh_token: activeSession.refresh_token,
        });
      }

      // 2. Save public profile
      const { error: profileErr } = await supabase.from("profiles").upsert({
        id: activeUser.id,
        display_name: displayName.trim() || email.split("@")[0],
        city: city.trim() || null,
        occupation: occupation.trim() || null,
        timezone: timezone || "UTC",
        is_discoverable: true,
        updated_at: new Date().toISOString(),
      });

      if (profileErr) {
        console.warn("Profile save warning:", profileErr.message);
      }

      // 3. Save private birth data & trigger Swiss Ephemeris calculation
      const birthPayload: BirthDataPayload = {
        birth_date: birthDate,
        birth_time: precision === "unknown" ? null : `${birthTime}:00`,
        birth_time_precision: precision,
        birth_timezone: timezone,
        latitude: latitude ? parseFloat(latitude) : null,
        longitude: longitude ? parseFloat(longitude) : null,
        place_label: placeLabel || null,
      };

      await API.astrology.saveBirthData(activeUser.id, birthPayload);

      // 4. Update auth state and refresh
      setHasBirthData(true);
      await refreshBirthDataCheck(activeUser.id);

      // 5. Navigate straight to ME page
      navigate("/me", { replace: true });
    } catch (err: any) {
      setError(err.message || "რეგისტრაციისას დაფიქსირდა შეცდომა.");
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
      <div
        style={{
          width: "100%",
          maxWidth: "500px",
          background: "#fff",
          border: "1px solid #d9d9d9",
          borderRadius: "8px",
          padding: "2rem",
          boxSizing: "border-box",
        }}
      >
        {/* Step Indicator */}
        <div style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", color: "#666", marginBottom: "0.5rem" }}>
            <span>ეტაპობრივი რეგისტრაცია</span>
            <span>ნაბიჯი {step} / 5</span>
          </div>
          <div style={{ height: "4px", width: "100%", background: "#f0f0f0", borderRadius: "2px", overflow: "hidden" }}>
            <div
              style={{
                height: "100%",
                width: `${(step / 5) * 100}%`,
                background: "#1890ff",
                transition: "width 0.3s ease",
              }}
            />
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div
            style={{
              padding: "0.75rem",
              marginBottom: "1.2rem",
              background: "#fff1f0",
              border: "1px solid #ff4d4f",
              borderRadius: "4px",
              color: "#cf1322",
              fontSize: "0.85rem",
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {/* STEP 1: ACCOUNT CREDENTIALS */}
        {step === 1 && (
          <div>
            <h3 style={{ marginTop: 0, marginBottom: "0.5rem" }}>1. ანგარიშის შექმნა</h3>
            <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "1.2rem" }}>
              შეიყვანეთ ელფოსტა და პაროლი სისტემაში შემოსასვლელად.
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div>
                <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
                  ელფოსტა (Email) *
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={{ width: "100%", padding: "0.55rem", boxSizing: "border-box" }}
                  placeholder="name@example.com"
                />
              </div>

              <div>
                <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
                  პაროლი (Password) *
                </label>
                <input
                  type="password"
                  required
                  minLength={6}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{ width: "100%", padding: "0.55rem", boxSizing: "border-box" }}
                  placeholder="მინიმუმ 6 სიმბოლო"
                />
              </div>

              <button
                type="button"
                disabled={!canGoToStep2}
                onClick={() => setStep(2)}
                style={{
                  marginTop: "0.5rem",
                  padding: "0.65rem",
                  background: canGoToStep2 ? "#1890ff" : "#d9d9d9",
                  color: "#fff",
                  border: "none",
                  borderRadius: "4px",
                  fontWeight: "bold",
                  cursor: canGoToStep2 ? "pointer" : "not-allowed",
                }}
              >
                შემდეგი ➡️
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: PROFILE & IDENTITY */}
        {step === 2 && (
          <div>
            <h3 style={{ marginTop: 0, marginBottom: "0.5rem" }}>2. პირადი პროფილი</h3>
            <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "1.2rem" }}>
              როგორ გაგიცნონ სხვებმა JESTER-ის ქსელში.
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div>
                <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
                  თქვენი სახელი / Display Name *
                </label>
                <input
                  type="text"
                  required
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  style={{ width: "100%", padding: "0.55rem", boxSizing: "border-box" }}
                  placeholder="მაგ. ალექსანდრე, ანა"
                />
              </div>

              <div>
                <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
                  ქალაქი (City)
                </label>
                <input
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  style={{ width: "100%", padding: "0.55rem", boxSizing: "border-box" }}
                  placeholder="მაგ. თბილისი, ბათუმი"
                />
              </div>

              <div>
                <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
                  საქმიანობა / პროფესია (Occupation)
                </label>
                <input
                  type="text"
                  value={occupation}
                  onChange={(e) => setOccupation(e.target.value)}
                  style={{ width: "100%", padding: "0.55rem", boxSizing: "border-box" }}
                  placeholder="მაგ. დიზაინერი, დეველოპერი, არქიტექტორი"
                />
              </div>

              <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  style={{
                    flex: 1,
                    padding: "0.65rem",
                    background: "#f0f0f0",
                    color: "#333",
                    border: "1px solid #d9d9d9",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  ⬅️ უკან
                </button>
                <button
                  type="button"
                  disabled={!canGoToStep3}
                  onClick={() => setStep(3)}
                  style={{
                    flex: 1,
                    padding: "0.65rem",
                    background: canGoToStep3 ? "#1890ff" : "#d9d9d9",
                    color: "#fff",
                    border: "none",
                    borderRadius: "4px",
                    fontWeight: "bold",
                    cursor: canGoToStep3 ? "pointer" : "not-allowed",
                  }}
                >
                  შემდეგი ➡️
                </button>
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: BIRTH DATE & TIME */}
        {step === 3 && (
          <div>
            <h3 style={{ marginTop: 0, marginBottom: "0.5rem" }}>3. დაბადების თარიღი და დრო</h3>
            <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "1.2rem" }}>
              ეს მონაცემები საჭიროა ასტრონომიული კალკულაციისთვის (მზე, მთვარე, ასცენდენტი).
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div>
                <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
                  დაბადების თარიღი *
                </label>
                <input
                  type="date"
                  required
                  value={birthDate}
                  onChange={(e) => setBirthDate(e.target.value)}
                  style={{ width: "100%", padding: "0.55rem", boxSizing: "border-box" }}
                />
              </div>

              <div>
                <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
                  დროის სიზუსტე
                </label>
                <select
                  value={precision}
                  onChange={(e) => setPrecision(e.target.value as any)}
                  style={{ width: "100%", padding: "0.55rem", boxSizing: "border-box" }}
                >
                  <option value="exact">ზუსტი დრო ვიცი (Exact)</option>
                  <option value="approximate">მიახლოებით ვიცი (Approximate)</option>
                  <option value="unknown">დრო არ ვიცი (Unknown - შუადღის საშუალო)</option>
                </select>
              </div>

              {precision !== "unknown" && (
                <div>
                  <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
                    დაბადების დრო (24-საათიანი) *
                  </label>
                  <input
                    type="time"
                    required
                    value={birthTime}
                    onChange={(e) => setBirthTime(e.target.value)}
                    style={{ width: "100%", padding: "0.55rem", boxSizing: "border-box" }}
                  />
                  <div style={{ fontSize: "0.75rem", color: "#888", marginTop: "0.2rem" }}>
                    ზუსტი დრო განსაზღვრავს თქვენს ასცენდენტსა (Rising) და სახლებს.
                  </div>
                </div>
              )}

              {precision === "unknown" && (
                <div style={{ padding: "0.6rem", background: "#f6ffed", border: "1px solid #b7eb8f", borderRadius: "4px", fontSize: "0.8rem", color: "#389e0d" }}>
                  ℹ️ დროის გარეშე გაითვლება პლანეტების პოზიციები 12:00 UTC-ზე (ასცენდენტი გამოტოვებული იქნება).
                </div>
              )}

              <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  style={{
                    flex: 1,
                    padding: "0.65rem",
                    background: "#f0f0f0",
                    color: "#333",
                    border: "1px solid #d9d9d9",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  ⬅️ უკან
                </button>
                <button
                  type="button"
                  disabled={!canGoToStep4}
                  onClick={() => setStep(4)}
                  style={{
                    flex: 1,
                    padding: "0.65rem",
                    background: canGoToStep4 ? "#1890ff" : "#d9d9d9",
                    color: "#fff",
                    border: "none",
                    borderRadius: "4px",
                    fontWeight: "bold",
                    cursor: canGoToStep4 ? "pointer" : "not-allowed",
                  }}
                >
                  შემდეგი ➡️
                </button>
              </div>
            </div>
          </div>
        )}

        {/* STEP 4: LOCATION & TIMEZONE */}
        {step === 4 && (
          <div>
            <h3 style={{ marginTop: 0, marginBottom: "0.5rem" }}>4. დაბადების ადგილი</h3>
            <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "0.8rem" }}>
              აირჩიეთ ქალაქი ან შეიყვანეთ კოორდინატები ასცენდენტის გამოსათვლელად.
            </p>

            {/* Quick Presets */}
            <div style={{ marginBottom: "1rem" }}>
              <div style={{ fontSize: "0.8rem", fontWeight: "bold", marginBottom: "0.4rem" }}>
                სწრაფი არჩევანი (საქართველო):
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                {CITY_PRESETS.map((p) => (
                  <button
                    key={p.label}
                    type="button"
                    onClick={() => handleSelectPreset(p)}
                    style={{
                      padding: "0.3rem 0.6rem",
                      fontSize: "0.8rem",
                      border: placeLabel === p.place ? "1px solid #1890ff" : "1px solid #d9d9d9",
                      background: placeLabel === p.place ? "#e6f7ff" : "#fafafa",
                      color: placeLabel === p.place ? "#1890ff" : "#333",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "0.8rem" }}>
              <div>
                <label style={{ display: "block", marginBottom: "0.2rem", fontWeight: "bold", fontSize: "0.8rem" }}>
                  ადგილის დასახელება
                </label>
                <input
                  type="text"
                  value={placeLabel}
                  onChange={(e) => setPlaceLabel(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
                  placeholder="მაგ. Tbilisi, Georgia"
                />
              </div>

              <div style={{ display: "flex", gap: "0.5rem" }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: "block", marginBottom: "0.2rem", fontWeight: "bold", fontSize: "0.8rem" }}>
                    განედი (Latitude)
                  </label>
                  <input
                    type="text"
                    value={latitude}
                    onChange={(e) => setLatitude(e.target.value)}
                    style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
                    placeholder="41.7151"
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: "block", marginBottom: "0.2rem", fontWeight: "bold", fontSize: "0.8rem" }}>
                    გრძედი (Longitude)
                  </label>
                  <input
                    type="text"
                    value={longitude}
                    onChange={(e) => setLongitude(e.target.value)}
                    style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
                    placeholder="44.8271"
                  />
                </div>
              </div>

              <div>
                <label style={{ display: "block", marginBottom: "0.2rem", fontWeight: "bold", fontSize: "0.8rem" }}>
                  დროის სარტყელი (Timezone)
                </label>
                <input
                  type="text"
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
                  placeholder="Asia/Tbilisi"
                />
              </div>

              <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
                <button
                  type="button"
                  onClick={() => setStep(3)}
                  style={{
                    flex: 1,
                    padding: "0.65rem",
                    background: "#f0f0f0",
                    color: "#333",
                    border: "1px solid #d9d9d9",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  ⬅️ უკან
                </button>
                <button
                  type="button"
                  onClick={() => setStep(5)}
                  style={{
                    flex: 1,
                    padding: "0.65rem",
                    background: "#1890ff",
                    color: "#fff",
                    border: "none",
                    borderRadius: "4px",
                    fontWeight: "bold",
                    cursor: "pointer",
                  }}
                >
                  შემდეგი ➡️
                </button>
              </div>
            </div>
          </div>
        )}

        {/* STEP 5: SUMMARY & CONFIRMATION */}
        {step === 5 && (
          <div>
            <h3 style={{ marginTop: 0, marginBottom: "0.5rem" }}>5. შეჯამება და დამახსოვრება</h3>
            <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "1rem" }}>
              გადაამოწმეთ შეყვანილი მონაცემები. ღილაკზე დაჭერისას მონაცემები შეინახება და დაითვლება თქვენი რუკა.
            </p>

            <div
              style={{
                background: "#fafafa",
                border: "1px solid #e8e8e8",
                borderRadius: "6px",
                padding: "1rem",
                fontSize: "0.85rem",
                display: "flex",
                flexDirection: "column",
                gap: "0.6rem",
                marginBottom: "1.2rem",
              }}
            >
              <div>
                <strong>👤 ანგარიში:</strong> {email}
              </div>
              <div>
                <strong>✨ სახელი:</strong> {displayName}
              </div>
              {city && (
                <div>
                  <strong>🏙️ ქალაქი:</strong> {city}
                </div>
              )}
              {occupation && (
                <div>
                  <strong>💼 საქმიანობა:</strong> {occupation}
                </div>
              )}
              <div>
                <strong>📅 დაბადების თარიღი:</strong> {birthDate}
              </div>
              <div>
                <strong>⏰ დრო:</strong>{" "}
                {precision === "unknown" ? "უცნობია (შუადღე)" : `${birthTime} (${precision})`}
              </div>
              <div>
                <strong>📍 ადგილი:</strong> {placeLabel} ({latitude}, {longitude})
              </div>
              <div>
                <strong>🌐 დროის სარტყელი:</strong> {timezone}
              </div>
            </div>

            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button
                type="button"
                disabled={loading}
                onClick={() => setStep(4)}
                style={{
                  flex: 1,
                  padding: "0.7rem",
                  background: "#f0f0f0",
                  color: "#333",
                  border: "1px solid #d9d9d9",
                  borderRadius: "4px",
                  cursor: loading ? "not-allowed" : "pointer",
                }}
              >
                ⬅️ უკან
              </button>
              <button
                type="button"
                disabled={loading}
                onClick={handleFinalSubmit}
                style={{
                  flex: 2,
                  padding: "0.7rem",
                  background: loading ? "#87d068" : "#52c41a",
                  color: "#fff",
                  border: "none",
                  borderRadius: "4px",
                  fontWeight: "bold",
                  cursor: loading ? "not-allowed" : "pointer",
                  fontSize: "0.9rem",
                }}
              >
                {loading ? "⌛ ინახება და ითვლება..." : "🚀 დარეგისტრირება და რუკის გამოთვლა"}
              </button>
            </div>
          </div>
        )}

        <div style={{ marginTop: "1.5rem", textAlign: "center", fontSize: "0.85rem", borderTop: "1px solid #f0f0f0", paddingTop: "1rem" }}>
          უკვე გაქვთ ანგარიში? <Link to="/auth/login" style={{ color: "#1890ff", fontWeight: "bold" }}>შესვლა</Link>
        </div>
      </div>
    </div>
  );
};
