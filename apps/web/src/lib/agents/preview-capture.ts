/**
 * Capture desktop + mobile d'une preview sandbox `/t/{slug}`.
 * Jamais une URL de production. Le Vision Critic consomme le résultat ; cette
 * couche ne parle pas au LLM.
 */

const PREVIEW_HREF = /^\/t\/[a-z0-9]+(?:-[a-z0-9]+)*$/;
const GOTO_TIMEOUT_MS = 15_000;
const DEFAULT_LOCAL_BASE = "http://127.0.0.1:3000";

type Env = Record<string, string | undefined>;

export type PreviewCaptureResult = {
  desktopPng: string;
  mobilePng: string;
};

export type PreviewCapturer = (input: {
  href: string;
  baseUrl: string;
}) => Promise<PreviewCaptureResult>;

export class PreviewCaptureError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "PreviewCaptureError";
  }
}

export function isPreviewTenantHref(href: string): boolean {
  return PREVIEW_HREF.test(href);
}

export function resolveCaptureBaseUrl(
  override?: string,
  env: Env = process.env,
): string {
  const raw = (override ?? env.VISION_BASE_URL ?? env.APP_URL ?? DEFAULT_LOCAL_BASE).trim();
  if (!raw) {
    throw new PreviewCaptureError("Base URL de capture absente.");
  }
  let parsed: URL;
  try {
    parsed = new URL(raw);
  } catch {
    throw new PreviewCaptureError("Base URL de capture invalide.");
  }
  const host = parsed.hostname.replace(/^\[|\]$/g, "");
  const loopback = host === "127.0.0.1" || host === "localhost" || host === "::1";
  if (parsed.protocol !== "http:" || !loopback) {
    throw new PreviewCaptureError(
      "Capture refusée : seule une preview locale (http://127.0.0.1 ou localhost) est autorisée.",
    );
  }
  return parsed.origin;
}

export function resolvePreviewPageUrl(href: string, baseUrl: string): string {
  if (!isPreviewTenantHref(href)) {
    throw new PreviewCaptureError("Capture refusée : l’URL doit être un href sandbox /t/{slug}.");
  }
  const origin = resolveCaptureBaseUrl(baseUrl);
  return `${origin}${href}`;
}

export function shouldSkipPreviewCapture(input: {
  capture?: boolean;
  skipCapture?: boolean;
  env?: Env;
}): boolean {
  const env = input.env ?? process.env;
  if (input.skipCapture === true) return true;
  if (env.AFROSITE_SKIP_PREVIEW_CAPTURE === "1") return true;
  return input.capture !== true;
}

export async function capturePreview(
  input: {
    href: string;
    baseUrl?: string;
    capturer?: PreviewCapturer;
  },
): Promise<PreviewCaptureResult> {
  const baseUrl = resolveCaptureBaseUrl(input.baseUrl);
  resolvePreviewPageUrl(input.href, baseUrl);
  const capturer = input.capturer ?? capturePreviewWithPlaywright;
  const result = await capturer({ href: input.href, baseUrl });
  if (!result.desktopPng.startsWith("data:image/png") || !result.mobilePng.startsWith("data:image/png")) {
    throw new PreviewCaptureError("Captures desktop/mobile attendues en data URL PNG.");
  }
  return result;
}

export async function maybeCapturePreview(input: {
  href: string;
  capture?: boolean;
  skipCapture?: boolean;
  baseUrl?: string;
  capturer?: PreviewCapturer;
  env?: Env;
}): Promise<{
  captures?: { desktop: string; mobile: string };
  captureError?: string;
}> {
  if (shouldSkipPreviewCapture(input)) {
    return {};
  }
  try {
    const result = await capturePreview({
      href: input.href,
      baseUrl: input.baseUrl,
      capturer: input.capturer,
    });
    return {
      captures: {
        desktop: result.desktopPng,
        mobile: result.mobilePng,
      },
    };
  } catch (error) {
    return {
      captureError:
        error instanceof Error ? error.message : "Capture preview impossible.",
    };
  }
}

export async function capturePreviewWithPlaywright(input: {
  href: string;
  baseUrl: string;
}): Promise<PreviewCaptureResult> {
  const pageUrl = resolvePreviewPageUrl(input.href, input.baseUrl);
  const { chromium, devices } = await import("@playwright/test");
  const browser = await chromium.launch();
  try {
    const desktopPng = await screenshotPage(browser, pageUrl, devices, false);
    const mobilePng = await screenshotPage(browser, pageUrl, devices, true);
    return { desktopPng, mobilePng };
  } finally {
    await browser.close();
  }
}

async function screenshotPage(
  browser: {
    newContext: (options?: object) => Promise<{
      newPage: () => Promise<{
        goto: (
          url: string,
          options?: { waitUntil?: "networkidle"; timeout?: number },
        ) => Promise<unknown>;
        screenshot: (options?: {
          fullPage?: boolean;
          timeout?: number;
        }) => Promise<Buffer>;
      }>;
      close: () => Promise<void>;
    }>;
  },
  pageUrl: string,
  devices: Record<string, object>,
  mobile: boolean,
): Promise<string> {
  const context = await browser.newContext(
    mobile ? devices["Pixel 7"] : { viewport: { width: 1280, height: 800 } },
  );
  try {
    const page = await context.newPage();
    await page.goto(pageUrl, {
      waitUntil: "networkidle",
      timeout: GOTO_TIMEOUT_MS,
    });
    const buffer = await page.screenshot({ fullPage: true, timeout: GOTO_TIMEOUT_MS });
    return `data:image/png;base64,${buffer.toString("base64")}`;
  } finally {
    await context.close();
  }
}
