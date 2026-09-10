"""GeniusPayProvider sandbox — mapping ADR 0001 (rév. 10 sept. 2026).

Le runtime HTTP vit dans apps/web/src/lib/pay/geniuspay.ts :
- marchand : pk_sandbox_ + sk_sandbox_ → POST /api/v1/merchant/payments
- virtuel  : sbx_test_ → POST https://pay.genius.ci/sandbox/payments/initiate
Ne pas importer le SDK Genius dans le métier.
"""

from __future__ import annotations

from typing import Literal


class GeniusPayProvider:
    id: Literal["geniuspay"] = "geniuspay"

    def create_transaction(self, order: dict) -> dict:
        raise NotImplementedError(
            "Implémentation HTTP : apps/web/src/lib/pay/geniuspay.ts (sandbox)."
        )

    def verify(self, reference: str) -> dict | None:
        raise NotImplementedError("verify() serveur — ADR 0001 GET /payments/{reference}")

    def handle_webhook(self, raw_body: str, signature: str, timestamp: str) -> dict | None:
        raise NotImplementedError("HMAC-SHA256(timestamp + '.' + raw_body, whsec_sandbox_)")

    def refund(self, reference: str, amount_xof: int, reason: str) -> dict:
        raise NotImplementedError("Après create + verify sandbox verts.")

    def reconcile(self, date_from: str, date_to: str) -> dict:
        raise NotImplementedError("GET /payments?from=&to= rapproché du ledger.")
