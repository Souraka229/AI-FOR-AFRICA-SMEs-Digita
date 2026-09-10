import type { Metadata } from "next";
import Link from "next/link";
import { connection } from "next/server";
import { AppNav } from "@/components/app-nav";
import { Money } from "@/components/money";
import { PaymentStatus } from "@/components/payment-status";
import { Button } from "@/components/ui/button";
import { ALL_EXAMPLES } from "@afrosite/contracts";
import {
  costsForTenant,
  ensureBlueprint,
  ledgerForTenant,
  todayTotals,
  totalsFromRows,
  whatsappForTenant,
} from "@/lib/demo/store";
import { fetchApiLedger } from "@/lib/pay";
import { formatXof } from "@/lib/money";

export const dynamic = "force-dynamic";
export const dynamicParams = true;

export function generateStaticParams() {
  return ALL_EXAMPLES.map((item) => ({ tenant: item.tenant.slug }));
}

export const metadata: Metadata = {
  title: "Caisse du soir — Afrosite",
  robots: { index: false, follow: false },
};

function channelLabel(channel: string) {
  if (channel === "mtn_momo") return "MTN MoMo";
  if (channel === "moov_money") return "Moov Money";
  return "Espèces";
}

export default async function DashboardPage({
  params,
}: {
  params: Promise<{ tenant: string }>;
}) {
  await connection();
  const { tenant } = await params;
  const blueprint = ensureBlueprint(tenant);
  const apiRows = await fetchApiLedger(tenant);
  const rows = apiRows ?? ledgerForTenant(tenant);
  const totals = apiRows ? totalsFromRows(apiRows) : todayTotals(tenant);
  const messages = whatsappForTenant(tenant);
  const costs = costsForTenant(tenant);
  const creditsUsed = costs.reduce((sum, row) => sum + row.credits, 0);
  const name = blueprint.tenant.name;

  const summary = [
    `Résumé ${name} — aujourd'hui`,
    `Encaissé : ${formatXof(totals.total)} (${totals.count} paiement${totals.count > 1 ? "s" : ""} confirmé${totals.count > 1 ? "s" : ""})`,
    `MTN MoMo ${formatXof(totals.byChannel.mtn_momo)} · Moov ${formatXof(totals.byChannel.moov_money)} · Espèces ${formatXof(totals.byChannel.cash)}`,
    totals.unpaid > 0 ? `${totals.unpaid} en attente de verify()` : "Aucun impayé en attente",
  ].join("\n");

  return (
    <>
      <AppNav current="caisse" tenantSlug={tenant} />
      <main className="mx-auto max-w-4xl space-y-8 px-4 py-8">
        <div>
          <p className="text-sm text-muted-foreground">Réconciliation du jour</p>
          <h1 className="font-heading text-3xl font-semibold tracking-tight">{name}</h1>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          {(
            [
              ["MTN MoMo", totals.byChannel.mtn_momo],
              ["Moov Money", totals.byChannel.moov_money],
              ["Espèces", totals.byChannel.cash],
            ] as const
          ).map(([label, amount]) => (
            <div key={label} className="rounded-xl border border-border p-4">
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="font-heading text-2xl font-semibold">
                <Money amountXof={amount} />
              </p>
            </div>
          ))}
        </div>

        <div className="rounded-xl border border-border p-4">
          <p className="text-xs text-muted-foreground">Total confirmé</p>
          <p className="font-heading text-4xl font-semibold">
            <Money amountXof={totals.total} />
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            {totals.unpaid} en attente — la redirection n&apos;apparaît jamais ici.
          </p>
        </div>

        <div className="overflow-x-auto rounded-xl border border-border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50 text-left text-xs text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Référence</th>
                <th className="px-3 py-2 font-medium">Canal</th>
                <th className="px-3 py-2 font-medium">Montant</th>
                <th className="px-3 py-2 font-medium">Statut</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td className="px-3 py-4 text-muted-foreground" colSpan={4}>
                    Aucun encaissement pour l&apos;instant. Passez une commande depuis la boutique.
                  </td>
                </tr>
              ) : (
                rows.map((row) => (
                  <tr key={row.id} className="border-t border-border">
                    <td className="px-3 py-2 font-mono text-xs">{row.reference}</td>
                    <td className="px-3 py-2">{channelLabel(row.channel)}</td>
                    <td className="px-3 py-2">
                      <Money amountXof={row.amountXof} />
                    </td>
                    <td className="px-3 py-2">
                      <PaymentStatus
                        status={row.status}
                        refundedAmountXof={row.refundedAmountXof}
                      />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="rounded-xl border border-border p-4">
          <p className="mb-2 text-sm font-medium">Résumé WhatsApp du soir</p>
          <pre className="whitespace-pre-wrap rounded-lg bg-muted p-3 text-sm">{summary}</pre>
          {messages.length > 0 ? (
            <ul className="mt-3 space-y-2 text-sm">
              {messages.slice(0, 6).map((row) => (
                <li key={row.id} className="rounded-lg bg-muted/60 px-3 py-2">
                  <p className="text-xs text-muted-foreground">
                    {row.to === "customer" ? "Client" : "Commerçante"} · simulé
                  </p>
                  <p>{row.body}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-xs text-muted-foreground">
              Les reçus WhatsApp apparaissent ici après un verify() serveur.
            </p>
          )}
        </div>

        <div className="rounded-xl border border-border p-4">
          <p className="text-xs text-muted-foreground">Coût IA estimé (crédits démo)</p>
          <p className="font-heading text-2xl font-semibold tabular-nums">{creditsUsed}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Intent 1 + Architect {blueprint.estimated_cost_credits} + Gate 1 gratuit. Plafond{" "}
            {blueprint.gates.budget_credits_max}.
          </p>
        </div>

        <Button asChild variant="outline">
          <Link href={`/t/${tenant}`}>Retour à la boutique</Link>
        </Button>
      </main>
    </>
  );
}
