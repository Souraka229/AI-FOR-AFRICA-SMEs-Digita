import { createHmac, timingSafeEqual } from "node:crypto";

function hexEqual(expected: string, given: string): boolean {
  try {
    const a = Buffer.from(expected, "hex");
    const b = Buffer.from(given, "hex");
    if (a.length !== b.length || a.length === 0) return false;
    return timingSafeEqual(a, b);
  } catch {
    return false;
  }
}

/** Variante dashboard : HMAC-SHA256(timestamp + "." + raw_body). */
export function geniusPaySignature(
  rawBody: string,
  timestamp: string,
  secret: string,
): string {
  return createHmac("sha256", secret)
    .update(`${timestamp}.${rawBody}`)
    .digest("hex");
}

/** Variante doc officielle : HMAC-SHA256(raw_body). */
export function geniusPayPayloadSignature(rawBody: string, secret: string): string {
  return createHmac("sha256", secret).update(rawBody).digest("hex");
}

export function verifyGeniusPaySignature(
  rawBody: string,
  timestamp: string,
  signature: string,
  secret: string,
): boolean {
  if (!secret.startsWith("whsec_")) return false;
  if (secret.includes("_live_")) return false;
  const given = signature.replace(/^sha256=/i, "").trim();
  if (hexEqual(geniusPaySignature(rawBody, timestamp, secret), given)) return true;
  return hexEqual(geniusPayPayloadSignature(rawBody, secret), given);
}
