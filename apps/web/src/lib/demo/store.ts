import fs from "node:fs";
import path from "node:path";
import {
  ALL_EXAMPLES,
  COMMERCE_EXAMPLE,
  type Blueprint,
} from "@afrosite/contracts";

export type PaymentChannel = "mtn_momo" | "moov_money" | "cash";
export type PaymentStatus =
  | "pending"
  | "confirmed"
  | "failed"
  | "expired"
  | "refunded";

export type LedgerEvent = {
  at: string;
  type: "created" | "verified" | "failed" | "expired" | "refunded";
  amountXof?: number;
  reason?: string;
};
export type WhatsAppAudience = "customer" | "owner";

export type LedgerEntry = {
  id: string;
  reference: string;
  tenantSlug: string;
  amountXof: number;
  channel: PaymentChannel;
  status: PaymentStatus;
  createdAt: string;
  confirmedAt?: string;
  verifiedServer: boolean;
  idemKey?: string;
  refundedAmountXof?: number;
  events?: LedgerEvent[];
  checkoutUrl?: string;
};

export type WhatsAppMessage = {
  id: string;
  tenantSlug: string;
  to: WhatsAppAudience;
  body: string;
  at: string;
  paymentRef?: string;
};

export type CostEvent = {
  id: string;
  at: string;
  tenantSlug: string;
  runId?: string;
  promptHash?: string;
  agent: string;
  action: string;
  credits: number;
  model?: string;
  inputTokens?: number;
  outputTokens?: number;
  cacheReadTokens?: number;
  durationMs?: number;
  estimatedCostUsd?: number;
  estimatedCostXof?: number;
};

export type BlueprintVersion = {
  id: string;
  at: string;
  blueprint: Blueprint;
};

type Persisted = {
  blueprints: Record<string, Blueprint>;
  blueprintHistory: Record<string, BlueprintVersion[]>;
  ledger: LedgerEntry[];
  whatsapp: WhatsAppMessage[];
  costs: CostEvent[];
};

const FILE = path.join(process.cwd(), ".demo", "state.json");

function seedBlueprints(): Record<string, Blueprint> {
  return Object.fromEntries(
    ALL_EXAMPLES.map((item) => [item.tenant.slug, structuredClone(item)]),
  );
}

function emptyState(): Persisted {
  return {
    blueprints: seedBlueprints(),
    blueprintHistory: {},
    ledger: [],
    whatsapp: [],
    costs: [],
  };
}

function load(): Persisted {
  try {
    const raw = fs.readFileSync(FILE, "utf8");
    const parsed = JSON.parse(raw) as Partial<Persisted>;
    return {
      blueprints: { ...seedBlueprints(), ...parsed.blueprints },
      blueprintHistory: parsed.blueprintHistory ?? {},
      ledger: parsed.ledger ?? [],
      whatsapp: parsed.whatsapp ?? [],
      costs: parsed.costs ?? [],
    };
  } catch {
    return emptyState();
  }
}

function persist(data: Persisted) {
  fs.mkdirSync(path.dirname(FILE), { recursive: true });
  fs.writeFileSync(FILE, JSON.stringify(data, null, 2), "utf8");
}

function mutate<T>(fn: (data: Persisted) => T): T {
  const data = load();
  const result = fn(data);
  persist(data);
  return result;
}

export function saveBlueprint(blueprint: Blueprint) {
  mutate((data) => {
    data.blueprints[blueprint.tenant.slug] = blueprint;
    const history = data.blueprintHistory[blueprint.tenant.slug] ?? [];
    history.unshift({
      id: crypto.randomUUID(),
      at: new Date().toISOString(),
      blueprint: structuredClone(blueprint),
    });
    data.blueprintHistory[blueprint.tenant.slug] = history.slice(0, 10);
  });
}

export function blueprintVersions(slug: string): BlueprintVersion[] {
  return load().blueprintHistory[slug] ?? [];
}

export function rollbackBlueprint(slug: string, versionId: string): Blueprint {
  return mutate((data) => {
    const version = data.blueprintHistory[slug]?.find((row) => row.id === versionId);
    if (!version) throw new Error("Version de preview introuvable.");
    data.blueprints[slug] = structuredClone(version.blueprint);
    return data.blueprints[slug];
  });
}

