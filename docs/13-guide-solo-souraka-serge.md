# Guide solo — faire Souraka **et** Serge

> Tu portes deux casquettes. Ce fichier est le **point d’entrée unique** : quoi livrer, où c’est dans le code, quelles docs ouvrir, dans quel ordre travailler. Les docs 01→12 restent la source de vérité ; ici on les traduit en actions.

**Produit en une phrase.** Un commerçant décrit son activité → Afrosite personnalise un blueprint (commerce / resto / services) → mini-site + commande + Mobile Money + caisse du soir. Jamais d’USD. Jamais dépositaire des fonds.

**Démo à connaître par cœur** ([doc 12 §5](12-pitch-hackathon.md#5-déroulé-de-la-démo-en-direct-2-min--obligatoire-à-répéter-5-fois)) :

1. `/studio` — « boutique de tissus wax à Cadjehoun, livraison quartier, paiement Mobile Money »
2. Blueprint Commerce validé (Gate 1)
3. `/t/cadjehoun-wax` — panier **24 500 FCFA** (12 500 + 8 000 + 4 000)
4. Paiement MTN MoMo → `verify()` serveur → vert « confirmé » → WhatsApp client + commerçante
5. `/dashboard/cadjehoun-wax` — réconciliation + résumé WhatsApp

---

## 1. Lire dans cet ordre (45 min, pas 3 jours)

| Ordre | Fichier | Pourquoi |
|---|---|---|
| 1 | Ce guide | Carte + état réel du repo |
| 2 | [00-README](00-README.md) | Index de toute la doc |
| 3 | [12 — pitch hackathon](12-pitch-hackathon.md) §5, §7, §8 | Ce qu’on doit **montrer** |
| 4 | [11 — playbook](11-playbook-equipe.md) §2, §3, §10, §16 | Règles + RACI + paiement + cases semaine |
| 5 | [ADR 0001](adr/0001-genius-pay-psp-primaire.md) | Contrat Genius Pay (quand tu codes le PSP) |
| 6 | Le code dans l’ordre du §4 ci-dessous | Comprendre le flux réel |

Le reste : **à la demande**, pas en lecture linéaire.

| Doc | Ouvre seulement si… |
|---|---|
| [01 cahier](01-cahier-des-charges.md) | Tu doutes du périmètre (3 blueprints, hors-scope) |
| [02 business](02-business-model.md) | Pricing, marge, « qui paie les frais PSP » |
| [03 concurrence](03-analyse-concurrentielle.md) | Pitch / Q&A jury |
| [04 différenciation](04-differenciation-positionnement.md) | Message commercial |
| [05 roadmap Afrique](05-roadmap-leadership-afrique.md) | 5 pilotes, go-to-market |
| [06 architecture](06-architecture-technique.md) | Tu poses FastAPI / LangGraph / Temporal |
| [07 plan 90 j](07-plan-execution-90-jours.md) | Planning phase 1/2/3 |
| [08 SEO](08-seo-et-clonage-de-sites.md) | Metadata, sitemap, JSON-LD |
| [09 branding](09-branding-logo-positionnement.md) | Couleurs, typo, interdits visuels |
| [10 ressources A–Z](10-ressources-de-a-a-z.md) | Lien officiel d’un outil (PSP, BCEAO, LiteLLM…) |
| [cost-instrumentation-plan](cost-instrumentation-plan.md) | Compteurs IA / PSP |
| [target-list-cotonou](target-list-cotonou.md) | Terrain, visites |
| `deeprecherche_important/` | Veille (streaming, critique visuelle, routage modèles) |
| `brand/afrosite-charte/` | Charte visuelle HTML |

---

## 2. Deux rôles, une tête — qui fait quoi

| Casquette | Tu possèdes | Tu ne touches pas (CHITOU) |
|---|---|---|
| **Souraka** | Contrat Blueprint, front Next/SSR/SEO, studio, eval agents, coûts, terrain, Notion | Tokens, patterns POS/QR/checkout « polis », Vision Critic |
| **Serge** | API, Postgres, CI, Genius Pay réel, ledger, webhooks, agents LangGraph, Temporal, Docker/Coolify | Direction artistique |

Si tu es seul : **Souraka d’abord (déjà largement livré), puis Serge dans l’ordre du §7.** Ne pas absorber le design system complet — UI minimale + charte suffisent pour la démo.

---

## 3. État réel du dépôt (10 sept. 2026)

`services/api` existe (`/health` + validate Blueprint). Pas encore de Postgres branché, pas de LangGraph, pas de Temporal, pas de Genius Pay réel sans clés. Le parcours démo tourne dans **Next.js** (`apps/web`) + store fichier.

### Fait (casquette Souraka)

| Livrable | Où |
|---|---|
| Schéma Blueprint v0.1.0 (Zod + miroir Pydantic) | `packages/contracts/` + copie `apps/web/src/lib/contracts/` |
| 3 exemples (wax, maquis, salon) | `examples.ts` — slugs `cadjehoun-wax`, `maquis-fidjrosse`, `salon-awa-cadjehoun` |
| Studio prompt → blueprint | `/studio` + `POST /api/studio/run` (NDJSON) |
| Agents heuristiques (regex, **pas** un LLM) | `src/lib/agents/{intent,architect,pipeline}.ts` |
| Gate 1 (Zod + budget + secrets) | `architect.ts` → `runGate1` |
| Eval 96 prompts (32 × 3 verticaux) | `pnpm eval:agents` |
| Boutique + checkout | `/t/[tenant]` + `tenant-checkout.tsx` |
| Paiement **simulé** + ledger | `actions/payment.ts` + `lib/demo/store.ts` |
| WhatsApp **simulé** (client + gérante) | écrit dans le store après `verifyAndConfirm` |
| Caisse du soir | `/dashboard/[tenant]` |
| SEO marketing + tenant | `robots.ts`, `sitemap.ts`, `json-ld.tsx`, `t/[tenant]/sitemap.xml/route.ts` |
| ADR Genius Pay, plan coûts, liste Cotonou | `docs/adr/0001-…`, `cost-instrumentation-plan.md`, `target-list-cotonou.md` |

### Fait (casquette Serge — posé le 10 sept. 2026)

| Livrable | Où |
|---|---|
| `THIRDPARTY.md` (10 briques playbook §6.2) | racine |
| Docker Compose Postgres / Redis / MinIO | `infra/docker-compose.yml` + `infra/README.md` |
| CI Gate 2 + scan secrets | `.github/workflows/ci.yml` |
| `PaymentProvider` + démo + Genius sandbox | `apps/web/src/lib/pay/` · miroir Python `services/api/payments/` |
| Webhook HMAC (route) | `POST /api/pay/webhook` |
| 8 cas Gate 4 + runbook | `pnpm check:pay` · `docs/runbook-paiement-bloque.md` |
| FastAPI `/health` + validate + ledger | `services/api` · `python check.py` (mémoire ; Postgres si `DATABASE_URL`) |
| Checkout passe par le provider | `app/actions/payment.ts` — sans clés = démo, démo wax intacte |

### Encore à faire (Serge)

| Livrable | Statut |
|---|---|
| Auth/RBAC + registre tenants | **Livré** : JWT + isolation slug ; `POST/GET/PATCH /tenants` |
| Schéma Postgres (Alembic) | **Livré (branche)** : 11 tables, seed wax 24 500 FCFA, roundtrip upgrade/downgrade |
| CRM léger | **Livré (branche)** : téléphone Bénin, visites, fidélité ; montant pris sur la commande |
| Dashboard gérant | **Livré (branche)** : activité du jour, panier moyen, tops, retards ; encaissé = verify |
| Catalogue + commandes API | **Livré** : prix XOF serveur, commande wax 24 500 FCFA, idempotence, pas de « payé » sans verify |
| Clés `pk_sandbox_` en local pour un vrai `verify()` Genius | **Configuré, en pause** : compte actif mais jetons sandbox GeniusPay à 0 |
| Preview par PR | **À faire** |
| WhatsApp Meta / Twilio | **À faire** (simulé OK pour le pitch) |

### Hors dépôt (manuel)

- Notion : 4 bases (Board, ADR, Risques, Bibliothèque de prompts) — playbook §4
- Clés Genius Pay sandbox (jamais dans le git, jamais dans un prompt)
- Audit sécurité externe **avant** clés production

---

## 4. Comprendre le code — lire dans cet ordre

Tout le flux démo tient dans **une chaîne**. Suis-la une fois à voix haute.

```
Prompt
  → POST /api/studio/run
  → runPipeline()
       → analyzeIntent()     regex → vertical + quartier
       → buildBlueprint()    clone un exemple + personnalise
       → runGate1()          Zod + plafond crédits + pas de secret
  → saveBlueprint()          .demo/state.json
  → /t/{slug}                catalogue + TenantCheckout
  → createSandboxPayment()   montant RECALCULÉ serveur (ignore le client)
  → confirmSandboxPayment()  verifyAndConfirm() → ledger + 2 WhatsApp
  → /dashboard/{slug}        totaux + messages
```

| # | Fichier | Rôle |
|---|---|---|
| 1 | `packages/contracts/src/blueprint.schema.ts` | **Contrat.** Si ça n’est pas dans le Zod, ça n’existe pas. |
| 2 | `packages/contracts/src/examples.ts` | Données de démo. Check wax : 24 500 = 12500+8000+4000. |
| 3 | `apps/web/src/lib/contracts/` | **Copie runtime** (le package n’est pas encore un workspace pnpm). Modifier les deux. |
| 4 | `lib/agents/intent.ts` | Classifie commerce / resto / services + quartier Cotonou. Refuse PAN/CVV/clés. |
| 5 | `lib/agents/architect.ts` | Construit le Blueprint + Gate 1. |
| 6 | `lib/agents/pipeline.ts` | Orchestre + `recordCost()`. |
| 7 | `app/api/studio/run/route.ts` | Streame du NDJSON (une ligne JSON par événement). |
| 8 | `app/studio/studio-client.tsx` | UI qui lit le stream. |
| 9 | `lib/demo/store.ts` | **Backend de poche.** Fichier `.demo/state.json` (gitignoré). Blueprints, ledger, WhatsApp, coûts. |
| 10 | `app/actions/payment.ts` | Server Actions : créer / confirmer / preview WhatsApp. |
| 11 | `components/tenant-checkout.tsx` | Panier + bouton payer. |
| 12 | `app/t/[tenant]/page.tsx` | Mini-site. `dynamic = force-dynamic`. |
| 13 | `app/dashboard/[tenant]/page.tsx` | Caisse. `robots: noindex`. |
| 14 | `lib/money.ts` | Affichage FCFA. Jamais d’USD. |
| 15 | `lib/agents/eval/{cases,check,run}.ts` | Régression des agents. |

### Règles déjà dans le code (ne les casse pas)

- Le montant affiché au client **n’est jamais cru** : `createSandboxPayment` somme les SKU côté serveur.
- « Payé » seulement après `verifyAndConfirm` (`verifiedServer: true`), pas après un clic « retour ».
- Vert **uniquement** pour paiement confirmé (charte + playbook §2).
- Tenant en `noindex` (preview). Sitemap marketing = `/` seulement.
- Sitemap tenant = `sitemap.xml/route.ts` (**pas** `sitemap.ts` dans `[tenant]` : Next ne passe pas `params`).

### Ce qui n’est pas ce que les docs décrivent

| Docs disent | Code aujourd’hui |
|---|---|
| LangGraph + LiteLLM | Regex + templates |
| FastAPI + Postgres | Next Server Actions + JSON fichier |
| Genius Pay HMAC | Référence `MTX-DEMO-…` inventée |
| Temporal (paiement) | Fonction synchrone |
| WhatsApp Cloud API | Textes stockés dans le JSON |

C’est voulu pour le hackathon ([doc 12 §7](12-pitch-hackathon.md#7-périmètre-de-build-pour-la-finale-1-semaine-réaliste) : « simulé proprement » OK). Le travail Serge = **remplacer le store par de vrais services**, sans casser le contrat Blueprint ni le parcours UI.

---

## 5. Lancer, tester, se promener

```powershell
cd C:\Users\DELL\AI\apps\web
pnpm install
pnpm dev
```

Ouvre :

- http://localhost:3000 — landing
- http://localhost:3000/studio — tape le prompt wax
- http://localhost:3000/t/cadjehoun-wax — paie 24 500 FCFA
- http://localhost:3000/dashboard/cadjehoun-wax — caisse

Contrôles sans navigateur :

```powershell
cd C:\Users\DELL\AI\apps\web
pnpm eval:agents
pnpm check:contracts
npx tsc --noEmit
```

État persisté : `apps/web/.demo/state.json`. Pour reset : supprimer le fichier, relancer.

PowerShell : `curl` = `Invoke-WebRequest`. Pour un POST brut : `curl.exe`.

---

## 6. Ressources — comment les **utiliser** (pas juste les liens)

Source complète : [doc 10](10-ressources-de-a-a-z.md). Ici : **quand** et **comment**.

### Tout de suite (démo + code actuel)

| Ressource | Usage concret |
|---|---|
| [Next.js App Router](https://nextjs.org/docs) | Pages dans `src/app`, Server Actions, Metadata API |
| [Zod](https://zod.dev) | Tout ce qui entre/sort du Blueprint passe par le schéma |
| [shadcn/ui](https://ui.shadcn.com/docs) | Composants **copiés** dans `src/components/ui` — pas une lib npm magique |
| [Tailwind 4](https://tailwindcss.com/docs) | Styles. Tokens marque : terracotta `#C1502E`, or `#D89B3C`, charbon `#211B17`, sable `#FBF4EC` |
| Charte `brand/afrosite-charte/` | Ouvre `Colors.dc.html` avant tout écran nouveau |

### Dès que tu fais Serge (paiement)

| Ressource | Usage concret |
|---|---|
| [Genius Pay API](https://geniuspay.ci/docs/api) | `POST /payments`, `GET /payments/{ref}` (`completed`), webhook HMAC + `X-Webhook-Environment`. Mapping [ADR 0001](adr/0001-genius-pay-psp-primaire.md) |
| [Genius Pay Sandbox](https://geniuspay.ci/docs/sandbox) | Scénarios virtuels `sbx_test_…` — `POST /sandbox/payments/initiate` |
| [Genius Pay MCP](geniuspay-mcp.example.json) | SSE `https://geniuspay.ci/api/mcp` — lire la doc officielle depuis Cursor. **Pas** `sk_live_` |
| [Genius Pay SDK](https://geniuspay.ci/docs/sdk) | **À lire, pas à importer dans le métier.** Seulement dans `GeniusPayProvider` |
| Playbook §10.2–10.4 | Checklist : idempotence, `verify()`, pas de PAN, sandbox d’abord |
| BCEAO (doc 10 §B) | Argumentaire : on orchestre, on ne détient pas les fonds |

Séquence à implémenter (ne pas inverser) :

1. Interface `PaymentProvider` (5 méthodes)
2. `GeniusPayProvider` sandbox : `createTransaction` + `verify`
3. Webhook : vérifier HMAC **avant** d’écrire
4. Brancher `actions/payment.ts` dessus (garder le même UX)
5. Remboursement + reconcile **après** que succès/échec/double-webhook passent

### Dès que tu poses l’infra

| Ressource | Usage concret |
|---|---|
| [Docker Compose](https://docs.docker.com/) | Postgres + Redis + MinIO en local. **Pas** de Kubernetes |
| [FastAPI](https://fastapi.tiangolo.com/) | `services/api` — le schéma Pydantic est déjà dans `packages/contracts/python/` |
| [GitHub Actions](https://docs.github.com/en/actions) | Lint, `tsc`, eval, CodeQL, TruffleHog |
| [Coolify](https://coolify.io/docs) | Déploiement Git plus tard |
| [CodeQL](https://codeql.github.com/docs/) · [TruffleHog](https://github.com/trufflesecurity/trufflehog) · [Semgrep](https://semgrep.dev/docs/) | Scans CI — playbook §14 |
| [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) | Checklist sécu MVP |

### Plus tard (phase 2, pas cette semaine)

LiteLLM, LangGraph, Temporal, Playwright E2E, OpenTelemetry, WhatsApp Cloud API, Keycloak, Vault — liens dans [doc 10 §C–J](10-ressources-de-a-a-z.md). Le pitch autorise un worker simple à la place de Temporal.

### Cursor (critère jury)

Playbook [§8](11-playbook-equipe.md#8-système-de-prompts--pour-aller-très-vite) : chaque prompt = **bloc de contexte** + branche + fichiers + DoD + « Ne pas faire ».

Modèle de prompt (à coller tel quel) :

```
[BLOC] Afrosite · FCFA · fr-BJ · jamais dépositaire · vert = paiement confirmé
Branche : feat/pay-paymentprovider-interface
Fichiers : <liste exacte>
Objectif : <une phrase>
DoD : playbook §13.1
NE PAS FAIRE : clés prod, SDK Genius dans le métier, casser le contrat Blueprint
```

---

## 7. Feuille de route si tu fais les deux

Priorité = **la démo ne doit jamais casser**. Chaque chantier Serge se branche **derrière** le contrat existant.

### Cette semaine (ordre imposé)

| # | Casquette | Tâche | Branche | Done quand |
|---|---|---|---|---|
| 1 | S | Notion 4 bases (manuel) | — | Board + ADR + Risques + prompts |
| 2 | SERGE | `THIRDPARTY.md` (10 briques doc 06) | `chore/infra-thirdparty-inventory` | Fichier à la racine |
| 3 | SERGE | `docker-compose.yml` Postgres/Redis/MinIO + README « golden path » | `chore/infra-monorepo-bootstrap` | `docker compose up` marche |
| 4 | SERGE | CI : lint + `tsc` + `eval:agents` | `chore/infra-github-actions` | Vert sur PR |
| 5 | SERGE | `PaymentProvider` TypeScript (interface seule) | `feat/pay-paymentprovider-interface` | 5 méthodes typées |
| 6 | SERGE | `GeniusPayProvider` sandbox `create` + `verify` | `feat/pay-geniuspay-sandbox` | Appel sandbox, clés en env |
| 7 | SERGE | Remplacer le confirm simulé par `verify()` (garder le store en fallback si pas de clés) | même branche | Démo wax toujours verte |
| 8 | SERGE | Webhook HMAC + idempotence | `feat/pay-geniuspay-webhook` | Double POST = 1 ligne ledger |
| 9 | SERGE | Modèle de données socle + migrations Alembic | `feat/api-core-schema` | upgrade → downgrade → upgrade ; seed wax 24 500 FCFA |

**Couper si le temps manque** (doc 12 §7) : FastAPI complet, Temporal, multi-PSP, offline, Keycloak, 3 blueprints polis. Un Commerce de bout en bout + paiement sandbox + dashboard suffit.

### Phase 1 (J1–30) — après le hackathon

Socle identique pour 3 blueprints · paiement sandbox réconcilié · tenant de démo créable. Détail : playbook §9.

### Phase 2 (J31–60)

Vrais agents (Intent + Architect via LLM) · eval reste le filet · Code Agent sandbox · Temporal paiement/provisioning.

### Phase 3 (J61–90)

5 pilotes Cotonou, paiement **réel** seulement après audit + gate 6. Toi (Souraka) : dashboard coûts, terrain, témoignages.

---

## 8. Comment travailler sans te noyer

1. **Une carte = une branche = une PR < ~400 lignes.** Noms : `feat/pay-…`, `chore/infra-…`, `feat/api-…` (playbook §5).
2. **WIP max 2.** Si tu codes le webhook, tu ne refais pas la landing.
3. **Ne jamais** : clés `sk_live_` / `whsec_live_` dans le repo ; pousser sur `main` sans PR ; absorber les frais PSP ; afficher de l’USD ; mettre du vert hors « confirmé ».
4. **Si le live casse** : vidéo de la même séquence (plan B pitch §5).
5. **Contradiction docs vs code** : le code de démo gagne pour le hackathon ; ouvre un ADR si tu changes l’archi cible.

### Glossaire express

| Mot | Sens ici |
|---|---|
| **Blueprint** | JSON métier (vertical, catalogue, modules, SEO, PSP) validé Zod |
| **Tenant** | Un établissement (`cadjehoun-wax`) |
| **Gate 1** | Schéma + budget crédits + pas de secret dans le prompt |
| **PSP** | Prestataire de paiement (Genius Pay) |
| **PaymentProvider** | Interface maison — le reste du code ne parle qu’à elle |
| **Ledger** | Journal interne (≠ les vrais flux BCEAO) |
| **Verify** | Appel serveur au PSP ; seul lui autorise « payé » |
| **Sandbox** | Clés `pk_sandbox_` / `sk_sandbox_` — argent fictif |

---

## 9. Checklist « je suis opérationnel »

- [ ] `pnpm dev` + parcours wax 24 500 FCFA + caisse verte
- [ ] `pnpm eval:agents` = 96/96
- [ ] Tu sais reciter le pitch 30 s et la démo 2 min ([doc 12](12-pitch-hackathon.md))
- [ ] Tu sais où est le contrat, le store, le paiement simulé
- [ ] Prochaine PR Serge choisie dans le tableau §7 (pas « tout le backend »)
- [ ] Clés sandbox dans l’env local seulement, si tu attaques Genius Pay
