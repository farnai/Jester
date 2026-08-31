import React, { useEffect, useState } from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../core/auth/useAuth";
import { API } from "../core/api/endpoints";
import { supabase } from "../core/realtime/supabase";
import { DebugBar } from "./DebugBar";

export const AppShell: React.FC = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState<number>(0);

  useEffect(() => {
    if (!user) return;

    // Fetch initial unread count
    API.notifications
      .list()
      .then((items) => {
        const unread = items.filter((n) => !n.read_at).length;
        setUnreadCount(unread);
      })
      .catch(() => {});

    // Subscribe to realtime notifications
    const channel = supabase
      .channel(`public:notifications:user_id=eq.${user.id}`)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "notifications",
          filter: `user_id=eq.${user.id}`,
        },
        () => {
          setUnreadCount((prev) => prev + 1);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [user]);

  const handleSignOut = async () => {
    await signOut();
    navigate("/auth/login");
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* Global Header */}
      <header
        style={{
          borderBottom: "1px solid #e8e8e8",
          padding: "0.75rem 1.5rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          backgroundColor: "#fff",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
          <Link
            to="/self/astrology"
            style={{
              fontWeight: "bold",
              fontSize: "1.25rem",
              textDecoration: "none",
              color: "#111",
            }}
          >
            🃏 JESTER
          </Link>
          <nav style={{ display: "flex", gap: "1rem" }}>
            <Link to="/self/astrology" style={{ textDecoration: "none", color: "#1890ff" }}>
              Self
            </Link>
            <Link to="/connections" style={{ textDecoration: "none", color: "#1890ff" }}>
              Connections
            </Link>
            <Link to="/self/profile" style={{ textDecoration: "none", color: "#1890ff" }}>
              Profile
            </Link>
          </nav>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <Link
            to="/notifications"
            style={{
              textDecoration: "none",
              color: "#333",
              position: "relative",
              padding: "0.3rem 0.6rem",
              borderRadius: "4px",
              background: "#f5f5f5",
            }}
          >
            🔔 Notifications
            {unreadCount > 0 && (
              <span
                style={{
                  marginLeft: "0.4rem",
                  backgroundColor: "#ff4d4f",
                  color: "#fff",
                  padding: "0.1rem 0.4rem",
                  borderRadius: "10px",
                  fontSize: "0.75rem",
                  fontWeight: "bold",
                }}
              >
                {unreadCount}
              </span>
            )}
          </Link>
          <button
            onClick={handleSignOut}
            style={{
              padding: "0.4rem 0.8rem",
              cursor: "pointer",
              border: "1px solid #d9d9d9",
              background: "#fff",
              borderRadius: "4px",
            }}
          >
            Sign Out
          </button>
        </div>
      </header>

      {/* Main Viewport */}
      <main
        style={{
          flex: 1,
          maxWidth: "960px",
          width: "100%",
          margin: "0 auto",
          padding: "1.5rem",
          boxSizing: "border-box",
        }}
      >
        <Outlet />
      </main>

      {/* Persistent Debug Bar */}
      <DebugBar />
    </div>
  );
};