export function getBlueprint(slug: string): Blueprint | undefined {
  return load().blueprints[slug];
}

export function listBlueprints(): Blueprint[] {
  return Object.values(load().blueprints);
}

function titleFromSlug(slug: string): string {
  return slug
    .split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function ensureBlueprint(slug: string): Blueprint {
  const existing = getBlueprint(slug);
  if (existing) return existing;
  const seeded = ALL_EXAMPLES.find((item) => item.tenant.slug === slug);
  const blueprint = seeded
    ? structuredClone(seeded)
    : {
        ...structuredClone(COMMERCE_EXAMPLE),
        tenant: {
          ...COMMERCE_EXAMPLE.tenant,
          slug,
          name: titleFromSlug(slug),
          activity_description: `${titleFromSlug(slug)} — établissement créé depuis le studio. Catalogue de départ, paiement Mobile Money en FCFA.`,
        },
      };
  saveBlueprint(blueprint);
  return blueprint;
}

export function findPaymentByIdemKey(idemKey: string): LedgerEntry | undefined {
  if (!idemKey) return undefined;
  return load().ledger.find((row) => row.idemKey === idemKey);
}

export function createPendingPayment(input: {
  tenantSlug: string;
  amountXof: number;
  channel: PaymentChannel;
  idemKey?: string;
  reference?: string;
  checkoutUrl?: string;
}): LedgerEntry {
  return mutate((data) => {
    if (input.idemKey) {
      const existing = data.ledger.find((row) => row.idemKey === input.idemKey);
      if (existing) return existing;
    }
    const entry: LedgerEntry = {
      id: crypto.randomUUID(),
      reference:
        input.reference ??
        `MTX-DEMO-${crypto.randomUUID().slice(0, 8).toUpperCase()}`,
      tenantSlug: input.tenantSlug,
      amountXof: input.amountXof,
      channel: input.channel,
      status: "pending",
      createdAt: new Date().toISOString(),
      verifiedServer: false,
      idemKey: input.idemKey,
      refundedAmountXof: 0,
      checkoutUrl: input.checkoutUrl,
      events: [
        {
          at: new Date().toISOString(),
          type: "created",
          amountXof: input.amountXof,
        },
      ],
    };
    data.ledger.unshift(entry);
    return entry;
  });
}

function pushEvent(entry: LedgerEntry, event: LedgerEvent) {
  entry.events = [...(entry.events ?? []), event];
}

function pushWhatsapp(data: Persisted, entry: LedgerEntry) {
  const already = data.whatsapp.some((row) => row.paymentRef === entry.reference);
  if (already) return;
  const channel =
    entry.channel === "mtn_momo"
      ? "MTN MoMo"
      : entry.channel === "moov_money"
        ? "Moov Money"
        : "espèces";
  const amount = `${entry.amountXof.toLocaleString("fr-FR")} FCFA`;
  const tenant = data.blueprints[entry.tenantSlug];
  const name = tenant?.tenant.name ?? entry.tenantSlug;
  const at = entry.confirmedAt ?? new Date().toISOString();
  data.whatsapp.unshift({
    id: crypto.randomUUID(),
    tenantSlug: entry.tenantSlug,
    to: "customer",
    body: `${name} — reçu ${amount}. Réf ${entry.reference}. Paiement confirmé via ${channel}.`,
    at,
    paymentRef: entry.reference,
  });
  data.whatsapp.unshift({
    id: crypto.randomUUID(),
    tenantSlug: entry.tenantSlug,
    to: "owner",
    body: `Nouvelle vente ${amount} (${channel}). Réf ${entry.reference}. Vérifié côté serveur.`,
    at,
    paymentRef: entry.reference,
  });
}

/** Reçus locaux après un verify() venu de l’API FastAPI. */
export function recordWhatsappForPayment(entry: LedgerEntry) {
  mutate((data) => {
    pushWhatsapp(data, entry);
  });
}

export function verifyAndConfirm(reference: string): LedgerEntry | undefined {
  return mutate((data) => {
    const entry = data.ledger.find((row) => row.reference === reference);
    if (!entry) return undefined;
    if (entry.status === "confirmed" || entry.status === "refunded") {
      return entry;
    }
    if (entry.status === "failed" || entry.status === "expired") {
      return entry;
    }

    entry.verifiedServer = true;
    entry.status = "confirmed";
    entry.confirmedAt = new Date().toISOString();
    pushEvent(entry, {
      at: entry.confirmedAt,
      type: "verified",
      amountXof: entry.amountXof,
    });

    pushWhatsapp(data, entry);
    return entry;
  });
}

export function failPayment(
  reference: string,
  reason = "échec PSP",
): LedgerEntry | undefined {
  return mutate((data) => {
    const entry = data.ledger.find((row) => row.reference === reference);
    if (!entry) return undefined;
    if (entry.status === "confirmed" || entry.status === "refunded") {
      return entry;
    }
    if (entry.status === "failed") return entry;
    entry.status = "failed";
    entry.verifiedServer = true;
    pushEvent(entry, {
      at: new Date().toISOString(),
      type: "failed",
      reason,
    });
    return entry;
  });
}

export function expirePayment(reference: string): LedgerEntry | undefined {
  return mutate((data) => {
    const entry = data.ledger.find((row) => row.reference === reference);
    if (!entry) return undefined;
    if (entry.status !== "pending") return entry;
    entry.status = "expired";
    entry.verifiedServer = true;
    pushEvent(entry, {
      at: new Date().toISOString(),
      type: "expired",
      reason: "expiration sandbox",
    });
    return entry;
  });
}

export function refundPayment(
  reference: string,
  amountXof: number,
  reason: string,
): LedgerEntry | undefined {
  return mutate((data) => {
    const entry = data.ledger.find((row) => row.reference === reference);
    if (!entry) return undefined;
    if (entry.status !== "confirmed" && entry.status !== "refunded") {
      return undefined;
    }
    const already = entry.refundedAmountXof ?? 0;
    const remaining = entry.amountXof - already;
    if (amountXof <= 0 || amountXof > remaining) return undefined;
    entry.refundedAmountXof = already + amountXof;
    if (entry.refundedAmountXof >= entry.amountXof) {
      entry.status = "refunded";
    }
    pushEvent(entry, {
      at: new Date().toISOString(),
      type: "refunded",
      amountXof,
      reason,
    });
    return entry;
  });
}

export function getPayment(reference: string): LedgerEntry | undefined {
  return load().ledger.find((row) => row.reference === reference);
}

export function ledgerForTenant(slug: string): LedgerEntry[] {
  return load().ledger.filter((row) => row.tenantSlug === slug);
}

export function listLedger(): LedgerEntry[] {
  return load().ledger;
}

export function netCollected(row: LedgerEntry): number {
  if (row.status !== "confirmed" && row.status !== "refunded") return 0;
  return row.amountXof - (row.refundedAmountXof ?? 0);
}

export function whatsappForTenant(slug: string): WhatsAppMessage[] {
  return load().whatsapp.filter((row) => row.tenantSlug === slug);
}

export function recordCost(input: Omit<CostEvent, "id" | "at">) {
  mutate((data) => {
    data.costs.unshift({
      id: crypto.randomUUID(),
      at: new Date().toISOString(),
      ...input,
    });
  });
}

export function costsForTenant(slug: string): CostEvent[] {
  return load().costs.filter((row) => row.tenantSlug === slug);
}

export function totalsFromRows(rows: LedgerEntry[]) {
  const collected = rows.filter(
    (row) => row.status === "confirmed" || row.status === "refunded",
  );
  const byChannel: Record<PaymentChannel, number> = {
    mtn_momo: 0,
    moov_money: 0,
    cash: 0,
  };
  for (const row of collected) {
    byChannel[row.channel] += netCollected(row);
  }
  const total = collected.reduce((sum, row) => sum + netCollected(row), 0);
  return {
    count: collected.filter((row) => netCollected(row) > 0).length,
    total,
    byChannel,
    unpaid: rows.filter((row) => row.status === "pending").length,
  };
}

export function todayTotals(slug: string) {
  return totalsFromRows(ledgerForTenant(slug));
}
