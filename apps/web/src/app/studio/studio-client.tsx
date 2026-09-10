"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { Blueprint, Gate1Result, Intent } from "@afrosite/contracts";
import type { AuditEvent, PipelineResult } from "@/lib/agents/pipeline";
import { Money } from "@/components/money";

const EXAMPLES = [
  {
    label: "Commerce",
    prompt:
      "boutique de tissus wax à Cadjehoun, livraison quartier, paiement Mobile Money",
  },
  {
    label: "Restaurant",
    prompt: "maquis à Fidjrossè, menu QR, à emporter, paiement MTN MoMo",
  },
  {
    label: "Services",
    prompt: "salon de coiffure à Cadjehoun, rendez-vous et rappels WhatsApp",
  },
];

const STEPS = [
  { id: "intent", title: "Intent Agent", detail: "Normalise le besoin" },
  { id: "architect", title: "Product Architect", detail: "Produit le Blueprint JSON" },
  { id: "gate1", title: "Gate 1", detail: "Schéma, budget, pas de secret" },
  { id: "preview", title: "Preview", detail: "Mini-site prêt à vendre" },
] as const;

type StepState = "idle" | "running" | "done" | "blocked";

export function StudioClient() {
  const [prompt, setPrompt] = useState(EXAMPLES[0].prompt);
  const [steps, setSteps] = useState<Record<string, StepState>>({});
  const [intent, setIntent] = useState<Intent | null>(null);
  const [blueprint, setBlueprint] = useState<Blueprint | null>(null);
  const [gate1, setGate1] = useState<Gate1Result | null>(null);
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [usage, setUsage] = useState<PipelineResult["usage"] | null>(null);
  const [previewHref, setPreviewHref] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const catalogTotal = useMemo(
    () => blueprint?.catalog.reduce((sum, item) => sum + item.price_xof, 0) ?? 0,
    [blueprint],
  );

  async function run() {
    setRunning(true);
    setError(null);
    setIntent(null);
    setBlueprint(null);
    setGate1(null);
    setAudit([]);
    setUsage(null);
    setPreviewHref(null);
    setSteps({
      intent: "running",
      architect: "idle",
      gate1: "idle",
      preview: "idle",
    });

    try {
      const response = await fetch("/api/studio/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      if (!response.ok) {
        const failure = (await response.json().catch(() => null)) as {
          error?: string;
        } | null;
        throw new Error(failure?.error || "Le pipeline n’a pas démarré.");
      }
      if (!response.body) {
        throw new Error("Le pipeline n’a pas démarré.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          if (!line.trim()) continue;
          const event = JSON.parse(line) as {
            type: string;
            id?: string;
            status?: StepState;
            data?: unknown;
            intent?: Intent;
            blueprint?: Blueprint;
            gate1?: Gate1Result;
            audit?: AuditEvent[];
            usage?: PipelineResult["usage"];
            message?: string;
          };
          if (event.type === "step" && event.id) {
            setSteps((prev) => ({ ...prev, [event.id!]: event.status ?? "done" }));
            if (event.id === "intent" && event.data) setIntent(event.data as Intent);
            if (event.id === "gate1" && event.data) setGate1(event.data as Gate1Result);
          }
          if (event.type === "result") {
            if (event.intent) setIntent(event.intent);
            if (event.blueprint) setBlueprint(event.blueprint);
            if (event.gate1) setGate1(event.gate1);
            if (event.audit) setAudit(event.audit);
            if (event.usage) setUsage(event.usage);
          }
          if (event.type === "error") {
            throw new Error(event.message || "La génération LLM a échoué.");
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur pipeline");
    } finally {
      setRunning(false);
    }
  }

  async function approvePreview() {
    if (!blueprint) return;
    setRunning(true);
    setError(null);
    try {
      const response = await fetch("/api/studio/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ blueprint, capture: true }),
      });
      const data = (await response.json()) as { href?: string; error?: string };
      if (!response.ok || !data.href) {
        throw new Error(data.error || "La preview n’a pas été créée.");
      }
      setPreviewHref(data.href);
      setSteps((previous) => ({ ...previous, preview: "done" }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Preview impossible");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
      <section className="space-y-4">
        <div>
          <Badge>Hackathon · prompt → blueprint</Badge>
          <h1 className="mt-3 font-heading text-3xl font-semibold tracking-tight md:text-4xl">
            Décrivez l&apos;activité. Le contrat sort validé.
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Intent Agent, puis Product Architect, puis Gate 1. Rien n&apos;est
            déployé en production. Streaming à chaque étape.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((example) => (
            <Button
              key={example.label}
              type="button"
              size="sm"
              variant={prompt === example.prompt ? "default" : "outline"}
              onClick={() => setPrompt(example.prompt)}
            >
              {example.label}
            </Button>
          ))}
        </div>

        <label className="block space-y-2">
          <span className="text-sm font-medium">Prompt</span>
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            rows={5}
            className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
          />
        </label>

        <Button size="lg" onClick={run} disabled={running}>
          {running ? "Pipeline en cours…" : "Lancer le pipeline"}
        </Button>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}

        <ol className="space-y-2">
          {STEPS.map((step) => {
            const state = steps[step.id] ?? "idle";
            return (
              <li
                key={step.id}
                className="flex items-center justify-between rounded-lg border border-border px-3 py-2"
              >
                <div>
                  <p className="text-sm font-medium">{step.title}</p>
                  <p className="text-xs text-muted-foreground">{step.detail}</p>
                </div>
                <span className="font-heading text-xs tabular-nums text-muted-foreground">
                  {state === "idle" && "—"}
                  {state === "running" && "en cours"}
                  {state === "done" && "ok"}
                  {state === "blocked" && "bloqué"}
                </span>
              </li>
            );
          })}
        </ol>
      </section>

      <section className="space-y-4">
        {intent ? (
          <div className="rounded-xl border border-border bg-card p-4 text-card-foreground">
            <p className="text-xs text-muted-foreground">Intention</p>
            <p className="font-heading text-lg font-semibold">
              {intent.vertical} · {intent.neighborhood}
            </p>
            <p className="text-sm text-muted-foreground">{intent.activity_summary}</p>
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-border p-6 text-sm text-muted-foreground">
            Le Blueprint JSON apparaîtra ici après Gate 1.
          </div>
        )}

        {gate1 ? (
          <div className="rounded-xl border border-border bg-card p-4 text-card-foreground">
            <p className="text-xs text-muted-foreground">Gate 1</p>
            <p className="font-heading text-lg font-semibold">
              {gate1.passed ? "Conforme" : "Rejeté"}
            </p>
            <p className="font-heading text-sm tabular-nums">
              {gate1.credits} / {gate1.budget_credits_max} crédits estimés
            </p>
            {gate1.errors.length > 0 ? (
              <ul className="mt-2 list-disc pl-4 text-sm text-destructive">
                {gate1.errors.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : null}
          </div>
        ) : null}

        {usage ? (
          <div className="rounded-xl border border-border bg-card p-4 text-card-foreground">
            <p className="text-xs text-muted-foreground">Consommation du run</p>
            <p className="font-heading text-sm tabular-nums">
              {usage.totalTokens.toLocaleString("fr-FR")} tokens ·{" "}
              {usage.durationMs.toLocaleString("fr-FR")} ms · env.{" "}
              <Money amountXof={usage.estimatedCostXof} />
            </p>
            <p className="text-xs text-muted-foreground">
              Entrée {usage.inputTokens.toLocaleString("fr-FR")} · sortie{" "}
              {usage.outputTokens.toLocaleString("fr-FR")} · cache{" "}
              {usage.cacheReadTokens.toLocaleString("fr-FR")}
            </p>
          </div>
        ) : null}

        {blueprint && gate1?.passed ? (
          <div className="space-y-3 rounded-xl border border-border bg-card p-4 text-card-foreground">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-heading text-lg font-semibold">{blueprint.tenant.name}</p>
                <p className="font-mono text-xs text-muted-foreground">
                  {blueprint.tenant.slug}
                </p>
              </div>
              <div className="flex gap-2">
                {previewHref ? (
                  <>
                    <Button asChild>
                      <Link href={previewHref}>Ouvrir la preview</Link>
                    </Button>
                    <Button asChild variant="outline">
                      <Link href={`/dashboard/${blueprint.tenant.slug}`}>Caisse</Link>
                    </Button>
                  </>
                ) : (
                  <Button onClick={approvePreview} disabled={running}>
                    Approuver la preview
                  </Button>
                )}
              </div>
            </div>
            <ul className="space-y-1 text-sm">
              {blueprint.catalog.map((item) => (
                <li key={item.sku} className="flex justify-between gap-3">
                  <span>{item.name}</span>
                  <span className="font-heading tabular-nums">
                    <Money amountXof={item.price_xof} />
                  </span>
                </li>
              ))}
            </ul>
            <p className="text-right text-xs text-muted-foreground">
              Panier démo (3 lignes) :{" "}
              <Money amountXof={catalogTotal} />
              {" · "}
              {blueprint.estimated_cost_credits} / {gate1.budget_credits_max} crédits
            </p>
            <p className="text-xs text-muted-foreground">
              Gate 1 passé. Une approbation humaine explicite crée la preview ;
              elle ne déploie jamais en production.
            </p>
            <pre className="max-h-64 overflow-auto rounded-lg bg-muted p-3 font-mono text-[11px] leading-relaxed">
              {JSON.stringify(blueprint, null, 2)}
            </pre>
          </div>
        ) : null}

        {audit.length > 0 ? (
          <div className="rounded-xl border border-border bg-card p-4 text-card-foreground">
            <p className="mb-2 text-xs text-muted-foreground">Audit trail</p>
            <ol className="space-y-2">
              {audit.map((event, index) => (
                <li key={`${event.at}-${index}`} className="text-xs">
                  <span className="font-mono text-muted-foreground">
                    {event.at.slice(11, 19)}
                  </span>{" "}
                  <span className="font-medium">{event.agent}</span> · {event.action} →{" "}
                  {event.result}
                  {event.model ? ` · ${event.model}` : ""}
                  {event.tokens !== undefined ? ` · ${event.tokens} tokens` : ""}
                </li>
              ))}
            </ol>
          </div>
        ) : null}
      </section>
    </div>
  );
}
