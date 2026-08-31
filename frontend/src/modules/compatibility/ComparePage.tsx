import React from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { LoadingState, ErrorState } from "../../shared/StatusState";

export const ComparePage: React.FC = () => {
  const { target_id } = useParams<{ target_id: string }>();
  const targetId = target_id || "";

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["compatibility", targetId],
    queryFn: () => API.compatibility.compare(targetId),
    enabled: !!targetId,
    retry: false,
  });

  if (isLoading) return <LoadingState message="Calculating Synastry V1 compatibility..." />;
  if (error) {
    const err = error as any;
    if (err.statusCode === 403) {
      return (
        <div style={{ padding: "2rem", textAlign: "center" }}>
          <h3>Active Connection Required</h3>
          <p style={{ color: "#666" }}>
            You must have an active, accepted connection with this person to run Synastry compatibility calculations.
          </p>
          <Link to={`/people/${targetId}`} style={{ color: "#1890ff", fontWeight: "bold" }}>
            Go to Person Profile
          </Link>
        </div>
      );
    }
    return <ErrorState error={error as Error} onRetry={refetch} />;
  }

  if (!data) return null;

  const { score, dimensions, signals, data_quality, engine_version, calculated_at } = data;

  const categoryColors: Record<string, string> = {
    harmony: "#52c41a",
    attraction: "#eb2f96",
    communication: "#1890ff",
    growth: "#722ed1",
    stability: "#fa8c16",
    notice: "#faad14",
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h2 style={{ margin: 0 }}>Synastry Compatibility</h2>
          <div style={{ color: "#666", fontSize: "0.85rem", marginTop: "0.2rem" }}>
            Deterministic cross-chart comparison with Person (<code>{targetId.slice(0, 8)}...</code>)
          </div>
        </div>
        <Link
          to={`/why/${targetId}`}
          style={{
            padding: "0.5rem 1rem",
            background: "#722ed1",
            color: "#fff",
            textDecoration: "none",
            borderRadius: "4px",
            fontWeight: "bold",
            fontSize: "0.9rem",
          }}
        >
          🔍 Why This Person
        </Link>
      </div>

      {/* Overall Score Banner */}
      <div
        style={{
          padding: "2rem",
          border: "1px solid #d9d9d9",
          borderRadius: "8px",
          backgroundColor: "#fff",
          textAlign: "center",
          marginBottom: "1.5rem",
        }}
      >
        <div style={{ fontSize: "0.9rem", textTransform: "uppercase", color: "#888", letterSpacing: "1px" }}>
          Overall Relationship Compatibility
        </div>
        <div style={{ fontSize: "3.5rem", fontWeight: "bold", color: "#722ed1", margin: "0.5rem 0" }}>
          {score.toFixed(1)} <span style={{ fontSize: "1.5rem", color: "#888" }}>/ 100</span>
        </div>
        <div style={{ display: "inline-block", padding: "0.2rem 0.8rem", background: "#f0f5ff", border: "1px solid #adc6ff", borderRadius: "12px", fontSize: "0.8rem", color: "#1d39c4" }}>
          Confidence: {(data_quality.confidence * 100).toFixed(0)}% ({data_quality.time_precision} birth time)
        </div>
      </div>

      {/* 4 Core Dimensions */}
      <h3 style={{ marginBottom: "0.8rem" }}>4-Dimensional Breakdown</h3>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
        <div style={{ padding: "1rem", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff" }}>
          <div style={{ fontSize: "0.85rem", color: "#666" }}>🌸 Emotional Harmony</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold", marginTop: "0.3rem" }}>{dimensions.emotional_harmony.toFixed(1)}</div>
        </div>

        <div style={{ padding: "1rem", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff" }}>
          <div style={{ fontSize: "0.85rem", color: "#666" }}>💡 Communication</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold", marginTop: "0.3rem" }}>{dimensions.communication.toFixed(1)}</div>
        </div>

        <div style={{ padding: "1rem", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff" }}>
          <div style={{ fontSize: "0.85rem", color: "#666" }}>⚡ Attraction & Chemistry</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold", marginTop: "0.3rem" }}>{dimensions.attraction.toFixed(1)}</div>
        </div>

        <div style={{ padding: "1rem", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff" }}>
          <div style={{ fontSize: "0.85rem", color: "#666" }}>🌱 Growth & Resilience</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold", marginTop: "0.3rem" }}>{dimensions.growth_long_term.toFixed(1)}</div>
        </div>
      </div>

      {/* Top Signals */}
      <h3 style={{ marginBottom: "0.8rem" }}>Key Relationship Signals (Max 6)</h3>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginBottom: "2rem" }}>
        {signals.length === 0 ? (
          <div style={{ color: "#888", fontStyle: "italic" }}>No active significant aspects detected.</div>
        ) : (
          signals.map((sig, idx) => (
            <div
              key={idx}
              style={{
                padding: "1rem",
                border: "1px solid #e8e8e8",
                borderRadius: "6px",
                backgroundColor: "#fff",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <div style={{ fontWeight: "bold", fontSize: "1rem" }}>{sig.label}</div>
                <div style={{ color: "#666", fontSize: "0.8rem", marginTop: "0.2rem" }}>
                  {sig.source_aspects.join(" • ")}
                </div>
              </div>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <span
                  style={{
                    padding: "0.2rem 0.6rem",
                    borderRadius: "4px",
                    fontSize: "0.75rem",
                    textTransform: "uppercase",
                    fontWeight: "bold",
                    color: "#fff",
                    backgroundColor: categoryColors[sig.category] || "#888",
                  }}
                >
                  {sig.category}
                </span>
                <span
                  style={{
                    padding: "0.2rem 0.5rem",
                    borderRadius: "4px",
                    fontSize: "0.75rem",
                    background: "#f5f5f5",
                    color: "#555",
                    border: "1px solid #d9d9d9",
                  }}
                >
                  {sig.strength}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Engine & Calculation Metadata */}
      <div style={{ padding: "1rem", background: "#fafafa", borderRadius: "4px", fontSize: "0.8rem", color: "#666" }}>
        <div><strong>Engine Version:</strong> {engine_version}</div>
        <div><strong>Calculated At:</strong> {new Date(calculated_at).toLocaleString()}</div>
        <div><strong>Ascendant Factored:</strong> {data_quality.ascendant_used ? "Yes" : "No (Unknown/Missing)"}</div>
        <div><strong>Houses Factored:</strong> {data_quality.houses_used ? "Yes" : "No"}</div>
      </div>
    </div>
  );
};
