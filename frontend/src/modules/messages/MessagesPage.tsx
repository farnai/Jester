import React from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { useAuth } from "../../core/auth/useAuth";
import { Card, Button, LoadingState, ErrorState } from "../../shared/ui";

export const MessagesPage: React.FC = () => {
  const { user } = useAuth();

  // Fetch connections to display direct messageable interlocutors
  const { data: connections, isLoading, error, refetch } = useQuery({
    queryKey: ["connections"],
    queryFn: API.connections.list,
  });

  if (isLoading) {
    return <LoadingState message="საუბრებისა და კავშირების ჩატვირთვა..." />;
  }

  if (error) {
    return <ErrorState error={error as Error} onRetry={refetch} />;
  }

  const accepted = (connections || []).filter((c) => c.status === "accepted");

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "0.75rem" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "1.5rem" }}>💬</span>
            <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 800, color: "#0f172a" }}>
              შეტყობინებები
            </h1>
          </div>
          <p style={{ margin: "0.25rem 0 0 0", color: "#64748b", fontSize: "0.9rem" }}>
            აქტიური დიალოგები და ურთიერთობის კონტექსტი.
          </p>
        </div>

        <Link to="/connections" style={{ textDecoration: "none" }}>
          <Button variant="outline" size="sm">
            🤝 ყველა კავშირი ({accepted.length})
          </Button>
        </Link>
      </div>

      {/* Backend Dependency Notice for Codex */}
      <div
        style={{
          padding: "0.85rem 1rem",
          backgroundColor: "#f8fafc",
          border: "1px dashed #94a3b8",
          borderRadius: "8px",
          fontSize: "0.825rem",
          color: "#475569",
          lineHeight: 1.5,
        }}
      >
        <strong>📌 არქიტექტურული შენიშვნა (Codex Backend Dependency):</strong>
        <br />
        სრულფასოვანი საუბრების სიის (Inbox) გამოსატანად საჭიროა <code>GET /v1/conversations</code> ენდფოინთი.
        მანამდე საუბრის გახსნა შესაძლებელია დადასტურებული კავშირის პროფილის ან კავშირების გვერდიდან.
      </div>

      {/* Active Interlocutors List */}
      <div>
        <h3 style={{ margin: "0 0 0.75rem 0", fontSize: "1.05rem", color: "#1e293b" }}>
          დადასტურებული კონტაქტები საუბრისთვის
        </h3>

        {accepted.length === 0 ? (
          <Card padded style={{ textAlign: "center", padding: "2.5rem 1rem" }}>
            <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>👥</div>
            <div style={{ fontWeight: 700, fontSize: "1rem", color: "#1e293b", marginBottom: "0.3rem" }}>
              აქტიური საუბრები ჯერ არ გაქვთ
            </div>
            <p style={{ color: "#64748b", fontSize: "0.85rem", maxWidth: "380px", margin: "0 auto 1.25rem auto" }}>
              გადადით აღმოჩენის გვერდზე, ნახეთ სინასტრიული რუკები და დაამყარეთ პირველი კავშირები.
            </p>
            <Link to="/discover" style={{ textDecoration: "none" }}>
              <Button variant="brand" size="md">
                🔍 ადამიანების აღმოჩენა
              </Button>
            </Link>
          </Card>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {accepted.map((conn) => {
              const targetId = conn.user_a_id === user?.id ? conn.user_b_id : conn.user_a_id;

              return (
                <Card
                  key={conn.id}
                  padded
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "0.75rem",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                    <div
                      style={{
                        width: "40px",
                        height: "40px",
                        borderRadius: "50%",
                        backgroundColor: "#e0e7ff",
                        color: "#4338ca",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontWeight: 700,
                      }}
                    >
                      👤
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: "0.95rem", color: "#0f172a" }}>
                        მომხმარებელი: {targetId.slice(0, 8)}...
                      </div>
                      <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.15rem" }}>
                        დაკავშირებულია: {new Date(conn.created_at).toLocaleDateString("ka-GE")}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    <Link to={`/people/${targetId}`} style={{ textDecoration: "none" }}>
                      <Button variant="outline" size="sm">
                        პროფილი
                      </Button>
                    </Link>
                    <Link to={`/people/${targetId}/why`} style={{ textDecoration: "none" }}>
                      <Button variant="outline" size="sm">
                        რატომ?
                      </Button>
                    </Link>
                    <Button
                      variant="brand"
                      size="sm"
                      onClick={async () => {
                        try {
                          const conv = await API.conversations.createOrGetDirect(targetId);
                          window.location.href = `/chat/${conv.id}`;
                        } catch (err: any) {
                          alert(err.message || "Could not open direct chat.");
                        }
                      }}
                    >
                      💬 ჩატის გახსნა
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
