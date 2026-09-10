# Webhooks GeniusPay — contrat officiel (30 déc. 2025)

Source : *geniuspay-webhook-integration-guide*. Sandbox et live : même code, secrets différents. **Afrosite n’accepte que `sandbox` jusqu’au gate 6.**

## Headers

`X-Webhook-Signature` · `X-Webhook-Timestamp` · `X-Webhook-Event` (requis)  
`X-Webhook-Environment` (`sandbox` | `live`) · `X-Webhook-Delivery` · `X-Webhook-Retry`

## Signature

`HMAC-SHA256(timestamp + "." + raw_body, whsec_sandbox_…)`  
Rejouer si `|now - timestamp| > 300s`. Body **brut**, pas un objet re-sérialisé.

## Payload

`data.reference`, `data.status` (`completed` = payé), `environment` au top-level.  
Événements paiement : `initiated` / `success` / `failed` / `cancelled` / `refunded` / `expired` + `webhook.test`.  
Cashout : plus tard.

## Endpoint maison

`POST /api/pay/webhook` — 200 `{ success, message }` · 400 headers/timestamp · 401 signature · 403 live.
