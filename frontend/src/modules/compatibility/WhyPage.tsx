import React, { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { LoadingState, ErrorState } from "../../shared/StatusState";

export const WhyPage: React.FC = () => {
  const { target_id } = useParams<{ target_id: string }>();
  const targetId = target_id || "";
  const navigate = useNavigate();

  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["why", targetId],
    queryFn: () => API.compatibility.why(targetId),
    enabled: !!targetId,
    retry: false,
  });

  const handleSendStarterToChat = async (starterText: string) => {
    try {
      const conv = await API.conversations.createOrGetDirect(targetId);
      navigate(`/chat/${conv.id}?starter=${encodeURIComponent(starterText)}`);
    } catch (err: any) {
      alert(err.message || "Failed to start conversation.");
    }
  };

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2500);
  };

  if (isLoading) return <LoadingState message="Loading relationship dynamics and conversation starters..." />;
  if (error) return <ErrorState error={error as Error} onRetry={refetch} />;
  if (!data) return null;

  const { score, best_topics, conversation_starters } = data;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h2 style={{ margin: 0 }}>Why This Person?</h2>
          <div style={{ color: "#666", fontSize: "0.85rem", marginTop: "0.2rem" }}>
            Astrological relationship dynamics and actionable conversation themes.
          </div>
        </div>
        <Link
          to={`/compare/${targetId}`}
          style={{
            padding: "0.4rem 0.8rem",
            background: "#f0f2f5",
            color: "#333",
            textDecoration: "none",
            borderRadius: "4px",
            border: "1px solid #d9d9d9",
            fontSize: "0.85rem",
          }}
        >
          ← Back to Compare
        </Link>
      </div>

      {/* Relationship Summary Banner */}
      <div style={{ padding: "1.5rem", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff", marginBottom: "1.5rem" }}>
        <h3 style={{ marginTop: 0 }}>Core Synergy Index: {score.toFixed(1)} / 100</h3>
        <p style={{ color: "#444", fontSize: "0.95rem", lineHeight: "1.5" }}>
          This compatibility profile is driven by mutual planetary alignments and elemental balances. Use these suggested themes to connect on common ground and spark natural conversational chemistry.
        </p>
      </div>

      {/* Recommended Conversation Topics (Max 4) */}
      <div style={{ padding: "1.5rem", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff", marginBottom: "1.5rem" }}>
        <h3 style={{ marginTop: 0, marginBottom: "0.5rem" }}>Recommended Topics (Max 4)</h3>
        <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "1rem" }}>
          Derived deterministically from Mercury communication patterns and dominant element synergies.
        </p>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem" }}>
          {best_topics.map((topic, i) => (
            <span
              key={i}
              style={{
                padding: "0.4rem 0.9rem",
                background: "#f0f5ff",
                border: "1px solid #adc6ff",
                color: "#1d39c4",
                borderRadius: "16px",
                fontWeight: "bold",
                fontSize: "0.85rem",
                textTransform: "capitalize",
              }}
            >
              🏷️ {topic.replace("_", " ")}
            </span>
          ))}
        </div>
      </div>

      {/* Actionable Conversation Starters (Max 3) */}
      <div style={{ padding: "1.5rem", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff" }}>
        <h3 style={{ marginTop: 0, marginBottom: "0.5rem" }}>Astrological Conversation Starters (Max 3)</h3>
        <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "1.2rem" }}>
          High-resonance questions derived from your active planetary interactions.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {conversation_starters.map((starter, idx) => (
            <div
              key={idx}
              style={{
                padding: "1rem",
                border: "1px solid #e8e8e8",
                borderRadius: "6px",
                backgroundColor: "#fafafa",
              }}
            >
              <div style={{ fontSize: "1rem", fontStyle: "italic", marginBottom: "0.8rem", color: "#222" }}>
                "{starter}"
              </div>

              <div style={{ display: "flex", gap: "0.5rem" }}>
                <button
                  onClick={() => handleSendStarterToChat(starter)}
                  style={{
                    padding: "0.4rem 0.8rem",
                    background: "#1890ff",
                    color: "#fff",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontWeight: "bold",
                    fontSize: "0.8rem",
                  }}
                >
                  💬 Send into Chat
                </button>
                <button
                  onClick={() => handleCopy(starter, idx)}
                  style={{
                    padding: "0.4rem 0.8rem",
                    background: "#fff",
                    border: "1px solid #d9d9d9",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontSize: "0.8rem",
                  }}
                >
                  {copiedIndex === idx ? "✅ Copied!" : "📋 Copy"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
