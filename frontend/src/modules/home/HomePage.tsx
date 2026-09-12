import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { useAuth } from "../../core/auth/useAuth";
import { DailyEnergyResponse, DiscoveryPerson, ConnectionResponse, ProfileResponse } from "../../core/api/types";
import { Card, Button, Badge, Avatar, Skeleton, ErrorState } from "../../shared/ui";

export const HomePage: React.FC = () => {
  const { user } = useAuth();
  const [showTransitWhy, setShowTransitWhy] = useState<boolean>(false);

  // 1. User Profile for personalized greeting
  const { data: profile } = useQuery<ProfileResponse>({
    queryKey: ["profile", "me"],
    queryFn: API.profiles.getMyProfile,
  });

  // 2. Today's Insight / Daily Energy (Single primary insight from backend)
  const {
    data: dailyEnergy,
    isLoading: loadingDaily,
    error: errorDaily,
    refetch: refetchDaily,
  } = useQuery<DailyEnergyResponse>({
    queryKey: ["daily-energy", user?.id],
    queryFn: () => API.interpretations.getDailyEnergy("auto", "ka"),
  });

  // 3. People Worth Discovering (Top Matches)
  const {
    data: discoveryPeople,
    isLoading: loadingPeople,
    error: errorPeople,
    refetch: refetchPeople,
  } = useQuery<DiscoveryPerson[]>({
    queryKey: ["discovery-people", user?.id],
    queryFn: () => API.interpretations.getDiscoveryPeople(user?.id),
    enabled: !!user?.id,
  });

  // 4. Active Connections Summary
  const {
    data: connections,
    isLoading: loadingConnections,
  } = useQuery<ConnectionResponse[]>({
    queryKey: ["connections"],
    queryFn: API.connections.list,
  });

  // Greeting based on local hour
  const currentHour = new Date().getHours();
  const timeGreeting =
    currentHour >= 5 && currentHour < 12
      ? "დილა მშვიდობისა"
      : currentHour >= 12 && currentHour < 18
      ? "გამარჯობა"
      : "საღამო მშვიდობისა";

  const greetingName = profile?.display_name || user?.email?.split("@")[0] || "მეგობარო";

  const acceptedConnections = (connections || []).filter((c) => c.status === "accepted");
  const incomingRequests = (connections || []).filter(
    (c) => c.status === "pending" && c.initiated_by !== user?.id
  );

  // Top 3 people for Home feed
  const topPeople = (discoveryPeople || []).slice(0, 3);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
      {/* 1. Contextual Greeting & Status Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <Avatar src={profile?.avatar_url} name={greetingName} size="lg" />
          <div>
            <div style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 600 }}>
              {timeGreeting} 👋
            </div>
            <h1 style={{ margin: 0, fontSize: "1.45rem", fontWeight: 800, color: "#0f172a", letterSpacing: "-0.01em" }}>
              {greetingName}
            </h1>
          </div>
        </div>

        <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
          <Link to="/discover" style={{ textDecoration: "none" }}>
            <Button variant="brand" size="md" icon={<span>🧭</span>}>
              აღმოჩენა (Discover)
            </Button>
          </Link>
          <Link to="/me" style={{ textDecoration: "none" }}>
            <Button variant="outline" size="md" icon={<span>👤</span>}>
              ჩემი პროფილი
            </Button>
          </Link>
        </div>
      </div>

      {/* 2. Today's Insight / Daily Energy Hero (Human-first Interpretation) */}
      <section>
        <Card variant="accent" padded style={{ padding: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Badge variant="score" size="md">
                ☀️ დღის ხედვა & ენერგია
              </Badge>
              {/* Single clean date badge */}
              <span style={{ fontSize: "0.825rem", color: "#64748b", fontWeight: 500 }}>
                {new Date().toLocaleDateString("ka-GE", { weekday: "long", month: "short", day: "numeric" })}
              </span>
            </div>
          </div>

          {loadingDaily ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              <Skeleton height="1.5rem" width="60%" />
              <Skeleton height="4.5rem" width="100%" />
            </div>
          ) : errorDaily ? (
            <ErrorState error={errorDaily as Error} onRetry={refetchDaily} />
          ) : dailyEnergy ? (
            <div>
              <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.25rem", color: "#1e1b4b", fontWeight: 800 }}>
                {dailyEnergy.label}
              </h2>

              <p style={{ margin: "0 0 1.25rem 0", color: "#334155", fontSize: "0.95rem", lineHeight: 1.65 }}>
                {dailyEnergy.interpretation?.text ||
                  "დღევანდელი ენერგია ხელს უწყობს პირდაპირ კომუნიკაციას და ახალი კონტაქტების გაცნობას."}
              </p>

              {/* DO / DON'T Behavioral Guidance */}
              {(dailyEnergy.do || dailyEnergy.dont) && (
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem", marginBottom: "1.25rem" }}>
                  {dailyEnergy.do && (
                    <div
                      style={{
                        padding: "0.75rem 0.9rem",
                        backgroundColor: "#f0fdf4",
                        border: "1px solid #bbf7d0",
                        borderRadius: "10px",
                        fontSize: "0.85rem",
                        color: "#166534",
                        lineHeight: 1.5,
                      }}
                    >
                      <div style={{ fontWeight: 800, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#15803d", marginBottom: "0.25rem", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                        <span>✓</span> DO
                      </div>
                      <div>
                        {Array.isArray(dailyEnergy.do) ? (
                          <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                            {dailyEnergy.do.map((tag, idx) => (
                              <span key={idx} style={{ fontWeight: 600 }}>• {tag}</span>
                            ))}
                          </div>
                        ) : (
                          <div>{dailyEnergy.do}</div>
                        )}
                      </div>
                    </div>
                  )}
                  {dailyEnergy.dont && (
                    <div
                      style={{
                        padding: "0.75rem 0.9rem",
                        backgroundColor: "#fef2f2",
                        border: "1px solid #fecaca",
                        borderRadius: "10px",
                        fontSize: "0.85rem",
                        color: "#991b1b",
                        lineHeight: 1.5,
                      }}
                    >
                      <div style={{ fontWeight: 800, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#b91c1c", marginBottom: "0.25rem", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                        <span>✕</span> DON'T
                      </div>
                      <div>
                        {Array.isArray(dailyEnergy.dont) ? (
                          <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                            {dailyEnergy.dont.map((tag, idx) => (
                              <span key={idx} style={{ fontWeight: 600 }}>• {tag}</span>
                            ))}
                          </div>
                        ) : (
                          <div>{dailyEnergy.dont}</div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Collapsible "See Why / Context" */}
              <div style={{ borderTop: "1px solid #f5d0fe", paddingTop: "0.75rem" }}>
                <button
                  onClick={() => setShowTransitWhy(!showTransitWhy)}
                  style={{
                    background: "none",
                    border: "none",
                    padding: 0,
                    color: "#9333ea",
                    fontSize: "0.85rem",
                    fontWeight: 700,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.35rem",
                  }}
                >
                  <span>{showTransitWhy ? "▼" : "▶"}</span>
                  <span>რატომ ეს ენერგია? (See Why)</span>
                </button>

                {showTransitWhy && (
                  <div
                    style={{
                      marginTop: "0.6rem",
                      padding: "0.75rem",
                      backgroundColor: "rgba(255, 255, 255, 0.7)",
                      borderRadius: "8px",
                      fontSize: "0.825rem",
                      color: "#475569",
                      lineHeight: 1.5,
                    }}
                  >
                    <div>
                      <strong>ფოკუსი:</strong> {dailyEnergy.label}
                    </div>
                    {dailyEnergy.primary_transit ? (
                      <div style={{ marginTop: "0.25rem" }}>
                        <strong>აქტიური ტრანზიტი:</strong>{" "}
                        {dailyEnergy.primary_transit.context_label_ka} (ორბი: {dailyEnergy.primary_transit.orb_diff}°,{" "}
                        {dailyEnergy.primary_transit.is_applying ? "უახლოვდება" : "შორდება"})
                      </div>
                    ) : (
                      dailyEnergy.available_archetypes?.find((a) => a.id === dailyEnergy.energy_type)?.transit && (
                        <div style={{ marginTop: "0.25rem" }}>
                          <strong>ასტროლოგიური კონტექსტი:</strong>{" "}
                          {dailyEnergy.available_archetypes.find((a) => a.id === dailyEnergy.energy_type)?.transit}
                        </div>
                      )
                    )}
                    <div style={{ marginTop: "0.35rem", fontSize: "0.75rem", color: "#94a3b8" }}>
                      ტონი: <code>{dailyEnergy.interpretation?.tone || "witty"}</code>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </Card>
      </section>

      {/* 3. Active Connections & Activity Summary Card */}
      <section>
        <Card padded style={{ padding: "1.25rem 1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span style={{ fontSize: "1.2rem" }}>🤝</span>
                <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700, color: "#0f172a" }}>
                  ჩემი კავშირები & შეტყობინებები
                </h3>
              </div>
              <div style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "0.2rem" }}>
                {loadingConnections ? (
                  "კავშირების სტატუსი იტვირთება..."
                ) : (
                  <>
                    <span><strong>{acceptedConnections.length}</strong> აქტიური კავშირი</span>
                    {incomingRequests.length > 0 && (
                      <span style={{ color: "#d97706", marginLeft: "0.6rem", fontWeight: 700 }}>
                        • <strong>{incomingRequests.length}</strong> ახალი მოთხოვნა
                      </span>
                    )}
                  </>
                )}
              </div>
            </div>

            <div style={{ display: "flex", gap: "0.5rem" }}>
              <Link to="/connections" style={{ textDecoration: "none" }}>
                <Button variant="secondary" size="sm">
                  კავშირების მართვა
                </Button>
              </Link>
              <Link to="/messages" style={{ textDecoration: "none" }}>
                <Button variant="brand" size="sm">
                  💬 ჩატები
                </Button>
              </Link>
            </div>
          </div>
        </Card>
      </section>

      {/* 4. People Worth Discovering (Entry into Product Loop: ME -> YOU -> US) */}
      <section>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 800, color: "#0f172a" }}>
              ადამიანები აღმოსაჩენად
            </h2>
            <div style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "0.15rem" }}>
              მაღალი სინასტრიული თანხვედრა და საინტერესო დინამიკა
            </div>
          </div>

          <Link to="/discover" style={{ textDecoration: "none" }}>
            <Button variant="outline" size="sm">
              ყველას ნახვა ({discoveryPeople?.length || 0}) →
            </Button>
          </Link>
        </div>

        {loadingPeople ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1rem" }}>
            <Skeleton height="180px" borderRadius="12px" />
            <Skeleton height="180px" borderRadius="12px" />
            <Skeleton height="180px" borderRadius="12px" />
          </div>
        ) : errorPeople ? (
          <ErrorState error={errorPeople as Error} onRetry={refetchPeople} />
        ) : topPeople.length === 0 ? (
          <Card padded style={{ textAlign: "center", padding: "2rem" }}>
            <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>🧭</div>
            <div style={{ fontWeight: 700, color: "#1e293b", marginBottom: "0.3rem" }}>
              ამ მომენტში ახალი პროფილები არ ჩანს
            </div>
            <p style={{ color: "#64748b", fontSize: "0.85rem", margin: 0 }}>
              გადაამოწმეთ ცოტა ხანში ან განაახლეთ აღმოჩენის სია.
            </p>
          </Card>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(270px, 1fr))", gap: "1rem" }}>
            {topPeople.map((person) => {
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
                    gap: "0.85rem",
                  }}
                >
                  <div>
                    {/* Person Header */}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem" }}>
                      <div style={{ display: "flex", gap: "0.65rem", alignItems: "center" }}>
                        <Avatar src={person.avatar_url} name={person.display_name} size="md" />
                        <div>
                          <div style={{ fontWeight: 700, fontSize: "0.975rem", color: "#0f172a" }}>
                            {person.display_name}
                          </div>
                          {(person.occupation || person.city) && (
                            <div style={{ fontSize: "0.775rem", color: "#64748b" }}>
                              {[person.occupation, person.city].filter(Boolean).join(" • ")}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Score Badge */}
                      <div
                        style={{
                          backgroundColor: "#fdf4ff",
                          border: "1px solid #f0abfc",
                          borderRadius: "8px",
                          padding: "0.2rem 0.5rem",
                          textAlign: "center",
                          minWidth: "40px",
                        }}
                        title="სინასტრიული თანხვედრა"
                      >
                        <span style={{ fontSize: "1rem", fontWeight: 800, color: "#9333ea" }}>
                          {Math.round(score)}
                        </span>
                      </div>
                    </div>

                    {/* Safe Astrology Pills */}
                    <div style={{ display: "flex", gap: "0.3rem", marginTop: "0.6rem", flexWrap: "wrap" }}>
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
                    </div>

                    {/* JESTER Hook Observation */}
                    {hookText && (
                      <p
                        style={{
                          margin: "0.6rem 0 0 0",
                          fontSize: "0.825rem",
                          color: "#334155",
                          lineHeight: 1.45,
                          fontStyle: "italic",
                          display: "-webkit-box",
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: "vertical",
                          overflow: "hidden",
                        }}
                      >
                        💡 {hookText}
                      </p>
                    )}
                  </div>

                  {/* Actions leading to Why & Person Profile */}
                  <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.25rem" }}>
                    <Link to={`/people/${person.id}/why`} style={{ flex: 1, textDecoration: "none" }}>
                      <Button variant="brand" size="sm" fullWidth>
                        რატომ? (Why)
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
      </section>

      {/* 5. Natural Path into Discover Loop Banner */}
      <section>
        <Card variant="default" padded style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem", backgroundColor: "#f8fafc" }}>
          <div>
            <h3 style={{ margin: "0 0 0.25rem 0", fontSize: "1.1rem", color: "#0f172a" }}>
              გსურს მეტი ადამიანის აღმოჩენა?
            </h3>
            <p style={{ margin: 0, color: "#64748b", fontSize: "0.875rem" }}>
              დაათვალიერე სრული სია, გაიგე ურთიერთობის დინამიკა და დაიწყე ახალი საუბრები.
            </p>
          </div>

          <Link to="/discover" style={{ textDecoration: "none" }}>
            <Button variant="brand" size="md">
              🚀 აღმოჩენის სიაზე გადასვლა
            </Button>
          </Link>
        </Card>
      </section>
    </div>
  );
};
