"use client";

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import type { AuthChangeEvent, Session, User } from "@supabase/supabase-js";
import { supabaseBrowser } from "@/lib/supabase/client";

type AuthContextValue = {
  session: Session | null;
  user: User | null;
  loading: boolean;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(
    () => Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY),
  );

  useEffect(() => {
    let active = true;
    let subscription: { unsubscribe: () => void } | undefined;
    try {
      const client = supabaseBrowser();
      client.auth.getSession().then(({ data }: { data: { session: Session | null } }) => {
        if (active) setSession(data.session);
        if (active) setLoading(false);
      });
      const result = client.auth.onAuthStateChange((_event: AuthChangeEvent, nextSession: Session | null) => {
        if (active) setSession(nextSession);
      });
      subscription = result.data.subscription;
    } catch {
      // Les variables absentes sont gérées par l’état initial ; ne pas boucler dans l’effet.
    }
    return () => {
      active = false;
      subscription?.unsubscribe();
    };
  }, []);

  const value = useMemo(
    () => ({
      session,
      user: session?.user ?? null,
      loading,
      signOut: async () => {
        await supabaseBrowser().auth.signOut();
      },
    }),
    [loading, session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth doit être utilisé dans AuthProvider.");
  return context;
}
