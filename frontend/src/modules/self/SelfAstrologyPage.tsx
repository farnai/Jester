import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { API } from "../../core/api/endpoints";
import { LoadingState, ErrorState } from "../../shared/StatusState";

export const SelfAstrologyPage: React.FC = () => {
  const queryClient = useQueryClient();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["astrology", "me"],
    queryFn: API.astrology.getMySafeAstro,
  });

  const recalcMutation = useMutation({
    mutationFn: API.astrology.recalculate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["astrology", "me"] });
    },
  });

  if (isLoading) return <LoadingState message="Loading your natal astrology profile..." />;
  if (error) return <ErrorState error={error as Error} onRetry={refetch} />;
  if (!data) return null;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h2 style={{ margin: 0 }}>My Astrological Identity</h2>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <Link
            to="/onboarding/birth-data"
            style={{
              padding: "0.4rem 0.8rem",
              background: "#f0f2f5",
              color: "#333",
              textDecoration: "none",
              borderRadius: "4px",
              fontSize: "0.85rem",
              border: "1px solid #d9d9d9",
            }}
          >
            Edit Birth Data
          </Link>
          <button
            onClick={() => recalcMutation.mutate()}
            disabled={recalcMutation.isPending}
            style={{
              padding: "0.4rem 0.8rem",
              background: "#1890ff",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              cursor: recalcMutation.isPending ? "not-allowed" : "pointer",
              fontSize: "0.85rem",
            }}
          >
            {recalcMutation.isPending ? "Recalculating..." : "Recalculate"}
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
        {/* Core Signs */}
        <div style={{ padding: "1.2rem", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff" }}>
          <div style={{ color: "#888", fontSize: "0.8rem", textTransform: "uppercase" }}>Sun Sign</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold", marginTop: "0.3rem" }}>☀️ {data.sun_sign}</div>
        </div>

        <div style={{ padding: "1.2rem", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff" }}>
          <div style={{ color: "#888", fontSize: "0.8rem", textTransform: "uppercase" }}>Moon Sign</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold", marginTop: "0.3rem" }}>🌙 {data.moon_sign}</div>
        </div>

        <div style={{ padding: "1.2rem", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff" }}>
          <div style={{ color: "#888", fontSize: "0.8rem", textTransform: "uppercase" }}>Ascendant Sign</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold", marginTop: "0.3rem" }}>
            🌅 {data.ascendant_sign || <span style={{ fontSize: "1rem", color: "#999" }}>Unknown</span>}
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem", marginTop: "1rem" }}>
        {/* Elemental & Modality Weights */}
        <div style={{ padding: "1.2rem", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff" }}>
          <div style={{ color: "#888", fontSize: "0.8rem", textTransform: "uppercase" }}>Dominant Element</div>
          <div style={{ fontSize: "1.3rem", fontWeight: "bold", marginTop: "0.3rem" }}>🔥 {data.element_primary}</div>
        </div>

        <div style={{ padding: "1.2rem", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff" }}>
          <div style={{ color: "#888", fontSize: "0.8rem", textTransform: "uppercase" }}>Dominant Modality</div>
          <div style={{ fontSize: "1.3rem", fontWeight: "bold", marginTop: "0.3rem" }}>⚡ {data.modality_primary}</div>
        </div>
      </div>

      <div style={{ marginTop: "1.5rem", padding: "1rem", background: "#fafafa", borderRadius: "4px", fontSize: "0.85rem", color: "#666" }}>
        <div><strong>Data Version:</strong> {data.source_birth_data_version}</div>
        <div><strong>Engine Version:</strong> {data.engine_version}</div>
        <div><strong>Last Calculated:</strong> {new Date(data.updated_at).toLocaleString()}</div>
      </div>
    </div>
  );
};
