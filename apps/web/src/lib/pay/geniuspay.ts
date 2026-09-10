import {
  createPendingPayment,
  expirePayment,
  failPayment,
  findPaymentByIdemKey,
  getPayment,
  verifyAndConfirm,
  type LedgerEntry,
  type PaymentChannel,
} from "@/lib/demo/store";
import { verifyGeniusPaySignature } from "@/lib/pay/hmac";
import type {
  PaymentOrder,
  PaymentProvider,
  ReconcileResult,
  RefundResult,
  WebhookHeaders,
} from "@/lib/pay/provider";

/** Doc officielle marchand : https://geniuspay.ci/docs/api */
const MERCHANT_BASE = "https://geniuspay.ci/api/v1/merchant";
/** Sandbox virtuel (scénarios) : https://geniuspay.ci/docs/sandbox */
const VIRTUAL_SANDBOX_BASE = "https://pay.genius.ci/sandbox";

type MerchantData = {
  reference?: string;
  id?: string | number;
  status?: string;
  checkout_url?: string;
  payment_url?: string;
};

function refuseLive(value: string, name: string) {
  if (value.includes("_live_")) {
    throw new Error(`${name} production refusée avant audit + gate 6.`);
  }
}

function sandboxEnv() {
  const apiKey = process.env.GENIUSPAY_API_KEY ?? "";
  const apiSecret = process.env.GENIUSPAY_API_SECRET ?? "";
  const webhookSecret = process.env.GENIUSPAY_WEBHOOK_SECRET ?? "";
  refuseLive(apiKey, "GENIUSPAY_API_KEY");
  refuseLive(apiSecret, "GENIUSPAY_API_SECRET");
  refuseLive(webhookSecret, "GENIUSPAY_WEBHOOK_SECRET");

  const merchant = apiKey.startsWith("pk_sandbox_") && apiSecret.startsWith("sk_sandbox_");
  const virtual = apiKey.startsWith("sbx_test_");
  if (!merchant && !virtual) {
    throw new Error(
      "Genius Pay : clés sandbox manquantes (pk_sandbox_ + sk_sandbox_ ou sbx_test_).",
    );
  }
  return {
    apiKey,
    apiSecret,
    webhookSecret,
    mode: merchant ? ("merchant" as const) : ("virtual" as const),
    merchantBase: process.env.GENIUSPAY_BASE_URL || MERCHANT_BASE,
    virtualBase: process.env.GENIUSPAY_SANDBOX_URL || VIRTUAL_SANDBOX_BASE,
  };
}

export function hasGeniusPaySandboxKeys(): boolean {
  const key = process.env.GENIUSPAY_API_KEY ?? "";
  const secret = process.env.GENIUSPAY_API_SECRET ?? "";
  if (key.includes("_live_") || secret.includes("_live_")) return false;
  if (key.startsWith("sbx_test_")) return true;
  return key.startsWith("pk_sandbox_") && secret.startsWith("sk_sandbox_");
}

function gatewayFor(channel: PaymentChannel): string {
  if (channel === "moov_money") return "moov_money";
  return "mtn_momo";
}

const MERCHANT_HEADERS = {
  Accept: "application/json",
  "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
};

async function readGeniusError(response: Response, fallback: string): Promise<string> {
  const text = await response.text();
  try {
    const parsed = JSON.parse(text) as {
      error?: { message?: string; code?: string } | string;
      message?: string;
    };
    if (typeof parsed.error === "string" && parsed.error) return parsed.error;
    if (parsed.error && typeof parsed.error === "object") {
      return parsed.error.message ?? parsed.error.code ?? fallback;
    }
    if (parsed.message) return parsed.message;
  } catch {
    /* corps non JSON */
  }
  return text.slice(0, 180) || fallback;
}

function merchantHeaders(env: ReturnType<typeof sandboxEnv>, json = false) {
  return {
    ...MERCHANT_HEADERS,
    "X-API-Key": env.apiKey,
    "X-API-Secret": env.apiSecret,
    ...(json ? { "Content-Type": "application/json" } : {}),
  };
}

function unwrap(payload: unknown): MerchantData {
  const root = payload as { data?: MerchantData; reference?: string; status?: string };
  return root.data ?? root;
}

/**
 * Contrat officiel GeniusPay (docs/api + docs/sandbox).
 * Jamais de SDK dans le métier — uniquement ici.
 */
export class GeniusPayProvider implements PaymentProvider {
  readonly id = "geniuspay" as const;

  async createTransaction(order: PaymentOrder): Promise<LedgerEntry> {
    const env = sandboxEnv();
    const replay = findPaymentByIdemKey(order.idemKey);
    if (replay) return replay;
    if (order.amountXof < 200) {
      throw new Error("Montant Genius Pay minimum : 200 XOF.");
    }

    const created =
      env.mode === "virtual"
        ? await initiateVirtual(env, order)
        : await initiateMerchant(env, order);

    return createPendingPayment({
      tenantSlug: order.tenantSlug,
      amountXof: order.amountXof,
      channel: order.channel,
      idemKey: order.idemKey,
      reference: created.reference,
      checkoutUrl: created.checkoutUrl,
    });
  }

  async verify(reference: string): Promise<LedgerEntry | undefined> {
    const env = sandboxEnv();
    const local = getPayment(reference);
    if (!local) return undefined;
    if (local.status === "failed" || local.status === "expired" || local.status === "refunded") {
      return local;
    }
    if (local.status === "confirmed") return local;

    if (env.mode === "virtual") {
      return local;
    }

    const response = await fetch(
      `${env.merchantBase}/payments/${encodeURIComponent(reference)}`,
      {
        headers: merchantHeaders(env),
      },
    );
    if (!response.ok) return local;

    const payload = unwrap(JSON.parse(await response.text()));
    const status = (payload.status ?? "").toLowerCase();
    if (status === "failed" || status === "cancelled") {
      return failPayment(reference, `geniuspay ${status}`);
    }
    if (status === "expired") return expirePayment(reference);
    if (status === "completed" || status === "success" || status === "paid") {
      return verifyAndConfirm(reference);
    }
    return local;
  }

