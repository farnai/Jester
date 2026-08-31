import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { LoginPage } from "../modules/auth/LoginPage";
import { RegisterPage } from "../modules/auth/RegisterPage";
import { BirthDataOnboardingPage } from "../modules/onboarding/BirthDataOnboardingPage";
import { SelfAstrologyPage } from "../modules/self/SelfAstrologyPage";
import { SelfProfilePage } from "../modules/self/SelfProfilePage";
import { PersonProfilePage } from "../modules/people/PersonProfilePage";
import { ConnectionsPage } from "../modules/connections/ConnectionsPage";
import { ComparePage } from "../modules/compatibility/ComparePage";
import { WhyPage } from "../modules/compatibility/WhyPage";
import { ChatPage } from "../modules/chat/ChatPage";
import { NotificationsPage } from "../modules/notifications/NotificationsPage";
import { ProtectedRoute } from "./ProtectedRoute";
import { AppShell } from "../shared/AppShell";

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />

      {/* Onboarding Route */}
      <Route
        path="/onboarding/birth-data"
        element={
          <ProtectedRoute requireBirthData={false}>
            <BirthDataOnboardingPage />
          </ProtectedRoute>
        }
      />

      {/* Authenticated Application Shell */}
      <Route
        path="/"
        element={
          <ProtectedRoute requireBirthData={true}>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/self/astrology" replace />} />
        <Route path="self/astrology" element={<SelfAstrologyPage />} />
        <Route path="self/profile" element={<SelfProfilePage />} />
        <Route path="people" element={<PersonProfilePage />} />
        <Route path="people/:id" element={<PersonProfilePage />} />
        <Route path="connections" element={<ConnectionsPage />} />
        <Route path="compare/:target_id" element={<ComparePage />} />
        <Route path="why/:target_id" element={<WhyPage />} />
        <Route path="chat/:conversation_id" element={<ChatPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
