import React, { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { Card, Button, Badge, LoadingState, ErrorState } from "../../shared/ui";

export const WhyPage: React.FC = () => {
  const { id, target_id } = useParams<{ id?: string; target_id?: string }>();
  const targetId = (id || target_id || "").trim();
  const navigate = useNavigate();

  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["why", targetId],
    queryFn: async () => {
      try {
        return await API.compatibility.why(targetId);
      } catch (err: any) {
        // Safe preview for unconnected discovery users per Product Decision #2
        if (err.statusCode === 403) {
          const preview = await API.interpretations.comparePreview({
            target_user_id: targetId,
            locale: "ka",
          });
          return {
            id: `preview-${targetId}`,
            target_user_id: targetId,
            score: preview.score,
            best_topics: preview.best_topics || [],
            conversation_starters: preview.conversation_starters || [],
            dimensions: preview.dimensions,
            signals: preview.signals || [],
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

  const handleSendStarterToChat = async (starterText: string) => {
    try {
      const conv = await API.conversations.createOrGetDirect(targetId);
      navigate(`/chat/${conv.id}?starter=${encodeURIComponent(starterText)}`);
    } catch (err: any) {
      alert(err.message || "Failed to start direct conversation. Make sure connection is active.");
    }
  };

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2500);
  };

  if (isLoading) return <LoadingState message="ურთიერთობის დინამიკისა და თემების გამოთვლა..." />;
  if (error) return <ErrorState error={error as Error} onRetry={refetch} />;
  if (!data) return null;

  const { score, best_topics = [], conversation_starters = [] } = data;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Header & Back Action */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "1.5rem" }}>💡</span>
            <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 800, color: "#0f172a" }}>
              რატომ ეს ადამიანი? (Why?)
            </h1>
          </div>
          <p style={{ margin: "0.25rem 0 0 0", color: "#64748b", fontSize: "0.9rem" }}>
            ურთიერთობის დინამიკა, საერთო წერტილები და საუბრის დასაწყები თემები.
          </p>
        </div>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <Link to={`/people/${targetId}`} style={{ textDecoration: "none" }}>
            <Button variant="outline" size="sm">
              ← პროფილი
            </Button>
          </Link>
          <Link to={`/compare/${targetId}`} style={{ textDecoration: "none" }}>
            <Button variant="brand" size="sm">
              ⚖️ სრული შედარება (US) →
            </Button>
          </Link>
        </div>
      </div>

      {/* Relationship Synergy Card */}
      <Card variant="accent" padded>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
          <Badge variant="score" size="md">
            სინერგიის ინდექსი
          </Badge>
          <span style={{ fontSize: "1.25rem", fontWeight: 800, color: "#9333ea" }}>
            {score.toFixed(1)} / 100
          </span>
        </div>
        <p style={{ margin: 0, color: "#334155", fontSize: "0.95rem", lineHeight: 1.6 }}>
          ეს თანხვედრა ეფუძნება თქვენი პლანეტარული პოზიციებისა და სტიქიების ურთიერთქმედებას.
          ქვემოთ მოცემული თემები დაგეხმარებათ პირველი კონტაქტის ბუნებრივად და საინტერესოდ დაწყებაში.
        </p>
      </Card>

      {/* Recommended Topics */}
      {best_topics.length > 0 && (
        <Card padded>
          <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "1.05rem", color: "#0f172a" }}>
            რეკომენდებული სასაუბრო თემები
          </h3>
          <p style={{ margin: "0 0 1rem 0", color: "#64748b", fontSize: "0.85rem" }}>
            თემები, სადაც კომუნიკაცია ყველაზე მარტივად და დინამიკურად ვითარდება:
          </p>

          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {best_topics.map((topic, i) => (
              <Badge key={i} variant="brand" size="md">
                🏷️ {topic.replace("_", " ")}
              </Badge>
            ))}
          </div>
        </Card>
      )}

      {/* Actionable Conversation Starters */}
      {conversation_starters.length > 0 && (
        <Card padded>
          <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "1.05rem", color: "#0f172a" }}>
            საუბრის დასაწყები ფრაზები (Icebreakers)
          </h3>
          <p style={{ margin: "0 0 1rem 0", color: "#64748b", fontSize: "0.85rem" }}>
            პირდაპირი, ცნობისმოყვარე კითხვები, რომლებიც შეგიძლიათ გამოიყენოთ პირველი შეტყობინებისთვის:
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {conversation_starters.map((starter, i) => (
              <div
                key={i}
                style={{
                  padding: "0.85rem 1rem",
                  backgroundColor: "#f8fafc",
                  border: "1px solid #e2e8f0",
                  borderRadius: "8px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: "1rem",
                }}
              >
                <div style={{ fontStyle: "italic", fontSize: "0.9rem", color: "#334155" }}>
                  "{starter}"
                </div>

                <div style={{ display: "flex", gap: "0.4rem", flexShrink: 0 }}>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCopy(starter, i)}
                  >
                    {copiedIndex === i ? "✓ კოპირებულია" : "📋 კოპირება"}
                  </Button>
                  <Button
                    variant="brand"
                    size="sm"
                    onClick={() => handleSendStarterToChat(starter)}
                  >
                    💬 ჩატში გაგზავნა
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};
