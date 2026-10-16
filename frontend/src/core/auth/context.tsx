import React, { createContext, useCallback, useEffect, useRef, useState } from "react";
import { Session, User } from "@supabase/supabase-js";
import { useQueryClient } from "@tanstack/react-query";
import { supabase } from "../realtime/supabase";
import { ApiClientError } from "../api/client";
import { API } from "../api/endpoints";
import { ProfileResponse } from "../api/types";

export interface SignUpParams {
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
}

export interface AuthContextType {
  user: User | null;
  session: Session | null;
  profile: ProfileResponse | null;
  isLoading: boolean;
  profileError: string | null;
  onboardingCompleted: boolean;
  onboardingStep: number;
  hasBirthData: boolean | null;
  setHasBirthData: (val: boolean) => void;
  refreshProfile: () => Promise<ProfileResponse | null>;
  signOut: () => Promise<void>;
  signUp: (params: SignUpParams) => Promise<{ confirmationRequired: boolean }>;
  refreshBirthDataCheck: (explicitUserId?: string) => Promise<boolean>;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  profile: null,
  isLoading: true,
  profileError: null,
  onboardingCompleted: false,
  onboardingStep: 1,
  hasBirthData: null,
  setHasBirthData: () => {},
  refreshProfile: async () => null,
  signOut: async () => {},
  signUp: async () => {
    throw new Error("AuthProvider not mounted");
  },
  refreshBirthDataCheck: async () => false,
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = useQueryClient();
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [hasBirthData, setHasBirthData] = useState<boolean | null>(null);

  const [profileError, setProfileError] = useState<string | null>(null);
  const activeUserId = useRef<string | null>(null);

  const fetchProfile = useCallback(async (): Promise<ProfileResponse | null> => {
    const id = activeUserId.current;
    if (!id) return null;
    try {
      const p = await API.profiles.getMyProfile().catch((error) => {
        if (error instanceof ApiClientError && error.statusCode === 404) {
          return API.profiles.initializeProfile();
        }
        throw error;
      });
      if (activeUserId.current !== id) return null;
      setProfile(p);
      setProfileError(null);
      return p;
    } catch {
      if (activeUserId.current === id) {
        setProfileError("პროფილის ჩატვირთვა ვერ მოხერხდა. სცადეთ ხელახლა.");
      }
      return null;
    }
  }, []);

  const checkBirthData = useCallback(async (id: string) => {
    const exists = await API.astrology.checkHasBirthData(id);
    if (activeUserId.current === id) setHasBirthData(exists);
    return exists;
  }, []);

  useEffect(() => {
    // Auth callbacks must return synchronously: API calls also acquire the
    // Supabase session lock. Hydrate the profile in a separate React effect.
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, next) => {
      const nextId = next?.user.id ?? null;
      if (nextId !== activeUserId.current) {
        activeUserId.current = nextId;
        setProfile(null);
        setProfileError(null);
        setHasBirthData(null);
        queryClient.clear();
        setIsLoading(!!nextId);
      }
      setSession(next);
      setUser(next?.user ?? null);
      if (!nextId) setIsLoading(false);
    });
    return () => subscription.unsubscribe();
  }, [queryClient]);

  const userId = user?.id;
  useEffect(() => {
    if (!userId) return;
    let cancelled = false;
    Promise.allSettled([fetchProfile(), checkBirthData(userId)]).finally(() => {
      if (!cancelled) setIsLoading(false);
    });
    return () => { cancelled = true; };
  }, [userId, fetchProfile, checkBirthData]);

  const signUp = async ({
    email,
    password,
    firstName,
    lastName,
  }: SignUpParams): Promise<{ confirmationRequired: boolean }> => {
    const cleanEmail = email.trim();
    const fn = firstName?.trim();
    const ln = lastName?.trim();
    const metadata: Record<string, any> = {};
    if (fn && ln) {
      metadata.first_name = fn;
      metadata.last_name = ln;
      metadata.display_name = `${fn} ${ln[0].toUpperCase()}.`;
    }

    const { data: authData, error: authErr } = await supabase.auth.signUp({
      email: cleanEmail,
      password,
      options: { data: metadata, emailRedirectTo: `${window.location.origin}/auth/callback` },
    });

    if (authErr) {
      throw authErr;
    }

    if (authData.user && authData.user.identities && authData.user.identities.length === 0) {
      throw new Error("already registered");
    }

    // If no session returned directly, attempt password sign-in for seamless local/unconfirmed progression
    if (!authData.session) {
      try {
        const { data: signInData, error: signInErr } = await supabase.auth.signInWithPassword({
          email: cleanEmail,
          password,
        });
        if (!signInErr && signInData.session) {
          return { confirmationRequired: false };
        }
      } catch {
        // Fallback to email confirmation required
      }
    }

    return { confirmationRequired: !authData.session };
  };

  const refreshProfile = fetchProfile;

  const refreshBirthDataCheck = async (explicitUserId?: string) => {
    const targetId = explicitUserId || user?.id;
    if (!targetId) return false;
    return checkBirthData(targetId);
  };

  const signOut = useCallback(async () => {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    activeUserId.current = null;
    queryClient.clear();
    setSession(null);
    setUser(null);
    setProfile(null);
    setHasBirthData(null);
  }, [queryClient]);

  const onboardingCompleted = !!profile?.onboarding_completed;
  const onboardingStep = profile?.onboarding_step ?? 1;

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        profile,
        isLoading,
        profileError,
        onboardingCompleted,
        onboardingStep,
        hasBirthData,
        setHasBirthData,
        refreshProfile,
        signOut,
        signUp,
        refreshBirthDataCheck,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
