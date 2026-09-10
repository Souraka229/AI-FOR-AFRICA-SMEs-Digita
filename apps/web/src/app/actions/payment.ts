"use server";

import {
  ensureBlueprint,
  recordWhatsappForPayment,
  whatsappForTenant,
  type PaymentChannel,
} from "@/lib/demo/store";
import { getPaymentProvider } from "@/lib/pay";

export async function createSandboxPayment(input: {
  tenantSlug: string;
  itemSkus: string[];
  channel: PaymentChannel;
}) {
  const blueprint = ensureBlueprint(input.tenantSlug);

  const amountXof = blueprint.catalog
    .filter((item) => input.itemSkus.includes(item.sku))
    .reduce((sum, item) => sum + item.price_xof, 0);

  if (amountXof <= 0) {
    return { ok: false as const, error: "Panier vide — montant recalculé serveur." };
  }

  const idemKey = `${input.tenantSlug}:${[...input.itemSkus].sort().join("+")}:${input.channel}`;
  try {
    const entry = await getPaymentProvider().createTransaction({
      tenantSlug: input.tenantSlug,
      amountXof,
      channel: input.channel,
      idemKey,
      customerCountry: "BJ",
    });
    return { ok: true as const, entry };
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Paiement refusé côté serveur.";
    return { ok: false as const, error: message };
  }
}

export async function confirmSandboxPayment(reference: string) {
  const entry = await getPaymentProvider().verify(reference);
  if (!entry) {
    return { ok: false as const, error: "Référence inconnue ou non vérifiée." };
  }
  if (entry.status !== "confirmed" || !entry.verifiedServer) {
    return {
      ok: false as const,
      error: "Paiement encore en attente — verify() serveur non confirmé.",
    };
  }
  recordWhatsappForPayment(entry);
  return { ok: true as const, entry };
}

export async function getWhatsappPreview(tenantSlug: string, reference?: string) {
  const rows = whatsappForTenant(tenantSlug);
  if (!reference) return rows.slice(0, 4);
  return rows.filter((row) => row.paymentRef === reference);
}
