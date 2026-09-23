import type { Metadata } from "next";
import Link from "next/link";
import { Card, Money, OrderStatus, PaymentStatus } from "@afrosite/design-system";
import { AppNav } from "@/components/app-nav";
import { HeroMarkClient } from "@/components/HeroMarkClient";
import { MarketingJsonLd } from "@/components/json-ld";
import { MeshBackdrop } from "@/components/MeshBackdrop";
import { PromptLaunch } from "@/components/PromptLaunch";
import { WordmarkStroke } from "@/components/WordmarkStroke";

export const metadata: Metadata = {
  title: "Afrosite — vendez et encaissez, sans une ligne de code",
};

export default function Home() {
  return (
    <>
      <MarketingJsonLd />
      <AppNav />
      <main className="landing">
        <MeshBackdrop />
        <section className="landing__hero" aria-labelledby="landing-title">
          <p className="landing__eyebrow">Cotonou · FCFA · Mobile Money</p>
          <h1 id="landing-title" className="landing__title">
            Le système <span className="landing__accent">vivant</span> des PME africaines
          </h1>
          <p className="landing__lede">
            Décrivez votre activité. En quelques minutes, vendez et encaissez en Mobile Money,
            en FCFA, sans une ligne de code.
          </p>
          <PromptLaunch />
          <div className="landing__actions" aria-label="Parcours de démonstration">
            <Link className="landing__action landing__action--primary" href="/studio">
              Ouvrir le Studio
            </Link>
            <Link className="landing__action landing__action--secondary" href="/t/cadjehoun-wax">
              Voir la boutique démo · 24 500 FCFA
            </Link>
          </div>
        </section>

        <HeroMarkClient />

        <section className="landing__kit" aria-label="Parcours produit">
          <Card>
            <p className="landing__kit-label">1 · Blueprint</p>
            <p className="landing__kit-copy">Prompt → Intent → Architect → Gate 1</p>
            <Link className="landing__kit-link" href="/studio">
              Construire un outil
            </Link>
          </Card>
          <Card>
            <p className="landing__kit-label">2 · Commerce</p>
            <Money amountXof={24500} />
            <div className="landing__kit-row">
              <PaymentStatus status="pending" />
              <PaymentStatus status="confirmed" />
            </div>
            <Link className="landing__kit-link" href="/t/cadjehoun-wax">
              Ouvrir la boutique
            </Link>
          </Card>
          <Card>
            <p className="landing__kit-label">3 · Opérations</p>
            <div className="landing__kit-row">
              <OrderStatus status="received" />
              <OrderStatus status="urgent" />
            </div>
            <Link className="landing__kit-link" href="/dashboard/cadjehoun-wax">
              Voir la caisse
            </Link>
          </Card>
        </section>

        <WordmarkStroke />
      </main>
    </>
  );
}
