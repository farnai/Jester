import React, { createContext, useEffect, useState } from "react";
import { Session, User } from "@supabase/supabase-js";
import { useQueryClient } from "@tanstack/react-query";
import { supabase } from "../realtime/supabase";
import { API } from "../api/endpoints";
import { ProfileResponse } from "../api/types";

export interface AuthContextType {
  user: User | null;
  session: Session | null;
  profile: ProfileResponse | null;
  isLoading: boolean;
  onboardingCompleted: boolean;
  onboardingStep: number;
  hasBirthData: boolean | null;
  setHasBirthData: (val: boolean) => void;
  refreshProfile: () => Promise<ProfileResponse | null>;
  signOut: () => Promise<void>;
  refreshBirthDataCheck: (explicitUserId?: string) => Promise<boolean>;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  profile: null,
  isLoading: true,
  onboardingCompleted: false,
  onboardingStep: 1,
  hasBirthData: null,
  setHasBirthData: () => {},
  refreshProfile: async () => null,
  signOut: async () => {},
  refreshBirthDataCheck: async () => false,
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = useQueryClient();
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [hasBirthData, setHasBirthData] = useState<boolean | null>(null);

  const fetchProfile = async (): Promise<ProfileResponse | null> => {
    try {
      const p = await API.profiles.getMyProfile();
      setProfile(p);
      return p;
    } catch {
      setProfile(null);
      return null;
    }
  };

  const checkBirthData = async (uId: string) => {
    try {
      const exists = await API.astrology.checkHasBirthData(uId);
      setHasBirthData(exists);
      return exists;
    } catch {
      setHasBirthData(false);
      return false;
    }
  };

  const loadUserData = async (uId: string) => {
    await Promise.allSettled([
      fetchProfile(),
      checkBirthData(uId),
    ]);
  };

  useEffect(() => {
    // Initial session load
    supabase.auth.getSession().then(({ data, error }) => {
      if (error) {
        setSession(null);
        setUser(null);
        setProfile(null);
        setIsLoading(false);
        return;
      }
      const activeSession = data?.session ?? null;
      setSession(activeSession);
      setUser(activeSession?.user ?? null);
      if (activeSession?.user) {
        loadUserData(activeSession.user.id).finally(() => setIsLoading(false));
      } else {
        setIsLoading(false);
      }
    }).catch(() => {
      setSession(null);
      setUser(null);
      setProfile(null);
      setIsLoading(false);
    });

    // Listen for auth state changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, activeSession) => {
      setSession(activeSession);
      setUser(activeSession?.user ?? null);
      if (activeSession?.user) {
        await loadUserData(activeSession.user.id);
      } else {
        setProfile(null);
        setHasBirthData(null);
        queryClient.clear();
      }
      setIsLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [queryClient]);

  const refreshProfile = async (): Promise<ProfileResponse | null> => {
    return fetchProfile();
  };

  const refreshBirthDataCheck = async (explicitUserId?: string) => {
    const targetId = explicitUserId || user?.id;
    if (!targetId) return false;
    return checkBirthData(targetId);
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    queryClient.clear();
    setSession(null);
    setUser(null);
    setProfile(null);
    setHasBirthData(null);
  };

  const onboardingCompleted = !!profile?.onboarding_completed;
  const onboardingStep = profile?.onboarding_step ?? 1;

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        profile,
        isLoading,
        onboardingCompleted,
        onboardingStep,
        hasBirthData,
        setHasBirthData,
        refreshProfile,
        signOut,
        refreshBirthDataCheck,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
