import React from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { useAuth } from "../../core/auth/useAuth";
import { Card, Button, Badge, LoadingState, ErrorState } from "../../shared/ui";

export const ComparePage: React.FC = () => {
  const { id, target_id } = useParams<{ id?: string; target_id?: string }>();
  const targetId = (id || target_id || "").trim();
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["compatibility", targetId],
    queryFn: async () => {
      try {
        return await API.compatibility.compare(targetId);
      } catch (err: any) {
        // Fallback to safe preview for unconnected users per Product Decision #2
        if (err.statusCode === 403) {
          const preview = await API.interpretations.comparePreview({
            target_user_id: targetId,
            locale: "ka",
          });
          return {
            id: `preview-${targetId}`,
            target_user_id: targetId,
            score: preview.score,
            dimensions: preview.dimensions,
            signals: preview.signals || [],
            best_topics: preview.best_topics || [],
            conversation_starters: preview.conversation_starters || [],
            data_quality: preview.data_quality,
            engine_version: preview.engine_version,
            calculated_at: preview.calculated_at,
          };
        }
        throw err;
      }
    },
    enabled: !!targetId,
    retry: false,
  });

  // Check connection status
  const { data: connections } = useQuery({
    queryKey: ["connections"],
    queryFn: API.connections.list,
  });

  const myConnection = connections?.find(
    (c) =>
      (c.user_a_id === user?.id && c.user_b_id === targetId) ||
      (c.user_b_id === user?.id && c.user_a_id === targetId)
  );

  const connectMutation = useMutation({
    mutationFn: () => API.connections.create(targetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connections"] });
    },
  });

  if (isLoading) return <LoadingState message="სინასტრიული რუკებისა და 4 განზომილების გამოთვლა..." />;
  if (error) return <ErrorState error={error as Error} onRetry={refetch} />;
  if (!data) return null;

  const { score, dimensions, signals = [], data_quality } = data;

  const dimensionList = [
    { key: "emotional_harmony", label: "ემოციური ჰარმონია", value: dimensions.emotional_harmony, icon: "🌊", color: "#3b82f6" },
    { key: "communication", label: "კომუნიკაცია & ინტელექტი", value: dimensions.communication, icon: "💡", color: "#6366f1" },
    { key: "attraction", label: "მიზიდულობა & ქიმია", value: dimensions.attraction, icon: "✨", color: "#ec4899" },
    { key: "growth_long_term", label: "გრძელვადიანი ზრდა", value: dimensions.growth_long_term, icon: "🌱", color: "#10b981" },
  ];

  const isConnected = myConnection?.status === "accepted";
  const isPending = myConnection?.status === "pending";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "1.5rem" }}>⚖️</span>
            <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 800, color: "#0f172a" }}>
              სინასტრიული შედარება (US)
            </h1>
          </div>
          <p style={{ margin: "0.25rem 0 0 0", color: "#64748b", fontSize: "0.9rem" }}>
            დეტერმინისტული Swiss Ephemeris გაანგარიშება და ურთიერთობის 4 განზომილება.
          </p>
        </div>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <Link to={`/people/${targetId}/why`} style={{ textDecoration: "none" }}>
            <Button variant="outline" size="sm">
              💡 რატომ ეს ადამიანი?
            </Button>
          </Link>
          <Link to={`/people/${targetId}`} style={{ textDecoration: "none" }}>
            <Button variant="outline" size="sm">
              ← პროფილი
            </Button>
          </Link>
        </div>
      </div>

      {/* Overall Score Banner */}
      <Card variant="accent" padded style={{ textAlign: "center", padding: "2.5rem 1.5rem" }}>
        <div style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "#7e22ce", fontWeight: 700, letterSpacing: "0.05em" }}>
          ურთიერთობის სინერგიის საერთო ქულა
        </div>
        <div style={{ fontSize: "3.75rem", fontWeight: 900, color: "#9333ea", margin: "0.5rem 0", lineHeight: 1 }}>
          {score.toFixed(1)} <span style={{ fontSize: "1.5rem", color: "#a855f7", fontWeight: 600 }}>/ 100</span>
        </div>
        <div style={{ display: "inline-block", marginTop: "0.5rem" }}>
          <Badge variant="brand" size="md">
            სიზუსტის კოეფიციენტი: {Math.round((data_quality?.confidence ?? 0.85) * 100)}% ({data_quality?.time_precision || "exact"})
          </Badge>
        </div>

        {/* CTA: If unconnected, invite connection! "The insight becomes the invitation" */}
        {!isConnected && (
          <div style={{ marginTop: "1.5rem", paddingTop: "1.25rem", borderTop: "1px solid #f0abfc" }}>
            <p style={{ margin: "0 0 0.75rem 0", fontSize: "0.9rem", color: "#475569" }}>
              ინსაითმა ინტერესი გაგიჩინათ? გაუგზავნეთ დაკავშირების მოწვევა:
            </p>
            {isPending ? (
              <Badge variant="warning" size="md">
                ⏳ მოთხოვნა გაგზავნილია
              </Badge>
            ) : (
              <Button
                variant="brand"
                size="md"
                isLoading={connectMutation.isPending}
                onClick={() => connectMutation.mutate()}
                icon={<span>🤝</span>}
              >
                დაკავშირების მოწვევა (Connect)
              </Button>
            )}
          </div>
        )}
      </Card>

      {/* 4 Core Dimensions Breakdown */}
      <div>
        <h3 style={{ margin: "0 0 0.75rem 0", fontSize: "1.1rem", color: "#0f172a" }}>
          4-განზომილებიანი ბალანსი
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
          {dimensionList.map((d) => (
            <Card key={d.key} padded>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                <span style={{ fontSize: "0.9rem", fontWeight: 600, color: "#1e293b", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                  <span>{d.icon}</span> {d.label}
                </span>
                <span style={{ fontWeight: 800, fontSize: "1rem", color: d.color }}>
                  {Math.round(d.value)}%
                </span>
              </div>
              <div style={{ height: "8px", backgroundColor: "#f1f5f9", borderRadius: "9999px", overflow: "hidden" }}>
                <div
                  style={{
                    height: "100%",
                    width: `${Math.min(100, Math.max(0, d.value))}%`,
                    backgroundColor: d.color,
                    borderRadius: "9999px",
                    transition: "width 0.5s ease",
                  }}
                />
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Relationship Signals (if any) */}
      {signals.length > 0 && (
        <Card padded>
          <h3 style={{ margin: "0 0 0.75rem 0", fontSize: "1.05rem", color: "#0f172a" }}>
            ასტროლოგიური სიგნალები & ასპექტები
          </h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {signals.map((sig, i) => (
              <Badge key={i} variant={sig.category === "harmony" ? "success" : sig.category === "attraction" ? "score" : "default"} size="md">
                {sig.label || sig.type} ({sig.strength})
              </Badge>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};
