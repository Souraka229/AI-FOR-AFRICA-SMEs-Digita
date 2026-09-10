type Bucket = {
  windowStartedAt: number;
  requests: number;
  day: string;
  dailyRuns: number;
};

const buckets = new Map<string, Bucket>();
const WINDOW_MS = 10 * 60 * 1_000;
const WINDOW_LIMIT = 5;
const DAILY_LIMIT = 20;

function callerKey(request: Request): string {
  const forwarded = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim();
  return forwarded || request.headers.get("x-real-ip") || "local";
}

export function guardStudio(request: Request): Response | null {
  const production = process.env.VERCEL_ENV === "production";
  const expected = process.env.AFROSITE_STUDIO_ACCESS_KEY;
  if (production && !expected) {
    return Response.json(
      { error: "Studio désactivé : clé d’accès serveur absente." },
      { status: 503 },
    );
  }
  if (expected) {
    const supplied = request.headers.get("authorization");
    if (supplied !== `Bearer ${expected}`) {
      return Response.json({ error: "Accès Studio refusé." }, { status: 401 });
    }
  }

  const now = Date.now();
  const day = new Date(now).toISOString().slice(0, 10);
  const key = callerKey(request);
  const current = buckets.get(key);
  const bucket: Bucket =
    !current || now - current.windowStartedAt >= WINDOW_MS
      ? {
          windowStartedAt: now,
          requests: 0,
          day,
          dailyRuns: current?.day === day ? current.dailyRuns : 0,
        }
      : current;
  if (bucket.day !== day) {
    bucket.day = day;
    bucket.dailyRuns = 0;
  }
  if (bucket.requests >= WINDOW_LIMIT || bucket.dailyRuns >= DAILY_LIMIT) {
    return Response.json(
      { error: "Quota Studio atteint. Réessayez plus tard." },
      { status: 429, headers: { "Retry-After": "600" } },
    );
  }
  bucket.requests += 1;
  bucket.dailyRuns += 1;
  buckets.set(key, bucket);
  return null;
}

export function resetStudioGuardForTests() {
  buckets.clear();
}
