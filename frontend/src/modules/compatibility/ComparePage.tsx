import React from "react";
import { useParams, useNavigate, Navigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { useAuth } from "../../core/auth/useAuth";
import { ProfileResponse, Signal } from "../../core/api/types";
import {
  Skeleton,
  ErrorState,
  PrivacySafeNotFoundState,
} from "../../shared/ui";
import { RelationshipHeader } from "./components/RelationshipHeader";
import { RelationshipHighlights } from "./components/RelationshipHighlights";
import { DimensionCards } from "./components/DimensionCards";
import { DeepAnalysisSection } from "./components/DeepAnalysisSection";
import { ConversationStarters } from "./components/ConversationStarters";
import { RelationshipAction } from "./components/RelationshipAction";

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const ComparePage: React.FC = () => {
  const { id, target_id } = useParams<{ id?: string; target_id?: string }>();
  const targetId = (id || target_id || "").trim();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const isValidUUID = UUID_REGEX.test(targetId);

  // If no target ID or invalid format -> Redirect to Discover
  if (!targetId || !isValidUUID) {
    return <Navigate to="/discover" replace />;
  }

  // 1. Fetch Target Profile for contextual identity
  const { data: targetProfile, error: targetProfileError } = useQuery({
    queryKey: ["profile", targetId],
    queryFn: () => API.profiles.getProfileById(targetId),
    retry: false,
  });

  // 2. Fetch Own Profile for ME + YOU dual header
  const { data: viewerProfile } = useQuery<ProfileResponse>({
    queryKey: ["profile", "me"],
    queryFn: API.profiles.getMyProfile,
    enabled: !!user,
  });

  // 3. Fetch Connections to determine relationship state & privacy
  const { data: connections } = useQuery({
    queryKey: ["connections"],
    queryFn: API.connections.list,
  });

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

  // 4. Fetch Relationship Intelligence (US / Compatibility)
  // Product Decision #2: Uses safe comparePreview for unconnected discovery users
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["compatibility-us", targetId],
    queryFn: async () => {
      try {
        const res = await API.compatibility.compare(targetId);
        return {
          score: res.score,
          dimensions: res.dimensions,
          interpretation: res.interpretation,
          connection_invitation: res.connection_invitation,
          signals: (res.signals || []) as unknown as Signal[],
          best_topics: res.best_topics || [],
          conversation_starters: res.conversation_starters || [],
          conversation_starter_details: res.conversation_starter_details,
          data_quality: res.data_quality,
          deep_analysis: res.deep_analysis,
          raw: res,
          isFullComparison: true,
        };
      } catch (err: any) {
        if (err.statusCode === 403 || err.status === 403) {
          const preview = await API.interpretations.comparePreview({
            target_user_id: targetId,
            locale: "ka",
          });
          return {
            score: preview.score,
            dimensions: preview.dimensions,
            interpretation: preview.interpretation,
            connection_invitation: preview.connection_invitation,
            signals: (preview.signals || []) as unknown as Signal[],
            best_topics: preview.best_topics || [],
            conversation_starters: preview.conversation_starters || [],
            conversation_starter_details: preview.conversation_starter_details,
            data_quality: preview.data_quality,
            deep_analysis: preview.deep_analysis,
            raw: preview,
            isFullComparison: false,
          };
        }
        throw err;
      }
    },
    enabled: !!targetId && relState !== "blocked",
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

  const handleOpenChat = async () => {
    try {
      const conv = await API.conversations.createOrGetDirect(targetId);
      navigate(`/chat/${conv.id}`);
    } catch (err: any) {
      alert(err.message || "პირდაპირი მიმოწერის გასახსნელად საჭიროა დადასტურებული კავშირი.");
    }
  };

  const handleSendStarterToChat = async (starterText: string) => {
    try {
      const conv = await API.conversations.createOrGetDirect(targetId);
      navigate(`/chat/${conv.id}?starter=${encodeURIComponent(starterText)}`);
    } catch (err: any) {
      alert(err.message || "პირდაპირი მიმოწერის გასახსნელად საჭიროა დადასტურებული კავშირი.");
    }
  };

  // Privacy invariant: If blocked or 404/403, render privacy-safe not-found
  if (relState === "blocked") {
    return <PrivacySafeNotFoundState message="პროფილი ან ურთიერთობის მონაცემები ვერ მოიძებნა." />;
  }

  if (targetProfileError) {
    const err = targetProfileError as any;
    if (err.statusCode === 404 || err.statusCode === 403) {
      return <PrivacySafeNotFoundState message="პროფილი ან ურთიერთობის მონაცემები ვერ მოიძებნა." />;
    }
  }

  if (error) {
    const err = error as any;
    if (err.statusCode === 404) {
      return <PrivacySafeNotFoundState message="პროფილი ან ურთიერთობის მონაცემები ვერ მოიძებნა." />;
    }
    return <ErrorState error={error as Error} onRetry={refetch} />;
  }

  if (isLoading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", maxWidth: "860px", margin: "0 auto" }}>
        {/* Header Skeleton */}
        <div
          style={{
            backgroundColor: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: "16px",
            padding: "1.75rem 1.5rem",
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <Skeleton width="120px" height="1.2rem" />
            <Skeleton width="90px" height="1.5rem" borderRadius="9999px" />
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <Skeleton width="56px" height="56px" circle />
            <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
              <Skeleton width="160px" height="0.9rem" />
              <Skeleton width="240px" height="1.4rem" />
            </div>
          </div>
        </div>

        {/* Highlights Skeleton */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <Skeleton width="200px" height="1.2rem" />
          <Skeleton width="100%" height="80px" borderRadius="12px" />
          <Skeleton width="100%" height="70px" borderRadius="12px" />
        </div>

        {/* Dimensions Skeleton */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <Skeleton width="220px" height="1.2rem" />
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "0.85rem" }}>
            <Skeleton width="100%" height="90px" borderRadius="12px" />
            <Skeleton width="100%" height="90px" borderRadius="12px" />
            <Skeleton width="100%" height="90px" borderRadius="12px" />
            <Skeleton width="100%" height="90px" borderRadius="12px" />
          </div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const targetName = targetProfile?.display_name || "მომხმარებელი";

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "1.75rem",
        maxWidth: "860px",
        margin: "0 auto",
        paddingBottom: "3rem",
      }}
    >
      {/* A. RELATIONAL HEADER */}
      <RelationshipHeader
        targetProfile={targetProfile}
        viewerProfile={viewerProfile}
        score={data.score}
        dataQuality={data.data_quality}
        interpretation={data.interpretation}
      />



      {/* B. WHAT STANDS OUT */}
      <RelationshipHighlights
        interpretation={data.interpretation}
        signals={data.signals}
      />



      {/* C. FOUR RELATIONSHIP DIMENSIONS */}
      <DimensionCards dimensions={data.dimensions} />

      {/* D. DEEPER LAYER (Deep Analysis with Progressive Disclosure) */}
      <DeepAnalysisSection deepAnalysis={data.deep_analysis} />

      {/* E. SHARED TOPICS & CONVERSATION STARTERS */}
      <ConversationStarters
        bestTopics={data.best_topics}
        conversationStarters={data.conversation_starters}
        isConnected={relState === "accepted"}
        onSendToChat={handleSendStarterToChat}
      />



      {/* F. TERMINAL ACTION */}
      <RelationshipAction
        targetName={targetName}
        relState={relState}
        onConnect={() => connectMutation.mutate()}
        onAccept={() => transitionMutation.mutate("accept")}
        onDecline={() => transitionMutation.mutate("decline")}
        onOpenChat={handleOpenChat}
        isConnecting={connectMutation.isPending}
        isTransitioning={transitionMutation.isPending}
      />
    </div>
  );
};
