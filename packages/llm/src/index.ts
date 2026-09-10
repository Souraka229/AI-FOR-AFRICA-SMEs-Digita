import { createOpenAICompatible } from "@ai-sdk/openai-compatible";
import {
  Output,
  generateText as aiGenerateText,
  streamText as aiStreamText,
  type LanguageModel,
  type LanguageModelUsage,
  type ModelMessage,
} from "ai";
import type { ZodType } from "zod";

export type LlmModel = LanguageModel;
export type ModelCapability = "light" | "reasoning" | "code";

export type LlmMetadata = {
  model: string;
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  cacheReadTokens: number;
  durationMs: number;
  estimatedCostUsd: number;
  estimatedCostXof: number;
};

export type StructuredResult<T> = {
  output: T;
  metadata: LlmMetadata;
};

export type TextResult = {
  text: string;
  metadata: LlmMetadata;
};

export type LlmCallOptions = {
  capability: ModelCapability;
  system: string;
  prompt: string;
  abortSignal?: AbortSignal;
  maxRetries?: number;
  model?: LanguageModel;
  tags?: Record<string, string>;
};

export type StructuredCallOptions<T> = LlmCallOptions & {
  schema: ZodType<T>;
  schemaName: string;
  schemaDescription?: string;
  images?: string[];
};

const DEFAULT_MODELS: Record<ModelCapability, string> = {
  light: "openai/gpt-5.6-luna",
  reasoning: "anthropic/claude-sonnet-5",
  code: "openai/gpt-6-astra",
};

const PRICE_USD_PER_MILLION: Record<string, { input: number; output: number }> = {
  "openai/gpt-5.6-luna": { input: 0.2, output: 1.2 },
  "anthropic/claude-sonnet-5": { input: 2, output: 10 },
  "openai/gpt-6-astra": { input: 10, output: 50 },
};
const USD_TO_XOF_ESTIMATE = 600;

export class LlmConfigurationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "LlmConfigurationError";
  }
}

export function modelId(capability: ModelCapability): string {
  const key = `AFROSITE_LLM_MODEL_${capability.toUpperCase()}`;
  return process.env[key] || DEFAULT_MODELS[capability];
}

function resolveModel(options: LlmCallOptions): {
  id: string;
  model: LanguageModel;
} {
  const id = modelId(options.capability);
  if (options.model) return { id: `injected:${options.capability}`, model: options.model };

  if (process.env.AFROSITE_LLM_BACKEND === "litellm") {
    const baseURL = process.env.LITELLM_PROXY_API_BASE;
    const apiKey = process.env.LITELLM_PROXY_API_KEY;
    if (!baseURL || !apiKey) {
      throw new LlmConfigurationError(
        "LiteLLM nécessite LITELLM_PROXY_API_BASE et LITELLM_PROXY_API_KEY.",
      );
    }
    const provider = createOpenAICompatible({
      name: "afrosite-litellm",
      baseURL,
      apiKey,
    });
    return { id, model: provider.chatModel(id) };
  }

  if (!process.env.AI_GATEWAY_API_KEY && !process.env.VERCEL_OIDC_TOKEN) {
    throw new LlmConfigurationError(
      "Configurez AI_GATEWAY_API_KEY (local) ou VERCEL_OIDC_TOKEN (Vercel).",
    );
  }
  return { id, model: id };
}

function metadata(
  id: string,
  startedAt: number,
  usage: LanguageModelUsage,
): LlmMetadata {
  const inputTokens = usage.inputTokens ?? 0;
  const outputTokens = usage.outputTokens ?? 0;
  const price = PRICE_USD_PER_MILLION[id];
  const estimatedCostUsd = price
    ? (inputTokens * price.input + outputTokens * price.output) / 1_000_000
    : 0;
  return {
    model: id,
    inputTokens,
    outputTokens,
    totalTokens: usage.totalTokens ?? inputTokens + outputTokens,
    cacheReadTokens: usage.inputTokenDetails.cacheReadTokens ?? 0,
    durationMs: Date.now() - startedAt,
    estimatedCostUsd,
    estimatedCostXof: Math.ceil(estimatedCostUsd * USD_TO_XOF_ESTIMATE),
  };
}

function promptInput(options: { prompt: string; images?: string[] }):
  | { prompt: string }
  | { messages: ModelMessage[] } {
  if (!options.images?.length) return { prompt: options.prompt };
  return {
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: options.prompt },
          ...options.images.map((image) => ({ type: "image" as const, image })),
        ],
      },
    ],
  };
}

export async function generateStructured<T>(
  options: StructuredCallOptions<T>,
): Promise<StructuredResult<T>> {
  const startedAt = Date.now();
  const resolved = resolveModel(options);
  const result = await aiGenerateText({
    model: resolved.model,
    system: options.system,
    ...promptInput(options),
    output: Output.object({
      schema: options.schema,
      name: options.schemaName,
      description: options.schemaDescription,
    }),
    abortSignal: options.abortSignal,
    maxRetries: options.maxRetries ?? 1,
    experimental_telemetry: {
      isEnabled: true,
      functionId: `afrosite.${options.schemaName}`,
      metadata: options.tags,
    },
  });
  return {
    output: result.output,
    metadata: metadata(resolved.id, startedAt, result.usage),
  };
}

export function streamStructured<T>(options: StructuredCallOptions<T>) {
  const startedAt = Date.now();
  const resolved = resolveModel(options);
  const result = aiStreamText({
    model: resolved.model,
    system: options.system,
    ...promptInput(options),
    output: Output.object({
      schema: options.schema,
      name: options.schemaName,
      description: options.schemaDescription,
    }),
    abortSignal: options.abortSignal,
    maxRetries: options.maxRetries ?? 1,
    experimental_telemetry: {
      isEnabled: true,
      functionId: `afrosite.${options.schemaName}`,
      metadata: options.tags,
    },
  });
  return {
    partialOutputStream: result.partialOutputStream,
    output: result.output,
    metadata: result.usage.then((usage) =>
      metadata(resolved.id, startedAt, usage),
    ),
  };
}

export async function generateText(options: LlmCallOptions): Promise<TextResult> {
  const startedAt = Date.now();
  const resolved = resolveModel(options);
  const result = await aiGenerateText({
    model: resolved.model,
    system: options.system,
    prompt: options.prompt,
    abortSignal: options.abortSignal,
    maxRetries: options.maxRetries ?? 1,
    experimental_telemetry: {
      isEnabled: true,
      functionId: "afrosite.text",
      metadata: options.tags,
    },
  });
  return {
    text: result.text,
    metadata: metadata(resolved.id, startedAt, result.usage),
  };
}
