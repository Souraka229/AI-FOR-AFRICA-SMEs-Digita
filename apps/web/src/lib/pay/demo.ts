import {
  createPendingPayment,
  expirePayment,
  failPayment,
  getPayment,
  listLedger,
  netCollected,
  refundPayment,
  verifyAndConfirm,
  type LedgerEntry,
} from "@/lib/demo/store";
import { verifyGeniusPaySignature } from "@/lib/pay/hmac";
import type {
  PaymentOrder,
  PaymentProvider,
  ReconcileResult,
  RefundResult,
  WebhookHeaders,
} from "@/lib/pay/provider";

type WebhookBody = {
  reference?: string;
  data?: { reference?: string };
  event?: string;
};

/**
 * Fallback hackathon : ledger fichier (.demo/state.json).
 * Couvre les 8 cas Gate 4 sans clés PSP.
 */
export class DemoPaymentProvider implements PaymentProvider {
  readonly id = "demo" as const;

  async createTransaction(order: PaymentOrder): Promise<LedgerEntry> {
    if (order.amountXof <= 0) {
      throw new Error("Montant recalculé serveur invalide.");
    }
    return createPendingPayment({
      tenantSlug: order.tenantSlug,
      amountXof: order.amountXof,
      channel: order.channel,
      idemKey: order.idemKey,
    });
  }

  async verify(reference: string): Promise<LedgerEntry | undefined> {
    const existing = getPayment(reference);
    if (!existing) return undefined;
    if (existing.status !== "pending" && existing.status !== "confirmed") {
      return existing;
    }
    if (existing.status === "confirmed") return existing;
    return verifyAndConfirm(reference);
  }

  async handleWebhook(
    rawBody: string,
    headers: WebhookHeaders,
  ): Promise<LedgerEntry | undefined> {
    const secret = process.env.GENIUSPAY_WEBHOOK_SECRET ?? "";
    if (
      !secret ||
      !verifyGeniusPaySignature(rawBody, headers.timestamp, headers.signature, secret)
    ) {
      return undefined;
    }

    let parsed: WebhookBody;
    try {
      parsed = JSON.parse(rawBody) as WebhookBody;
    } catch {
      return undefined;
    }

    const reference = parsed.reference ?? parsed.data?.reference;
    const event = (headers.event ?? parsed.event ?? "payment.success").toLowerCase();
    if (event === "webhook.test") {
      return {
        id: "webhook-test",
        reference: reference || "webhook.test",
        tenantSlug: "system",
        amountXof: 0,
        channel: "cash",
        status: "pending",
        createdAt: new Date().toISOString(),
        verifiedServer: false,
      };
    }
    if (!reference) return undefined;
    if (event === "payment.failed") return failPayment(reference, "webhook payment.failed");
    if (event === "payment.expired") return expirePayment(reference);
    if (event === "payment.refunded") {
      const local = getPayment(reference);
      if (!local) return undefined;
      const remaining = local.amountXof - (local.refundedAmountXof ?? 0);
      return refundPayment(reference, remaining, "webhook payment.refunded");
    }
    return this.verify(reference);
  }

  async refund(
    reference: string,
    amountXof: number,
    reason: string,
  ): Promise<RefundResult> {
    const entry = refundPayment(reference, amountXof, reason);
    if (!entry) {
      return {
        ok: false,
        reference,
        error: "Remboursement refusé (pas confirmé, ou montant hors reste).",
      };
    }
    return { ok: true, reference: entry.reference };
  }

  async reconcile(range: { from: string; to: string }): Promise<ReconcileResult> {
    const from = Date.parse(range.from);
    const to = Date.parse(range.to);
    const rows = listLedger()
      .filter((row) => {
        const at = Date.parse(row.createdAt);
        return at >= from && at <= to;
      })
      .map((row) => ({
        reference: row.reference,
        amountXof: netCollected(row),
        matched:
          (row.status === "confirmed" || row.status === "refunded") &&
          row.verifiedServer,
      }));
    return {
      from: range.from,
      to: range.to,
      rows,
      discrepancies: rows.filter((row) => !row.matched).map((row) => row.reference),
    };
  }
}
