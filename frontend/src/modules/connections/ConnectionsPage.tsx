import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { API } from "../../core/api/endpoints";
import { useAuth } from "../../core/auth/useAuth";
import { ConnectionResponse } from "../../core/api/types";
import { LoadingState, ErrorState, EmptyState } from "../../shared/StatusState";

export const ConnectionsPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<"active" | "incoming" | "outgoing">("active");

  const { data: connections, isLoading, error, refetch } = useQuery({
    queryKey: ["connections"],
    queryFn: API.connections.list,
  });

  const transitionMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: "accept" | "decline" | "block" | "remove" }) =>
      API.connections.transition(id, action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connections"] });
    },
  });

  const handleStartChat = async (targetUserId: string) => {
    try {
      const conv = await API.conversations.createOrGetDirect(targetUserId);
      navigate(`/chat/${conv.id}`);
    } catch (err: any) {
      alert(err.message || "Could not open conversation.");
    }
  };

  if (isLoading) return <LoadingState message="Loading your connections..." />;
  if (error) return <ErrorState error={error as Error} onRetry={refetch} />;

  const allConns = connections || [];

  const accepted = allConns.filter((c) => c.status === "accepted");
  const incoming = allConns.filter((c) => c.status === "pending" && c.initiated_by !== user?.id);
  const outgoing = allConns.filter((c) => c.status === "pending" && c.initiated_by === user?.id);

  const getTargetId = (conn: ConnectionResponse) =>
    conn.user_a_id === user?.id ? conn.user_b_id : conn.user_a_id;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h2 style={{ margin: 0 }}>Social Connections</h2>
        <Link
          to="/people"
          style={{
            padding: "0.4rem 0.8rem",
            background: "#1890ff",
            color: "#fff",
            textDecoration: "none",
            borderRadius: "4px",
            fontSize: "0.85rem",
            fontWeight: "bold",
          }}
        >
          🔍 Discover Person
        </Link>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", borderBottom: "1px solid #d9d9d9", marginBottom: "1rem" }}>
        <button
          onClick={() => setActiveTab("active")}
          style={{
            padding: "0.6rem 1.2rem",
            background: "none",
            border: "none",
            borderBottom: activeTab === "active" ? "2px solid #1890ff" : "none",
            color: activeTab === "active" ? "#1890ff" : "#555",
            fontWeight: activeTab === "active" ? "bold" : "normal",
            cursor: "pointer",
          }}
        >
          Active Connections ({accepted.length})
        </button>
        <button
          onClick={() => setActiveTab("incoming")}
          style={{
            padding: "0.6rem 1.2rem",
            background: "none",
            border: "none",
            borderBottom: activeTab === "incoming" ? "2px solid #1890ff" : "none",
            color: activeTab === "incoming" ? "#1890ff" : "#555",
            fontWeight: activeTab === "incoming" ? "bold" : "normal",
            cursor: "pointer",
          }}
        >
          Incoming Requests ({incoming.length})
        </button>
        <button
          onClick={() => setActiveTab("outgoing")}
          style={{
            padding: "0.6rem 1.2rem",
            background: "none",
            border: "none",
            borderBottom: activeTab === "outgoing" ? "2px solid #1890ff" : "none",
            color: activeTab === "outgoing" ? "#1890ff" : "#555",
            fontWeight: activeTab === "outgoing" ? "bold" : "normal",
            cursor: "pointer",
          }}
        >
          Sent Requests ({outgoing.length})
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === "active" && (
        <div>
          {accepted.length === 0 ? (
            <EmptyState
              title="No Active Connections Yet"
              description="Connect with discoverable users to unlock full Synastry comparisons and 1-on-1 chat."
              actionLabel="Discover People"
              onAction={() => navigate("/people")}
            />
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {accepted.map((conn) => {
                const targetId = getTargetId(conn);
                return (
                  <div
                    key={conn.id}
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
                      <Link to={`/people/${targetId}`} style={{ fontWeight: "bold", textDecoration: "none", color: "#1890ff" }}>
                        Person (ID: {targetId.slice(0, 8)}...)
                      </Link>
                      <div style={{ color: "#888", fontSize: "0.8rem", marginTop: "0.2rem" }}>
                        Connected since {new Date(conn.updated_at).toLocaleDateString()}
                      </div>
                    </div>

                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <Link
                        to={`/compare/${targetId}`}
                        style={{
                          padding: "0.4rem 0.8rem",
                          background: "#722ed1",
                          color: "#fff",
                          textDecoration: "none",
                          borderRadius: "4px",
                          fontSize: "0.85rem",
                          fontWeight: "bold",
                        }}
                      >
                        🔮 Compare
                      </Link>
                      <button
                        onClick={() => handleStartChat(targetId)}
                        style={{
                          padding: "0.4rem 0.8rem",
                          background: "#1890ff",
                          color: "#fff",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontSize: "0.85rem",
                          fontWeight: "bold",
                        }}
                      >
                        💬 Chat
                      </button>
                      <button
                        onClick={() => transitionMutation.mutate({ id: conn.id, action: "remove" })}
                        style={{
                          padding: "0.4rem 0.6rem",
                          background: "#fff",
                          border: "1px solid #d9d9d9",
                          borderRadius: "4px",
                          color: "#666",
                          cursor: "pointer",
                          fontSize: "0.8rem",
                        }}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {activeTab === "incoming" && (
        <div>
          {incoming.length === 0 ? (
            <EmptyState title="No Incoming Requests" description="You have responded to all incoming connection requests." />
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {incoming.map((conn) => {
                const targetId = getTargetId(conn);
                return (
                  <div
                    key={conn.id}
                    style={{
                      padding: "1rem",
                      border: "1px solid #ffd591",
                      borderRadius: "6px",
                      backgroundColor: "#fffbe6",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div>
                      <Link to={`/people/${targetId}`} style={{ fontWeight: "bold", textDecoration: "none", color: "#d46b08" }}>
                        New Request from Person ({targetId.slice(0, 8)}...)
                      </Link>
                      <div style={{ color: "#888", fontSize: "0.8rem", marginTop: "0.2rem" }}>
                        Received {new Date(conn.created_at).toLocaleDateString()}
                      </div>
                    </div>

                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <button
                        onClick={() => transitionMutation.mutate({ id: conn.id, action: "accept" })}
                        style={{
                          padding: "0.4rem 0.8rem",
                          background: "#52c41a",
                          color: "#fff",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontWeight: "bold",
                        }}
                      >
                        Accept
                      </button>
                      <button
                        onClick={() => transitionMutation.mutate({ id: conn.id, action: "decline" })}
                        style={{
                          padding: "0.4rem 0.8rem",
                          background: "#f5222d",
                          color: "#fff",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                        }}
                      >
                        Decline
                      </button>
                      <button
                        onClick={() => transitionMutation.mutate({ id: conn.id, action: "block" })}
                        style={{
                          padding: "0.4rem 0.6rem",
                          background: "#333",
                          color: "#fff",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontSize: "0.75rem",
                        }}
                      >
                        Block
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {activeTab === "outgoing" && (
        <div>
          {outgoing.length === 0 ? (
            <EmptyState title="No Sent Requests" description="You have no pending outgoing connection requests." />
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {outgoing.map((conn) => {
                const targetId = getTargetId(conn);
                return (
                  <div
                    key={conn.id}
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
                      <Link to={`/people/${targetId}`} style={{ fontWeight: "bold", textDecoration: "none", color: "#1890ff" }}>
                        Person ({targetId.slice(0, 8)}...)
                      </Link>
                      <div style={{ color: "#888", fontSize: "0.8rem", marginTop: "0.2rem" }}>
                        Sent on {new Date(conn.created_at).toLocaleDateString()}
                      </div>
                    </div>

                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <span style={{ fontSize: "0.85rem", color: "#fa8c16", padding: "0.3rem 0.6rem" }}>
                        ⏳ Pending Approval
                      </span>
                      <button
                        onClick={() => transitionMutation.mutate({ id: conn.id, action: "remove" })}
                        style={{
                          padding: "0.4rem 0.6rem",
                          background: "#fff",
                          border: "1px solid #d9d9d9",
                          borderRadius: "4px",
                          color: "#666",
                          cursor: "pointer",
                          fontSize: "0.8rem",
                        }}
                      >
                        Cancel Request
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
