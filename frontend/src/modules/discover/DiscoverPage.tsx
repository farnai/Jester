import React from "react";
import { useQuery } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { useAuth } from "../../core/auth/useAuth";
import { DiscoveryPerson, ConnectionResponse } from "../../core/api/types";
import { Badge, Skeleton, Card, ErrorState, EmptyState } from "../../shared/ui";
import { PersonCard } from "./PersonCard";

export const DiscoverPage: React.FC = () => {
  const { user } = useAuth();

  // 1. Fetch Discovery People (Production Endpoint)
  const {
    data: people,
    isLoading: loadingPeople,
    error: errorPeople,
    refetch: refetchPeople,
  } = useQuery<DiscoveryPerson[]>({
    queryKey: ["discovery-people", user?.id],
    queryFn: () => API.interpretations.getDiscoveryPeople(user?.id),
    enabled: !!user?.id,
  });

  // 2. Fetch Connections to determine relationship states and enforce privacy/block filters
  const { data: connections, isLoading: loadingConnections } = useQuery<ConnectionResponse[]>({
    queryKey: ["connections"],
    queryFn: API.connections.list,
  });

  // Loading State with Skeletons matching PersonCard structure
  if (loadingPeople || loadingConnections) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <Skeleton width="220px" height="2rem" />
            <div style={{ marginTop: "0.5rem" }}>
              <Skeleton width="340px" height="1rem" />
            </div>
          </div>
          <Skeleton width="80px" height="2rem" borderRadius="20px" />
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
            gap: "1.5rem",
          }}
        >
          {[1, 2, 3, 4].map((n) => (
            <Card key={n} padded style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
                  <Skeleton width="48px" height="48px" borderRadius="9999px" />
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                    <Skeleton width="120px" height="1.1rem" />
                    <Skeleton width="90px" height="0.8rem" />
                  </div>
                </div>
                <Skeleton width="48px" height="42px" borderRadius="10px" />
              </div>
              <Skeleton width="100%" height="4.5rem" borderRadius="8px" />
              <div style={{ display: "flex", gap: "0.4rem" }}>
                <Skeleton width="70px" height="1.5rem" borderRadius="12px" />
                <Skeleton width="70px" height="1.5rem" borderRadius="12px" />
              </div>
              <Skeleton width="100%" height="44px" borderRadius="8px" />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  // Error State
  if (errorPeople) {
    return <ErrorState error={errorPeople as Error} onRetry={refetchPeople} />;
  }

  const rawPeople = people || [];
  const connList = connections || [];

  // Build map of connection statuses & exclude blocked users (Privacy Invariant)
  const connectionMap = new Map<string, ConnectionResponse>();
  const blockedUserIds = new Set<string>();

  for (const conn of connList) {
    const otherId = conn.user_a_id === user?.id ? conn.user_b_id : conn.user_a_id;
    connectionMap.set(otherId, conn);
    if (conn.status === "blocked") {
      blockedUserIds.add(otherId);
    }
  }

  // Filter out any blocked users to prevent existence leak
  const visiblePeople = rawPeople.filter((p) => !blockedUserIds.has(p.id));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
      {/* Editorial Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          flexWrap: "wrap",
          gap: "1rem",
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <span style={{ fontSize: "1.5rem" }}>🧭</span>
            <h1
              style={{
                margin: 0,
                fontSize: "1.65rem",
                fontWeight: 800,
                color: "#0f172a",
                letterSpacing: "-0.02em",
              }}
            >
              აღმოაჩინე ადამიანები
            </h1>
          </div>
          <p
            style={{
              margin: "0.35rem 0 0 0",
              color: "#475569",
              fontSize: "0.95rem",
              lineHeight: 1.5,
              maxWidth: "600px",
            }}
          >
            ადამიანები, რომელთა გაცნობაც ღირს — სინასტრიული თანხვედრა და JESTER-ის ხედვა.
          </p>
        </div>

        <Badge variant="score" size="md">
          {visiblePeople.length} ხელმისაწვდომი
        </Badge>
      </div>

      {/* Main Discover Feed */}
      {visiblePeople.length === 0 ? (
        <EmptyState
          title="ამ ეტაპზე ახალი პროფილები არ ჩანს"
          description="თქვენ უკვე გაეცანით ყველა ხელმისაწვდომ პროფილს, ან ახალი მონაცემები ემატება. გადაამოწმეთ ცოტა ხანში."
          actionLabel="განახლება"
          onAction={() => refetchPeople()}
        />
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
            gap: "1.5rem",
          }}
        >
          {visiblePeople.map((person) => {
            const conn = connectionMap.get(person.id);
            let relStatus: "none" | "pending_out" | "pending_in" | "accepted" | "blocked" = "none";

            if (conn) {
              if (conn.status === "accepted") {
                relStatus = "accepted";
              } else if (conn.status === "pending") {
                relStatus = conn.initiated_by === user?.id ? "pending_out" : "pending_in";
              } else if (conn.status === "blocked") {
                relStatus = "blocked";
              }
            }

            return (
              <PersonCard
                key={person.id}
                person={person}
                connectionStatus={relStatus}
              />
            );
          })}
        </div>
      )}
    </div>
  );
};
