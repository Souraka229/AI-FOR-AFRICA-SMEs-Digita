export type ModelCapability = "light" | "reasoning" | "code";
export type LlmBackend = "gateway" | "litellm" | "openrouter";

/**
 * Alias de démarrage — format `fournisseur/modèle` (docs AI Gateway).
 * La liste live se confirme avec `pnpm --filter @afrosite/llm discover`
 * dès qu’une clé Gateway / OIDC est disponible. On n’invente pas d’alias.
 */
const STARTER_MODELS: Record<ModelCapability, string> = {
  light: "anthropic/claude-haiku-4.5",
  reasoning: "anthropic/claude-sonnet-4.6",
  code: "openai/gpt-5.4",
};

const STARTER_FALLBACKS: Record<ModelCapability, string[]> = {
  light: ["google/gemini-3-flash", "openai/gpt-5.4"],
  reasoning: ["openai/gpt-5.4", "google/gemini-3-flash"],
  code: ["anthropic/claude-sonnet-4.6"],
};

export function llmBackend(): LlmBackend {
  const raw = (process.env.AFROSITE_LLM_BACKEND ?? "gateway").trim().toLowerCase();
  if (raw === "litellm" || raw === "openrouter") return raw;
  return "gateway";
}

export function assertModelId(id: string): string {
  if (!id.includes("/") || id.includes(" ")) {
    throw new Error(`Alias modèle invalide (attendu fournisseur/modèle) : ${id}`);
  }
  return id;
}

export function modelId(capability: ModelCapability): string {
  const key = `AFROSITE_LLM_MODEL_${capability.toUpperCase()}`;
  return assertModelId(process.env[key] || STARTER_MODELS[capability]);
}

export function fallbackModelIds(capability: ModelCapability): string[] {
  const key = `AFROSITE_LLM_FALLBACK_${capability.toUpperCase()}`;
  const raw = process.env[key];
  const listed = raw
    ? raw
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean)
    : STARTER_FALLBACKS[capability];
  return listed.map(assertModelId).filter((id) => id !== modelId(capability));
}

export function starterCatalog(): Record<ModelCapability, { primary: string; fallbacks: string[] }> {
  return {
    light: { primary: modelId("light"), fallbacks: fallbackModelIds("light") },
    reasoning: { primary: modelId("reasoning"), fallbacks: fallbackModelIds("reasoning") },
    code: { primary: modelId("code"), fallbacks: fallbackModelIds("code") },
  };
}
