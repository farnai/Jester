import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../core/auth/useAuth";
import { API } from "../../core/api/endpoints";
import { BirthDataPayload } from "../../core/api/types";
import { LoadingState } from "../../shared/StatusState";

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

export const BirthDataOnboardingPage: React.FC = () => {
  const { user, setHasBirthData } = useAuth();
  const navigate = useNavigate();

  const [loadingInitial, setLoadingInitial] = useState(true);
  const [isExistingData, setIsExistingData] = useState(false);

  const [birthDate, setBirthDate] = useState("");
  const [precision, setPrecision] = useState<"exact" | "approximate" | "unknown">("exact");
  const [birthTime, setBirthTime] = useState("12:00");
  const [timezone, setTimezone] = useState("Asia/Tbilisi");
  const [placeLabel, setPlaceLabel] = useState("Tbilisi, Georgia");
  const [latitude, setLatitude] = useState<string>("41.7151");
  const [longitude, setLongitude] = useState<string>("44.8271");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load existing birth data from PostgreSQL so user's true data is preserved and shown
  useEffect(() => {
    if (!user) return;
    let isMounted = true;

    API.astrology.getBirthData(user.id)
      .then((saved) => {
        if (!isMounted) return;
        if (saved) {
          setIsExistingData(true);
          if (saved.birth_date) setBirthDate(saved.birth_date);
          if (saved.birth_time_precision) setPrecision(saved.birth_time_precision);
          if (saved.birth_time) setBirthTime(saved.birth_time.slice(0, 5));
          if (saved.birth_timezone) setTimezone(saved.birth_timezone);
          if (saved.place_label) setPlaceLabel(saved.place_label);
          if (saved.latitude != null) setLatitude(saved.latitude.toString());
          if (saved.longitude != null) setLongitude(saved.longitude.toString());
        }
      })
      .catch((err) => {
        console.warn("Could not load existing birth data:", err);
      })
      .finally(() => {
        if (isMounted) setLoadingInitial(false);
      });

    return () => {
      isMounted = false;
    };
  }, [user]);

  const handleSelectPreset = (preset: CityPreset) => {
    setPlaceLabel(preset.place);
    setLatitude(preset.lat);
    setLongitude(preset.lon);
    setTimezone(preset.tz);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    if (!birthDate) {
      setError("გთხოვთ მიუთითოთ დაბადების თარიღი.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload: BirthDataPayload = {
        birth_date: birthDate,
        birth_time: precision === "unknown" ? null : `${birthTime}:00`,
        birth_time_precision: precision,
        birth_timezone: timezone,
        latitude: latitude ? parseFloat(latitude) : null,
        longitude: longitude ? parseFloat(longitude) : null,
        place_label: placeLabel || null,
      };

      await API.astrology.saveBirthData(user.id, payload);
      setHasBirthData(true);
      navigate("/me");
    } catch (err: any) {
      setError(err.message || "ასტროლოგიური მონაცემების შენახვა ვერ მოხერხდა.");
    } finally {
      setLoading(false);
    }
  };

  if (loadingInitial) {
    return <LoadingState message="ასტროლოგიური მონაცემების შემოწმება..." />;
  }

  return (
    <div
      style={{
        maxWidth: "540px",
        margin: "2rem auto",
        padding: "2rem",
        border: "1px solid #e2e8f0",
        borderRadius: "12px",
        backgroundColor: "#fff",
        boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
        <div>
          <h2 style={{ margin: 0, color: "#0f172a", fontSize: "1.35rem", fontWeight: 800 }}>
            {isExistingData ? "ასტროლოგიური მონაცემების რედაქტირება" : "ასტროლოგიური მონაცემები"}
          </h2>
          <p style={{ margin: "0.35rem 0 0 0", color: "#64748b", fontSize: "0.9rem" }}>
            {isExistingData
              ? "თქვენი შენახული დაბადების პარამეტრები. ცვლილების შემთხვევაში ნატალური რუკა გადაითვლება."
              : "შეიყვანეთ დაბადების პარამეტრები Swiss Ephemeris-ით ზუსტი ნატალური რუკის გამოსათვლელად."}
          </p>
        </div>
        {isExistingData && (
          <Link
            to="/me"
            style={{
              fontSize: "0.85rem",
              color: "#3b82f6",
              textDecoration: "none",
              fontWeight: 600,
              padding: "0.3rem 0.6rem",
              background: "#eff6ff",
              borderRadius: "6px",
            }}
          >
            გაუქმება
          </Link>
        )}
      </div>

      {error && (
        <div
          style={{
            padding: "0.75rem",
            marginBottom: "1rem",
            background: "#fff1f0",
            border: "1px solid #ff4d4f",
            borderRadius: "6px",
            color: "#cf1322",
            fontSize: "0.85rem",
          }}
        >
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
        <div>
          <label style={{ display: "block", marginBottom: "0.35rem", fontWeight: 700, fontSize: "0.85rem", color: "#1e293b" }}>
            დაბადების თარიღი (Date of Birth) *
          </label>
          <input
            type="date"
            required
            value={birthDate}
            onChange={(e) => setBirthDate(e.target.value)}
            style={{
              width: "100%",
              padding: "0.6rem",
              borderRadius: "6px",
              border: "1px solid #cbd5e1",
              fontSize: "0.95rem",
              boxSizing: "border-box",
            }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "0.35rem", fontWeight: 700, fontSize: "0.85rem", color: "#1e293b" }}>
            დროის სიზუსტე (Birth Time Precision)
          </label>
          <div style={{ display: "flex", gap: "1.25rem" }}>
            {[
              { key: "exact", label: "ზუსტი" },
              { key: "approximate", label: "მიახლოებითი" },
              { key: "unknown", label: "უცნობი" },
            ].map(({ key, label }) => (
              <label key={key} style={{ fontSize: "0.9rem", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.35rem" }}>
                <input
                  type="radio"
                  name="precision"
                  value={key}
                  checked={precision === key}
                  onChange={() => setPrecision(key as any)}
                />
                {label}
              </label>
            ))}
          </div>
        </div>

        {precision !== "unknown" ? (
          <div>
            <label style={{ display: "block", marginBottom: "0.35rem", fontWeight: 700, fontSize: "0.85rem", color: "#1e293b" }}>
              დაბადების დრო (24h)
            </label>
            <input
              type="time"
              required
              value={birthTime}
              onChange={(e) => setBirthTime(e.target.value)}
              style={{
                width: "100%",
                padding: "0.6rem",
                borderRadius: "6px",
                border: "1px solid #cbd5e1",
                fontSize: "0.95rem",
                boxSizing: "border-box",
              }}
            />
          </div>
        ) : (
          <div
            style={{
              padding: "0.75rem",
              background: "#f0fdf4",
              border: "1px solid #bbf7d0",
              borderRadius: "6px",
              color: "#166534",
              fontSize: "0.85rem",
            }}
          >
            ℹ️ <em>თუ დაბადების დრო უცნობია, ასცენდენტი და სახლები არ გამოითვლება. პლანეტები დალაგდება UTC 12:00 შუადღის მიხედვით.</em>
          </div>
        )}

        <div>
          <label style={{ display: "block", marginBottom: "0.35rem", fontWeight: 700, fontSize: "0.85rem", color: "#1e293b" }}>
            სწრაფი არჩევანი (ქალაქი)
          </label>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
            {CITY_PRESETS.map((preset) => (
              <button
                key={preset.label}
                type="button"
                onClick={() => handleSelectPreset(preset)}
                style={{
                  padding: "0.35rem 0.65rem",
                  fontSize: "0.8rem",
                  border: placeLabel === preset.place ? "1px solid #2563eb" : "1px solid #cbd5e1",
                  borderRadius: "6px",
                  background: placeLabel === preset.place ? "#eff6ff" : "#f8fafc",
                  color: placeLabel === preset.place ? "#1d4ed8" : "#334155",
                  cursor: "pointer",
                  fontWeight: placeLabel === preset.place ? 700 : 500,
                }}
              >
                📍 {preset.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "0.35rem", fontWeight: 700, fontSize: "0.85rem", color: "#1e293b" }}>
            დაბადების ქალაქი / ადგილი
          </label>
          <input
            type="text"
            value={placeLabel}
            onChange={(e) => setPlaceLabel(e.target.value)}
            style={{
              width: "100%",
              padding: "0.6rem",
              borderRadius: "6px",
              border: "1px solid #cbd5e1",
              fontSize: "0.95rem",
              boxSizing: "border-box",
            }}
            placeholder="მაგ. Tbilisi, Georgia"
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "0.35rem", fontWeight: 700, fontSize: "0.85rem", color: "#1e293b" }}>
            დროის სარტყელი (IANA Timezone) *
          </label>
          <input
            type="text"
            required
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
            style={{
              width: "100%",
              padding: "0.6rem",
              borderRadius: "6px",
              border: "1px solid #cbd5e1",
              fontSize: "0.95rem",
              boxSizing: "border-box",
            }}
            placeholder="მაგ. Asia/Tbilisi ან Europe/London"
          />
        </div>

        <div style={{ display: "flex", gap: "1rem" }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "0.35rem", fontSize: "0.8rem", color: "#64748b" }}>
              განედი (Latitude)
            </label>
            <input
              type="number"
              step="any"
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              style={{
                width: "100%",
                padding: "0.5rem",
                borderRadius: "6px",
                border: "1px solid #cbd5e1",
                fontSize: "0.85rem",
                boxSizing: "border-box",
              }}
              placeholder="41.7151"
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "0.35rem", fontSize: "0.8rem", color: "#64748b" }}>
              გრძედი (Longitude)
            </label>
            <input
              type="number"
              step="any"
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              style={{
                width: "100%",
                padding: "0.5rem",
                borderRadius: "6px",
                border: "1px solid #cbd5e1",
                fontSize: "0.85rem",
                boxSizing: "border-box",
              }}
              placeholder="44.8271"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "0.8rem",
            background: "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            fontWeight: 700,
            fontSize: "1rem",
            cursor: loading ? "not-allowed" : "pointer",
            marginTop: "0.5rem",
            transition: "background 0.15s ease",
          }}
        >
          {loading
            ? "მიმდინარეობს რუკის გამოთვლა..."
            : isExistingData
            ? "მონაცემების განახლება და რუკის გადათვლა"
            : "ნატალური რუკის გამოთვლა"}
        </button>
      </form>
    </div>
  );
};
