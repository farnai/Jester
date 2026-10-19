import React, { useEffect, useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../core/auth/useAuth";
import { API } from "../core/api/endpoints";
import { supabase } from "../core/realtime/supabase";
import { DebugBar } from "./DebugBar";
import { SocialSync } from '../core/realtime/SocialSync';
import { HomeNavigation, HomeMobileNavigation } from "../modules/home/HomeNavigation";

export const AppShell: React.FC = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState<number>(0);

  const profile = useQuery({
    queryKey: ['profile', 'me'],
    queryFn: API.profiles.getMyProfile,
    enabled: !!user,
    staleTime: 60_000,
  });

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
    <div className="app-container home-shell">
      <SocialSync />
      {/* Global Desktop Header */}
      <HomeNavigation
        unreadCount={unreadCount}
        signOut={handleSignOut}
        profileName={profile.data?.display_name}
        avatarUrl={profile.data?.avatar_url}
        userEmail={user?.email}
      />

      {/* Main Responsive Viewport */}
      <main className="app-main-viewport home-main-viewport">
        <Outlet />
      </main>

      {/* Mobile Bottom Navigation Bar */}
      <HomeMobileNavigation />

      {/* Development-Only Debug Bar */}
      <DebugBar />
    </div>
  );
};
