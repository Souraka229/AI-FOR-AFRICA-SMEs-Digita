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
  return new DemoPaymentProvider();
}
