import type { Metadata } from "next";
import Link from "next/link";
import { connection } from "next/server";
import { AppNav } from "@/components/app-nav";
import { Button } from "@/components/ui/button";
import { listBlueprints } from "@/lib/demo/store";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Établissements — Afrosite",
  robots: { index: false, follow: false },
};

export default async function DashboardIndex() {
  await connection();
  const tenants = listBlueprints();

  return (
    <>
      <AppNav current="caisse" />
      <main className="mx-auto max-w-4xl space-y-6 px-4 py-8">
        <div>
          <p className="text-sm text-muted-foreground">Registre</p>
          <h1 className="font-heading text-3xl font-semibold tracking-tight">
            Établissements
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Un tenant se crée au studio (Gate 1) ou à la première visite de{" "}
            <span className="font-mono">/t/…</span>.
          </p>
        </div>

        <ul className="space-y-2">
          {tenants.map((item) => (
            <li
              key={item.tenant.slug}
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border px-4 py-3"
            >
              <div>
                <p className="font-heading font-semibold">{item.tenant.name}</p>
                <p className="font-mono text-xs text-muted-foreground">
                  {item.tenant.slug} · {item.tenant.neighborhood}
                </p>
              </div>
              <div className="flex gap-2">
                <Button asChild variant="outline" size="sm">
                  <Link href={`/t/${item.tenant.slug}`}>Boutique</Link>
                </Button>
                <Button asChild size="sm">
                  <Link href={`/dashboard/${item.tenant.slug}`}>Caisse</Link>
                </Button>
              </div>
            </li>
          ))}
        </ul>

        <Button asChild variant="outline">
          <Link href="/studio">Créer depuis le studio</Link>
        </Button>
      </main>
    </>
  );
}
