"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { supabaseBrowser } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";

export default function AuthPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const client = supabaseBrowser();
      const result = mode === "login"
        ? await client.auth.signInWithPassword({ email, password })
        : await client.auth.signUp({ email, password, options: { emailRedirectTo: `${window.location.origin}/auth` } });
      if (result.error) throw result.error;
      if (mode === "signup" && !result.data.session) {
        setMessage("Compte créé. Vérifiez votre boîte mail avant de vous connecter.");
      } else {
        router.push("/studio");
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Authentification impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-xl items-center px-4 py-16">
      <section className="w-full rounded-2xl border border-border bg-card p-6 text-card-foreground shadow-sm sm:p-8">
        <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">← Retour à Afrosite</Link>
        <p className="mt-8 text-sm text-muted-foreground">Espace créateur</p>
        <h1 className="mt-2 font-heading text-3xl font-semibold">{mode === "login" ? "Bon retour." : "Créez votre compte."}</h1>
        <p className="mt-2 text-sm text-muted-foreground">Accédez au Studio IA, à vos previews et à vos futurs établissements.</p>
        <form className="mt-6 space-y-4" onSubmit={submit}>
          <label className="block space-y-2 text-sm font-medium">Email<input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-1 w-full rounded-lg border border-input bg-background px-3 py-2 font-normal outline-none focus-visible:ring-2 focus-visible:ring-ring" /></label>
          <label className="block space-y-2 text-sm font-medium">Mot de passe<input required minLength={8} type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="mt-1 w-full rounded-lg border border-input bg-background px-3 py-2 font-normal outline-none focus-visible:ring-2 focus-visible:ring-ring" /></label>
          <Button type="submit" className="w-full" disabled={busy}>{busy ? "Patientez…" : mode === "login" ? "Se connecter" : "Créer mon compte"}</Button>
        </form>
        {message ? <p className="mt-4 text-sm text-emerald-600">{message}</p> : null}
        {error ? <p className="mt-4 text-sm text-destructive">{error}</p> : null}
        <button type="button" className="mt-6 text-sm text-muted-foreground underline underline-offset-4" onClick={() => setMode(mode === "login" ? "signup" : "login")}>
          {mode === "login" ? "Créer un nouveau compte" : "J’ai déjà un compte"}
        </button>
      </section>
    </main>
  );
}
