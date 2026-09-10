import {
  PreviewCaptureError,
  capturePreview,
  maybeCapturePreview,
  resolveCaptureBaseUrl,
  resolvePreviewPageUrl,
  shouldSkipPreviewCapture,
} from "@/lib/agents/preview-capture";

const MOCK_PNG = "data:image/png;base64,iVBORw0KGgo=";

async function expectThrow(run: () => unknown, fragment: string) {
  try {
    await run();
  } catch (error) {
    if (error instanceof PreviewCaptureError && error.message.includes(fragment)) {
      return;
    }
    throw error instanceof Error
      ? error
      : new Error("échec inattendu de la capture");
  }
  throw new Error(`Attendu un refus contenant « ${fragment} ».`);
}

async function main() {
  if (resolvePreviewPageUrl("/t/cadjehoun-wax", "http://127.0.0.1:3000") !== "http://127.0.0.1:3000/t/cadjehoun-wax") {
    throw new Error("URL sandbox locale mal construite.");
  }
  if (resolveCaptureBaseUrl(undefined, { APP_URL: "http://localhost:3000" }) !== "http://localhost:3000") {
    throw new Error("APP_URL locale non acceptée.");
  }

  await expectThrow(() => resolvePreviewPageUrl("/studio", "http://127.0.0.1:3000"), "/t/");
  await expectThrow(() => resolvePreviewPageUrl("https://evil.example/t/x", "http://127.0.0.1:3000"), "/t/");
  await expectThrow(
    () => resolveCaptureBaseUrl("https://afrosite.example"),
    "preview locale",
  );
  await expectThrow(
    () => resolveCaptureBaseUrl("http://preview.vercel.app"),
    "preview locale",
  );

  const captured = await capturePreview({
    href: "/t/cadjehoun-wax",
    baseUrl: "http://127.0.0.1:3000",
    capturer: async () => ({ desktopPng: MOCK_PNG, mobilePng: MOCK_PNG }),
  });
  if (captured.desktopPng !== MOCK_PNG || captured.mobilePng !== MOCK_PNG) {
    throw new Error("Capture mockée non renvoyée.");
  }

  if (!shouldSkipPreviewCapture({})) {
    throw new Error("Sans capture:true la capture doit être sautée.");
  }
  if (!shouldSkipPreviewCapture({ capture: true, skipCapture: true })) {
    throw new Error("skipCapture doit primer.");
  }
  if (
    !shouldSkipPreviewCapture({
      capture: true,
      env: { AFROSITE_SKIP_PREVIEW_CAPTURE: "1" },
    })
  ) {
    throw new Error("AFROSITE_SKIP_PREVIEW_CAPTURE=1 doit sauter Chromium.");
  }

  const skipped = await maybeCapturePreview({ href: "/t/cadjehoun-wax" });
  if (skipped.captures) {
    throw new Error("Capture lancée alors qu'elle devait être sautée.");
  }

  const requested = await maybeCapturePreview({
    href: "/t/cadjehoun-wax",
    capture: true,
    capturer: async () => ({ desktopPng: MOCK_PNG, mobilePng: MOCK_PNG }),
  });
  if (requested.captures?.desktop !== MOCK_PNG) {
    throw new Error("maybeCapturePreview n'a pas renvoyé les PNG mockés.");
  }

  const failed = await maybeCapturePreview({
    href: "/t/cadjehoun-wax",
    capture: true,
    capturer: async () => {
      throw new PreviewCaptureError("navigateur absent");
    },
  });
  if (!failed.captureError?.includes("navigateur absent") || failed.captures) {
    throw new Error("Échec de capture mal exposé.");
  }

  console.log(
    "Eval capture preview : sandbox /t/ · refus prod · mock PNG · skip CI OK",
  );
}

void main();
