import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { API } from "../../core/api/endpoints";
import { NotificationResponse } from "../../core/api/types";
import { LoadingState, ErrorState, EmptyState } from "../../shared/StatusState";

const getNotificationFallbackMessage = (type?: string, payload?: Record<string, any>): string => {
  if (typeof payload?.message === "string" && payload.message.trim().length > 0) {
    return payload.message.trim();
  }

  switch (type) {
    case "connection_request":
      return "ახალი კავშირის მოთხოვნა — დააჭირეთ სანახავად";
    case "connection_accepted":
      return "თქვენი კავშირის მოთხოვნა მიღებულია — ნახეთ სრული შედარება";
    case "message_received":
      return "ახალი შეტყობინება პირად ჩატში";
    case "daily_energy":
      return "დღის ასტროლოგიური ენერგია და გზამკვლევი მზად არის";
    default:
      return "ახალი შეტყობინება სისტემაში";
  }
};

const getNotificationTitle = (type?: string): string => {
  switch (type) {
    case "connection_request":
      return "🤝 ახალი კავშირის მოთხოვნა";
    case "connection_accepted":
      return "🎉 კავშირი მიღებულია";
    case "message_received":
      return "💬 ახალი შეტყობინება";
    case "daily_energy":
      return "☀️ დღის ასტროლოგიური ენერგია";
    default:
      return "🔔 შეტყობინება";
  }
};

export const NotificationsPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: notifications, isLoading, error, refetch } = useQuery({
    queryKey: ["notifications"],
    queryFn: API.notifications.list,
  });

  const markReadMutation = useMutation({
    mutationFn: (id: string) => API.notifications.markRead(id),
    onSuccess: (updated) => {
      queryClient.setQueryData<NotificationResponse[]>(["notifications"], (old) => {
        if (!old) return [updated];
        return old.map((n) => (n.id === updated.id ? updated : n));
      });
    },
  });

  const handleNotificationClick = (n: NotificationResponse) => {
    if (!n.read_at) {
      markReadMutation.mutate(n.id);
    }

    const nType = n.notification_type || (n as any).type;

    if (nType === "connection_request") {
      navigate("/connections?tab=incoming");
    } else if (nType === "connection_accepted") {
      const otherId = n.payload?.other_user_id || n.payload?.actor_id;
      if (otherId) navigate(`/compare/${otherId}`);
      else navigate("/connections");
    } else if (nType === "message_received") {
      const convId = n.payload?.conversation_id;
      if (convId) navigate(`/chat/${convId}`);
      else navigate("/connections");
    } else if (nType === "daily_energy") {
      navigate("/self/astrology");
    }
  };

  if (isLoading) return <LoadingState message="შეტყობინებების ჩატვირთვა..." />;
  if (error) return <ErrorState error={error as Error} onRetry={refetch} />;

  const list = notifications || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      <div>
        <h2 style={{ marginTop: 0, marginBottom: "0.25rem" }}>შეტყობინებები</h2>
        <div style={{ fontSize: "0.85rem", color: "#64748b" }}>
          კავშირების, შეტყობინებებისა და ასტროლოგიური მოვლენების ჟურნალი
        </div>
      </div>

      {list.length === 0 ? (
        <EmptyState title="შეტყობინებები არ არის" description="თქვენ არ გაქვთ ახალი შეტყობინებები." />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {list.map((n) => {
            const isUnread = !n.read_at;
            const nType = n.notification_type || (n as any).type;
            const displayMessage = getNotificationFallbackMessage(nType, n.payload);
            const title = getNotificationTitle(nType);

            return (
              <div
                key={n.id}
                onClick={() => handleNotificationClick(n)}
                style={{
                  padding: "1rem",
                  border: isUnread ? "1px solid #93c5fd" : "1px solid #e2e8f0",
                  borderRadius: "8px",
                  backgroundColor: isUnread ? "#eff6ff" : "#ffffff",
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.5rem",
                  cursor: "pointer",
                  transition: "border-color 0.15s, background-color 0.15s",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <span
                        style={{
                          fontSize: "0.7rem",
                          fontWeight: 700,
                          padding: "0.15rem 0.4rem",
                          borderRadius: "4px",
                          backgroundColor: isUnread ? "#2563eb" : "#94a3b8",
                          color: "#ffffff",
                          textTransform: "uppercase",
                        }}
                      >
                        {isUnread ? "ახალი" : "წაკითხული"}
                      </span>
                      <strong style={{ fontSize: "0.95rem", color: "#0f172a" }}>
                        {title}
                      </strong>
                    </div>

                    {displayMessage && (
                      <div style={{ fontSize: "0.875rem", color: "#334155", marginTop: "0.35rem" }}>
                        {displayMessage}
                      </div>
                    )}
                  </div>

                  {isUnread && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        markReadMutation.mutate(n.id);
                      }}
                      style={{
                        padding: "0.3rem 0.6rem",
                        background: "#ffffff",
                        border: "1px solid #93c5fd",
                        borderRadius: "4px",
                        color: "#2563eb",
                        fontSize: "0.75rem",
                        cursor: "pointer",
                        fontWeight: 600,
                        flexShrink: 0,
                      }}
                    >
                      წაკითხვა
                    </button>
                  )}
                </div>

                <div style={{ fontSize: "0.75rem", color: "#94a3b8", borderTop: "1px dashed #f1f5f9", paddingTop: "0.4rem" }}>
                  {new Date(n.created_at).toLocaleString("ka-GE")}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
