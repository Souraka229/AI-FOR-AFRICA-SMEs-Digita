# ADR 0001 — Genius Pay comme PSP primaire du MVP

- **Statut** : accepté
- **Date** : 2026-09-09
- **Décideur** : Souraka HAMIDA (produit) · consultés : SERGE (paiement), CHITOU
- **Docs à tenir cohérents** : [03 §5](../03-analyse-concurrentielle.md#5-concurrence-paiement--le-combat-le-plus-stratégique), [06 §3 et §6](../06-architecture-technique.md), [10 §F](../10-ressources-de-a-a-z.md#f--paiement-mobile-money-béninuemoa), [playbook §10](../11-playbook-equipe.md#10-paiement--genius-pay)

## Contexte

Les docs 03, 06 et 10 nommaient KKiaPay, FedaPay et CinetPay comme rails de paiement. L'équipe a les clés et la documentation de **Genius Pay** (produit GeniusPay, [docs.api](https://geniuspay.ci/docs/api)) en main. Il faut un PSP *primaire* pour le MVP et le hackathon, sans devenir dépendants d'un seul acteur, et sans jamais détenir les fonds.

Genius Pay couvre le Bénin (`BJ`, devise `XOF`) via PawaPay : opérateurs `MTN_MOMO_BEN` et `MOOV_BEN`. Sandbox et live sont le même contrat API — seules les clés changent (`pk_sandbox_` / `sk_sandbox_` vs `pk_live_` / `sk_live_`).

## Options envisagées

| Option | Pour | Contre |
|---|---|---|
| **A. Genius Pay primaire** derrière `PaymentProvider` | Clés + doc disponibles ; checkout hébergé ; webhooks signés HMAC-SHA256 ; Bénin MTN/Moov documentés | Acteur moins cité que KKiaPay/FedaPay dans l'écosystème local ; dépendance à PawaPay pour le MoMo BJ |
| **B. KKiaPay ou FedaPay primaire** | Marque locale, docs déjà listées | Pas les clés en main aujourd'hui ; retarde le sandbox du hackathon et de la phase 1 |
| **C. Intégrer 3 PSP en parallèle dès J1** | Moins de risque de panne | Hors de portée à trois ; le [doc 01 §5.2](../01-cahier-des-charges.md#52-phase-2-3-9-mois--approfondissement-et-nouveaux-verticaux) réserve le multi-PSP à la Phase 2 |

## Décision

**Option A.** Genius Pay est le PSP primaire du MVP. Toute la logique métier parle à l'interface maison `PaymentProvider` ([playbook §10.2](../11-playbook-equipe.md#102--la-couche-paymentprovider-contrat-maison)). FedaPay et KKiaPay restent des *fallback* activables — le routage multi-PSP est Phase 2, pas un chantier de la semaine 1.

Mapping contractuel pour SERGE (`feat/pay-geniuspay-sandbox`) :

| Méthode `PaymentProvider` | API Genius Pay |
|---|---|
| `createTransaction(order, idemKey)` | `POST /api/v1/merchant/payments` — montant **recalculé serveur**, `currency: XOF`, `customer.country: BJ`, `metadata.idempotency_key` + `metadata.order_id`. Omettre `payment_method` pour le checkout hébergé. |
| `verify(reference)` | `GET /api/v1/merchant/payments/{reference}` — seul ce statut (après webhook) autorise l'écriture « payé » |
| `handleWebhook(payload, signature)` | HMAC-SHA256(`timestamp + "." + raw_body`, `whsec_…`) ; headers `X-Webhook-Signature`, `X-Webhook-Timestamp`, `X-Webhook-Event` ; événements `payment.success` / `payment.failed` / `payment.refunded` |
| `refund(reference, amount, reason)` | Endpoint remboursement Genius Pay — confirmation admin + audit trail |
| `reconcile(dateRange)` | `GET /api/v1/merchant/payments?from=&to=` rapproché du ledger interne |

Base URL documentée : `https://geniuspay.ci/api/v1/merchant` (variante `https://pay.genius.ci/api/v1/merchant`). Auth : `X-API-Key` + `X-API-Secret`, **jamais** côté client.

Ce qui ne change pas : Afrosite n'est jamais dépositaire ; pas de PAN/CVV chez nous ; la redirection `success_url` ne prouve rien ; montants recalculés serveur ; idempotence partout ; vert uniquement pour « paiement confirmé ».

## Conséquences

- SERGE implémente `GeniusPayProvider` en **sandbox uniquement** jusqu'à l'audit externe + gate 6.
- Les docs 03 §5, 06 §3/§6 et 10 §F doivent citer Genius Pay comme primaire et KKiaPay/FedaPay/CinetPay comme fallback / Phase 2.
- Risque « un seul PSP » : déjà dans le [playbook §15](../11-playbook-equipe.md#15-risques--propriétaire) — mitigation = l'interface, pas un second SDK dès J1.
- À revisiter si Genius Pay ne livre pas le Bénin en sandbox avant la fin de la phase 1, ou si l'agrément / le rail PawaPay pose un blocage BCEAO. Dans ce cas : basculer le primaire vers FedaPay sans changer le métier.

## Révision 10 sept. 2026 — doc officielle dashboard

La doc marchand ([geniuspay.ci/docs/api](https://geniuspay.ci/docs/api)) et la page sandbox ([docs/sandbox](https://geniuspay.ci/docs/sandbox)) coexistent. Le métier continue de parler à `PaymentProvider`. Seul `GeniusPayProvider` change.

| Source | Base | Clés | Init |
|---|---|---|---|
| API marchand (primaire) | `https://geniuspay.ci/api/v1/merchant` | `pk_sandbox_` + `sk_sandbox_` | `POST /payments` — omettre `payment_method` → `checkout_url` |
| Sandbox virtuel (scénarios) | `https://pay.genius.ci/sandbox` | `sbx_test_…` | `POST /payments/initiate` + `scenario` + `gateway` |

Mapping à jour :

| Méthode | Appel |
|---|---|
| `createTransaction` | Marchand : `POST /payments` `{ amount, currency: XOF, customer.country: BJ, metadata }` → `data.reference` + `data.checkout_url`. Virtuel : `POST /sandbox/payments/initiate`. |
| `verify` | `GET /payments/{reference}` — « payé » seulement si `data.status` = `completed` |
| `handleWebhook` | HMAC-SHA256(`timestamp + "." + raw_body`, `whsec_sandbox_`) ; rejeter `X-Webhook-Environment: live` |
| `reconcile` | `GET /payments?from=&to=` |

MCP officiel (docs, pas le métier) : SSE `https://geniuspay.ci/api/mcp`, header `Authorization: Bearer pk_sandbox_…`. Modèle : [geniuspay-mcp.example.json](../geniuspay-mcp.example.json). Jamais de clé live dans l’IDE. Ne pas coller `sk_sandbox_` / `sk_live_` dans Cursor — `pk_sandbox_` suffit pour lire la doc.

Montant min documenté : **200 XOF**. Wax démo = 24 500 FCFA.
