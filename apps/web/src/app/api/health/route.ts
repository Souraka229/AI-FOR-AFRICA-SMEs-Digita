import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export function GET() {
  const environment = process.env.AFROSITE_ENV ?? "development";
  const apiConfigured = Boolean(process.env.AFROSITE_API_URL);
  const studioConfigured = Boolean(process.env.AFROSITE_STUDIO_ACCESS_KEY);
  const productionReady = environment !== "production" || (apiConfigured && studioConfigured);

  return NextResponse.json(
    {
      status: productionReady ? "healthy" : "degraded",
      service: "afrosite-web",
      environment,
      checks: {
        api: apiConfigured,
        studio: studioConfigured,
      },
    },
    { status: productionReady ? 200 : 503 },
  );
}
