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
  Skeleton,
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

  const isSelf = user?.id === targetId;

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

  // 2. Fetch Target Safe Astrology (Deterministic Placements)
  const {
    data: astro,
    isLoading: loadingAstro,
  } = useQuery({
    queryKey: ["astrology", targetId],
    queryFn: () => API.astrology.getPersonSafeAstro(targetId),
    enabled: !!profile && !profileError,
    retry: false,
  });

  // 3. Fetch Connections to determine relationship state & enforce block privacy
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

  // 4. Fetch Relationship Preview (ME -> YOU Synastry Insight)
  // Product Decision #2: Insight is discoverable BEFORE connection via safe comparePreview
  const {
    data: preview,
    isLoading: loadingPreview,
  } = useQuery({
    queryKey: ["compare-preview", targetId],
    queryFn: () =>
      API.interpretations.comparePreview({
        target_user_id: targetId,
        locale: "ka",
      }),
    enabled: !!profile && !profileError && !isSelf && relState !== "blocked",
    retry: false,
  });

  // Mutations
  const connectMutation = useMutation({
    mutationFn: () => API.connections.create(targetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connections"] });
      queryClient.invalidateQueries({ queryKey: ["compatibility-us", targetId] });
      queryClient.invalidateQueries({ queryKey: ["why-experience", targetId] });
    },
  });

  const transitionMutation = useMutation({
    mutationFn: (action: "accept" | "decline" | "block" | "remove") => {
      if (!myConnection) throw new Error("No active connection ID");
      return API.connections.transition(myConnection.id, action);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connections"] });
      queryClient.invalidateQueries({ queryKey: ["compatibility-us", targetId] });
      queryClient.invalidateQueries({ queryKey: ["why-experience", targetId] });
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

  // Privacy invariant: If blocked or 404/403, render privacy-safe not-found
  if (relState === "blocked") {
    return <PrivacySafeNotFoundState message="პროფილი ვერ მოიძებნა ან მიუწვდომელია." />;
  }

  if (profileError) {
    const err = profileError as any;
    if (err.statusCode === 404 || err.statusCode === 403) {
      return <PrivacySafeNotFoundState message="პროფილი ვერ მოიძებნა ან მიუწვდომელია." />;
    }
    return <ErrorState error={profileError as Error} />;
  }

  if (loadingProfile || loadingAstro || loadingConnections) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        <Skeleton width="180px" height="1.5rem" />
        <Card padded style={{ display: "flex", gap: "1.25rem", alignItems: "center", padding: "1.5rem" }}>
          <Skeleton width="80px" height="80px" borderRadius="9999px" />
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", flex: 1 }}>
            <Skeleton width="180px" height="1.5rem" />
            <Skeleton width="120px" height="1rem" />
          </div>
        </Card>
        <Skeleton width="100%" height="160px" borderRadius="12px" />
      </div>
    );
  }

  if (!profile) return null;

  const score = preview ? Math.round(preview.score) : 60;
  const relationshipHook =
    preview?.interpretation?.text ||
    preview?.deep_analysis?.core_dynamic?.text ||
    preview?.deep_analysis?.primary_interpretation?.text;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* 1. Breadcrumb Navigation */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Link
          to="/discover"
          style={{
            textDecoration: "none",
            color: "#6366f1",
            fontSize: "0.875rem",
            fontWeight: 600,
            display: "flex",
            alignItems: "center",
            gap: "0.35rem",
          }}
        >
          ← აღმოჩენის სიაში დაბრუნება
        </Link>
        {isSelf && (
          <Badge variant="brand" size="sm">
            ეს თქვენი პროფილია
          </Badge>
        )}
      </div>

      {/* 2. Identity Header Card (Clean, Human, Uncluttered) */}
      <Card padded style={{ padding: "1.5rem" }}>
        <div style={{ display: "flex", gap: "1.25rem", alignItems: "center", flexWrap: "wrap" }}>
          <Avatar src={profile.avatar_url} name={profile.display_name} size="xl" />
          <div style={{ flex: 1, minWidth: "220px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
              <h1
                style={{
                  margin: 0,
                  fontSize: "1.5rem",
                  fontWeight: 800,
                  color: "#0f172a",
                  letterSpacing: "-0.01em",
                }}
              >
                {profile.display_name}
              </h1>
              {astro?.sun_sign && (
                <Badge variant="astrology" size="sm">
                  ☀️ {astro.sun_sign}
                </Badge>
              )}
            </div>

            {(profile.occupation || profile.city) && (
              <div style={{ fontSize: "0.9rem", color: "#64748b", marginTop: "0.25rem", fontWeight: 500 }}>
                {[profile.occupation, profile.city].filter(Boolean).join(" • ")}
              </div>
            )}

            {profile.bio && (
              <p
                style={{
                  margin: "0.75rem 0 0 0",
                  color: "#334155",
                  fontSize: "0.925rem",
                  lineHeight: 1.55,
                  fontStyle: "italic",
                }}
              >
                "{profile.bio}"
              </p>
            )}
          </div>
        </div>
      </Card>

      {/* 3. Hero JESTER Relationship Insight (ME -> YOU Dynamic) */}
      {!isSelf && (
        <Card variant="accent" padded style={{ padding: "1.75rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "0.75rem", marginBottom: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontSize: "1.3rem" }}>💡</span>
              <h2 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 800, color: "#1e1b4b" }}>
                რატომ ეს ადამიანი თქვენთვის?
              </h2>
            </div>

            {/* Restrained Curiosity Score */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.4rem",
                backgroundColor: "#ffffff",
                border: "1px solid #f0abfc",
                borderRadius: "20px",
                padding: "0.3rem 0.75rem",
              }}
              title="სინასტრიული თანხვედრა (Curiosity Signal)"
            >
              <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "#7e22ce" }}>
                თანხვედრა
              </span>
              <span style={{ fontSize: "1.1rem", fontWeight: 800, color: "#9333ea" }}>
                {score}
              </span>
            </div>
          </div>

          {loadingPreview ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <Skeleton width="100%" height="4.5rem" />
            </div>
          ) : relationshipHook ? (
            <div style={{ margin: "0 0 1.5rem 0" }}>
              <p
                style={{
                  margin: 0,
                  fontSize: "1.05rem",
                  color: "#1e1b4b",
                  lineHeight: 1.65,
                  fontWeight: 500,
                }}
              >
                {relationshipHook}
              </p>
            </div>
          ) : (
            <p style={{ margin: "0 0 1.25rem 0", color: "#475569", fontSize: "0.95rem", lineHeight: 1.6 }}>
              თქვენს ასტროლოგიურ რუკებს შორის შეინიშნება უნიკალური სინასტრიული თანხვედრა, რაც კომუნიკაციას განსაკუთრებით საინტერესოს ხდის.
            </p>
          )}

          {/* Primary CTA: WHY? (The Natural Next Step) */}
          <div>
            <Link to={`/people/${targetId}/why`} style={{ textDecoration: "none" }}>
              <Button
                variant="brand"
                size="lg"
                fullWidth
                style={{
                  minHeight: "48px",
                  fontSize: "1rem",
                  fontWeight: 700,
                  boxShadow: "0 4px 12px rgba(147, 51, 234, 0.2)",
                }}
              >
                💡 რატომ ეს ადამიანი? (See Why) →
              </Button>
            </Link>
          </div>
        </Card>
      )}

      {/* 4. Supporting Astrological Signals (Deterministic Intelligence Layer) */}
      {astro && (
        <Card padded style={{ padding: "1.25rem 1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
            <h3 style={{ margin: 0, fontSize: "0.95rem", fontWeight: 700, color: "#0f172a", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              ასტროლოგიური კონტექსტი
            </h3>
            <span style={{ fontSize: "0.75rem", color: "#64748b" }}>
              უსაფრთხო დეტერმინისტული პროფილის სიგნალები
            </span>
          </div>

          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {astro.sun_sign && (
              <Badge variant="astrology" size="md">
                ☀️ მზე: {astro.sun_sign}
              </Badge>
            )}
            {astro.moon_sign && (
              <Badge variant="default" size="md">
                🌙 მთვარე: {astro.moon_sign}
              </Badge>
            )}
            {astro.ascendant_sign && (
              <Badge variant="default" size="md">
                🌅 ასცენდენტი: {astro.ascendant_sign}
              </Badge>
            )}
            {astro.element_primary && (
              <Badge variant="outline" size="md">
                🔥 სტიქია: {astro.element_primary}
              </Badge>
            )}
            {astro.modality_primary && (
              <Badge variant="outline" size="md">
                ⚡ მოდალობა: {astro.modality_primary}
              </Badge>
            )}
          </div>
        </Card>
      )}

      {/* 5. State-Aware Connection Invitation (INSIGHT -> INVITATION) */}
      {!isSelf && (
        <Card padded style={{ padding: "1.25rem 1.5rem", backgroundColor: "#f8fafc" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
            <div>
              <div style={{ fontWeight: 700, fontSize: "0.975rem", color: "#0f172a" }}>
                {relState === "accepted"
                  ? "თქვენ უკვე დაკავშირებული ხართ"
                  : relState === "pending_out"
                  ? "კავშირის მოთხოვნა გაგზავნილია"
                  : relState === "pending_in"
                  ? "ამ ადამიანმა გამოგიგზავნათ კავშირის მოთხოვნა"
                  : "გსურთ საუბრის დაწყება?"}
              </div>
              <div style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "0.15rem" }}>
                {relState === "accepted"
                  ? "გადადით პირდაპირ ჩატში და გააგრძელეთ საუბარი."
                  : relState === "pending_out"
                  ? "დაელოდეთ დასტურს საუბრის დასაწყებად."
                  : relState === "pending_in"
                  ? "მიიღეთ მოთხოვნა პირდაპირი მიმოწერის გასახსნელად."
                  : preview?.connection_invitation?.text || "გაგზავნეთ მოთხოვნა, რათა გაიხსნას სრული შედარება (US) და მიმოწერა."}
              </div>
            </div>

            <div style={{ display: "flex", gap: "0.6rem" }}>
              {relState === "none" && (
                <Button
                  variant="outline"
                  size="md"
                  isLoading={connectMutation.isPending}
                  onClick={() => connectMutation.mutate()}
                  icon={<span>🤝</span>}
                  style={{ minHeight: "44px", padding: "0 1.25rem" }}
                >
                  კავშირის შეთავაზება (Connect)
                </Button>
              )}

              {relState === "pending_out" && (
                <Badge variant="warning" size="md" style={{ padding: "0.5rem 0.85rem" }}>
                  ⏳ მოთხოვნა გაგზავნილია
                </Badge>
              )}

              {relState === "pending_in" && (
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <Button
                    variant="brand"
                    size="md"
                    isLoading={transitionMutation.isPending}
                    onClick={() => transitionMutation.mutate("accept")}
                    style={{ minHeight: "44px" }}
                  >
                    ✓ მიღება (Accept)
                  </Button>
                  <Button
                    variant="outline"
                    size="md"
                    isLoading={transitionMutation.isPending}
                    onClick={() => transitionMutation.mutate("decline")}
                    style={{ minHeight: "44px" }}
                  >
                    ✕ უარყოფა
                  </Button>
                </div>
              )}

              {relState === "accepted" && (
                <Button
                  variant="brand"
                  size="md"
                  onClick={handleStartChat}
                  icon={<span>💬</span>}
                  style={{ minHeight: "44px", padding: "0 1.25rem" }}
                >
                  ჩატის დაწყება
                </Button>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};
