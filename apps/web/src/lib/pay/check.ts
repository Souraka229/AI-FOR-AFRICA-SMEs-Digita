import { createHmac } from "node:crypto";
import { whatsappForTenant } from "@/lib/demo/store";
import { DemoPaymentProvider } from "@/lib/pay/demo";
import {
  geniusPayPayloadSignature,
  geniusPaySignature,
  verifyGeniusPaySignature,
} from "@/lib/pay/hmac";
import { getPaymentProvider, hasGeniusPaySandboxKeys } from "@/lib/pay";

const SECRET = "whsec_sandbox_check_only";
const TENANT = "cadjehoun-wax";

function fail(message: string): never {
  console.error(message);
  process.exit(1);
}

function sign(body: string, timestamp = "1700000000") {
  return {
    timestamp,
    signature: geniusPaySignature(body, timestamp, SECRET),
  };
}

async function webhook(
  provider: DemoPaymentProvider,
  payload: Record<string, unknown>,
  event?: string,
) {
  const rawBody = JSON.stringify(payload);
  const headers = sign(rawBody);
  return provider.handleWebhook(rawBody, { ...headers, event });
}

async function main() {
  process.env.GENIUSPAY_WEBHOOK_SECRET = SECRET;

  const valid = geniusPaySignature('{"reference":"x"}', "100", SECRET);
  if (!verifyGeniusPaySignature('{"reference":"x"}', "100", valid, SECRET)) {
    fail("HMAC : signature valide rejetée.");
  }
  const forged = createHmac("sha256", "whsec_sandbox_other")
    .update('100.{"reference":"x"}')
    .digest("hex");
  if (verifyGeniusPaySignature('{"reference":"x"}', "100", forged, SECRET)) {
    fail("HMAC : signature étrangère acceptée.");
  }
  if (verifyGeniusPaySignature("{}", "1", valid, "whsec_live_nope")) {
    fail("HMAC : secret live accepté.");
  }
  const bodyOnly = geniusPayPayloadSignature('{"reference":"x"}', SECRET);
  if (!verifyGeniusPaySignature('{"reference":"x"}', "", bodyOnly, SECRET)) {
    fail("HMAC : signature body-only (doc officielle) rejetée.");
  }

  if (getPaymentProvider().id !== "demo") {
    fail("Sans clés sandbox, le provider factory doit rester demo.");
  }

  const prevKey = process.env.GENIUSPAY_API_KEY;
  const prevSecret = process.env.GENIUSPAY_API_SECRET;
  process.env.GENIUSPAY_API_KEY = "pk_live_refuse";
  process.env.GENIUSPAY_API_SECRET = "sk_live_refuse";
  if (hasGeniusPaySandboxKeys()) {
    fail("Clés *_live_* acceptées par hasGeniusPaySandboxKeys.");
  }
  if (prevKey === undefined) delete process.env.GENIUSPAY_API_KEY;
  else process.env.GENIUSPAY_API_KEY = prevKey;
  if (prevSecret === undefined) delete process.env.GENIUSPAY_API_SECRET;
  else process.env.GENIUSPAY_API_SECRET = prevSecret;

  const pay = new DemoPaymentProvider();
  const stamp = Date.now().toString(36);

  // 1. Succès + montant wax + idempotence create
  const first = await pay.createTransaction({
    tenantSlug: TENANT,
    amountXof: 24500,
    channel: "mtn_momo",
    idemKey: `case-ok-${stamp}`,
  });
  const replay = await pay.createTransaction({
    tenantSlug: TENANT,
    amountXof: 24500,
    channel: "mtn_momo",
    idemKey: `case-ok-${stamp}`,
  });
  if (first.reference !== replay.reference || first.amountXof !== 24500) {
    fail("1 succès : idempotence ou montant 24500 cassé.");
  }
  const confirmed = await pay.verify(first.reference);
  if (!confirmed?.verifiedServer || confirmed.status !== "confirmed") {
    fail("1 succès : verify() n’a pas confirmé.");
  }

  // 2. Échec (webhook payment.failed) — verify ne passe pas à confirmé
  const failing = await pay.createTransaction({
    tenantSlug: TENANT,
    amountXof: 4000,
    channel: "moov_money",
    idemKey: `case-fail-${stamp}`,
  });
  const failed = await webhook(
    pay,
    { reference: failing.reference },
    "payment.failed",
  );
  if (failed?.status !== "failed") fail("2 échec : statut attendu failed.");
  const stillFailed = await pay.verify(failing.reference);
  if (stillFailed?.status !== "failed") {
    fail("2 échec : verify() a réécrit un paiement failed.");
  }

  // 3. Expiration
  const expiring = await pay.createTransaction({
    tenantSlug: TENANT,
    amountXof: 8000,
    channel: "mtn_momo",
    idemKey: `case-exp-${stamp}`,
  });
  const expired = await webhook(
    pay,
    { reference: expiring.reference },
    "payment.expired",
  );
  if (expired?.status !== "expired") fail("3 expiration : statut attendu expired.");
  const stillExpired = await pay.verify(expiring.reference);
  if (stillExpired?.status === "confirmed") {
    fail("3 expiration : verify() a confirmé un expiré.");
  }

  // 4. Double webhook succès — une seule paire WhatsApp
  const once = await pay.createTransaction({
    tenantSlug: TENANT,
    amountXof: 12500,
    channel: "mtn_momo",
    idemKey: `case-dup-${stamp}`,
  });
  const body = { reference: once.reference };
  const a = await webhook(pay, body, "payment.success");
  const b = await webhook(pay, body, "payment.success");
  if (a?.status !== "confirmed" || b?.status !== "confirmed") {
    fail("4 double webhook : les deux livraisons doivent confirmer.");
  }
  const wa = whatsappForTenant(TENANT).filter((row) => row.paymentRef === once.reference);
  if (wa.length !== 2) {
    fail(`4 double webhook : WhatsApp doublé (${wa.length} messages).`);
  }

  // 5. Webhook en retard (pending longtemps, puis succès)
  const late = await pay.createTransaction({
    tenantSlug: TENANT,
    amountXof: 4000,
    channel: "cash",
    idemKey: `case-late-${stamp}`,
  });
  const lateOk = await webhook(pay, { reference: late.reference }, "payment.success");
  if (lateOk?.status !== "confirmed" || !lateOk.verifiedServer) {
    fail("5 webhook tardif : doit quand même passer par verify().");
  }

  // 6. Remboursement total
  const full = await pay.createTransaction({
    tenantSlug: TENANT,
    amountXof: 8000,
    channel: "mtn_momo",
    idemKey: `case-rfull-${stamp}`,
  });
  await pay.verify(full.reference);
  const fullRefund = await pay.refund(full.reference, 8000, "annulation cliente");
  if (!fullRefund.ok) fail("6 remboursement total : refusé.");
  const fullState = await pay.verify(full.reference);
  if (fullState?.status !== "refunded" || (fullState.refundedAmountXof ?? 0) !== 8000) {
    fail("6 remboursement total : statut / montant.");
  }

  // 7. Remboursement partiel puis trop-perçu refusé
  const part = await pay.createTransaction({
    tenantSlug: TENANT,
    amountXof: 12500,
    channel: "moov_money",
    idemKey: `case-rpart-${stamp}`,
  });
  await pay.verify(part.reference);
  const half = await pay.refund(part.reference, 5000, "geste commercial");
  if (!half.ok) fail("7 remboursement partiel : refusé.");
  const overflow = await pay.refund(part.reference, 9000, "trop");
  if (overflow.ok) fail("7 remboursement partiel : le trop-perçu a passé.");
  const rest = await pay.refund(part.reference, 7500, "solde");
  if (!rest.ok) fail("7 remboursement partiel : solde refusé.");

  // 8. Réconciliation : pending = écart ; confirmé = matched
  const dangling = await pay.createTransaction({
    tenantSlug: TENANT,
    amountXof: 4000,
    channel: "cash",
    idemKey: `case-recon-${stamp}`,
  });
  const report = await pay.reconcile({
    from: "2020-01-01T00:00:00.000Z",
    to: "2099-01-01T00:00:00.000Z",
  });
  if (!report.discrepancies.includes(dangling.reference)) {
    fail("8 réconciliation : le pending doit lever un écart.");
  }
  if (!report.rows.some((row) => row.reference === first.reference && row.matched)) {
    fail("8 réconciliation : le succès wax doit être matched.");
  }

  // Signature absente / pourrie
  const unsigned = await pay.handleWebhook(JSON.stringify({ reference: first.reference }), {
    signature: "00",
    timestamp: "1",
  });
  if (unsigned) fail("Webhook non signé accepté.");

  console.log("check:pay OK · 8 cas Gate 4 · HMAC · idempotence · 24500 FCFA");
}

void main();
