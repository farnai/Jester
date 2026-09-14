import React, { useState } from "react";
import { Button, Input } from "../../../shared/ui";

export interface PlacePreset {
  label: string;
  place: string;
  lat: number;
  lon: number;
  tz: string;
  country: string;
}

export const CANONICAL_PLACES: PlacePreset[] = [
  { label: "თბილისი (Tbilisi)", place: "Tbilisi, Georgia", lat: 41.7151, lon: 44.8271, tz: "Asia/Tbilisi", country: "Georgia" },
  { label: "ბათუმი (Batumi)", place: "Batumi, Georgia", lat: 41.6168, lon: 41.6367, tz: "Asia/Tbilisi", country: "Georgia" },
  { label: "ქუთაისი (Kutaisi)", place: "Kutaisi, Georgia", lat: 42.2662, lon: 42.7180, tz: "Asia/Tbilisi", country: "Georgia" },
  { label: "რუსთავი (Rustavi)", place: "Rustavi, Georgia", lat: 41.5495, lon: 45.0031, tz: "Asia/Tbilisi", country: "Georgia" },
  { label: "თელავი (Telavi)", place: "Telavi, Georgia", lat: 41.9198, lon: 45.4731, tz: "Asia/Tbilisi", country: "Georgia" },
  { label: "ზუგდიდი (Zugdidi)", place: "Zugdidi, Georgia", lat: 42.5088, lon: 41.8709, tz: "Asia/Tbilisi", country: "Georgia" },
  { label: "ლონდონი (London)", place: "London, United Kingdom", lat: 51.5074, lon: -0.1278, tz: "Europe/London", country: "UK" },
  { label: "ნიუ-იორკი (New York)", place: "New York, USA", lat: 40.7128, lon: -74.0060, tz: "America/New_York", country: "USA" },
  { label: "ბერლინი (Berlin)", place: "Berlin, Germany", lat: 52.5200, lon: 13.4050, tz: "Europe/Berlin", country: "Germany" },
  { label: "პარიზი (Paris)", place: "Paris, France", lat: 48.8566, lon: 2.3522, tz: "Europe/Paris", country: "France" },
  { label: "კიევი (Kyiv)", place: "Kyiv, Ukraine", lat: 50.4501, lon: 30.5234, tz: "Europe/Kyiv", country: "Ukraine" },
  { label: "ტოკიო (Tokyo)", place: "Tokyo, Japan", lat: 35.6762, lon: 139.6503, tz: "Asia/Tokyo", country: "Japan" },
];

interface BirthPlaceStepProps {
  placeLabel: string;
  setPlaceLabel: (val: string) => void;
  latitude: number | null;
  setLatitude: (val: number | null) => void;
  longitude: number | null;
  setLongitude: (val: number | null) => void;
  birthTimezone: string;
  setBirthTimezone: (val: string) => void;
  onNext: () => void;
  onBack: () => void;
}

