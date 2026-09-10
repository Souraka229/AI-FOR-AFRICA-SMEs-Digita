import { VisionCritiqueSchema, type VisionCritique } from "@afrosite/contracts";
import {
  generateStructured,
  type LlmMetadata,
  type LlmModel,
} from "@afrosite/llm";

export type VisionCriticInput = {
  desktopScreenshot: string;
  mobileScreenshot: string;
  blueprintName: string;
};

export async function critiquePreview(
  input: VisionCriticInput,
  model?: LlmModel,
): Promise<{ critique: VisionCritique; metadata: LlmMetadata }> {
  const generated = await generateStructured({
    capability: "reasoning",
    model,
    schema: VisionCritiqueSchema,
    schemaName: "vision-critique",
    schemaDescription: "Audit visuel bloquant d'une preview Afrosite.",
    system: [
      "Tu es le Vision Critic Afrosite.",
      "Évalue lisibilité, hiérarchie, contraste, débordements, mobile et confiance.",
      "Respecte une esthétique africaine contemporaine sans cliché.",
      "Une issue high ou un score sous 75 bloque la preview.",
      "Ne propose jamais de modifier le paiement ni les contrôles serveur.",
    ].join("\n"),
    prompt: `Compare les captures desktop et mobile de « ${input.blueprintName} ».`,
    images: [input.desktopScreenshot, input.mobileScreenshot],
    tags: { agent: "vision_critic" },
  });
  const critique = VisionCritiqueSchema.parse(generated.output);
  return {
    critique: {
      ...critique,
      passed:
        critique.score >= 75 &&
        !critique.issues.some((issue) => issue.severity === "high"),
    },
    metadata: generated.metadata,
  };
}
