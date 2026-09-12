import React from "react";
import { Link } from "react-router-dom";
import { DiscoveryPerson } from "../../core/api/types";
import { Card, Button, Badge, Avatar } from "../../shared/ui";
import { RuntimeJson } from "../../shared/runtime/RuntimeJson";

export interface PersonCardProps {
  person: DiscoveryPerson;
  connectionStatus?: "none" | "pending_out" | "pending_in" | "accepted" | "blocked";
}

export const PersonCard: React.FC<PersonCardProps> = ({ person, connectionStatus = "none" }) => {
  const score = Math.round(person.compatibility_score ?? 60);
  const hookText = person.hook_observation?.text;

  // Sign labels in Georgian
  const sunSign = person.astrology?.sun_sign;
  const moonSign = person.astrology?.moon_sign;
  const ascendantSign = person.astrology?.ascendant_sign;

  return (
    <Card
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        padding: "1.5rem",
        gap: "1.25rem",
        borderRadius: "16px",
        transition: "transform 0.2s ease, box-shadow 0.2s ease",
      }}
      className="person-discover-card"
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {/* 1. Header: Avatar + Identity + Curiosity Score */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.85rem" }}>
          <div style={{ display: "flex", gap: "0.85rem", alignItems: "center" }}>
            <Avatar
              src={person.avatar_url}
              name={person.display_name}
              size="lg"
            />
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", flexWrap: "wrap" }}>
                <h3
                  style={{
                    margin: 0,
                    fontWeight: 800,
                    fontSize: "1.1rem",
                    color: "#0f172a",
                    letterSpacing: "-0.01em",
                  }}
                >
                  {person.display_name}
                </h3>
                {connectionStatus === "accepted" && (
                  <Badge variant="brand" size="sm">
                    ✓ დაკავშირებული
                  </Badge>
                )}
                {connectionStatus === "pending_out" && (
                  <Badge variant="outline" size="sm" style={{ color: "#d97706", borderColor: "#fde68a" }}>
                    ⏳ მოთხოვნა გაგზავნილია
                  </Badge>
                )}
                {connectionStatus === "pending_in" && (
                  <Badge variant="outline" size="sm" style={{ color: "#2563eb", borderColor: "#bfdbfe" }}>
                    📩 მოთხოვნა შემოსულია
                  </Badge>
                )}
              </div>

              {(person.occupation || person.city) && (
                <div style={{ fontSize: "0.825rem", color: "#64748b", marginTop: "0.2rem", fontWeight: 500 }}>
                  {[person.occupation, person.city].filter(Boolean).join(" • ")}
                </div>
              )}
            </div>
          </div>

          {/* Curiosity Score Pill */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: "#faf5ff",
              border: "1px solid #e9d5ff",
              borderRadius: "12px",
              padding: "0.35rem 0.65rem",
              minWidth: "48px",
              flexShrink: 0,
            }}
            title="სინასტრიული თანხვედრის ინდექსი (Curiosity Score)"
          >
            <span style={{ fontSize: "1.15rem", fontWeight: 800, color: "#9333ea", lineHeight: 1 }}>
              {score}
            </span>
            <span
              style={{
                fontSize: "0.6rem",
                fontWeight: 700,
                color: "#a855f7",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                marginTop: "0.15rem",
              }}
            >
              თანხვედრა
            </span>
          </div>
        </div>

        {/* 2. JESTER Human-First Hook / Observation & Discovery Signal Metadata */}
        {hookText ? (
          <div
            style={{
              padding: "0.875rem 1rem",
              backgroundColor: "rgba(248, 250, 252, 0.9)",
              borderLeft: "3px solid #9333ea",
              borderRadius: "0 10px 10px 0",
              fontSize: "0.875rem",
              color: "#334155",
              lineHeight: 1.55,
              position: "relative",
            }}
          >
            <div
              style={{
                fontSize: "0.7rem",
                fontWeight: 700,
                color: "#7e22ce",
                textTransform: "uppercase",
                letterSpacing: "0.06em",
                marginBottom: "0.3rem",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "0.3rem",
              }}
            >
              <span>💡 JESTER-ის ხედვა (Discovery Presence)</span>
              <span style={{ fontSize: "0.65rem", color: "#64748b", fontFamily: "ui-monospace, monospace" }}>
                Source: {person.presence_sign_source || (ascendantSign ? "ascendant" : "sun")} ({person.presence_sign || ascendantSign || sunSign || "aries"})
              </span>
            </div>
            <div style={{ fontStyle: "normal", marginBottom: "0.4rem" }}>{hookText}</div>
            {person.hook_observation?.content_asset_id && (
              <div style={{ fontSize: "0.7rem", color: "#64748b", fontFamily: "ui-monospace, monospace", borderTop: "1px dashed #e2e8f0", paddingTop: "0.25rem" }}>
                Asset: <code>{person.hook_observation.content_asset_id}</code> | Status: <span style={{ color: "#059669", fontWeight: 600 }}>{person.hook_observation.content_status || "approved"}</span>
              </div>
            )}
          </div>
        ) : person.bio ? (
          <p
            style={{
              fontSize: "0.875rem",
              color: "#475569",
              margin: 0,
              lineHeight: 1.5,
              display: "-webkit-box",
              WebkitLineClamp: 3,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
            }}
          >
            {person.bio}
          </p>
        ) : null}

        {/* 3. Supporting Safe Astrology Chips (Deterministic Intelligence Layer) */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
          {sunSign && (
            <Badge variant="astrology" size="sm">
              ☀️ {sunSign}
            </Badge>
          )}
          {moonSign && (
            <Badge variant="default" size="sm">
              🌙 {moonSign}
            </Badge>
          )}
          {ascendantSign && (
            <Badge variant="default" size="sm">
              ⬆️ {ascendantSign}
            </Badge>
          )}
          {person.astrology?.element_primary && (
            <Badge variant="outline" size="sm">
              {person.astrology.element_primary}
            </Badge>
          )}
        </div>
      </div>

      {/* 4. Action Row: Primary "რატომ?" (Why) + Secondary "პროფილი" (Profile) */}
      <div style={{ display: "flex", gap: "0.6rem", alignItems: "center", paddingTop: "0.25rem" }}>
        <Link to={`/people/${person.id}/why`} style={{ flex: 1, textDecoration: "none" }}>
          <Button
            variant="brand"
            size="md"
            fullWidth
            style={{ minHeight: "44px", fontWeight: 700 }}
          >
            რატომ? (Why) →
          </Button>
        </Link>
        <Link to={`/people/${person.id}`} style={{ textDecoration: "none" }}>
          <Button
            variant="outline"
            size="md"
            style={{ minHeight: "44px", padding: "0 1.1rem" }}
          >
            პროფილი
          </Button>
        </Link>
      </div>

      <RuntimeJson data={person} label={`Pipeline Data (${person.display_name})`} />
    </Card>
  );
};