export const BirthPlaceStep: React.FC<BirthPlaceStepProps> = ({
  placeLabel,
  setPlaceLabel,
  latitude,
  setLatitude,
  longitude,
  setLongitude,
  birthTimezone,
  setBirthTimezone,
  onNext,
  onBack,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSelectPreset = (p: PlacePreset) => {
    setPlaceLabel(p.place);
    setLatitude(p.lat);
    setLongitude(p.lon);
    setBirthTimezone(p.tz);
    setError(null);
  };

  const filteredPlaces = CANONICAL_PLACES.filter((p) => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      p.label.toLowerCase().includes(q) ||
      p.place.toLowerCase().includes(q) ||
      p.country.toLowerCase().includes(q)
    );
  });

  const validateAndProceed = (e: React.FormEvent) => {
    e.preventDefault();
    if (!placeLabel) {
      setError("გთხოვთ აირჩიოთ დაბადების ადგილი.");
      return;
    }
    if (latitude === null || longitude === null || !birthTimezone) {
      // Auto-fallback to Tbilisi if place was custom typed without coordinates
      const matched = CANONICAL_PLACES.find(
        (p) => p.place.toLowerCase().includes(placeLabel.toLowerCase()) ||
               p.label.toLowerCase().includes(placeLabel.toLowerCase())
      );
      if (matched) {
        setLatitude(matched.lat);
        setLongitude(matched.lon);
        setBirthTimezone(matched.tz);
      } else {
        // Default to Tbilisi coordinates
        setLatitude(41.7151);
        setLongitude(44.8271);
        setBirthTimezone("Asia/Tbilisi");
      }
    }

    onNext();
  };

  return (
    <form onSubmit={validateAndProceed} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h3 style={{ margin: "0 0 0.4rem 0", fontSize: "1.2rem", fontWeight: 700, color: "#0f172a" }}>
          4. დაბადების ადგილი (Birth Place)
        </h3>
        <p style={{ margin: "0 0 1.25rem 0", color: "#64748b", fontSize: "0.875rem" }}>
          დაბადების გეოგრაფიული ადგილი საჭიროა ასცენდენტისა და სახლების ზუსტი გამოთვლისთვის.
        </p>
      </div>

      {error && (
        <div
          style={{
            padding: "0.75rem",
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

      {/* Currently Selected Place */}
      {placeLabel && (
        <div
          style={{
            padding: "0.85rem 1rem",
            background: "#f8fafc",
            border: "1.5px solid #6366f1",
            borderRadius: "8px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: "0.75rem", color: "#6366f1", fontWeight: 700, textTransform: "uppercase" }}>
              არჩეული ადგილი (Selected Place)
            </div>
            <div style={{ fontSize: "1.05rem", fontWeight: 700, color: "#0f172a", marginTop: "2px" }}>
              📍 {placeLabel}
            </div>
          </div>
          <span style={{ fontSize: "1.2rem" }}>✅</span>
        </div>
      )}

      {/* Quick Search */}
      <Input
        label="ქალაქის ძებნა (Search city)"
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="მაგ. თბილისი, Batumi, London..."
      />

      {/* Popular Chips (Georgia) */}
      <div>
        <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#475569", marginBottom: "0.4rem" }}>
          პოპულარული ქალაქები (საქართველო):
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
          {CANONICAL_PLACES.slice(0, 6).map((p) => {
            const isSelected = placeLabel === p.place;
            return (
              <button
                key={p.place}
                type="button"
                onClick={() => handleSelectPreset(p)}
                style={{
                  padding: "0.4rem 0.75rem",
                  fontSize: "0.825rem",
                  fontWeight: isSelected ? 700 : 500,
                  borderRadius: "6px",
                  border: isSelected ? "1.5px solid #6366f1" : "1px solid #e2e8f0",
                  backgroundColor: isSelected ? "#eef2ff" : "#ffffff",
                  color: isSelected ? "#6366f1" : "#1e293b",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                }}
              >
                {p.label.split(" ")[0]}
              </button>
            );
          })}
        </div>
      </div>

      {/* Filtered list if searching or international */}
      {searchQuery && (
        <div style={{ maxHeight: "160px", overflowY: "auto", border: "1px solid #e2e8f0", borderRadius: "6px", padding: "0.4rem" }}>
          {filteredPlaces.length === 0 ? (
            <div style={{ padding: "0.5rem", fontSize: "0.825rem", color: "#94a3b8", textAlign: "center" }}>
              ქალაქი ვერ მოიძებნა.
            </div>
          ) : (
            filteredPlaces.map((p) => (
              <div
                key={p.place}
                onClick={() => handleSelectPreset(p)}
                style={{
                  padding: "0.5rem 0.75rem",
                  fontSize: "0.85rem",
                  cursor: "pointer",
                  borderRadius: "4px",
                  backgroundColor: placeLabel === p.place ? "#eef2ff" : "transparent",
                  color: placeLabel === p.place ? "#6366f1" : "#0f172a",
                  fontWeight: placeLabel === p.place ? 700 : 400,
                }}
              >
                📍 {p.place}
              </div>
            ))
          )}
        </div>
      )}

      <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem" }}>
        <Button
          type="button"
          variant="secondary"
          size="lg"
          style={{ flex: 1 }}
          onClick={onBack}
        >
          ⬅️ უკან
        </Button>
        <Button
          type="submit"
          variant="brand"
          size="lg"
          style={{ flex: 2 }}
          disabled={!placeLabel}
        >
          შემდეგი ➡️
        </Button>
      </div>
    </form>
  );
};
