import React, { useEffect, useState, useRef } from "react";
import { useParams, useSearchParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { useAuth } from "../../core/auth/useAuth";
import { supabase } from "../../core/realtime/supabase";
import { MessageResponse } from "../../core/api/types";
import { LoadingState, ErrorState, EmptyState } from "../../shared/StatusState";

export const ChatPage: React.FC = () => {
  const { conversation_id } = useParams<{ conversation_id: string }>();
  const [searchParams] = useSearchParams();
  const conversationId = conversation_id || "";
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const [messageText, setMessageText] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Pre-fill input if starter query param was passed from Why Page
  useEffect(() => {
    const starterParam = searchParams.get("starter");
    if (starterParam) {
      setMessageText(starterParam);
    }
  }, [searchParams]);

  // Fetch initial message history
  const { data: messages, isLoading, error } = useQuery({
    queryKey: ["messages", conversationId],
    queryFn: () => API.conversations.listMessages(conversationId),
    enabled: !!conversationId,
  });

  // Realtime subscription for incoming messages
  useEffect(() => {
    if (!conversationId) return;

    const channel = supabase
      .channel(`public:messages:conversation_id=eq.${conversationId}`)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "messages",
          filter: `conversation_id=eq.${conversationId}`,
        },
        (payload) => {
          const newMsg = payload.new as MessageResponse;
          queryClient.setQueryData<MessageResponse[]>(
            ["messages", conversationId],
            (old) => {
              if (!old) return [newMsg];
              // Avoid duplicate if optimistic update or already present
              if (old.some((m) => m.id === newMsg.id)) return old;
              return [...old, newMsg];
            }
          );
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [conversationId, queryClient]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Send message mutation
  const sendMutation = useMutation({
    mutationFn: (body: string) => API.conversations.sendMessage(conversationId, body),
    onSuccess: (newMsg) => {
      setMessageText("");
      queryClient.setQueryData<MessageResponse[]>(
        ["messages", conversationId],
        (old) => {
          if (!old) return [newMsg];
          if (old.some((m) => m.id === newMsg.id)) return old;
          return [...old, newMsg];
        }
      );
    },
  });

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageText.trim() || sendMutation.isPending) return;
    sendMutation.mutate(messageText.trim());
  };

  if (isLoading) return <LoadingState message="Loading conversation messages..." />;
  if (error) {
    const err = error as any;
    if (err.statusCode === 404 || err.statusCode === 403) {
      return (
        <div style={{ padding: "2rem", textAlign: "center" }}>
          <h3>Conversation Unavailable</h3>
          <p style={{ color: "#666" }}>
            This conversation is inaccessible or the active connection is no longer present.
          </p>
          <Link to="/connections" style={{ color: "#1890ff", fontWeight: "bold" }}>
            Return to Connections
          </Link>
        </div>
      );
    }
    return <ErrorState error={error as Error} />;
  }

  const msgList = messages || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "75vh", border: "1px solid #d9d9d9", borderRadius: "6px", backgroundColor: "#fff" }}>
      {/* Chat Header */}
      <div style={{ padding: "0.75rem 1rem", borderBottom: "1px solid #e8e8e8", display: "flex", justifyContent: "space-between", alignItems: "center", backgroundColor: "#fafafa" }}>
        <div>
          <strong>Direct Conversation</strong>
          <div style={{ fontSize: "0.75rem", color: "#888" }}>ID: {conversationId.slice(0, 8)}...</div>
        </div>
        <Link to="/connections" style={{ textDecoration: "none", color: "#1890ff", fontSize: "0.85rem" }}>
          ← Connections
        </Link>
      </div>

      {/* Message History Stream */}
      <div style={{ flex: 1, padding: "1rem", overflowY: "auto", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {msgList.length === 0 ? (
          <EmptyState title="No messages yet" description="Send a greeting or a conversation starter to break the ice!" />
        ) : (
          msgList.map((m) => {
            const isMine = m.sender_user_id === user?.id;
            return (
              <div
                key={m.id}
                style={{
                  alignSelf: isMine ? "flex-end" : "flex-start",
                  maxWidth: "70%",
                  padding: "0.6rem 0.9rem",
                  borderRadius: "8px",
                  backgroundColor: isMine ? "#1890ff" : "#f0f0f0",
                  color: isMine ? "#fff" : "#111",
                  fontSize: "0.9rem",
                  lineHeight: "1.4",
                  wordBreak: "break-word",
                }}
              >
                <div>{m.body}</div>
                <div
                  style={{
                    fontSize: "0.7rem",
                    color: isMine ? "#e6f7ff" : "#888",
                    textAlign: "right",
                    marginTop: "0.2rem",
                  }}
                >
                  {new Date(m.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input Bar */}
      <form onSubmit={handleSend} style={{ padding: "0.75rem", borderTop: "1px solid #e8e8e8", display: "flex", gap: "0.5rem", backgroundColor: "#fff" }}>
        <input
          type="text"
          value={messageText}
          onChange={(e) => setMessageText(e.target.value)}
          placeholder="Type a message..."
          style={{ flex: 1, padding: "0.6rem", border: "1px solid #d9d9d9", borderRadius: "4px", outline: "none" }}
        />
        <button
          type="submit"
          disabled={sendMutation.isPending || !messageText.trim()}
          style={{
            padding: "0.6rem 1.2rem",
            background: "#1890ff",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            fontWeight: "bold",
            cursor: sendMutation.isPending || !messageText.trim() ? "not-allowed" : "pointer",
          }}
        >
          {sendMutation.isPending ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
};
