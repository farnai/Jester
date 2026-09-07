import React from "react";
import { useParams, useNavigate, Link, Navigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { useAuth } from "../../core/auth/useAuth";
import {
  Card,
  Button,
  Badge,
  Avatar,
  LoadingState,
  ErrorState,
  PrivacySafeNotFoundState,
} from "../../shared/ui";

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const PersonProfilePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const targetId = (id || "").trim();
  const isValidUUID = UUID_REGEX.test(targetId);

  // If no target ID or invalid format -> Redirect to Discover
  if (!targetId || !isValidUUID) {
    return <Navigate to="/discover" replace />;
  }

  // 1. Fetch Target Profile
  const {
    data: profile,
    isLoading: loadingProfile,
    error: profileError,
  } = useQuery({
    queryKey: ["profile", targetId],
    queryFn: () => API.profiles.getProfileById(targetId),
    retry: false,
  });

  // 2. Fetch Target Safe Astrology
  const {
    data: astro,
    isLoading: loadingAstro,
  } = useQuery({
    queryKey: ["astrology", targetId],
    queryFn: () => API.astrology.getPersonSafeAstro(targetId),
    enabled: !!profile && !profileError,
    retry: false,
  });

  // 3. Fetch Connections to determine state
  const { data: connections, isLoading: loadingConnections } = useQuery({
    queryKey: ["connections"],
    queryFn: API.connections.list,
  });

  // Determine relationship state
  const myConnection = connections?.find(
    (c) =>
      (c.user_a_id === user?.id && c.user_b_id === targetId) ||
      (c.user_b_id === user?.id && c.user_a_id === targetId)
  );

  let relState: "none" | "pending_out" | "pending_in" | "accepted" | "blocked" = "none";
  if (myConnection) {
    if (myConnection.status === "pending") {
      relState = myConnection.initiated_by === user?.id ? "pending_out" : "pending_in";
    } else if (myConnection.status === "accepted") {
      relState = "accepted";
    } else if (myConnection.status === "blocked") {
      relState = "blocked";
    }
  }

  // Mutations
  const connectMutation = useMutation({
    mutationFn: () => API.connections.create(targetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connections"] });
    },
  });

  const transitionMutation = useMutation({
    mutationFn: (action: "accept" | "decline" | "block" | "remove") => {
      if (!myConnection) throw new Error("No active connection ID");
      return API.connections.transition(myConnection.id, action);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connections"] });
    },
  });

  const handleStartChat = async () => {
    try {
      const conv = await API.conversations.createOrGetDirect(targetId);
      navigate(`/chat/${conv.id}`);
    } catch (err: any) {
      alert(err.message || "Failed to start direct conversation");
    }
  };

  if (loadingProfile || loadingAstro || loadingConnections) {
    return <LoadingState message="პროფილის ჩატვირთვა..." />;
  }

  if (profileError) {
    const err = profileError as any;
    if (err.statusCode === 404 || err.statusCode === 403) {
      return <PrivacySafeNotFoundState message="პროფილი ვერ მოიძებნა ან დაბლოკილია." />;
    }
    return <ErrorState error={profileError as Error} />;
  }

  if (!profile) return null;

  const isSelf = user?.id === targetId;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Top Breadcrumb Navigation */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Link to="/discover" style={{ textDecoration: "none", color: "#6366f1", fontSize: "0.875rem", fontWeight: 600 }}>
          ← აღმოჩენის სიაში დაბრუნება
        </Link>
      </div>

      {/* Profile Header Hero Card */}
      <Card padded style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1.25rem" }}>
        <div style={{ display: "flex", gap: "1.25rem", alignItems: "center" }}>
          <Avatar src={profile.avatar_url} name={profile.display_name} size="xl" />
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 800, color: "#0f172a" }}>
                {profile.display_name}
              </h1>
              {astro?.sun_sign && (
                <Badge variant="astrology" size="md">
                  ☀️ {astro.sun_sign}
                </Badge>
              )}
            </div>

            {(profile.occupation || profile.city) && (
              <div style={{ fontSize: "0.9rem", color: "#64748b", marginTop: "0.25rem" }}>
                {[profile.occupation, profile.city].filter(Boolean).join(" • ")}
              </div>
            )}
          </div>
        </div>

        {/* Relationship Action Area */}
        {!isSelf && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
            {relState === "none" && (
              <Button
                variant="brand"
                size="md"
                isLoading={connectMutation.isPending}
                onClick={() => connectMutation.mutate()}
                icon={<span>🤝</span>}
              >
                დაკავშირება (Connect)
              </Button>
            )}

            {relState === "pending_out" && (
              <Badge variant="warning" size="md">
                ⏳ მოთხოვნა გაგზავნილია
              </Badge>
            )}

            {relState === "pending_in" && (
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <Button
                  variant="brand"
                  size="sm"
                  isLoading={transitionMutation.isPending}
                  onClick={() => transitionMutation.mutate("accept")}
                >
                  ✓ მიღება (Accept)
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  isLoading={transitionMutation.isPending}
                  onClick={() => transitionMutation.mutate("decline")}
                >
                  ✕ უარყოფა
                </Button>
              </div>
            )}

            {relState === "accepted" && (
              <Button variant="brand" size="md" onClick={handleStartChat} icon={<span>💬</span>}>
                ჩატის დაწყება
              </Button>
            )}
          </div>
        )}
      </Card>

      {/* Bio / About */}
      {profile.bio && (
        <Card padded>
          <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "1.05rem", color: "#0f172a" }}>
            შესახებ
          </h3>
          <p style={{ margin: 0, color: "#334155", fontSize: "0.95rem", lineHeight: 1.6 }}>
            {profile.bio}
          </p>
        </Card>
      )}

      {/* Safe Astrological Placements (Deterministic Intelligence Layer) */}
      {astro && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <h3 style={{ margin: 0, fontSize: "1.05rem", color: "#0f172a" }}>
            ასტროლოგიური პროფილის სიგნალები
          </h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.75rem" }}>
            <Card padded>
              <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>
                მზე (Sun)
              </div>
              <div style={{ fontSize: "1.2rem", fontWeight: 800, marginTop: "0.2rem", color: "#0f172a" }}>
                ☀️ {astro.sun_sign}
              </div>
            </Card>

            <Card padded>
              <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>
                მთვარე (Moon)
              </div>
              <div style={{ fontSize: "1.2rem", fontWeight: 800, marginTop: "0.2rem", color: "#0f172a" }}>
                🌙 {astro.moon_sign}
              </div>
            </Card>

            {astro.ascendant_sign && (
              <Card padded>
                <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>
                  ასცენდენტი
                </div>
                <div style={{ fontSize: "1.2rem", fontWeight: 800, marginTop: "0.2rem", color: "#0f172a" }}>
                  🌅 {astro.ascendant_sign}
                </div>
              </Card>
            )}

            <Card padded>
              <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>
                სტიქია
              </div>
              <div style={{ fontSize: "1.2rem", fontWeight: 800, marginTop: "0.2rem", color: "#0f172a" }}>
                🔥 {astro.element_primary}
              </div>
            </Card>

            <Card padded>
              <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>
                მოდალობა
              </div>
              <div style={{ fontSize: "1.2rem", fontWeight: 800, marginTop: "0.2rem", color: "#0f172a" }}>
                ⚡ {astro.modality_primary}
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Core V1 Product Journey CTAs: WHY? & US / COMPARISON */}
      {!isSelf && (
        <Card variant="accent" padded style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <h3 style={{ margin: "0 0 0.25rem 0", fontSize: "1.15rem", color: "#1e1b4b" }}>
              გაინტერესებს ურთიერთობის დინამიკა?
            </h3>
            <p style={{ margin: 0, color: "#475569", fontSize: "0.875rem" }}>
              ნახე რატომ არის ეს ადამიანი საინტერესო და შეამოწმე სინასტრიული თანხვედრა.
            </p>
          </div>

          <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
            <Link to={`/people/${targetId}/why`} style={{ textDecoration: "none" }}>
              <Button variant="brand" size="md">
                💡 რატომ ეს ადამიანი? (Why?)
              </Button>
            </Link>
            <Link to={`/compare/${targetId}`} style={{ textDecoration: "none" }}>
              <Button variant="outline" size="md">
                ⚖️ შედარება (Compare)
              </Button>
            </Link>
          </div>
        </Card>
      )}
    </div>
  );
};
