/**
 * Vision Critic sur une preview déjà servie : captures desktop + mobile,
 * critique LLM bloquante. Nécessite le serveur lancé et une clé AI Gateway.
 */
import { capturePreview } from "@/lib/agents/preview-capture";
import { critiquePreview } from "@/lib/agents/vision-critic";

const slug = process.argv[2] ?? "cadjehoun-wax";
const baseUrl = process.env.VISION_BASE_URL ?? "http://127.0.0.1:3000";

async function main() {
  const { desktopPng, mobilePng } = await capturePreview({
    href: `/t/${slug}`,
    baseUrl,
  });
  const { critique, metadata } = await critiquePreview({
    desktopScreenshot: desktopPng,
    mobileScreenshot: mobilePng,
    blueprintName: slug,
  });

  console.log(
    `${critique.passed ? "OK" : "BLOQUÉ"} · score ${critique.score}/100 · ` +
      `${metadata.model} · ${metadata.totalTokens} tokens · ` +
      `~${metadata.estimatedCostXof} FCFA`,
  );
  console.log(critique.summary);
  for (const issue of critique.issues) {
    console.log(
      `- [${issue.severity}] ${issue.component}: ${issue.description} → ${issue.suggestion}`,
    );
  }
  if (!critique.passed) process.exit(1);
}

void main();
