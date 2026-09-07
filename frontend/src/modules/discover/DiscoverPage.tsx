import React from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { useAuth } from "../../core/auth/useAuth";
import { DiscoveryPerson } from "../../core/api/types";
import { Card, Button, Badge, Avatar, LoadingState, ErrorState, EmptyState } from "../../shared/ui";

export const DiscoverPage: React.FC = () => {
  const { user } = useAuth();

  const { data: people, isLoading, error, refetch } = useQuery<DiscoveryPerson[]>({
    queryKey: ["discovery-people", user?.id],
    queryFn: () => API.interpretations.getDiscoveryPeople(user?.id),
    enabled: !!user?.id,
  });

  if (isLoading) {
    return <LoadingState message="ადამიანების აღმოჩენა და სინასტრიული რუკების შედარება..." />;
  }

  if (error) {
    return <ErrorState error={error as Error} onRetry={refetch} />;
  }

  const list = people || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "0.75rem" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "1.5rem" }}>🧭</span>
            <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 800, color: "#0f172a" }}>
              აღმოაჩინე ადამიანები
            </h1>
          </div>
          <p style={{ margin: "0.25rem 0 0 0", color: "#64748b", fontSize: "0.9rem" }}>
            პროფილები გაანგარიშებული სინასტრიული თანხვედრითა და JESTER-ის დაკვირვებებით.
          </p>
        </div>

        <Badge variant="brand" size="md">
          {list.length} ადამიანი
        </Badge>
      </div>

      {list.length === 0 ? (
        <EmptyState
          title="ახალი ადამიანები ვერ მოიძებნა"
          description="ამ მომენტში ყველა ხელმისაწვდომი პროფილი უკვე ნანახია ან ახალი მონაცემები ემატება."
          actionLabel="განახლება"
          onAction={() => refetch()}
        />
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1.25rem" }}>
          {list.map((person) => {
            const score = person.compatibility_score ?? 60;
            const hookText = person.hook_observation?.text;

            return (
              <Card
                key={person.id}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  padding: "1.25rem",
                  gap: "1rem",
                }}
              >
                <div>
                  {/* Top Row: Avatar + Info + Score Badge */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.75rem" }}>
                    <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
                      <Avatar src={person.avatar_url} name={person.display_name} size="lg" />
                      <div>
                        <div style={{ fontWeight: 700, fontSize: "1.05rem", color: "#0f172a" }}>
                          {person.display_name}
                        </div>
                        {(person.occupation || person.city) && (
                          <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.15rem" }}>
                            {[person.occupation, person.city].filter(Boolean).join(" • ")}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Compatibility Curiosity Score */}
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        backgroundColor: "#fdf4ff",
                        border: "1px solid #f0abfc",
                        borderRadius: "10px",
                        padding: "0.3rem 0.6rem",
                        minWidth: "48px",
                      }}
                      title="სინასტრიული თანხვედრის ინდექსი"
                    >
                      <span style={{ fontSize: "1.1rem", fontWeight: 800, color: "#9333ea", lineHeight: 1 }}>
                        {Math.round(score)}
                      </span>
                      <span style={{ fontSize: "0.65rem", fontWeight: 600, color: "#a855f7", textTransform: "uppercase", marginTop: "0.1rem" }}>
                        Score
                      </span>
                    </div>
                  </div>

                  {/* Bio snippet if available */}
                  {person.bio && (
                    <p style={{ fontSize: "0.85rem", color: "#475569", margin: "0.75rem 0 0 0", lineHeight: 1.45 }}>
                      {person.bio}
                    </p>
                  )}

                  {/* Safe Derived Astrology Tags */}
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginTop: "0.75rem" }}>
                    {person.astrology?.sun_sign && (
                      <Badge variant="astrology" size="sm">
                        ☀️ {person.astrology.sun_sign}
                      </Badge>
                    )}
                    {person.astrology?.moon_sign && (
                      <Badge variant="default" size="sm">
                        🌙 {person.astrology.moon_sign}
                      </Badge>
                    )}
                    {person.astrology?.element_primary && (
                      <Badge variant="default" size="sm">
                        🔥 {person.astrology.element_primary}
                      </Badge>
                    )}
                  </div>

                  {/* JESTER Hook Observation (Human Interpretation First) */}
                  {hookText && (
                    <div
                      style={{
                        marginTop: "0.85rem",
                        padding: "0.75rem",
                        backgroundColor: "#f8fafc",
                        border: "1px solid #e2e8f0",
                        borderRadius: "8px",
                        fontSize: "0.825rem",
                        color: "#334155",
                        lineHeight: 1.45,
                        fontStyle: "italic",
                      }}
                    >
                      💡 {hookText}
                    </div>
                  )}
                </div>

                {/* Card Action CTAs */}
                <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
                  <Link to={`/people/${person.id}/why`} style={{ flex: 1, textDecoration: "none" }}>
                    <Button variant="brand" size="sm" fullWidth>
                      რატომ ეს ადამიანი?
                    </Button>
                  </Link>
                  <Link to={`/people/${person.id}`} style={{ textDecoration: "none" }}>
                    <Button variant="outline" size="sm">
                      პროფილი
                    </Button>
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
