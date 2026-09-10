import { NextResponse } from "next/server";
import { getPaymentProvider } from "@/lib/pay";

export const runtime = "nodejs";

function problem(status: number, title: string, detail: string) {
  return NextResponse.json(
    {
      type: "about:blank",
      title,
      status,
      detail,
      instance: "/api/pay/webhook",
    },
    { status },
  );
}

/** Guide officiel GeniusPay : headers requis, HMAC, TTL 5 min. Live refusé. */
export async function POST(request: Request) {
  const rawBody = await request.text();
  const signature = request.headers.get("x-webhook-signature") ?? "";
  const timestamp = request.headers.get("x-webhook-timestamp") ?? "";
  const event = request.headers.get("x-webhook-event") ?? undefined;
  const environment = request.headers.get("x-webhook-environment") ?? undefined;

  if ((environment ?? "").toLowerCase() === "live") {
    return problem(403, "Forbidden", "Webhook live rejeté avant gate 6.");
  }

  if (!signature || !timestamp || !event) {
    return problem(400, "Bad Request", "Required header is not present.");
  }

  const unix = Number(timestamp);
  if (!Number.isFinite(unix) || Math.abs(Date.now() / 1000 - unix) > 300) {
    return problem(400, "Bad Request", "Timestamp too old");
  }

  const entry = await getPaymentProvider().handleWebhook(rawBody, {
    signature,
    timestamp,
    event,
    environment,
  });

  if (!entry) {
    return problem(401, "Unauthorized", "Invalid signature");
  }

  return NextResponse.json({
    success: true,
    message: "Webhook processed successfully",
    reference: entry.reference,
    status: entry.status,
  });
}
