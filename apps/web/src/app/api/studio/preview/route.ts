import { BlueprintSchema } from "@afrosite/contracts";
import { guardStudio } from "@/lib/agents/guard";
import {
  blueprintVersions,
  rollbackBlueprint,
  saveBlueprint,
} from "@/lib/demo/store";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const denied = guardStudio(request);
  if (denied) return denied;
  const body = (await request.json()) as { blueprint?: unknown };
  const parsed = BlueprintSchema.safeParse(body.blueprint);
  if (!parsed.success || parsed.data.deployment_target !== "preview") {
    return Response.json(
      { error: "Blueprint invalide ou cible autre que preview." },
      { status: 400 },
    );
  }
  saveBlueprint(parsed.data);
  return Response.json({
    href: `/t/${parsed.data.tenant.slug}`,
    slug: parsed.data.tenant.slug,
    version: blueprintVersions(parsed.data.tenant.slug)[0]?.id,
  });
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
