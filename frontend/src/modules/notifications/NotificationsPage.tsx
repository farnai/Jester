import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { API } from "../../core/api/endpoints";
import { NotificationResponse } from "../../core/api/types";
import { LoadingState, ErrorState, EmptyState } from "../../shared/StatusState";

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

    if (n.notification_type === "connection_request") {
      navigate("/connections");
    } else if (n.notification_type === "connection_accepted") {
      const otherId = n.payload?.other_user_id;
      if (otherId) navigate(`/compare/${otherId}`);
      else navigate("/connections");
    } else if (n.notification_type === "message_received") {
      const convId = n.payload?.conversation_id;
      if (convId) navigate(`/chat/${convId}`);
      else navigate("/connections");
    } else if (n.notification_type === "daily_energy") {
      navigate("/self/astrology");
    }
  };

  if (isLoading) return <LoadingState message="Loading notifications..." />;
  if (error) return <ErrorState error={error as Error} onRetry={refetch} />;

  const list = notifications || [];

  return (
    <div>
      <h2 style={{ marginTop: 0, marginBottom: "1.5rem" }}>Notifications & In-App Activity</h2>

      {list.length === 0 ? (
        <EmptyState title="All Caught Up" description="You have no notifications at this time." />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {list.map((n) => {
            const isUnread = !n.read_at;
            return (
              <div
                key={n.id}
                onClick={() => handleNotificationClick(n)}
                style={{
                  padding: "1rem",
                  border: isUnread ? "1px solid #91d5ff" : "1px solid #e8e8e8",
                  borderRadius: "6px",
                  backgroundColor: isUnread ? "#e6f7ff" : "#fff",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  cursor: "pointer",
                }}
              >
                <div>
                  <div style={{ fontWeight: isUnread ? "bold" : "normal", fontSize: "0.95rem" }}>
                    {n.notification_type === "connection_request" && "🤝 New Connection Request"}
                    {n.notification_type === "connection_accepted" && "🎉 Connection Accepted"}
                    {n.notification_type === "message_received" && "💬 New Message Received"}
                    {n.notification_type === "daily_energy" && "☀️ Daily Astrological Energy"}
                    {n.notification_type === "system" && "🔔 System Notice"}
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "#666", marginTop: "0.2rem" }}>
                    {JSON.stringify(n.payload)}
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "#999", marginTop: "0.2rem" }}>
                    {new Date(n.created_at).toLocaleString()}
                  </div>
                </div>

                {isUnread && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      markReadMutation.mutate(n.id);
                    }}
                    style={{
                      padding: "0.3rem 0.6rem",
                      background: "#fff",
                      border: "1px solid #91d5ff",
                      borderRadius: "4px",
                      color: "#1890ff",
                      fontSize: "0.75rem",
                      cursor: "pointer",
                    }}
                  >
                    Mark Read
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
