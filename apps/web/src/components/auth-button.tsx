"use client";

import Link from "next/link";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";

export function AuthButton() {
  const { user, loading, signOut } = useAuth();
  if (loading) return <span className="text-xs text-muted-foreground">Chargement…</span>;
  if (!user) {
    return (
      <Button asChild size="sm" variant="outline">
        <Link href="/auth">Se connecter</Link>
      </Button>
    );
  }
  return (
    <div className="flex items-center gap-2">
      <span className="hidden max-w-32 truncate text-xs text-muted-foreground sm:inline">
        {user.email}
      </span>
      <Button type="button" size="sm" variant="outline" onClick={() => void signOut()}>
        Déconnexion
      </Button>
    </div>
  );
}
