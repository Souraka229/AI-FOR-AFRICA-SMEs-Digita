import {
  generateStructured,
  type LlmMetadata,
  type LlmModel,
} from "@afrosite/llm";
import {
  ALL_EXAMPLES,
  BlueprintDraftSchema,
  BlueprintSchema,
  COMMERCE_EXAMPLE,
  RESTAURANT_EXAMPLE,
  SERVICES_EXAMPLE,
  type Blueprint,
  type Gate1Result,
  type Intent,
} from "@afrosite/contracts";
import { detectSensitivePrompt, slugFromIntent } from "@/lib/agents/intent";

const CORE = [
  "onboarding",
  "catalog",
  "orders",
  "payments",
  "reconciliation",
  "crm",
  "dashboard",
  "notifications",
  "exports",
] as const;

const CONFIRMATIONS = [
  "production_deploy",
  "payment_live_activation",
  "database_deletion",
] as const;

const SYSTEM = [
  "Tu es le Product Architect d'Afrosite, l'AI Company Builder africain.",
  "Transforme l'intention en Blueprint concret, distinct et exploitable.",
  "Écris en français naturel pour le Bénin et propose 3 à 8 offres réalistes.",
  "Tous les prix sont des entiers FCFA plausibles. N'utilise jamais USD.",
  "Le paiement primaire est Genius Pay en sandbox derrière PaymentProvider.",
  "Ne produis ni code, ni secret, ni donnée personnelle.",
  "Le résultat doit rester dans l'un des 3 blueprints éprouvés.",
].join("\n");

function mergeMetadata(all: LlmMetadata[]): LlmMetadata {
  const last = all.at(-1);
  return {
    model: last?.model ?? "inconnu",
    inputTokens: all.reduce((sum, row) => sum + row.inputTokens, 0),
    outputTokens: all.reduce((sum, row) => sum + row.outputTokens, 0),
    totalTokens: all.reduce((sum, row) => sum + row.totalTokens, 0),
    cacheReadTokens: all.reduce((sum, row) => sum + row.cacheReadTokens, 0),
    durationMs: all.reduce((sum, row) => sum + row.durationMs, 0),
    estimatedCostUsd: all.reduce((sum, row) => sum + row.estimatedCostUsd, 0),
    estimatedCostXof: all.reduce((sum, row) => sum + row.estimatedCostXof, 0),
  };
}

function harden(draft: Blueprint, intent: Intent): Blueprint {
  const roles =
    intent.vertical === "restaurant"
      ? ["owner", "cashier", "kitchen", "customer"] as const
      : intent.vertical === "services"
        ? ["owner", "staff", "customer"] as const
        : ["owner", "cashier", "customer"] as const;
  return {
    ...draft,
    schema_version: "0.1.0",
    vertical: intent.vertical,
    country: "BJ",
    currency: "XOF",
    locale: "fr-BJ",
    tenant: {
      ...draft.tenant,
      slug: slugFromIntent({
        ...intent,
        suggested_name: draft.tenant.name || intent.suggested_name,
      }),
      city: draft.tenant.city || intent.city || "Cotonou",
      neighborhood: draft.tenant.neighborhood || intent.neighborhood,
      country: "BJ",
      activity_description: draft.tenant.activity_description || intent.activity_summary,
    },
    roles: [...roles],
    modules: {
      core: [...CORE],
      extra: draft.modules.extra,
    },
    integrations: [
      {
        category: "payment",
        mode: "sandbox",
        provider_candidates: ["geniuspay"],
      },
      ...(intent.wants_whatsapp
        ? [{
            category: "whatsapp" as const,
            mode: "sandbox" as const,
            provider_candidates: ["meta_cloud_api"],
          }]
        : []),
    ],
    deployment_target: "preview",
    estimated_cost_credits: intent.vertical === "restaurant" ? 9 : 8,
    requires_confirmation: [...CONFIRMATIONS],
    gates: {
      budget_credits_max: 20,
      contains_sensitive_data: detectSensitivePrompt(intent.raw_prompt),
    },
  };
}

export async function buildBlueprint(
  intent: Intent,
  abortSignal?: AbortSignal,
  model?: LlmModel,
): Promise<{ blueprint: Blueprint; metadata: LlmMetadata; attempts: number }> {
  const metadata: LlmMetadata[] = [];
  let feedback = "";
  let last: Blueprint | undefined;
  let lastError: unknown;

  for (let attempt = 1; attempt <= 2; attempt += 1) {
    let generated: Awaited<ReturnType<typeof generateStructured<Blueprint>>>;
    try {
      generated = await generateStructured({
        capability: "reasoning",
        schema: BlueprintDraftSchema,
        schemaName: "blueprint",
        schemaDescription: "Blueprint Afrosite v0.1.0 validé pour une TPE béninoise.",
        system: SYSTEM,
        abortSignal,
        model,
        maxRetries: 0,
        prompt: [
          `INTENTION:\n${JSON.stringify(intent)}`,
          `EXEMPLES DE FORME UNIQUEMENT:\n${JSON.stringify(ALL_EXAMPLES)}`,
          feedback,
        ].filter(Boolean).join("\n\n"),
        tags: { agent: "product_architect", vertical: intent.vertical },
      });
    } catch (error) {
      lastError = error;
      feedback = "La sortie précédente ne respectait pas le schéma JSON. Répare-la.";
      continue;
    }
    metadata.push(generated.metadata);
    last = harden(generated.output, intent);
    const gate = runGate1(last);
    if (gate.passed) {
      return { blueprint: last, metadata: mergeMetadata(metadata), attempts: attempt };
    }
    feedback = `RÉPARE CES ERREURS SANS CHANGER L'INTENTION:\n${gate.errors.join("\n")}`;
  }
  const reason = last
    ? runGate1(last).errors.join(" · ")
    : lastError instanceof Error
      ? lastError.message
      : "sortie structurée invalide";
  throw new Error(`Gate 1 impossible après 2 tentatives: ${reason}`);
}

export function runGate1(blueprint: Blueprint): Gate1Result {
  const parsed = BlueprintSchema.safeParse(blueprint);
  const errors = parsed.success
    ? []
    : parsed.error.issues.map((issue) => `${issue.path.join(".")}: ${issue.message}`);
  return {
    passed: parsed.success,
    errors,
    credits: blueprint.estimated_cost_credits,
    budget_credits_max: blueprint.gates.budget_credits_max,
  };
}

function baseFor(vertical: Intent["vertical"]): Blueprint {
  if (vertical === "restaurant") return structuredClone(RESTAURANT_EXAMPLE);
  if (vertical === "services") return structuredClone(SERVICES_EXAMPLE);
  return structuredClone(COMMERCE_EXAMPLE);
}

export function buildBlueprintBaseline(intent: Intent): Blueprint {
  return harden(baseFor(intent.vertical), intent);
}

export function exampleForSlug(slug: string): Blueprint | undefined {
  return ALL_EXAMPLES.find((item) => item.tenant.slug === slug);
}
