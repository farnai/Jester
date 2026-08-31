import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../core/auth/useAuth";
import { LoadingState } from "../shared/StatusState";

export const ProtectedRoute: React.FC<{
  children: React.ReactElement;
  requireBirthData?: boolean;
}> = ({ children, requireBirthData = true }) => {
  const { user, isLoading, hasBirthData } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingState message="Restoring session..." />;
  }

  if (!user) {
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }

  // If user has not completed birth data onboarding and is not already on onboarding page
  if (
    requireBirthData &&
    hasBirthData === false &&
    location.pathname !== "/onboarding/birth-data"
  ) {
    return <Navigate to="/onboarding/birth-data" replace />;
  }

  return children;
};
