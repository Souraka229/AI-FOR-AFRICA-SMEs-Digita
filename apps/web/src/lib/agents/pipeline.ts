import { createHash } from "node:crypto";
import type {
  Blueprint,
  Gate1Result,
  Intent,
} from "@afrosite/contracts";
import type { LlmMetadata, LlmModel } from "@afrosite/llm";
import {
  analyzeIntent,
  analyzeIntentBaseline,
} from "@/lib/agents/intent";
import {
  buildBlueprint,
  buildBlueprintBaseline,
  runGate1,
} from "@/lib/agents/architect";
import { recordCost } from "@/lib/demo/store";
import type { AuditEvent } from "@/lib/agents/audit";

export type { AuditEvent } from "@/lib/agents/audit";

export type PipelineStepId = "intent" | "architect" | "gate1" | "preview";
export type PipelineStepStatus = "running" | "done" | "blocked";

export type PipelineResult = {
  runId: string;
  promptHash: string;
  intent: Intent;
  blueprint: Blueprint;
  gate1: Gate1Result;
  audit: AuditEvent[];
  usage: {
    inputTokens: number;
    outputTokens: number;
    totalTokens: number;
    cacheReadTokens: number;
    durationMs: number;
    estimatedCostUsd: number;
    estimatedCostXof: number;
  };
};

export type StepEvent = {
  id: PipelineStepId;
  status: PipelineStepStatus;
  data?: unknown;
};

type RunOptions = {
  persistCost?: boolean;
  onStep?: (event: StepEvent) => void | Promise<void>;
  onAudit?: (event: AuditEvent) => void | Promise<void>;
  abortSignal?: AbortSignal;
  models?: {
    intent?: LlmModel;
    architect?: LlmModel;
  };
};

function promptHash(prompt: string): string {
  return createHash("sha256").update(prompt).digest("hex");
}

function usageOf(rows: LlmMetadata[]) {
  return {
    inputTokens: rows.reduce((sum, row) => sum + row.inputTokens, 0),
    outputTokens: rows.reduce((sum, row) => sum + row.outputTokens, 0),
    totalTokens: rows.reduce((sum, row) => sum + row.totalTokens, 0),
    cacheReadTokens: rows.reduce((sum, row) => sum + row.cacheReadTokens, 0),
    durationMs: rows.reduce((sum, row) => sum + row.durationMs, 0),
    estimatedCostUsd: rows.reduce((sum, row) => sum + row.estimatedCostUsd, 0),
    estimatedCostXof: rows.reduce((sum, row) => sum + row.estimatedCostXof, 0),
  };
}

export async function runPipeline(
  prompt: string,
  options: RunOptions = {},
): Promise<PipelineResult> {
  const runId = crypto.randomUUID();
  const hash = promptHash(prompt);
  const audit: AuditEvent[] = [];
  const stamp = (
    agent: string,
    action: string,
    result: string,
    metadata?: LlmMetadata,
  ) => {
    const event: AuditEvent = {
      at: new Date().toISOString(),
      agent,
      action,
      result,
      model: metadata?.model,
      tokens: metadata?.totalTokens,
      cacheReadTokens: metadata?.cacheReadTokens,
      durationMs: metadata?.durationMs,
      estimatedCostXof: metadata?.estimatedCostXof,
    };
    audit.push(event);
    void options.onAudit?.(event);
  };
  const step = async (event: StepEvent) => options.onStep?.(event);

  await step({ id: "intent", status: "running" });
  stamp("intent", "normalize_prompt", "démarré");
  const analyzed = await analyzeIntent(
    prompt,
    options.abortSignal,
    options.models?.intent,
  );
  const intent = analyzed.intent;
  stamp(
    "intent",
    "normalize_prompt",
    `${intent.vertical} · ${intent.neighborhood} · confiance ${Math.round(intent.confidence * 100)} %`,
    analyzed.metadata,
  );
  await step({ id: "intent", status: "done", data: intent });

  await step({ id: "architect", status: "running" });
  stamp("product_architect", "build_blueprint", "démarré");
  const built = await buildBlueprint(
    intent,
    options.abortSignal,
    options.models?.architect,
  );
  const blueprint = built.blueprint;
  stamp(
    "product_architect",
    "build_blueprint",
    `${blueprint.tenant.slug} · ${blueprint.catalog.length} offres · ${built.attempts} tentative(s)`,
    built.metadata,
  );
  await step({
    id: "architect",
    status: "done",
    data: {
      slug: blueprint.tenant.slug,
      attempts: built.attempts,
      blueprint,
    },
  });

  await step({ id: "gate1", status: "running" });
  const gate1 = runGate1(blueprint);
  stamp(
    "gate1",
    "validate_schema",
    gate1.passed ? "schéma conforme, budget sous plafond" : gate1.errors.join(" · "),
  );
  await step({
    id: "gate1",
    status: gate1.passed ? "done" : "blocked",
    data: gate1,
  });

  const usage = usageOf([analyzed.metadata, built.metadata]);
  if (options.persistCost !== false) {
    recordCost({
      tenantSlug: blueprint.tenant.slug,
      runId,
      promptHash: hash,
      agent: "pipeline",
      action: "prompt_to_blueprint",
      credits: blueprint.estimated_cost_credits,
      model: built.metadata.model,
      inputTokens: usage.inputTokens,
      outputTokens: usage.outputTokens,
      cacheReadTokens: usage.cacheReadTokens,
      durationMs: usage.durationMs,
      estimatedCostUsd: usage.estimatedCostUsd,
      estimatedCostXof: usage.estimatedCostXof,
    });
  }

  return {
    runId,
    promptHash: hash,
    intent,
    blueprint,
    gate1,
    audit,
    usage,
  };
}

export function runBaselinePipeline(
  prompt: string,
): Pick<PipelineResult, "intent" | "blueprint" | "gate1"> {
  const intent = analyzeIntentBaseline(prompt);
  const blueprint = buildBlueprintBaseline(intent);
  return { intent, blueprint, gate1: runGate1(blueprint) };
}