  async handleWebhook(
    rawBody: string,
    headers: WebhookHeaders,
  ): Promise<LedgerEntry | undefined> {
    if ((headers.environment ?? "").toLowerCase() === "live") {
      return undefined;
    }
    const env = sandboxEnv();
    if (!env.webhookSecret.startsWith("whsec_") || env.webhookSecret.includes("_live_")) {
      return undefined;
    }
    if (
      !verifyGeniusPaySignature(
        rawBody,
        headers.timestamp,
        headers.signature,
        env.webhookSecret,
      )
    ) {
      return undefined;
    }

    const parsed = JSON.parse(rawBody) as {
      event?: string;
      environment?: string;
      reference?: string;
      data?: {
        reference?: string;
        status?: string;
        environment?: string;
        transaction?: { reference?: string; status?: string };
      };
    };
    const payloadEnv = (
      parsed.data?.environment ??
      parsed.environment ??
      headers.environment ??
      ""
    ).toLowerCase();
    if (payloadEnv === "live") return undefined;

    const reference =
      parsed.data?.transaction?.reference ??
      parsed.data?.reference ??
      parsed.reference;
    const event = (headers.event ?? parsed.event ?? "").toLowerCase();
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
    if (event === "payment.initiated") return getPayment(reference);
    if (event === "payment.failed" || event === "payment.cancelled") {
      return failPayment(reference, event);
    }
    if (event === "payment.expired") return expirePayment(reference);
    if (event === "payment.refunded") {
      const local = getPayment(reference);
      return local;
    }
    return this.verify(reference);
  }

  async refund(): Promise<RefundResult> {
    return {
      ok: false,
      reference: "",
      error: "Remboursement Genius Pay : après create/verify sandbox verts.",
    };
  }

  async reconcile(range: { from: string; to: string }): Promise<ReconcileResult> {
    const env = sandboxEnv();
    if (env.mode !== "merchant") {
      return { from: range.from, to: range.to, rows: [], discrepancies: [] };
    }
    const params = new URLSearchParams({
      from: range.from.slice(0, 10),
      to: range.to.slice(0, 10),
      per_page: "100",
    });
    const response = await fetch(`${env.merchantBase}/payments?${params}`, {
      headers: merchantHeaders(env),
    });
    if (!response.ok) {
      return {
        from: range.from,
        to: range.to,
        rows: [],
        discrepancies: [`GET payments HTTP ${response.status}`],
      };
    }
    const payload = (await response.json()) as {
      data?: { reference?: string; amount?: number; status?: string }[];
    };
    const rows = (payload.data ?? []).map((row) => {
      const reference = String(row.reference ?? "");
      return {
        reference,
        amountXof: Number(row.amount ?? 0),
        matched:
          (row.status ?? "").toLowerCase() === "completed" &&
          Boolean(reference && getPayment(reference)),
      };
    });
    return {
      from: range.from,
      to: range.to,
      rows,
      discrepancies: rows.filter((row) => !row.matched).map((row) => row.reference),
    };
  }
}

async function initiateMerchant(
  env: ReturnType<typeof sandboxEnv>,
  order: PaymentOrder,
): Promise<{ reference: string; checkoutUrl?: string }> {
  const response = await fetch(`${env.merchantBase}/payments`, {
    method: "POST",
    headers: merchantHeaders(env, true),
    body: JSON.stringify({
      amount: order.amountXof,
      currency: "XOF",
      description: `Afrosite ${order.tenantSlug}`,
      success_url: process.env.APP_URL
        ? `${process.env.APP_URL}/t/${order.tenantSlug}`
        : undefined,
      error_url: process.env.APP_URL
        ? `${process.env.APP_URL}/t/${order.tenantSlug}`
        : undefined,
      metadata: {
        idempotency_key: order.idemKey,
        order_id: order.idemKey,
        tenant_slug: order.tenantSlug,
        country: order.customerCountry ?? "BJ",
      },
    }),
  });
  if (!response.ok) {
    throw new Error(
      await readGeniusError(response, `Genius Pay createTransaction HTTP ${response.status}`),
    );
  }
  const data = unwrap(JSON.parse(await response.text()));
  const reference = data.reference ?? (data.id != null ? String(data.id) : "");
  if (!reference) throw new Error("Genius Pay : référence absente.");
  return {
    reference,
    checkoutUrl: data.checkout_url ?? data.payment_url,
  };
}

async function initiateVirtual(
  env: ReturnType<typeof sandboxEnv>,
  order: PaymentOrder,
): Promise<{ reference: string; checkoutUrl?: string }> {
  const response = await fetch(`${env.virtualBase}/payments/initiate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${env.apiKey}`,
      "X-API-Key": env.apiKey,
    },
    body: JSON.stringify({
      amount: order.amountXof,
      scenario: process.env.GENIUSPAY_SANDBOX_SCENARIO || "success",
      gateway: gatewayFor(order.channel),
      external_reference: order.idemKey,
    }),
  });
  if (!response.ok) {
    throw new Error(`Genius Pay sandbox initiate HTTP ${response.status}`);
  }
  const data = unwrap(await response.json());
  const reference = data.reference ?? (data.id != null ? String(data.id) : "");
  if (!reference) throw new Error("Genius Pay sandbox : référence absente.");
  return {
    reference,
    checkoutUrl: data.checkout_url ?? data.payment_url,
  };
}
