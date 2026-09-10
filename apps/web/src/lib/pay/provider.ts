import type { LedgerEntry, PaymentChannel } from "@/lib/demo/store";

/** Contrat maison — playbook §10.2. Le métier ne parle jamais au SDK Genius Pay. */
export type PaymentOrder = {
  tenantSlug: string;
  amountXof: number;
  channel: PaymentChannel;
  idemKey: string;
  customerCountry?: "BJ";
};

export type WebhookHeaders = {
  signature: string;
  timestamp: string;
  event?: string;
  environment?: string;
};

export type RefundResult = {
  ok: boolean;
  reference: string;
  error?: string;
};

export type ReconcileRow = {
  reference: string;
  amountXof: number;
  matched: boolean;
};

export type ReconcileResult = {
  from: string;
  to: string;
  rows: ReconcileRow[];
  discrepancies: string[];
};

export interface PaymentProvider {
  readonly id: "geniuspay" | "demo" | "api";
  createTransaction(order: PaymentOrder): Promise<LedgerEntry>;
  verify(reference: string): Promise<LedgerEntry | undefined>;
  handleWebhook(
    rawBody: string,
    headers: WebhookHeaders,
  ): Promise<LedgerEntry | undefined>;
  refund(
    reference: string,
    amountXof: number,
    reason: string,
  ): Promise<RefundResult>;
  reconcile(range: { from: string; to: string }): Promise<ReconcileResult>;
}
