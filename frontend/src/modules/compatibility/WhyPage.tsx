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
import { RuntimeInfoBlock } from "../../shared/runtime/RuntimeInfoBlock";
import { SignalBlock } from "../../shared/runtime/SignalBlock";
import { StartersInspectionBlock } from "../../shared/runtime/StartersInspectionBlock";
import { RuntimeJson } from "../../shared/runtime/RuntimeJson";
import { getTopicLabel } from "./components/ConversationStarters";

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

const CATEGORY_MAP: Record<string, { label: string; icon: string }> = {
  harmony: { label: "ემოციური ჰარმონია", icon: "✨" },
  attraction: { label: "მიზიდულობა და ქიმია", icon: "🔥" },
  communication: { label: "ინტელექტუალური კავშირი", icon: "💬" },
  growth: { label: "პიროვნული ზრდა", icon: "🌱" },
  stability: { label: "სტაბილურობა და ნდობა", icon: "🏛️" },
  notice: { label: "ურთიერთობის დინამიკა", icon: "⚡" },
};

export const WhyPage: React.FC = () => {
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
  const { data: profile, error: profileError } = useQuery({
    queryKey: ["profile", targetId],
    queryFn: () => API.profiles.getProfileById(targetId),
    retry: false,
  });

  // 2. Fetch Connections to determine relationship state & privacy
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

  // 3. Fetch Relationship Insight (Why / Preview)
  // Product Decision #2: Uses safe comparePreview for unconnected discovery users
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["why-experience", targetId],
    queryFn: async () => {
      try {
        const res = await API.compatibility.why(targetId);
        return {
          score: res.score,
          interpretation: res.interpretation,
          connection_invitation: res.connection_invitation,
          conversation_starter_details: res.conversation_starter_details,
          data_quality: res.data_quality,
          signals: res.signals || [],
          best_topics: res.best_topics || [],
          conversation_starters: res.conversation_starters || [],
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
            interpretation: preview.interpretation,
            connection_invitation: preview.connection_invitation,
            conversation_starter_details: preview.conversation_starter_details,
            data_quality: preview.data_quality,
            signals: preview.signals || [],
            best_topics: preview.best_topics || [],
            conversation_starters: preview.conversation_starters || [],
            deepAnalysis: preview.deep_analysis,
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

  if (profileError) {
    const err = profileError as any;
    if (err.statusCode === 404 || err.statusCode === 403) {
      return <PrivacySafeNotFoundState message="პროფილი ან ურთიერთობის მონაცემები ვერ მოიძებნა." />;
    }
  }

  if (isLoading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        <Skeleton width="180px" height="1.5rem" />
        <Card padded style={{ padding: "1.75rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
          <Skeleton width="240px" height="1.75rem" />
          <Skeleton width="100%" height="4.5rem" />
        </Card>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem" }}>
          <Skeleton height="140px" borderRadius="12px" />
          <Skeleton height="140px" borderRadius="12px" />
        </div>
      </div>
    );
  }

  if (error) {
    return <ErrorState error={error as Error} onRetry={refetch} />;
  }

  if (!data) return null;

  const score = Math.round(data.score);
  const primaryInsight =
    data.interpretation?.text ||
    data.deepAnalysis?.core_dynamic?.text ||
    data.deepAnalysis?.primary_interpretation?.text ||
    "თქვენს სინასტრიულ რუკებს შორის გამოკვეთილია ბუნებრივი ინტერესი და საერთო დინამიკა.";

  // Filter top 2-4 signals with meaningful interpretations
  const supportingSignals = (data.signals || [])
    .filter((s) => s.interpretation?.text || s.label)
    .slice(0, 4);

  const bestTopics = data.best_topics || [];
  const conversationStarters = data.conversation_starters || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
      {/* 1. Header & Person Identity Context */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {profile && (
            <Avatar src={profile.avatar_url} name={profile.display_name} size="md" />
          )}
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <span style={{ fontSize: "1.25rem" }}>💡</span>
              <h1 style={{ margin: 0, fontSize: "1.35rem", fontWeight: 800, color: "#0f172a" }}>
                რატომ {profile?.display_name || "ეს ადამიანი"}?
              </h1>
            </div>
            <div style={{ fontSize: "0.825rem", color: "#64748b", marginTop: "0.15rem" }}>
              ურთიერთობის დინამიკა და JESTER-ის ანალიზი
            </div>
          </div>
        </div>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <Link to={`/people/${targetId}`} style={{ textDecoration: "none" }}>
            <Button variant="outline" size="sm">
              ← პროფილი
            </Button>
          </Link>
          <Link to="/discover" style={{ textDecoration: "none" }}>
            <Button variant="outline" size="sm">
              🧭 აღმოჩენა
            </Button>
          </Link>
        </div>
      </div>

      {/* 2. “Why this person?” Hero Insight (Emotional & Intellectual Core) */}
      <Card variant="accent" padded style={{ padding: "1.75rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
          <Badge variant="score" size="md">
            🌟 მთავარი ხედვა
          </Badge>

          {/* Restrained Curiosity Score */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
              backgroundColor: "#ffffff",
              border: "1px solid #f0abfc",
              borderRadius: "20px",
              padding: "0.25rem 0.7rem",
            }}
            title="სინასტრიული თანხვედრა"
          >
            <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "#7e22ce" }}>
              თანხვედრა
            </span>
            <span style={{ fontSize: "1.05rem", fontWeight: 800, color: "#9333ea" }}>
              {score} / 100
            </span>
          </div>
        </div>

        <p
          style={{
            margin: "0 0 1.25rem 0",
            color: "#1e1b4b",
            fontSize: "1.1rem",
            lineHeight: 1.7,
            fontWeight: 500,
          }}
        >
          {primaryInsight}
        </p>

        {data.interpretation?.tone && (
          <div style={{ fontSize: "0.75rem", color: "#7e22ce", fontWeight: 600, marginBottom: "0.75rem" }}>
            ტონი: <code>{data.interpretation.tone}</code> • დეტერმინისტული სინასტრიული ანალიზი
          </div>
        )}

        <RuntimeInfoBlock
          title="Runtime: Primary Interpretation Metadata"
          badge="Insight Engine"
          items={[
            { label: "Category", value: data.interpretation?.category || (data.signals?.[0]?.category) || "harmony" },
            { label: "Signal / Contract ID", value: data.signals?.[0]?.rule_id || data.signals?.[0]?.source_aspect || "synastry_v1" },
            { label: "Source Aspects", value: data.signals?.[0]?.aspect ? `${data.signals[0].planet_pair} (${data.signals[0].aspect})` : "N/A" },
            { label: "Score / Confidence", value: `${score} / 100` },
            { label: "Tone", value: data.interpretation?.tone || "direct" },
          ]}
        />
      </Card>

      {/* 2.5 Dedicated Connection Invitation: The insight becomes the invitation */}
      <Card padded style={{ padding: "1.25rem 1.5rem", borderLeft: "4px solid #8b5cf6" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
          <span style={{ fontSize: "1.1rem" }}>✉️</span>
          <h3 style={{ margin: 0, fontSize: "1rem", fontWeight: 800, color: "#4c1d95" }}>
            Connection Invitation (The insight becomes the invitation)
          </h3>
        </div>
        <p style={{ margin: "0 0 0.85rem 0", color: "#334155", fontSize: "0.95rem", lineHeight: 1.6, fontStyle: "italic" }}>
          "{data.connection_invitation?.text || "ინსაითი მოგეწონათ? გაუგზავნეთ კავშირის მოთხოვნა საუბრის დასაწყებად."}"
        </p>
        <RuntimeInfoBlock
          title="Runtime: Invitation Asset Metadata"
          badge="Invitation Engine"
          items={[
            { label: "Invitation Category", value: data.connection_invitation?.category || "invitation" },
            { label: "Invitation Asset ID", value: data.connection_invitation?.asset_id || "invitation.v1" },
            { label: "Target User", value: targetId },
          ]}
        />
      </Card>

      {/* 3. Supporting Relationship Dynamics (2–4 Human-Readable Signals) */}
      {supportingSignals.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.15rem", fontWeight: 800, color: "#0f172a" }}>
              ურთიერთობის დინამიკის მახასიათებლები
            </h2>
            <div style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "0.15rem" }}>
              გამოკვეთილი საერთო ასპექტები და ენერგეტიკული თანხვედრა
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap: "1rem",
            }}
          >
            {supportingSignals.map((sig, i) => {
              const meta = CATEGORY_MAP[sig.category] || { label: "დინამიკა", icon: "✨" };
              const text = sig.interpretation?.text || sig.label;

              return (
                <Card
                  key={i}
                  padded
                  style={{
                    padding: "1.25rem",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                    gap: "0.75rem",
                  }}
                >
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.5rem" }}>
                      <span style={{ fontSize: "1rem" }}>{meta.icon}</span>
                      <span style={{ fontSize: "0.825rem", fontWeight: 700, color: "#7e22ce", textTransform: "uppercase" }}>
                        {meta.label}
                      </span>
                    </div>

                    <p style={{ margin: 0, fontSize: "0.925rem", color: "#334155", lineHeight: 1.55 }}>
                      {text}
                    </p>
                  </div>

                  {sig.strength && (
                    <div style={{ fontSize: "0.75rem", color: "#94a3b8", fontWeight: 500 }}>
                      ინტენსივობა: <strong>{sig.strength}</strong>
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* 3.5 Runtime: Complete Active Signals Inspection */}
      <SignalBlock signals={data.signals} />

      {/* 4. Actionable Conversation Starters & Topics */}
      {(bestTopics.length > 0 || conversationStarters.length > 0) && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.15rem", fontWeight: 800, color: "#0f172a" }}>
              საუბრის დასაწყები თემები & ფრაზები
            </h2>
            <div style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "0.15rem" }}>
              თემები, სადაც კომუნიკაცია ყველაზე მარტივად და დინამიკურად ვითარდება
            </div>
          </div>

          {/* Topics Badges */}
          {bestTopics.length > 0 && (
            <Card padded style={{ padding: "1.25rem" }}>
              <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#475569", marginBottom: "0.6rem" }}>
                რეკომენდებული სასაუბრო სფეროები:
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem" }}>
                {bestTopics.map((topic, idx) => (
                  <Badge key={idx} variant="brand" size="md">
                    🏷️ {getTopicLabel(topic)}
                  </Badge>
                ))}
              </div>
            </Card>
          )}

          {/* Runtime Starters Inspection */}
          <StartersInspectionBlock
            starters={conversationStarters}
            starterDetails={data.conversation_starter_details}
            onSelectStarter={relState === "accepted" ? handleSendStarterToChat : undefined}
          />
        </div>
      )}

      {/* 5. US / Compare Transition Card */}
      <Card padded style={{ padding: "1.5rem", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem", backgroundColor: "#fdf4ff", border: "1px solid #f5d0fe" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
            <span style={{ fontSize: "1.2rem" }}>⚖️</span>
            <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 800, color: "#1e1b4b" }}>
              რა შეიძლება არსებობდეს ჩვენ შორის? (US)
            </h3>
          </div>
          <p style={{ margin: "0.3rem 0 0 0", color: "#475569", fontSize: "0.875rem", lineHeight: 1.5 }}>
            {relState === "accepted"
              ? "თქვენი კავშირი აქტიურია. შეგიძლიათ ნახოთ სრული მრავალგანზომილებიანი სინასტრიული ანალიზი."
              : "ღრმა მრავალგანზომილებიანი შედარება (US) ხელმისაწვდომი ხდება კავშირის დამყარების შემდეგ."}
          </p>
        </div>

        <div>
          {relState === "accepted" ? (
            <Link to={`/compare/${targetId}`} style={{ textDecoration: "none" }}>
              <Button variant="brand" size="md">
                ⚖️ სრული შედარება (US) →
              </Button>
            </Link>
          ) : (
            <Link to={`/people/${targetId}`} style={{ textDecoration: "none" }}>
              <Button variant="outline" size="md">
                პროფილის ნახვა
              </Button>
            </Link>
          )}
        </div>
      </Card>

      {/* 6. Connection Invitation (INSIGHT -> INVITATION) */}
      <Card padded style={{ padding: "1.25rem 1.5rem", backgroundColor: "#ffffff" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: "0.975rem", color: "#0f172a" }}>
              {relState === "accepted"
                ? "თქვენ უკვე დაკავშირებული ხართ"
                : relState === "pending_out"
                ? "კავშირის მოთხოვნა გაგზავნილია"
                : relState === "pending_in"
                ? "ამ ადამიანმა გამოგიგზავნათ კავშირის მოთხოვნა"
                : "ინსაითი მოგეწონათ? დაიწყეთ საუბარი"}
            </div>
            <div style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "0.15rem" }}>
              {relState === "accepted"
                ? "გადადით ჩატში ან გაუგზავნეთ ზემოთ მოცემული სასაუბრო ფრაზა."
                : relState === "pending_out"
                ? "მოთხოვნის დადასტურების შემდეგ გაიხსნება პირადი ჩატი."
                : relState === "pending_in"
                ? "დაადასტურეთ მოთხოვნა სასაუბროდ."
                : data.connection_invitation?.text || "გაგზავნეთ მოთხოვნა, რომ ინსაითი გადაიქცეს რეალურ საუბრად."}
            </div>
          </div>

          <div style={{ display: "flex", gap: "0.6rem" }}>
            {relState === "none" && (
              <Button
                variant="brand"
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
                onClick={() => handleSendStarterToChat("")}
                icon={<span>💬</span>}
                style={{ minHeight: "44px", padding: "0 1.25rem" }}
              >
                ჩატის დაწყება
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* 7. Runtime: Birth Data Confidence / QA Block */}
      {data.data_quality && (
        <RuntimeInfoBlock
          title="Runtime: Birth Data Confidence & QA State"
          badge="Astro Engine QA"
          items={[
            { label: "Confidence", value: `${Math.round((data.data_quality.confidence || 0) * 100)}%` },
            { label: "Time Precision", value: data.data_quality.time_precision },
            { label: "Ascendant Used", value: data.data_quality.ascendant_used ? "YES" : "NO (Unknown Time fallback)" },
            { label: "Houses Used", value: data.data_quality.houses_used ? "YES" : "NO" },
          ]}
        />
      )}

      {/* 8. Runtime Raw API Payload (Safe Collapsible) */}
      <RuntimeJson data={data.raw} label="Why Relationship Raw API Data" />
    </div>
  );
};
