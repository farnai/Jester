import React, { createContext, useEffect, useState } from "react";
import { Session, User } from "@supabase/supabase-js";
import { supabase } from "../realtime/supabase";
import { API } from "../api/endpoints";

export interface AuthContextType {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
  hasBirthData: boolean | null;
  setHasBirthData: (val: boolean) => void;
  signOut: () => Promise<void>;
  refreshBirthDataCheck: () => Promise<boolean>;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  isLoading: true,
  hasBirthData: null,
  setHasBirthData: () => {},
  signOut: async () => {},
  refreshBirthDataCheck: async () => false,
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [hasBirthData, setHasBirthData] = useState<boolean | null>(null);

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

  useEffect(() => {
    // Initial session load
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      if (session?.user) {
        checkBirthData(session.user.id).finally(() => setIsLoading(false));
      } else {
        setIsLoading(false);
      }
    });

    // Listen for auth state changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      if (session?.user) {
        await checkBirthData(session.user.id);
      } else {
        setHasBirthData(null);
      }
      setIsLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const refreshBirthDataCheck = async () => {
    if (!user) return false;
    return checkBirthData(user.id);
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    setSession(null);
    setUser(null);
    setHasBirthData(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        isLoading,
        hasBirthData,
        setHasBirthData,
        signOut,
        refreshBirthDataCheck,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
