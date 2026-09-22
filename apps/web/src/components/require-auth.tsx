"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";

export function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) {
    return <div className="mx-auto max-w-6xl px-4 py-16 text-sm text-muted-foreground">Vérification de votre session…</div>;
  }
  if (!user) {
    return (
      <main className="mx-auto max-w-xl px-4 py-16 text-center">
        <p className="text-sm text-muted-foreground">Espace créateur Afrosite</p>
        <h1 className="mt-3 font-heading text-3xl font-semibold">Connectez-vous pour ouvrir le Studio</h1>
        <p className="mt-3 text-sm text-muted-foreground">Votre compte protège vos projets, vos prompts et vos previews.</p>
        <Button asChild className="mt-6"><Link href="/auth?next=/studio">Se connecter ou créer un compte</Link></Button>
      </main>
    );
  }
  return children;
}
