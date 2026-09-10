import { BlueprintSchema } from "@afrosite/contracts";
import { guardStudio } from "@/lib/agents/guard";
import {
  maybeCapturePreview,
  resolveCaptureBaseUrl,
  shouldSkipPreviewCapture,
  type PreviewCapturer,
} from "@/lib/agents/preview-capture";
import {
  blueprintVersions,
  rollbackBlueprint,
  saveBlueprint,
} from "@/lib/demo/store";

export const runtime = "nodejs";

type PreviewBody = {
  blueprint?: unknown;
  capture?: boolean;
  skipCapture?: boolean;
};

export async function POST(request: Request) {
  const denied = guardStudio(request);
  if (denied) return denied;
  const body = (await request.json()) as PreviewBody;
  const parsed = BlueprintSchema.safeParse(body.blueprint);
  if (!parsed.success || parsed.data.deployment_target !== "preview") {
    return Response.json(
      { error: "Blueprint invalide ou cible autre que preview." },
      { status: 400 },
    );
  }

  const href = `/t/${parsed.data.tenant.slug}`;
  const skip = shouldSkipPreviewCapture({
    capture: body.capture,
    skipCapture: body.skipCapture,
  });
  if (!skip) {
    try {
      resolveCaptureBaseUrl();
    } catch (error) {
      return Response.json(
        {
          error:
            error instanceof Error
              ? error.message
              : "Capture refusée hors preview locale.",
        },
        { status: 400 },
      );
    }
  }

  saveBlueprint(parsed.data);
  const captured = await maybeCapturePreview({
    href,
    capture: body.capture,
    skipCapture: body.skipCapture,
    capturer: previewCapturerFromEnv(),
  });

  return Response.json({
    href,
    slug: parsed.data.tenant.slug,
    version: blueprintVersions(parsed.data.tenant.slug)[0]?.id,
    ...captured,
  });
}

function previewCapturerFromEnv(): PreviewCapturer | undefined {
  if (process.env.AFROSITE_PREVIEW_CAPTURE_MOCK === "1") {
    const png = "data:image/png;base64,iVBORw0KGgo=";
    return async () => ({ desktopPng: png, mobilePng: png });
  }
  return undefined;
}

export async function GET(request: Request) {
  const denied = guardStudio(request);
  if (denied) return denied;
  const slug = new URL(request.url).searchParams.get("slug") ?? "";
  return Response.json({
    versions: blueprintVersions(slug).map(({ id, at, blueprint }) => ({
      id,
      at,
      name: blueprint.tenant.name,
    })),
  });
}

export async function DELETE(request: Request) {
  const denied = guardStudio(request);
  if (denied) return denied;
  const body = (await request.json()) as { slug?: string; versionId?: string };
  if (!body.slug || !body.versionId) {
    return Response.json({ error: "slug et versionId requis." }, { status: 400 });
  }
  try {
    const blueprint = rollbackBlueprint(body.slug, body.versionId);
    return Response.json({ href: `/t/${blueprint.tenant.slug}` });
  } catch (error) {
    return Response.json(
      { error: error instanceof Error ? error.message : "Rollback impossible." },
      { status: 404 },
    );
  }
}
