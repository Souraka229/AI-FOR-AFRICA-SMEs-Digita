import { createClient } from "@supabase/supabase-js";

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

function callerKey(request: Request, userId?: string): string {
  if (userId) return `user:${userId}`;
  const forwarded = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim();
  return forwarded || request.headers.get("x-real-ip") || "local";
}

async function validSupabaseUser(request: Request): Promise<string | null> {
  const authorization = request.headers.get("authorization") ?? "";
  const token = authorization.startsWith("Bearer ") ? authorization.slice(7) : "";
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  if (!token || !url || !key) return null;
  const client = createClient(url, key, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
  const { data, error } = await client.auth.getUser(token);
  return error || !data.user ? null : data.user.id;
}

export async function guardStudio(request: Request): Promise<Response | null> {
  const production = process.env.VERCEL_ENV === "production" || process.env.AFROSITE_ENV === "production";
  const expected = process.env.AFROSITE_STUDIO_ACCESS_KEY;
  const authorization = request.headers.get("authorization") ?? "";
  let userId: string | undefined;

  if (authorization === `Bearer ${expected}` && expected) {
    userId = "access-key";
  } else {
    userId = (await validSupabaseUser(request)) ?? undefined;
  }

  if (production && !expected && !process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY) {
    return Response.json(
      { error: "Studio désactivé : Supabase Auth ou clé d’accès serveur absente." },
      { status: 503 },
    );
  }
  if (!userId && !production && !expected && !process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY) {
    userId = "local";
  }
  if (!userId) return Response.json({ error: "Accès Studio refusé." }, { status: 401 });

  const now = Date.now();
  const day = new Date(now).toISOString().slice(0, 10);
  const key = callerKey(request, userId);
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
