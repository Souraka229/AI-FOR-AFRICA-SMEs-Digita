/**
 * Vision Critic sur une preview déjà servie : captures desktop + mobile,
 * critique LLM bloquante. Nécessite le serveur lancé et une clé AI Gateway.
 */
import { chromium, devices } from "@playwright/test";
import { critiquePreview } from "@/lib/agents/vision-critic";

const slug = process.argv[2] ?? "cadjehoun-wax";
const baseUrl = process.env.VISION_BASE_URL ?? "http://127.0.0.1:3000";

async function capture(url: string, mobile: boolean): Promise<string> {
  const browser = await chromium.launch();
  try {
    const context = await browser.newContext(
      mobile ? devices["Pixel 7"] : { viewport: { width: 1280, height: 800 } },
    );
    const page = await context.newPage();
    await page.goto(url, { waitUntil: "networkidle" });
    const buffer = await page.screenshot({ fullPage: true });
    return `data:image/png;base64,${buffer.toString("base64")}`;
  } finally {
    await browser.close();
  }
}

async function main() {
  const url = `${baseUrl}/t/${slug}`;
  const [desktopScreenshot, mobileScreenshot] = await Promise.all([
    capture(url, false),
    capture(url, true),
  ]);
  const { critique, metadata } = await critiquePreview({
    desktopScreenshot,
    mobileScreenshot,
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
