import React, { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
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
    <div className="app-container">
      {/* Global Desktop & Mobile Top Header */}
      <header className="desktop-nav-header">
        <div style={{ display: "flex", alignItems: "center", gap: "2rem" }}>
          <Link
            to="/"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              fontWeight: 800,
              fontSize: "1.25rem",
              textDecoration: "none",
              color: "#0f172a",
              letterSpacing: "0.02em",
            }}
          >
            <span style={{ fontSize: "1.4rem" }}>🃏</span>
            <span>JESTER</span>
          </Link>

          {/* Desktop Primary Navigation (HOME | DISCOVER | MESSAGES | ME) */}
          <nav className="desktop-nav-links">
            <NavLink
              to="/"
              end
              className={({ isActive }) => `nav-item-link ${isActive ? "active" : ""}`}
            >
              <span>🏠</span>
              <span>HOME</span>
            </NavLink>
            <NavLink
              to="/discover"
              className={({ isActive }) => `nav-item-link ${isActive ? "active" : ""}`}
            >
              <span>🧭</span>
              <span>DISCOVER</span>
            </NavLink>
            <NavLink
              to="/messages"
              className={({ isActive }) => `nav-item-link ${isActive ? "active" : ""}`}
            >
              <span>💬</span>
              <span>MESSAGES</span>
            </NavLink>
            <NavLink
              to="/me"
              className={({ isActive }) => `nav-item-link ${isActive ? "active" : ""}`}
            >
              <span>👤</span>
              <span>ME</span>
            </NavLink>
          </nav>
        </div>

        {/* Right Header Area: Notifications, Dev Tools, Account */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {/* Notifications Indicator (Not a primary pillar, accessible utility) */}
          <Link
            to="/notifications"
            style={{
              textDecoration: "none",
              color: "#334155",
              position: "relative",
              padding: "0.4rem 0.65rem",
              borderRadius: "8px",
              backgroundColor: "#f1f5f9",
              border: "1px solid #e2e8f0",
              fontSize: "0.9rem",
              display: "flex",
              alignItems: "center",
            }}
            title="შეტყობინებები / Notifications"
          >
            🔔
            {unreadCount > 0 && (
              <span
                style={{
                  marginLeft: "0.35rem",
                  backgroundColor: "#ef4444",
                  color: "#ffffff",
                  padding: "0.1rem 0.4rem",
                  borderRadius: "9999px",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  lineHeight: 1,
                }}
              >
                {unreadCount}
              </span>
            )}
          </Link>

          {/* User Email Badge */}
          {user?.email && (
            <span
              style={{
                fontSize: "0.8rem",
                color: "#475569",
                backgroundColor: "#f8fafc",
                padding: "0.35rem 0.65rem",
                borderRadius: "9999px",
                border: "1px solid #e2e8f0",
                maxWidth: "180px",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                display: "none", // Hidden on small screens, visible via CSS media query
              }}
              className="user-badge"
              title={user.email}
            >
              {user.email}
            </span>
          )}

          {/* Developer Smoke Test Link */}
          <Link
            to="/smoke-test"
            style={{
              fontSize: "0.775rem",
              color: "#6366f1",
              backgroundColor: "#eef2ff",
              padding: "0.35rem 0.6rem",
              borderRadius: "6px",
              textDecoration: "none",
              border: "1px solid #c7d2fe",
              fontWeight: 600,
            }}
            title="ქართული კონტენტის აუდიტი (Developer Surface)"
          >
            🧪 Smoke
          </Link>

          {/* Universal Design System Visual Lab */}
          <Link
            to="/visual-lab"
            style={{
              fontSize: "0.775rem",
              color: "#9333ea",
              backgroundColor: "#fdf4ff",
              padding: "0.35rem 0.6rem",
              borderRadius: "6px",
              textDecoration: "none",
              border: "1px solid #f0abfc",
              fontWeight: 600,
            }}
            title="უნივერსალური დიზაინ სისტემის ლაბორატორია (Visual Lab)"
          >
            🎨 Lab
          </Link>

          {/* Forensic Backend -> Registered User Data Integrity Audit */}
          <Link
            to="/__debug/backend-audit"
            style={{
              fontSize: "0.775rem",
              color: "#0284c7",
              backgroundColor: "#f0f9ff",
              padding: "0.35rem 0.6rem",
              borderRadius: "6px",
              textDecoration: "none",
              border: "1px solid #bae6fd",
              fontWeight: 600,
            }}
            title="მონაცემთა მთლიანობის აუდიტი (Backend Data Integrity Audit)"
          >
            🔬 Audit
          </Link>

          {/* Sign Out Button */}
          <button
            onClick={handleSignOut}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.3rem",
              padding: "0.4rem 0.75rem",
              cursor: "pointer",
              border: "1px solid #ffa39e",
              backgroundColor: "#fff1f0",
              color: "#cf1322",
              borderRadius: "6px",
              fontWeight: 600,
              fontSize: "0.825rem",
              minHeight: "36px",
            }}
            title="სისტემიდან გასვლა / Sign Out"
          >
            🚪 <span className="signout-label">გასვლა</span>
          </button>
        </div>
      </header>

      {/* Main Responsive Viewport */}
      <main className="app-main-viewport">
        <Outlet />
      </main>

      {/* Mobile Bottom Navigation Bar (HOME | DISCOVER | MESSAGES | ME) */}
      <nav className="mobile-bottom-nav">
        <NavLink
          to="/"
          end
          className={({ isActive }) => `mobile-nav-tab ${isActive ? "active" : ""}`}
        >
          <span className="tab-icon">🏠</span>
          <span>HOME</span>
        </NavLink>
        <NavLink
          to="/discover"
          className={({ isActive }) => `mobile-nav-tab ${isActive ? "active" : ""}`}
        >
          <span className="tab-icon">🧭</span>
          <span>DISCOVER</span>
        </NavLink>
        <NavLink
          to="/messages"
          className={({ isActive }) => `mobile-nav-tab ${isActive ? "active" : ""}`}
        >
          <span className="tab-icon">💬</span>
          <span>MESSAGES</span>
        </NavLink>
        <NavLink
          to="/me"
          className={({ isActive }) => `mobile-nav-tab ${isActive ? "active" : ""}`}
        >
          <span className="tab-icon">👤</span>
          <span>ME</span>
        </NavLink>
      </nav>

      {/* Persistent Developer Debug Bar (Development Only) */}
      <DebugBar />
    </div>
  );
};
