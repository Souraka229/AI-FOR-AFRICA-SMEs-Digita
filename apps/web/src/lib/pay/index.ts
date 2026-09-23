import { ApiPaymentProvider, hasAfrositeApi } from "@/lib/pay/api-provider";
import { DemoPaymentProvider } from "@/lib/pay/demo";
import {
  GeniusPayProvider,
  hasGeniusPaySandboxKeys,
} from "@/lib/pay/geniuspay";
import type { PaymentProvider } from "@/lib/pay/provider";

export type { PaymentProvider } from "@/lib/pay/provider";
export { hasGeniusPaySandboxKeys } from "@/lib/pay/geniuspay";
export { hasAfrositeApi, fetchApiLedger } from "@/lib/pay/api-provider";

/** Genius sandbox > API FastAPI > fichier démo. */
export function getPaymentProvider(): PaymentProvider {
  if (hasGeniusPaySandboxKeys()) return new GeniusPayProvider();
  if (hasAfrositeApi()) return new ApiPaymentProvider();
  if (process.env.AFROSITE_ENV === "production") {
    throw new Error(
      "Configuration paiement manquante : AFROSITE_API_URL ou Genius Pay doit être configuré en production.",
    );
  }
  return new DemoPaymentProvider();
}
