import React, { createContext, useEffect, useRef, useState } from "react";
import { Session, User } from "@supabase/supabase-js";
import { useQueryClient } from "@tanstack/react-query";
import { supabase } from "../realtime/supabase";
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
  onboardingCompleted: boolean;
  onboardingStep: number;
  hasBirthData: boolean | null;
  setHasBirthData: (val: boolean) => void;
  refreshProfile: () => Promise<ProfileResponse | null>;
  signOut: () => Promise<void>;
  signUp: (params: SignUpParams) => Promise<ProfileResponse>;
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

  const isRegisteringRef = useRef<boolean>(false);

  const fetchProfile = async (): Promise<ProfileResponse | null> => {
    try {
      const p = await API.profiles.getMyProfile();
      setProfile(p);
      return p;
    } catch {
      // If profile has not yet been provisioned for this authenticated user, initialize it explicitly
      try {
        const initialized = await API.profiles.initializeProfile();
        setProfile(initialized);
        return initialized;
      } catch {
        setProfile(null);
        return null;
      }
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
      if (isRegisteringRef.current) {
        // Skip automatic background profile fetch during registration;
        // signUp explicitly initializes the profile first.
        return;
      }
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

  const signUp = async ({
    email,
    password,
    firstName,
    lastName,
  }: SignUpParams): Promise<ProfileResponse> => {
    isRegisteringRef.current = true;
    try {
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
        options: Object.keys(metadata).length > 0 ? { data: metadata } : undefined,
      });

      if (authErr) {
        throw authErr;
      }

      if (authData.user && authData.user.identities && authData.user.identities.length === 0) {
        throw new Error("already registered");
      }

      let activeSession = authData.session;
      if (!activeSession) {
        const { data: signInData, error: signInErr } = await supabase.auth.signInWithPassword({
          email: cleanEmail,
          password,
        });
        if (signInErr) throw signInErr;
        activeSession = signInData.session;
      }

      if (!activeSession) {
        throw new Error("Failed to acquire session after registration");
      }

      // Explicitly initialize profile via POST /v1/profiles/initialize
      // BEFORE any GET /v1/profiles/me can be triggered!
      const initPayload = fn && ln ? { first_name: fn, last_name: ln } : undefined;
      const initProfile = await API.profiles.initializeProfile(initPayload);

      setSession(activeSession);
      setUser(activeSession.user);
      setProfile(initProfile);
      setHasBirthData(false);
      setIsLoading(false);

      return initProfile;
    } finally {
      isRegisteringRef.current = false;
    }
  };

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
        signUp,
        refreshBirthDataCheck,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
