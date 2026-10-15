import React from "react";
import { Link } from "react-router-dom";
import { Avatar, Badge, Button } from "../../../shared/ui";
import { ProfileResponse, ResolvedInterpretationModel } from "../../../core/api/types";

interface RelationshipHeaderProps {
  targetProfile?: ProfileResponse | null;
  viewerProfile?: ProfileResponse | null;
  score: number;
  dataQuality?: {
    confidence?: number;
    time_precision?: string;
  };
  interpretation?: ResolvedInterpretationModel | null;
}

export const RelationshipHeader: React.FC<RelationshipHeaderProps> = ({
  targetProfile,
  viewerProfile,
  score,
  dataQuality,
  interpretation,
}) => {
  const targetName = targetProfile?.display_name || "მომხმარებელი";
  const viewerName = viewerProfile?.display_name || "შენ";
  const confidencePercent = Math.round((dataQuality?.confidence ?? 0.85) * 100);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "1.25rem",
        backgroundColor: "var(--jester-surface-card)",
        border: "1px solid var(--jester-border-soft)",
        borderRadius: "16px",
        padding: "1.75rem 1.5rem",
        boxShadow: "0 2px 8px rgba(34, 38, 48, 0.04)",
      }}
    >
      {/* Top Navigation Row */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "0.5rem",
        }}
      >
        <Link
          to={targetProfile ? `/people/${targetProfile.id}` : "/discover"}
          style={{ textDecoration: "none" }}
        >
          <Button variant="ghost" size="sm" style={{ paddingLeft: 0, color: "var(--jester-text-secondary)" }}>
            ← {targetName}-ის პროფილი
          </Button>
        </Link>

        {/* Secondary Compact Score Pill */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Badge variant="score" size="md">
            {Math.round(score)}% სინერგია
          </Badge>
          {dataQuality?.confidence !== undefined && (
            <Badge variant="default" size="sm" style={{ color: "var(--jester-text-secondary)" }}>
              {confidencePercent}% სიზუსტე
            </Badge>
          )}
        </div>
      </div>

      {/* Relational Dual-Avatar Hero */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "1rem",
          marginTop: "0.25rem",
        }}
      >
        {/* Avatars Linked Together */}
        <div style={{ display: "flex", alignItems: "center", position: "relative" }}>
          <Avatar
            src={viewerProfile?.avatar_url}
            name={viewerName}
            size="lg"
            style={{
              border: "3px solid #ffffff",
              boxShadow: "0 2px 6px rgba(0, 0, 0, 0.08)",
              zIndex: 2,
            }}
          />
          <div
            style={{
              width: "24px",
              height: "2px",
              backgroundColor: "var(--jester-brand-orange-400)",
              margin: "0 -4px",
              zIndex: 1,
            }}
          />
          <Avatar
            src={targetProfile?.avatar_url}
            name={targetName}
            size="lg"
            style={{
              border: "3px solid #ffffff",
              boxShadow: "0 2px 6px rgba(0, 0, 0, 0.08)",
              zIndex: 2,
            }}
          />
        </div>

        {/* Framing & Headline */}
        <div>
          <div
            style={{
              fontSize: "0.8rem",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: "var(--jester-brand-orange-800)",
              marginBottom: "0.2rem",
            }}
          >
            ME + YOU • ურთიერთობის დინამიკა
          </div>
          <h1
            style={{
              margin: 0,
              fontSize: "1.35rem",
              fontWeight: 800,
              color: "var(--jester-text-primary)",
              lineHeight: 1.25,
            }}
          >
            რა ხდება შენსა და {targetName}-ს შორის?
          </h1>
        </div>
      </div>

      {/* Primary Relational Hook if available */}
      {interpretation?.hook && (
        <div
          style={{
            backgroundColor: "var(--jester-accent-peach-soft)",
            borderLeft: "3px solid var(--jester-brand-orange-500)",
            padding: "0.75rem 1rem",
            borderRadius: "0 8px 8px 0",
            fontSize: "0.95rem",
            fontWeight: 500,
            color: "var(--jester-text-primary)",
            lineHeight: 1.4,
          }}
        >
          „{interpretation.hook}“
        </div>
      )}
    </div>
  );
};
