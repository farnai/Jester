import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../core/auth/useAuth";
import { API } from "../../core/api/endpoints";
import { BirthDataPayload } from "../../core/api/types";

export const BirthDataOnboardingPage: React.FC = () => {
  const { user, setHasBirthData } = useAuth();
  const navigate = useNavigate();

  const [birthDate, setBirthDate] = useState("1996-05-15");
  const [precision, setPrecision] = useState<"exact" | "approximate" | "unknown">("exact");
  const [birthTime, setBirthTime] = useState("14:30");
  const [timezone, setTimezone] = useState("America/New_York");
  const [placeLabel, setPlaceLabel] = useState("New York, NY");
  const [latitude, setLatitude] = useState<string>("40.7128");
  const [longitude, setLongitude] = useState<string>("-74.0060");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
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
      navigate("/self/astrology");
    } catch (err: any) {
      setError(err.message || "Failed to calculate natal astrology.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: "540px",
        margin: "2rem auto",
        padding: "2rem",
        border: "1px solid #d9d9d9",
        borderRadius: "6px",
        backgroundColor: "#fff",
      }}
    >
      <h2 style={{ marginTop: 0 }}>Astrological Onboarding</h2>
      <p style={{ color: "#666", fontSize: "0.9rem" }}>
        Enter your birth parameters to calculate your deterministic natal placements and chart.
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

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
        <div>
          <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
            Date of Birth
          </label>
          <input
            type="date"
            required
            value={birthDate}
            onChange={(e) => setBirthDate(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
            Birth Time Precision
          </label>
          <div style={{ display: "flex", gap: "1rem" }}>
            {(["exact", "approximate", "unknown"] as const).map((p) => (
              <label key={p} style={{ fontSize: "0.9rem", cursor: "pointer" }}>
                <input
                  type="radio"
                  name="precision"
                  value={p}
                  checked={precision === p}
                  onChange={() => setPrecision(p)}
                />{" "}
                {p.charAt(0).toUpperCase() + p.slice(1)}
              </label>
            ))}
          </div>
        </div>

        {precision !== "unknown" ? (
          <div>
            <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
              Exact / Approximate Birth Time (24h)
            </label>
            <input
              type="time"
              required
              value={birthTime}
              onChange={(e) => setBirthTime(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
            />
          </div>
        ) : (
          <div
            style={{
              padding: "0.75rem",
              background: "#f6ffed",
              border: "1px solid #b7eb8f",
              borderRadius: "4px",
              color: "#389e0d",
              fontSize: "0.85rem",
            }}
          >
            ℹ️ <em>Birth time unknown — some chart details, including Ascendant, cannot be calculated precisely. (Planets will be calculated for 12:00 UTC mean noon).</em>
          </div>
        )}

        <div>
          <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
            Birth Timezone (IANA)
          </label>
          <input
            type="text"
            required
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
            placeholder="e.g. America/New_York or UTC"
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
            Birth City / Location
          </label>
          <input
            type="text"
            value={placeLabel}
            onChange={(e) => setPlaceLabel(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
            placeholder="e.g. London, UK"
          />
        </div>

        <div style={{ display: "flex", gap: "1rem" }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "0.3rem", fontSize: "0.8rem", color: "#555" }}>
              Latitude (optional for houses)
            </label>
            <input
              type="number"
              step="any"
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              style={{ width: "100%", padding: "0.4rem", boxSizing: "border-box" }}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "0.3rem", fontSize: "0.8rem", color: "#555" }}>
              Longitude (optional for houses)
            </label>
            <input
              type="number"
              step="any"
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              style={{ width: "100%", padding: "0.4rem", boxSizing: "border-box" }}
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "0.7rem",
            background: "#1890ff",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            fontWeight: "bold",
            fontSize: "1rem",
            cursor: loading ? "not-allowed" : "pointer",
            marginTop: "0.5rem",
          }}
        >
          {loading ? "Calculating Chart with Swiss Ephemeris..." : "Calculate Natal Astrology"}
        </button>
      </form>
    </div>
  );
};
