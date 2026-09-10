# API Marchand GeniusPay (copie locale)

Source : documentation officielle marchand, 10 sept. 2026.  
Base HTTPS (dashboard) : `https://geniuspay.ci/api/v1/merchant`  
Le fichier téléchargé mentionne aussi `http://` — on utilise **https**.

## Auth

- `X-API-Key` : `pk_sandbox_…`
- `X-API-Secret` : `sk_sandbox_…`
- Jamais de `*_live_*` avant gate 6.

## Init checkout (recommandé)

`POST /payments` sans `payment_method` → `data.checkout_url`  
Montant min : 200 XOF. Payé = `data.status` `completed`.

## Webhooks (doc officielle fichier)

Headers : `X-GeniusPay-Signature`, `X-GeniusPay-Timestamp`, `X-GeniusPay-Event`.  
HMAC-SHA256 **du body brut** (variante dashboard : `timestamp + "." + body`, headers `X-Webhook-*`).  
Payload : `data.transaction.reference`, `data.environment`.

Événements : `payment.initiated` / `success` / `failed` / `cancelled` / `refunded`.

## Méthodes documentées

`wave`, `orange_money`, `mtn_money`, `card`. Afrosite omet `payment_method` (checkout hébergé).
