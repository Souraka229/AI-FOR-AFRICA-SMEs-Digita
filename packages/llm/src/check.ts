import { simulateReadableStream } from "ai";
import { MockLanguageModelV3 } from "ai/test";
import { z } from "zod";
import {
  LlmConfigurationError,
  fallbackModelIds,
  generateStructured,
  llmBackend,
  modelId,
  starterCatalog,
  streamStructured,
} from "./index";

const model = new MockLanguageModelV3({
  doGenerate: async () => ({
    content: [{ type: "text", text: '{"vertical":"commerce"}' }],
    finishReason: { unified: "stop", raw: undefined },
    usage: {
      inputTokens: {
        total: 10,
        noCache: 8,
        cacheRead: 2,
        cacheWrite: undefined,
      },
      outputTokens: {
        total: 4,
        text: 4,
        reasoning: undefined,
      },
    },
    warnings: [],
  }),
});

const result = await generateStructured({
  capability: "light",
  model,
  schemaName: "intent-check",
  schema: z.object({ vertical: z.literal("commerce") }),
  system: "Test.",
  prompt: "Boutique.",
});

if (result.output.vertical !== "commerce") throw new Error("Sortie structurée invalide.");
if (result.metadata.totalTokens !== 14) throw new Error("Comptage tokens invalide.");
if (result.metadata.cacheReadTokens !== 2) throw new Error("Cache non mesuré.");
if (!modelId("reasoning").includes("/")) throw new Error("Alias modèle invalide.");
if (modelId("light") !== "anthropic/claude-haiku-4.5") {
  throw new Error("Le modèle light de démarrage a changé sans mise à jour du check.");
}
if (fallbackModelIds("light").length === 0) {
  throw new Error("Aucun fallback light configuré.");
}
if (llmBackend() !== "gateway") throw new Error("Backend par défaut attendu : gateway.");
if (!starterCatalog().code.primary.includes("/")) {
  throw new Error("Catalogue code invalide.");
}

const previousBackend = process.env.AFROSITE_LLM_BACKEND;
process.env.AFROSITE_LLM_BACKEND = "openrouter";
delete process.env.OPENROUTER_API_KEY;
try {
  await generateStructured({
    capability: "light",
    schemaName: "intent-openrouter",
    schema: z.object({ vertical: z.literal("commerce") }),
    system: "Test.",
    prompt: "Boutique.",
  });
  throw new Error("OpenRouter sans clé doit échouer.");
} catch (error) {
  if (!(error instanceof LlmConfigurationError)) throw error;
} finally {
  if (previousBackend) process.env.AFROSITE_LLM_BACKEND = previousBackend;
  else delete process.env.AFROSITE_LLM_BACKEND;
}

const streamingModel = new MockLanguageModelV3({
  doStream: async () => ({
    stream: simulateReadableStream({
      chunks: [
        { type: "stream-start", warnings: [] },
        { type: "text-start", id: "0" },
        { type: "text-delta", id: "0", delta: '{"vertical":' },
        { type: "text-delta", id: "0", delta: '"commerce"}' },
        { type: "text-end", id: "0" },
        {
          type: "finish",
          finishReason: { unified: "stop", raw: undefined },
          usage: {
            inputTokens: {
              total: 6,
              noCache: 5,
              cacheRead: 1,
              cacheWrite: undefined,
            },
            outputTokens: { total: 3, text: 3, reasoning: undefined },
          },
        },
      ],
      chunkDelayInMs: 0,
      initialDelayInMs: 0,
    }),
  }),
});

const streamed = streamStructured({
  capability: "light",
  model: streamingModel,
  schemaName: "intent-stream",
  schema: z.object({ vertical: z.literal("commerce") }),
  system: "Test.",
  prompt: "Boutique.",
});

let partials = 0;
for await (const _partial of streamed.partialOutputStream) partials += 1;
const streamedOutput = await streamed.output;
const streamedMetadata = await streamed.metadata;
if (partials === 0) throw new Error("Aucun objet partiel streamé.");
if (streamedOutput.vertical !== "commerce") {
  throw new Error("Sortie streamée invalide.");
}
if (streamedMetadata.cacheReadTokens !== 1) {
  throw new Error("Cache non mesuré en streaming.");
}

const backend = process.env.AFROSITE_LLM_BACKEND;
const gatewayKey = process.env.AI_GATEWAY_API_KEY;
const oidcToken = process.env.VERCEL_OIDC_TOKEN;
delete process.env.AFROSITE_LLM_BACKEND;
delete process.env.AI_GATEWAY_API_KEY;
delete process.env.VERCEL_OIDC_TOKEN;
try {
  await generateStructured({
    capability: "light",
    schemaName: "intent-unconfigured",
    schema: z.object({ vertical: z.literal("commerce") }),
    system: "Test.",
    prompt: "Boutique.",
  });
  throw new Error("Un appel sans configuration LLM doit échouer.");
} catch (error) {
  if (!(error instanceof LlmConfigurationError)) throw error;
} finally {
  if (backend) process.env.AFROSITE_LLM_BACKEND = backend;
  if (gatewayKey) process.env.AI_GATEWAY_API_KEY = gatewayKey;
  if (oidcToken) process.env.VERCEL_OIDC_TOKEN = oidcToken;
}

console.log(
  "check:llm OK · sortie structurée · streaming · tokens · cache · alias · échec explicite sans clé",
);
