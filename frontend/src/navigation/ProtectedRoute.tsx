import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../core/auth/useAuth";
import { LoadingState } from "../shared/StatusState";

export const ProtectedRoute: React.FC<{
  children: React.ReactElement;
  requireOnboardingComplete?: boolean;
  requireBirthData?: boolean;
}> = ({ children, requireOnboardingComplete, requireBirthData }) => {
  const { user, isLoading, onboardingCompleted } = useAuth();
  const location = useLocation();
  const mustBeComplete = requireOnboardingComplete ?? requireBirthData ?? true;

  if (isLoading) {
    return <LoadingState message="სესიის აღდგენა / Restoring session..." />;
  }

  if (!user) {
    // If visitor lands on root without auth, direct to public Welcome
    if (location.pathname === "/") {
      return <Navigate to="/welcome" replace />;
    }
    // Deep links retain 'from' redirect to Login
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }

  // If user has not completed onboarding and tries to access authenticated main app
  if (mustBeComplete && !onboardingCompleted) {
    if (!location.pathname.startsWith("/onboarding")) {
      return <Navigate to="/onboarding" replace />;
    }
  }

  // If user has already completed onboarding and tries to access onboarding routes
  if (!mustBeComplete && onboardingCompleted && location.pathname.startsWith("/onboarding")) {
    return <Navigate to="/me" replace />;
  }

  return children;
};
