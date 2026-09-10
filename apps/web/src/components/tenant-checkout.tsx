"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  confirmSandboxPayment,
  createSandboxPayment,
  getWhatsappPreview,
} from "@/app/actions/payment";
import { Money } from "@/components/money";
import { PaymentStatus as StatusBadge } from "@/components/payment-status";
import type { PaymentChannel, PaymentStatus } from "@/lib/demo/store";

type Item = { sku: string; name: string; price_xof: number };

export function TenantCheckout({
  tenantSlug,
  items,
}: {
  tenantSlug: string;
  items: Item[];
}) {
  const router = useRouter();
  const [selected, setSelected] = useState<string[]>(items.map((item) => item.sku));
  const [channel, setChannel] = useState<PaymentChannel>("mtn_momo");
  const [status, setStatus] = useState<PaymentStatus | "idle">("idle");
  const [reference, setReference] = useState<string | null>(null);
  const [checkoutUrl, setCheckoutUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [receipts, setReceipts] = useState<
    { to: "customer" | "owner"; body: string }[]
  >([]);

  const total = items
    .filter((item) => selected.includes(item.sku))
    .reduce((sum, item) => sum + item.price_xof, 0);

  async function pay() {
    setBusy(true);
    setError(null);
    const created = await createSandboxPayment({
      tenantSlug,
      itemSkus: selected,
      channel,
    });
    if (!created.ok) {
      setError(created.error);
      setBusy(false);
      return;
    }
    setReference(created.entry.reference);
    setCheckoutUrl(created.entry.checkoutUrl ?? null);
    setStatus("pending");
    setBusy(false);
  }

  async function verify() {
    if (!reference) return;
    setBusy(true);
    const confirmed = await confirmSandboxPayment(reference);
    if (!confirmed.ok) {
      setError(confirmed.error);
      setBusy(false);
      return;
    }
    setStatus("confirmed");
    const messages = await getWhatsappPreview(tenantSlug, reference);
    setReceipts(messages.map((row) => ({ to: row.to, body: row.body })));
    setBusy(false);
    router.refresh();
  }

  return (
    <div className="space-y-4 rounded-xl border border-border bg-card p-4">
      <p className="font-heading text-lg font-semibold">Panier</p>
      <ul className="space-y-2">
        {items.map((item) => (
          <li key={item.sku}>
            <label className="flex items-center justify-between gap-3 text-sm">
              <span className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={selected.includes(item.sku)}
                  onChange={() => {
                    setSelected((current) =>
                      current.includes(item.sku)
                        ? current.filter((sku) => sku !== item.sku)
                        : [...current, item.sku],
                    );
                  }}
                />
                {item.name}
              </span>
              <Money amountXof={item.price_xof} />
            </label>
          </li>
        ))}
      </ul>

      <p className="text-right text-xl font-semibold">
        <Money amountXof={total} />
      </p>

      <div className="flex gap-2">
        <Button
          type="button"
          variant={channel === "mtn_momo" ? "default" : "outline"}
          onClick={() => setChannel("mtn_momo")}
        >
          MTN MoMo
        </Button>
        <Button
          type="button"
          variant={channel === "moov_money" ? "default" : "outline"}
          onClick={() => setChannel("moov_money")}
        >
          Moov Money
        </Button>
      </div>

      {status === "idle" ? (
        <Button size="lg" className="w-full" disabled={busy || total <= 0} onClick={pay}>
          Payer en sandbox
        </Button>
      ) : null}

      {status === "pending" ? (
        <div className="space-y-3 rounded-lg bg-muted p-3">
          <p className="text-sm font-medium">
            <StatusBadge status="pending" />
          </p>
          <p className="font-mono text-xs">{reference}</p>
          <p className="text-xs text-muted-foreground">
            La redirection ne prouve rien. Seul un verify() serveur confirme.
          </p>
          {checkoutUrl ? (
            <Button asChild variant="outline" className="w-full">
              <a href={checkoutUrl} target="_blank" rel="noreferrer">
                Ouvrir le checkout Genius Pay
              </a>
            </Button>
          ) : null}
          <Button size="lg" className="w-full" disabled={busy} onClick={verify}>
            verify() serveur
          </Button>
        </div>
      ) : null}

      {status === "confirmed" ? (
        <div className="rounded-lg border border-confirmed/30 bg-confirmed/10 p-3">
          <p className="font-medium">
            <StatusBadge status="confirmed" />
          </p>
          <p className="font-mono text-xs">{reference}</p>
          {receipts.length > 0 ? (
            <ul className="mt-3 space-y-2 text-xs">
              {receipts.map((row) => (
                <li key={row.body} className="rounded-md bg-background/70 px-2 py-1.5">
                  <span className="font-medium">
                    WhatsApp {row.to === "customer" ? "client" : "commerçante"}
                  </span>
                  <p className="mt-0.5 text-muted-foreground">{row.body}</p>
                </li>
              ))}
            </ul>
          ) : null}
          <Button asChild variant="outline" className="mt-3 w-full">
            <Link href={`/dashboard/${tenantSlug}`}>Voir la caisse du soir</Link>
          </Button>
        </div>
      ) : null}

      {error ? <p className="text-sm text-destructive">{error}</p> : null}
    </div>
  );
}
