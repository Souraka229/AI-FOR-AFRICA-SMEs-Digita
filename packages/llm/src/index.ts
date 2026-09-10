import { createOpenAICompatible } from "@ai-sdk/openai-compatible";
import {
  Output,
  gateway,
  generateText as aiGenerateText,
  streamText as aiStreamText,
  type LanguageModel,
  type LanguageModelUsage,
  type ModelMessage,
} from "ai";
import type { ZodType } from "zod";
import {
  fallbackModelIds,
  llmBackend,
  modelId,
  type ModelCapability,
} from "./catalog";

export type LlmModel = LanguageModel;
export type { ModelCapability };
export { fallbackModelIds, llmBackend, modelId, starterCatalog } from "./catalog";

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

const USD_TO_XOF_ESTIMATE = 600;

export class LlmConfigurationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "LlmConfigurationError";
  }
}

function compatibleChat(name: string, baseURL: string, apiKey: string, id: string): LanguageModel {
  return createOpenAICompatible({ name, baseURL, apiKey }).chatModel(id);
}

function resolveModel(options: LlmCallOptions): {
  id: string;
  model: LanguageModel;
} {
  const id = modelId(options.capability);
  if (options.model) return { id: `injected:${options.capability}`, model: options.model };

  const backend = llmBackend();
  if (backend === "litellm") {
    const baseURL = process.env.LITELLM_PROXY_API_BASE;
    const apiKey = process.env.LITELLM_PROXY_API_KEY;
    if (!baseURL || !apiKey) {
      throw new LlmConfigurationError(
        "LiteLLM nécessite LITELLM_PROXY_API_BASE et LITELLM_PROXY_API_KEY.",
      );
    }
    return { id, model: compatibleChat("afrosite-litellm", baseURL, apiKey, id) };
  }

  if (backend === "openrouter") {
    const apiKey = process.env.OPENROUTER_API_KEY;
    if (!apiKey) {
      throw new LlmConfigurationError("OpenRouter nécessite OPENROUTER_API_KEY.");
    }
    const baseURL = process.env.OPENROUTER_BASE_URL || "https://openrouter.ai/api/v1";
    return {
      id,
      model: compatibleChat("afrosite-openrouter", baseURL, apiKey, id),
    };
  }

  if (!process.env.AI_GATEWAY_API_KEY && !process.env.VERCEL_OIDC_TOKEN) {
    throw new LlmConfigurationError(
      "Configurez AI_GATEWAY_API_KEY (local) ou VERCEL_OIDC_TOKEN (Vercel).",
    );
  }
  return { id, model: gateway(id) };
}

function gatewayOptions(options: LlmCallOptions) {
  if (options.model || llmBackend() !== "gateway") return {};
  const fallbacks = fallbackModelIds(options.capability);
  return {
    providerOptions: {
      gateway: {
        models: fallbacks,
        tags: [
          `capability:${options.capability}`,
          ...Object.entries(options.tags ?? {}).map(([key, value]) => `${key}:${value}`),
        ],
      },
    },
  };
}

function metadata(
  id: string,
  startedAt: number,
  usage: LanguageModelUsage,
): LlmMetadata {
  const inputTokens = usage.inputTokens ?? 0;
  const outputTokens = usage.outputTokens ?? 0;
  const estimatedCostUsd = 0;
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
    ...gatewayOptions(options),
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
    ...gatewayOptions(options),
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
    ...gatewayOptions(options),
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
