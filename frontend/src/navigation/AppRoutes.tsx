import React, { useEffect } from "react";
import { Routes, Route, Navigate, useNavigate, useParams } from "react-router-dom";
import { LoginPage } from "../modules/auth/LoginPage";
import { RegisterPage } from "../modules/auth/RegisterPage";
import { BirthDataOnboardingPage } from "../modules/onboarding/BirthDataOnboardingPage";
import { HomePage } from "../modules/home/HomePage";
import { DiscoverPage } from "../modules/discover/DiscoverPage";
import { PersonProfilePage } from "../modules/people/PersonProfilePage";
import { WhyPage } from "../modules/compatibility/WhyPage";
import { ComparePage } from "../modules/compatibility/ComparePage";
import { ConnectionsPage } from "../modules/connections/ConnectionsPage";
import { MessagesPage } from "../modules/messages/MessagesPage";
import { ChatPage } from "../modules/chat/ChatPage";
import { MePage } from "../modules/me/MePage";
import { NotificationsPage } from "../modules/notifications/NotificationsPage";
import { ContentSmokeTestPage } from "../modules/smoke_test/ContentSmokeTestPage";
import { VisualLab } from "../ui/VisualLab";
import { BackendAuditDebugPage } from "../ui/BackendAuditDebugPage";
import { ProtectedRoute } from "./ProtectedRoute";
import { AppShell } from "../shared/AppShell";
import { useAuth } from "../core/auth/useAuth";
import { LoadingState } from "../shared/StatusState";

export const LogoutHandler: React.FC = () => {
  const { signOut } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    signOut().finally(() => {
      navigate("/auth/login", { replace: true });
    });
  }, [signOut, navigate]);

  return <LoadingState message="გამოსვლა / Logging out..." />;
};

// Redirect helper for legacy /why/:target_id to /people/:id/why
const LegacyWhyRedirect: React.FC = () => {
  const { target_id } = useParams<{ target_id: string }>();
  return <Navigate to={`/people/${target_id}/why`} replace />;
};

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Universal Design System Visual Foundation Lab */}
      <Route path="/visual-lab" element={<VisualLab />} />
      <Route path="/__lab" element={<VisualLab />} />

      {/* Forensic Backend -> Registered User -> Frontend Data Integrity Audit Lab */}
      <Route path="/__debug/backend-audit" element={<BackendAuditDebugPage />} />
      <Route path="/__lab/backend-audit" element={<BackendAuditDebugPage />} />
      <Route path="/debug/backend-audit" element={<BackendAuditDebugPage />} />

      {/* Primary UX & Content Smoke Test Route (Developer Audit Surface) */}
      <Route path="/smoke-test" element={<ContentSmokeTestPage />} />
      <Route path="/ux-test" element={<ContentSmokeTestPage />} />

      {/* Public Auth Routes */}
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />
      <Route path="/logout" element={<LogoutHandler />} />
      <Route path="/auth/logout" element={<LogoutHandler />} />

      {/* Onboarding Route */}
      <Route
        path="/onboarding/birth-data"
        element={
          <ProtectedRoute requireBirthData={false}>
            <BirthDataOnboardingPage />
          </ProtectedRoute>
        }
      />

      {/* Authenticated Application Shell (V1 Route Structure) */}
      <Route
        path="/"
        element={
          <ProtectedRoute requireBirthData={true}>
            <AppShell />
          </ProtectedRoute>
        }
      >
        {/* 1. HOME */}
        <Route index element={<HomePage />} />

        {/* 2. DISCOVER */}
        <Route path="discover" element={<DiscoverPage />} />

        {/* 3. PERSON & WHY */}
        <Route path="people/:id" element={<PersonProfilePage />} />
        <Route path="people/:id/why" element={<WhyPage />} />

        {/* 4. US / COMPARISON */}
        <Route path="compare/:id" element={<ComparePage />} />
        <Route path="compare/:target_id" element={<ComparePage />} />

        {/* 5. CONNECTIONS */}
        <Route path="connections" element={<ConnectionsPage />} />

        {/* 6. MESSAGES & CHAT */}
        <Route path="messages" element={<MessagesPage />} />
        <Route path="chat/:conversation_id" element={<ChatPage />} />

        {/* 7. ME */}
        <Route path="me" element={<MePage />} />

        {/* 8. NOTIFICATIONS */}
        <Route path="notifications" element={<NotificationsPage />} />

        {/* Compatibility Redirects for Previous Scaffold URLs */}
        <Route path="people" element={<Navigate to="/discover" replace />} />
        <Route path="why/:target_id" element={<LegacyWhyRedirect />} />
        <Route path="self/astrology" element={<Navigate to="/me" replace />} />
        <Route path="self/profile" element={<Navigate to="/me" replace />} />
        <Route path="self" element={<Navigate to="/me" replace />} />
      </Route>

      {/* Route Aliases */}
      <Route path="/app/*" element={<Navigate to="/" replace />} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
