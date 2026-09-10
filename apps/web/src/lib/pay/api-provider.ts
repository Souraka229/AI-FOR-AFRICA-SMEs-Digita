import type { LedgerEntry, PaymentStatus } from "@/lib/demo/store";
import type {
  PaymentOrder,
  PaymentProvider,
  ReconcileResult,
  RefundResult,
  WebhookHeaders,
} from "@/lib/pay/provider";

export function apiBaseUrl(): string {
  return (process.env.AFROSITE_API_URL ?? "").replace(/\/$/, "");
}

export function hasAfrositeApi(): boolean {
  return apiBaseUrl().startsWith("http://") || apiBaseUrl().startsWith("https://");
}

function mapEntry(raw: Record<string, unknown>): LedgerEntry {
  return {
    id: String(raw.id),
    reference: String(raw.reference),
    tenantSlug: String(raw.tenantSlug),
    amountXof: Number(raw.amountXof),
    channel: raw.channel as LedgerEntry["channel"],
    status: raw.status as PaymentStatus,
    createdAt: String(raw.createdAt),
    confirmedAt: raw.confirmedAt ? String(raw.confirmedAt) : undefined,
    verifiedServer: Boolean(raw.verifiedServer),
    idemKey: raw.idemKey ? String(raw.idemKey) : undefined,
    refundedAmountXof: Number(raw.refundedAmountXof ?? 0),
  };
}

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  const payload = (await response.json()) as T & { detail?: unknown };
  if (!response.ok) {
    throw new Error(
      typeof payload.detail === "string" ? payload.detail : `API ${response.status}`,
    );
  }
  return payload;
}

export async function fetchApiLedger(tenantSlug: string): Promise<LedgerEntry[] | null> {
  if (!hasAfrositeApi()) return null;
  try {
    const payload = await api<{ entries: Record<string, unknown>[] }>(
      `/ledger/${encodeURIComponent(tenantSlug)}`,
    );
    return payload.entries.map(mapEntry);
  } catch {
    return null;
  }
}

export class ApiPaymentProvider implements PaymentProvider {
  readonly id = "api" as const;

  async createTransaction(order: PaymentOrder): Promise<LedgerEntry> {
    const payload = await api<{ entry: Record<string, unknown> }>("/payments", {
      method: "POST",
      body: JSON.stringify({
        tenant_slug: order.tenantSlug,
        amount_xof: order.amountXof,
        channel: order.channel,
        idem_key: order.idemKey,
      }),
    });
    return mapEntry(payload.entry);
  }

  async verify(reference: string): Promise<LedgerEntry | undefined> {
    try {
      const payload = await api<{ entry: Record<string, unknown> }>(
        `/payments/${encodeURIComponent(reference)}/verify`,
        { method: "POST" },
      );
      return mapEntry(payload.entry);
    } catch {
      return undefined;
    }
  }

  async handleWebhook(
    rawBody: string,
    headers: WebhookHeaders,
  ): Promise<LedgerEntry | undefined> {
    const parsed = JSON.parse(rawBody) as { reference?: string };
    if (!parsed.reference) return undefined;
    if ((headers.event ?? "").includes("fail")) {
      const payload = await api<{ entry: Record<string, unknown> }>(
        `/payments/${encodeURIComponent(parsed.reference)}/fail`,
        { method: "POST" },
      );
      return mapEntry(payload.entry);
    }
    return this.verify(parsed.reference);
  }

  async refund(
    reference: string,
    amountXof: number,
    reason: string,
  ): Promise<RefundResult> {
    try {
      await api(`/payments/${encodeURIComponent(reference)}/refund`, {
        method: "POST",
        headers: { "X-Afrosite-Role": "owner" },
        body: JSON.stringify({ amount_xof: amountXof, reason }),
      });
      return { ok: true, reference };
    } catch (error) {
      return {
        ok: false,
        reference,
        error: error instanceof Error ? error.message : "remboursement refusé",
      };
    }
  }

  async reconcile(): Promise<ReconcileResult> {
    return { from: "", to: "", rows: [], discrepancies: [] };
  }
}
