import type { Metadata } from "next";
import Link from "next/link";
import { AppNav } from "@/components/app-nav";
import { MarketingJsonLd } from "@/components/json-ld";

export const metadata: Metadata = {
  title: "Afrosite — vendez et encaissez, sans une ligne de code",
};

export default function Home() {
  return (
    <>
      <MarketingJsonLd />
      <AppNav />
      <main className="mx-auto max-w-3xl px-4 py-16">
        <p className="text-sm text-muted-foreground">Cotonou · FCFA · Mobile Money</p>
        <h1 className="mt-3 font-heading text-4xl font-semibold tracking-tight md:text-5xl">
          Décrivez l&apos;activité. Encaissez le soir.
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Une phrase en français produit un Blueprint JSON, une boutique, le
          paiement MTN MoMo / Moov et la caisse. Afrosite n&apos;est jamais
          dépositaire des fonds.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/studio"
            className="inline-flex min-h-11 items-center rounded-lg bg-primary px-5 text-sm font-semibold text-primary-foreground"
          >
            Ouvrir le studio
          </Link>
          <Link
            href="/t/cadjehoun-wax"
            className="inline-flex min-h-11 items-center rounded-lg border border-border px-5 text-sm"
          >
            Boutique démo · 24 500 FCFA
          </Link>
        </div>
        <ol className="mt-14 space-y-3 text-sm">
          <li>
            <span className="font-medium">1. Studio</span> — prompt → Intent →
            Architect → Gate 1
          </li>
          <li>
            <span className="font-medium">2. Boutique</span> —{" "}
            <Link href="/t/cadjehoun-wax" className="underline">
              /t/cadjehoun-wax
            </Link>
          </li>
          <li>
            <span className="font-medium">3. Caisse</span> —{" "}
            <Link href="/dashboard/cadjehoun-wax" className="underline">
              réconciliation du soir
            </Link>
          </li>
        </ol>
      </main>
    </>
  );
}
