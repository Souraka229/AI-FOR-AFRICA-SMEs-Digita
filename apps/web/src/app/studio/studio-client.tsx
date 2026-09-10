"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { Blueprint, Gate1Result, Intent } from "@afrosite/contracts";
import {
  auditActionLabel,
  auditAgentLabel,
  formatAuditClock,
  type AuditEvent,
} from "@/lib/agents/audit";
import type { PipelineResult } from "@/lib/agents/pipeline";
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
  { id: "preview", title: "Preview", detail: "Accord humain, jamais la prod" },
] as const;

const CONFIRMATION_LABELS: Record<string, string> = {
  production_deploy: "Déploiement production",
  payment_live_activation: "Activation du paiement réel",
  database_deletion: "Suppression de données",
  mass_email: "Envoi d’e-mails de masse",
  access_change: "Changement d’accès",
};

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
  const [planAccepted, setPlanAccepted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const catalogTotal = useMemo(
    () => blueprint?.catalog.reduce((sum, item) => sum + item.price_xof, 0) ?? 0,
    [blueprint],
  );

  const liveCostXof = useMemo(
    () =>
      usage?.estimatedCostXof ??
      audit.reduce((sum, event) => sum + (event.estimatedCostXof ?? 0), 0),
    [audit, usage],
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
    setPlanAccepted(false);
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
            event?: AuditEvent;
            intent?: Intent;
            blueprint?: Blueprint;
            gate1?: Gate1Result;
            audit?: AuditEvent[];
            usage?: PipelineResult["usage"];
            message?: string;
          };
          if (event.type === "audit" && event.event) {
            setAudit((previous) => [...previous, event.event!]);
          }
          if (event.type === "step" && event.id) {
            setSteps((prev) => ({ ...prev, [event.id!]: event.status ?? "done" }));
            if (event.id === "intent" && event.data) setIntent(event.data as Intent);
            if (event.id === "architect" && event.data) {
              const payload = event.data as { blueprint?: Blueprint };
              if (payload.blueprint) setBlueprint(payload.blueprint);
            }
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
    if (!blueprint || !planAccepted) return;
    setRunning(true);
    setError(null);
    try {
      const response = await fetch("/api/studio/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ blueprint }),
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

  const canApprove = Boolean(blueprint && gate1?.passed && planAccepted && !previewHref);

  return (
    <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.15fr)]">
      <section className="space-y-4">
        <div>
          <Badge>Hackathon · validation client</Badge>
          <h1 className="mt-3 font-heading text-3xl font-semibold tracking-tight md:text-4xl">
            Décrivez l&apos;activité. Le contrat sort validé.
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Plan, coût estimé et audit trail en direct. Rien n&apos;est déployé
            en production sans accord explicite.
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

        <div>
          <h2 className="mb-2 font-heading text-sm font-semibold">État live</h2>
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
                    {state === "blocked" && "en attente"}
                  </span>
                </li>
              );
            })}
          </ol>
        </div>
      </section>

      <section className="space-y-4">
        <div className="rounded-xl border border-border bg-card p-4 text-card-foreground">
          <h2 className="font-heading text-sm font-semibold">Coût estimé</h2>
          {gate1 || usage || liveCostXof > 0 ? (
            <div className="mt-2 space-y-1">
              {gate1 ? (
                <p className="font-heading text-lg tabular-nums">
                  {gate1.credits} / {gate1.budget_credits_max} crédits
                </p>
              ) : (
                <p className="text-sm text-muted-foreground">Crédits en cours de calcul…</p>
              )}
              <p className="text-sm">
                Coût LLM env. <Money amountXof={liveCostXof} />
              </p>
              {usage ? (
                <p className="text-xs text-muted-foreground">
                  {usage.totalTokens.toLocaleString("fr-FR")} tokens · entrée{" "}
                  {usage.inputTokens.toLocaleString("fr-FR")} · sortie{" "}
                  {usage.outputTokens.toLocaleString("fr-FR")} · cache{" "}
                  {usage.cacheReadTokens.toLocaleString("fr-FR")} ·{" "}
                  {usage.durationMs.toLocaleString("fr-FR")} ms
                </p>
              ) : null}
            </div>
          ) : (
            <p className="mt-2 text-sm text-muted-foreground">
              Le coût apparaît dès le premier appel LLM.
            </p>
          )}
        </div>

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
            Le plan (modules, catalogue, coût) apparaîtra ici en direct.
          </div>
        )}

        {blueprint ? (
          <div className="space-y-3 rounded-xl border border-border bg-card p-4 text-card-foreground">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="font-heading text-lg font-semibold">Plan</h2>
                <p className="font-heading text-base">{blueprint.tenant.name}</p>
                <p className="font-mono text-xs text-muted-foreground">
                  {blueprint.tenant.slug} · {blueprint.tenant.city} · BJ · XOF ·{" "}
                  {blueprint.deployment_target}
                </p>
              </div>
              {gate1 ? (
                <Badge variant={gate1.passed ? "default" : "destructive"}>
                  Gate 1 {gate1.passed ? "conforme" : "rejeté"}
                </Badge>
              ) : (
                <Badge variant="outline">Gate 1 en cours</Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground">
              {blueprint.tenant.activity_description}
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <p className="text-xs text-muted-foreground">Modules</p>
                <p className="text-sm">
                  {[...blueprint.modules.core, ...blueprint.modules.extra].join(", ")}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Rôles</p>
                <p className="text-sm">{blueprint.roles.join(", ")}</p>
              </div>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Intégrations</p>
              <ul className="mt-1 space-y-1 text-sm">
                {blueprint.integrations.map((integration) => (
                  <li key={`${integration.category}-${integration.mode}`}>
                    {integration.category} · {integration.mode} ·{" "}
                    {integration.provider_candidates.join(", ")}
                  </li>
                ))}
              </ul>
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
              Panier démo : <Money amountXof={catalogTotal} />
            </p>
            <div>
              <p className="text-xs text-muted-foreground">Actions qui resteront bloquées</p>
              <ul className="mt-1 list-disc pl-4 text-sm">
                {blueprint.requires_confirmation.map((action) => (
                  <li key={action}>{CONFIRMATION_LABELS[action] ?? action}</li>
                ))}
              </ul>
            </div>
            {gate1 && !gate1.passed ? (
              <ul className="list-disc pl-4 text-sm text-destructive">
                {gate1.errors.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : null}

            {blueprint && gate1?.passed ? (
              <div className="space-y-3 border-t border-border pt-3">
                {previewHref ? (
                  <div className="flex flex-wrap gap-2">
                    <Button asChild>
                      <Link href={previewHref}>Ouvrir la preview</Link>
                    </Button>
                    <Button asChild variant="outline">
                      <Link href={`/dashboard/${blueprint.tenant.slug}`}>Caisse</Link>
                    </Button>
                  </div>
                ) : (
                  <>
                    <label className="flex items-start gap-2 text-sm">
                      <input
                        type="checkbox"
                        className="mt-1"
                        checked={planAccepted}
                        onChange={(event) => setPlanAccepted(event.target.checked)}
                      />
                      <span>
                        J’ai lu le plan et le coût estimé. J’autorise une preview
                        sandbox, pas la production.
                      </span>
                    </label>
                    <Button onClick={approvePreview} disabled={running || !canApprove}>
                      Approuver la preview
                    </Button>
                  </>
                )}
                <p className="text-xs text-muted-foreground">
                  Gate 1 passé. L’accord explicite crée uniquement une preview.
                </p>
              </div>
            ) : null}

            <details className="text-xs">
              <summary className="cursor-pointer text-muted-foreground">
                Blueprint JSON
              </summary>
              <pre className="mt-2 max-h-64 overflow-auto rounded-lg bg-muted p-3 font-mono text-[11px] leading-relaxed">
                {JSON.stringify(blueprint, null, 2)}
              </pre>
            </details>
          </div>
        ) : null}

        <div className="rounded-xl border border-border bg-card p-4 text-card-foreground">
          <h2 className="mb-2 font-heading text-sm font-semibold">Audit trail</h2>
          {audit.length > 0 ? (
            <ol className="space-y-2">
              {audit.map((event, index) => (
                <li key={`${event.at}-${event.action}-${index}`} className="text-sm">
                  <p>
                    <time className="font-mono text-xs text-muted-foreground" dateTime={event.at}>
                      {formatAuditClock(event.at)}
                    </time>{" "}
                    <span className="font-medium">{auditAgentLabel(event.agent)}</span>
                    {" · "}
                    {auditActionLabel(event.action)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {event.result}
                    {event.model ? ` · ${event.model}` : ""}
                    {event.tokens !== undefined ? ` · ${event.tokens} tokens` : ""}
                    {event.durationMs !== undefined
                      ? ` · ${event.durationMs.toLocaleString("fr-FR")} ms`
                      : ""}
                  </p>
                </li>
              ))}
            </ol>
          ) : (
            <p className="text-sm text-muted-foreground">
              Chaque étape (prompt, plan, outil, résultat, horodatage Porto-Novo)
              s’affiche ici en direct.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
