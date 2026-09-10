# Runbook — paiement bloqué

Propriétaire : **SERGE**. Réf. playbook §10.4 · [ADR 0001](adr/0001-genius-pay-psp-primaire.md).

Un paiement est « bloqué » si le client a débité (ou croit avoir débité) et que la caisse n’affiche pas **paiement confirmé**.

## 1. Diagnostic (dans l’ordre)

1. Prendre la **référence** (`MTX-…` ou réf. Genius Pay), jamais un montant tapé par le client.
2. Caisse `/dashboard/{tenant}` : statut `pending` / `failed` / `expired` / `confirmed` / `refunded`.
3. Store local (hackathon) : `apps/web/.demo/state.json` → `ledger[]` + `events[]`.
4. Si clés sandbox présentes : `verify(reference)` côté serveur — **seul** ce statut autorise « payé ».
5. Logs webhook : une ligne `rejeté` = signature invalide ou payload non signé. Ne jamais logger le body brut s’il peut contenir un secret.

## 2. Causes fréquentes

| Signal | Cause | Action |
|---|---|---|
| `pending` après retour navigateur | Redirection ≠ preuve | Relancer `verify()` ; attendre le webhook |
| Webhook 401 | HMAC faux / secret live / horloge | Vérifier `whsec_sandbox_` ; ne pas accepter `whsec_live_` |
| Webhook 403 | `X-Webhook-Environment: live` | Rejeté volontairement avant gate 6 |
| Pas de `checkout_url` | Clés absentes → Demo | Coller `pk_sandbox_`+`sk_sandbox_` ou `sbx_test_` dans `apps/web/.env.local` |
| Deux webhooks, un seul encaissement | Normal (idempotence) | Ne rien recréer |
| Montant différent du panier | Client a trafiqué le front | Le serveur ignore le montant client ; recalcul SKU |
| `expired` / `failed` | PSP a tranché | Ne pas forcer `confirmed` à la main |
| Écart reconcile | Ledger ≠ PSP | Alerte ; ne pas « arrondir » |

## 3. Remboursement manuel

1. Confirmation **admin** explicite (humain).
2. `refund(reference, amount, reason)` — total ou partiel, jamais au-dessus du reste.
3. Tracer la raison dans `events[]`.
4. Contact Genius Pay (sandbox) uniquement si `verify()` et le dashboard PSP divergent encore.

## 4. Interdit

- Écrire « payé » sans `verify()` serveur.
- Activer `*_live_*` avant audit + gate 6.
- Absorber les frais PSP.
- Coller une clé dans un prompt ou un ticket.
