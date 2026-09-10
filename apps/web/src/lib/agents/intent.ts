import {
  generateStructured,
  type LlmMetadata,
  type LlmModel,
} from "@afrosite/llm";
import {
  IntentSchema,
  type Intent,
  type Vertical,
} from "@afrosite/contracts";

const RESTAURANT =
  /\b(maquis|restaurant|resto|snack|fast[\s-]?food|menu|cuisine|plat|grill|brais[eé]|poisson|kds|qr\s*menu|traiteur|p[aâ]tisserie)\b/i;
const SERVICES =
  /\b(salon|coiffure|tresse|manucure|rendez-vous|\brdv\b|devis|artisan|plombier|coutur|prestataire|locking|barbier|pressing|m[eé]canique)\b/i;
const COMMERCE =
  /\b(boutique|tissu|wax|pagne|magasin|vente|stock|[eé]picerie|quincailler|cosm[eé]tique|d[eé]p[oô]t)\b/i;
const SENSITIVE =
  /\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b|\bcvv\s*[:=]?\s*\d{3,4}\b|\b(?:sk|pk|whsec)_(?:live|sandbox)_[a-z0-9]+\b/i;
const PROMPT_INJECTION =
  /\b(?:ignore|oublie|contourne)\b.{0,40}\b(?:instructions?|règles?|syst[eè]me)\b|\b(?:system prompt|developer message|jailbreak)\b/i;

const GENERATED_INTENT_SCHEMA = IntentSchema.omit({
  raw_prompt: true,
  flags: true,
});

const NEIGHBORHOODS: { match: RegExp; name: string }[] = [
  { match: /cadj[eè]houn/i, name: "Cadjehoun" },
  { match: /fidjross[eè]/i, name: "Fidjrossè" },
  { match: /haie\s*vive/i, name: "Haie Vive" },
  { match: /akogbato/i, name: "Akogbato" },
  { match: /dantokpa|tokpa/i, name: "Dantokpa" },
  { match: /hou[eé]yiho/i, name: "Houéyiho" },
  { match: /godomey/i, name: "Godomey" },
  { match: /akpakpa/i, name: "Akpakpa" },
];

export class SensitivePromptError extends Error {
  constructor() {
    super("Le prompt contient un secret ou une donnée de paiement. Retirez-la avant de continuer.");
    this.name = "SensitivePromptError";
  }
}

export class PromptInjectionError extends Error {
  constructor() {
    super("Le prompt tente de modifier les règles du Studio.");
    this.name = "PromptInjectionError";
  }
}

export function detectSensitivePrompt(prompt: string): boolean {
  return SENSITIVE.test(prompt);
}

export function detectPromptInjection(prompt: string): boolean {
  return PROMPT_INJECTION.test(prompt);
}

export async function analyzeIntent(
  rawPrompt: string,
  abortSignal?: AbortSignal,
  model?: LlmModel,
): Promise<{ intent: Intent; metadata: LlmMetadata }> {
  const prompt = rawPrompt.trim();
  if (detectSensitivePrompt(prompt)) throw new SensitivePromptError();
  if (detectPromptInjection(prompt)) throw new PromptInjectionError();

  const result = await generateStructured({
    capability: "light",
    schema: GENERATED_INTENT_SCHEMA,
    schemaName: "intent",
    schemaDescription: "Besoin normalisé d'une TPE béninoise.",
    system: [
      "Tu es l'Intent Agent Afrosite.",
      "Comprends le besoin en français d'une TPE du Bénin.",
      "Choisis exactement un vertical: commerce, restaurant ou services.",
      "N'invente pas de donnée personnelle ni de secret.",
      "Cotonou est la ville par défaut si elle n'est pas précisée.",
      "Le Mobile Money est natif. Réponds uniquement selon le schéma.",
    ].join("\n"),
    prompt,
    abortSignal,
    model,
    tags: { agent: "intent" },
  });
  return {
    intent: IntentSchema.parse({
      ...result.output,
      raw_prompt: prompt,
      flags: ["payment_native"],
      wants_mobile_money: true,
    }),
    metadata: result.metadata,
  };
}

function pickVertical(prompt: string): { vertical: Vertical; confidence: number } {
  const restaurant = RESTAURANT.test(prompt);
  const services = SERVICES.test(prompt);
  const commerce = COMMERCE.test(prompt);
  if (restaurant && !services && !commerce) return { vertical: "restaurant", confidence: 0.86 };
  if (services && !restaurant && !commerce) return { vertical: "services", confidence: 0.84 };
  if (commerce && !restaurant && !services) return { vertical: "commerce", confidence: 0.88 };
  if (restaurant && commerce) return { vertical: "restaurant", confidence: 0.62 };
  if (services) return { vertical: "services", confidence: 0.6 };
  if (restaurant) return { vertical: "restaurant", confidence: 0.7 };
  return { vertical: "commerce", confidence: 0.55 };
}

function pickPlace(prompt: string): { city: string; neighborhood: string } {
  for (const neighborhood of NEIGHBORHOODS) {
    if (neighborhood.match.test(prompt)) {
      return { city: "Cotonou", neighborhood: neighborhood.name };
    }
  }
  return { city: "Cotonou", neighborhood: "Cadjehoun" };
}

export function analyzeIntentBaseline(rawPrompt: string): Intent {
  const prompt = rawPrompt.trim();
  const { vertical, confidence } = pickVertical(prompt);
  const { city, neighborhood } = pickPlace(prompt);
  const suggestedName =
    vertical === "restaurant"
      ? `Maquis ${neighborhood}`
      : vertical === "services"
        ? `Salon ${neighborhood}`
        : /wax|tissu|pagne/i.test(prompt)
          ? `Wax ${neighborhood}`
          : `Boutique ${neighborhood}`;
  return IntentSchema.parse({
    raw_prompt: prompt,
    vertical,
    confidence,
    city,
    neighborhood,
    wants_mobile_money: true,
    wants_delivery: /livr/i.test(prompt),
    wants_whatsapp: /whats?app/i.test(prompt) || vertical !== "restaurant",
    activity_summary: prompt.slice(0, 220),
    suggested_name: suggestedName,
    flags: detectSensitivePrompt(prompt) ? ["sensitive_data", "payment_native"] : ["payment_native"],
  });
}

function slugPart(value: string): string {
  return value
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 40);
}

export function slugFromIntent(intent: Intent): string {
  if (
    intent.vertical === "commerce" &&
    /wax|tissu|pagne/i.test(intent.raw_prompt) &&
    /cadjehoun/i.test(intent.neighborhood)
  ) {
    return "cadjehoun-wax";
  }
  return slugPart(intent.suggested_name);
}
