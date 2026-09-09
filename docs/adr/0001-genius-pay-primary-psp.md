# ADR 0001 — Genius Pay as primary PSP

- Status: Accepted
- Date: 2026-09-09
- Deciders: Souraka (product), SERGE (implementation)

## Context

Docs 03/06/10 historically list KKiaPay / FedaPay / CinetPay as Mobile Money options in
UEMOA. The team holds Genius Pay API keys and wants a single primary PSP for the MVP
while keeping the door open for fallbacks.

## Decision

1. **Genius Pay is the primary PSP** for Afrosite MVP sandbox and (later) production.
2. All payment code talks only to the house `PaymentProvider` contract in
   `services/api/afrosite_api/payments/`. Genius Pay is one adapter
   (`GeniusPayProvider`); FedaPay/KKiaPay remain future adapters.
3. Default HTTP paths (`/v1/transactions`, `/v1/transactions/{provider_ref}`) and JSON
   field names are **provisional sandbox shapes** until official Genius Pay docs are
   pasted into this ADR. Override via `GENIUSPAY_*_PATH` env vars — never hardcode
   invented vendor URLs in callers.
4. Webhook authenticity uses HMAC-SHA256 over the raw body with
   `GENIUSPAY_WEBHOOK_SECRET`, sent as header `X-GeniusPay-Signature` (hex digest).
   Remap header/algorithm when vendor docs confirm.

## Consequences

- Docs 03 §5, 06 §5-6, and 10 §F should be updated by Souraka to name Genius Pay as
  primary and list FedaPay/KKiaPay as fallbacks.
- Production keys stay blocked until Gate 6 + external security audit
  (`feat/pay-geniuspay-production`).
- Changing PSP = new adapter class only; no business-logic rewrite.
