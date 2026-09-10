# Playbook d'équipe — Afrosite

> Qui fait quoi, dans quel ordre, avec quel niveau de qualité, **avec quels prompts** et **sur quelles branches** — pour livrer le MVP avancé à trois.

Ce document traduit les [docs 01 → 10](00-README.md) en responsabilités, tâches datées, prompts réutilisables et branches Git. **En cas de contradiction, les documents numérotés font foi** : signale l'écart dans le canal d'équipe et ouvre un ADR (§11).

« Avancé » ≠ « plus de périmètre ». Le périmètre reste **3 blueprints** (Commerce, Restaurant, Services — [doc 01 §5.4](01-cahier-des-charges.md#54-hors-périmètre-explicitement-exclu-du-mvp)). L'avancé est dans la **rigueur** du pipeline : gates, agents, audit trail, streaming, boucle de critique visuelle, couche paiement multi-PSP, tolérance réseau.

## Sommaire

| # | Section |
|---|---|
| 1 | [L'équipe — qui possède quoi](#1-léquipe--qui-possède-quoi) |
| 2 | [Principes non négociables](#2-principes-non-négociables) |
| 3 | [RACI par chantier](#3-raci-par-chantier) |
| 4 | [Méthode de travail — Agile / Kanban / Notion](#4-méthode-de-travail--agile--kanban--notion) |
| 5 | [Organisation Git — toutes les branches à créer](#5-organisation-git--toutes-les-branches-à-créer) |
| 6 | [Dépôts & open source sans perte de qualité](#6-dépôts--open-source-sans-perte-de-qualité) |
| 7 | [Le pipeline prompt → production](#7-le-pipeline-prompt--production) |
| 8 | [Système de prompts — pour aller très vite](#8-système-de-prompts--pour-aller-très-vite) |
| 9 | [Plan 90 jours, par personne](#9-plan-90-jours-par-personne) |
| 10 | [Paiement — Genius Pay](#10-paiement--genius-pay) |
| 11 | [Design system & critique visuelle](#11-design-system--critique-visuelle) |
| 12 | [Data, coûts IA & recherche](#12-data-coûts-ia--recherche) |
| 13 | [Qualité — Definition of Done](#13-qualité--definition-of-done) |
| 14 | [Sécurité — responsabilités](#14-sécurité--responsabilités) |
| 15 | [Risques & propriétaire](#15-risques--propriétaire) |
| 16 | [Cette semaine — action par personne](#16-cette-semaine--action-par-personne) |

---

## 1. L'équipe — qui possède quoi

Trois personnes, un MVP avancé. Chaque chantier a **un** propriétaire redevable (le « A » du RACI §3), même quand plusieurs contribuent. Le propriétaire ne fait pas tout : il garantit que le chantier avance, respecte les gates, et n'est jamais bloqué en silence.

| Personne | Rôle | Possède |
|---|---|---|
| **Souraka HAMIDA** | Product Lead · Front-end · Data / Recherche | Vision produit, backlog, priorisation, arbitrages de périmètre · contrat `Blueprint JSON` (`packages/contracts`) · architecture front-end (Next.js, SSR/SEO) · qualité des prompts & *eval harness* des agents · instrumentation des coûts IA/infra par client · observabilité produit & unit economics · veille / recherche (`deeprecherche_important/`) · go-to-market pilotes + onboarding |
| **CHITOU** | Design Lead · Design System · Design Engineering | Design system Afrosite (foundations, tokens sémantiques, composants) · bibliothèque de composants livrée **en code** (shadcn/ui personnalisé) · patterns par blueprint (POSLayout, KitchenBoard, QRMenu, MobileCheckout…) · direction artistique & rejet du « slop » IA ([doc 09 §3.4](09-branding-logo-positionnement.md#34-ce-que-la-marque-refuse-par-principe)) · boucle de critique visuelle (critères écrits, agent UI Critic / Vision Critic) · montage des écrans avec Souraka · accessibilité & Core Web Vitals mobile |
| **SERGE** | Backend · Infra · Paiement · Agents | API (FastAPI), modèle de données PostgreSQL, migrations, RBAC · orchestration agents (LangGraph) · workflows durables (Temporal : paiement, provisioning, webhooks) · intégration **Genius Pay** derrière `PaymentProvider` (§10) · CI/CD (GitHub Actions), déploiement (Docker Compose + Coolify), sauvegardes · sécurité applicative (SAST, scans, gates, sandbox) · ledger interne immuable, réconciliation quotidienne |

**Casquettes de secours** (personne dédiée impossible à trois) :

| Trou | Qui l'assure | Comment on limite le risque |
|---|---|---|
| PM | Souraka | Notion Kanban (§4) comme seule source de suivi |
| MLOps / Analytics | Souraka | Eval harness + coûts instrumentés dès le jour 1 (§12) |
| QA dédiée | Partagé, **outillé** | Playwright bloquant en CI ; pas de QA manuelle systématique |
| SRE / DevOps | SERGE | Infra volontairement légère : pas de Kubernetes, Vault ni cluster GPU au MVP ([doc 06 §2](06-architecture-technique.md#2-repos-et-briques-open-source-fondamentales)) |
| Sécurité offensive | SERGE + externe | **Audit sécurité tiers budgété avant l'activation des clés PSP en production** (§14) |

> Toute tâche hors compétence de l'équipe passe en **risque suivi** (§15) avec une date de décision « on forme / on sous-traite / on reporte ».

---

## 2. Principes non négociables

Affichés au mur. Toute PR, tout blueprint, toute décision d'archi se relit à travers cette liste.

| Règle | Ce que ça impose concrètement | Réf. |
|---|---|---|
| Un prompt n'exécute jamais une action risquée | Le prompt déclenche un workflow testable, réversible, observé. L'IA propose, les règles contrôlent, les tests vérifient, l'humain valide. | [06 §intro](06-architecture-technique.md) |
| 80 % éprouvé / 20 % généré | On personnalise des blueprints versionnés — on ne régénère pas une app de zéro. | [06 §12](06-architecture-technique.md#12-premier-produit-technique-à-construire) |
| Afrosite ne détient jamais de fonds | Orchestration au-dessus d'un PSP agréé BCEAO. Ledger interne ≠ flux réels. Jamais de PAN/CVV stockés. | [01 §7](01-cahier-des-charges.md#7-contraintes) · [06 §6](06-architecture-technique.md#6-sécurité--règles-non-négociables) |
| La redirection navigateur ne prouve rien | Seul un webhook signé + `verify()` serveur confirme un paiement. Idempotency key partout. Montants recalculés serveur. | [06 §6](06-architecture-technique.md#architecture-paiement) |
| Streaming systématique | Chaque étape (analyse, génération, test, déploiement) streame son statut dès qu'elle démarre. | [deep 04 §2A](../deeprecherche_important/04-application-a-afrosite.md#a-rendre-le-streaming-systématique-pas-optionnel) |
| Cache de prompts activé par défaut | Configuration par défaut du routeur LiteLLM. Cible marge brute ≥ 70 %. | [deep 04 §2C](../deeprecherche_important/04-application-a-afrosite.md#c-activer-le-cache-de-prompts-par-défaut-sur-le-routeur) |
| Offline-tolerant | Prise de commande et caisse en mode dégradé : file locale, synchro différée. | [01 §6](01-cahier-des-charges.md#6-exigences-non-fonctionnelles) |
| FCFA & français natifs | Jamais d'USD affiché au client final. Jamais de traduction approximative. | [01 §7](01-cahier-des-charges.md#7-contraintes) |
| Jamais de push généré sur `main` | Branche `feature/generated-<id>` + PR + CI avant merge. | [06 §8](06-architecture-technique.md#8-connexion-githubgitlab-et-push-de-code) |
| Réversibilité en un clic | Export intégral code + BDD + assets + config à tout moment. | [01 §6](01-cahier-des-charges.md#6-exigences-non-fonctionnelles) |
| 3 blueprints max au MVP | Tout 4ᵉ vertical se valide d'abord sur le socle commun. | [01 §5.4](01-cahier-des-charges.md#54-hors-périmètre-explicitement-exclu-du-mvp) · [07](07-plan-execution-90-jours.md) |
| Aucun secret dans le contexte LLM | Jeton temporaire par agent, liste blanche d'outils, toute donnée externe = non fiable. | [06 §6](06-architecture-technique.md#6-sécurité--règles-non-négociables) |
| Tokens sémantiques, jamais de couleur/police en dur | `--status-payment-confirmed`, pas `#1F7A53`. Vert **uniquement** pour « paiement confirmé ». | [06 §11](06-architecture-technique.md#11-design-system-et-direction-artistique) · [09 §3](09-branding-logo-positionnement.md#3-le-branding--système-de-marque) |

---

## 3. RACI par chantier

**R** réalise · **A** redevable / approuve · **C** consulté · **I** informé. Un seul **A** par ligne.

| Chantier | Souraka | CHITOU | SERGE |
|---|:--:|:--:|:--:|
| Vision produit & priorisation backlog | **A/R** | C | C |
| Contrat `Blueprint JSON` & `packages/contracts` | **A** | C | R |
| Design system, tokens, composants | C | **A/R** | I |
| Architecture front-end (Next.js, SSR, SEO) | **A/R** | R | C |
| Montage des écrans produit | C | **A/R** | C |
| API, modèle de données, migrations, RBAC | C | I | **A/R** |
| Agents LangGraph (implémentation, outils) | C | I | **A/R** |
| Prompts & eval harness des agents | **A/R** | C | C |
| Workflows Temporal (paiement, provisioning) | I | I | **A/R** |
| Intégration Genius Pay & couche PSP | C | I | **A/R** |
| Ledger interne & réconciliation quotidienne | C | I | **A/R** |
| Gates de sécurité & sandbox d'exécution | C | I | **A/R** |
| CI/CD, déploiement, sauvegardes | C | I | **A/R** |
| Observabilité & coûts IA / unit economics | **A/R** | I | C |
| Tests E2E Playwright | **A** | R (UI) | R (flux) |
| SEO natif par blueprint ([doc 08](08-seo-et-clonage-de-sites.md)) | **A/R** | C | C |
| Recherche & veille | **A/R** | C | C |
| Pilotes, onboarding, support terrain | **A/R** | C | I |

---

## 4. Méthode de travail — Agile / Kanban / Notion

On travaille en **Kanban** (flux continu, WIP limité), **pas en sprints à dates fixes**. La cadence longue vient des **3 phases de 90 jours** ([doc 07](07-plan-execution-90-jours.md)) ; la cadence courte vient du flux du board.

### 4.1 — Notion = source de suivi unique

Un espace Notion `Afrosite` avec **4 bases** :

| Base | Rôle |
|---|---|
| **Board** | Toutes les tâches, en Kanban (colonnes ci-dessous) |
| **ADR** | Journal des décisions d'architecture (miroir de `docs/adr/`) |
| **Risques** | Table du §15, revue chaque vendredi |
| **Bibliothèque de prompts** | Les prompts du §8, versionnés, copiables |

> Rien ne se pilote par WhatsApp ou par tête. Si ce n'est pas sur le Board, ça n'existe pas.

### 4.2 — Colonnes du Board

| Colonne | Règle d'entrée |
|---|---|
| **Backlog** | Idée ou besoin capturé. Pas encore prêt à démarrer. |
| **Prête** | La carte contient **le prompt complet + le nom de branche + la Definition of Done**. Sinon → reste en Backlog. |
| **En cours** | Quelqu'un travaille dessus. **Max 2 cartes « En cours » par personne** (limite WIP). |
| **En revue** | PR ouverte, en attente de relecture par une autre personne. |
| **En test** | Preview déployée, les 6 gates s'exécutent ([§7](#7-le-pipeline-prompt--production)). |
| **Fait** | PR mergée + gates vertes + checklist DoD cochée. |

### 4.3 — Propriétés d'une carte

- **Titre** — verbe + objet (« Créer l'endpoint POST /orders »)
- **Responsable** — Souraka / CHITOU / SERGE
- **Chantier** — une ligne du RACI (§3)
- **Phase** — 1 / 2 / 3
- **Branche** — nom exact ([§5](#5-organisation-git--toutes-les-branches-à-créer))
- **Docs liés** — `docs/06 §5`, etc.
- **Gate cible** — Gate 1 → 6
- **Prompt utilisé** — lien vers la Bibliothèque de prompts
- **Estimation** — S (≤ ½ j) / M (1–2 j) / L (> 2 j → à découper)
- **Bloqué par** — carte ou personne

### 4.4 — Rituels reliés au board

| Rituel | Quand | Ce qu'on regarde |
|---|---|---|
| Point quotidien | 15 min, async ou visio | On « marche le board » de droite à gauche. Un bloqué = on s'arrête dessus après le point. |
| Revue hebdo | Vendredi, 45 min | Indicateurs [doc 07](07-plan-execution-90-jours.md#indicateurs-à-suivre-dès-le-jour-1) : temps prompt→preview, coût IA/client, taux de réconciliation auto, usage quotidien par pilote, recommandations. |
| Revue de blueprint | À chaque DoD blueprint | Les 3 membres passent la DoD [§13.2](#132--dod-dun-blueprint) ensemble. |
| ADR | À chaque décision d'archi | 1 fichier `docs/adr/NNNN-titre.md` : contexte, options, décision, conséquences. Court. |
| Rétro de phase | Fin de chaque phase 90 j | Ce qui marche / coince / ce qu'on change. Décisions tracées. |
| Post-mortem incident | Sous 48 h | Sans blâme : chronologie, cause racine, actions (§14). |

---

## 5. Organisation Git — toutes les branches à créer

### 5.1 — Modèle

**Trunk-based** : `main` protégée = production. Branches **courtes** (vie ≤ 3 jours), une par carte Notion, PR obligatoire, jamais de commit direct sur `main`.

### 5.2 — Convention de nommage

```
<type>/<scope>-<court-slug>
```

| `<type>` | Usage |
|---|---|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correctif |
| `chore` | Outillage, config, CI, dépendances |
| `docs` | Documentation |
| `spike` | Exploration jetable (jamais mergée telle quelle) |
| `feature/generated-<id>` | **Réservé au Code Agent** — code produit par l'IA, ne merge jamais sans passer les 6 gates |

| `<scope>` | Zone |
|---|---|
| `web` | `apps/web` |
| `ds` | `packages/design-system` |
| `bp` | `packages/blueprints` |
| `contracts` | `packages/contracts` |
| `api` | `services/api` |
| `agents` | `services/agents` |
| `wf` | `services/workflows` |
| `llm` | `packages/llm` |
| `pay` | tout ce qui touche Genius Pay / paiement |
| `infra` | `infra/`, CI/CD, déploiement |

Exemples : `feat/api-orders-endpoint`, `feat/ds-money-component`, `chore/infra-github-actions`, `fix/pay-webhook-idempotency`.

### 5.3 — Règles de branche

- [ ] `main` protégée : PR + 1 relecture + CI verte obligatoires pour merger.
- [ ] Une branche = une carte Notion = une PR. PR < ~400 lignes si possible.
- [ ] Commits en [Conventional Commits](https://www.conventionalcommits.org/) : `feat:`, `fix:`, `chore:`, `docs:`, `test:`.
- [ ] Rebase sur `main` avant d'ouvrir la PR. Squash-merge.
- [ ] Supprimer la branche après merge.
- [ ] Le Code Agent pousse **uniquement** sur `feature/generated-<id>` + ouvre une PR automatique ([doc 06 §8](06-architecture-technique.md#8-connexion-githubgitlab-et-push-de-code)). Merge humain après gates.

### 5.4 — Branches à créer **maintenant** (semaine 1)

**Souraka**

- [ ] `chore/infra-monorepo-bootstrap` *(en binôme avec SERGE)*
- [ ] `chore/contracts-blueprint-schema-v0` — schéma `Blueprint JSON` + validateur Zod/Pydantic
- [ ] `feat/web-skeleton-ssr` — Next.js, SSR, Metadata API, route sitemap par tenant
- [ ] `docs/cost-instrumentation-plan` — quelles métriques, où, quel dashboard
- [ ] `docs/target-list-cotonou` — liste des 100 établissements

**CHITOU**

- [ ] `feat/ds-tokens` — `tokens.json` + `semantic-tokens.json` depuis la [charte](09-branding-logo-positionnement.md#3-le-branding--système-de-marque)
- [ ] `feat/ds-core-components` — Button, Input, Card, Money, PaymentStatus, OrderStatus
- [ ] `docs/visual-identity-rules` — critères de rejet du Vision Critic
- [ ] `feat/ds-pattern-mobilecheckout` — le parcours qui touche l'argent

**SERGE**

- [ ] `chore/infra-monorepo-bootstrap` — monorepo + `docker-compose` (Postgres, Redis, MinIO) + golden-path README
- [ ] `chore/infra-github-actions` — lint, typecheck, tests, CodeQL, TruffleHog, preview par PR
- [x] `feat/api-auth-rbac` — JWT courts + RBAC owner/cashier/kitchen/customer + isolation tenant
- [x] `feat/api-core-schema` — modèle de données du socle commun
- [x] `feat/api-crm` — clients par téléphone, historique, fidélité
- [x] `feat/api-dashboard` — ventes du jour, panier moyen, tops, retards
- [ ] `feat/pay-paymentprovider-interface` — l'interface `PaymentProvider`
- [ ] `feat/pay-geniuspay-sandbox` — `GeniusPayProvider` : `createTransaction` + `verify` en **sandbox**
- [ ] `chore/infra-thirdparty-inventory` — `THIRDPARTY.md` avec les 10 briques épinglées

### 5.5 — Branches par phase

Le [plan 90 jours (§9)](#9-plan-90-jours-par-personne) indique la branche associée à chaque livrable. Toute nouvelle carte Notion crée sa branche avant de passer en colonne **Prête**.

### 5.6 — Liste maître de toutes les branches (créées dans l'ordre)

Cocher au fur et à mesure. Chaque ligne = une carte Notion = une PR. `feature/generated-*` n'apparaît pas ici : elle est créée à la volée par le Code Agent.

**Bootstrap (jour 1, binôme Souraka + SERGE)**

- [ ] `chore/infra-monorepo-bootstrap` — pnpm + turbo + uv, `docker-compose`, golden-path README
- [ ] `chore/infra-github-actions` — `ci.yml`, `preview.yml`, `security.yml`, `smoke-thirdparty.yml`
- [ ] `chore/infra-thirdparty-inventory` — `THIRDPARTY.md`, 10 briques épinglées par digest

**Phase 1 — Fondation (J1 → J30)**

| Branche | Qui | Contenu |
|---|---|---|
| `chore/contracts-blueprint-schema-v0` | S | Schéma `Blueprint JSON` (3 verticaux) Zod + codegen Pydantic + validateur |
| `feat/web-skeleton-ssr` | S | Next.js App Router, SSR, Metadata API, `robots.ts` |
| `feat/web-tenant-sitemap` | S | `sitemap.ts` par tenant + `noindex` previews ([doc 08 §4](08-seo-et-clonage-de-sites.md#4-architecture-seo-en-environnement-multi-tenant)) |
| `docs/cost-instrumentation-plan` | S | Quelles métriques, où, quel dashboard |
| `docs/target-list-cotonou` | S | Liste des 100 établissements |
| `feat/ds-tokens` | CHITOU | `tokens.json` + `semantic-tokens.json` |
| `feat/ds-core-components` | CHITOU | Button, Input, Card, Money, PaymentStatus, OrderStatus |
| `feat/ds-components-data` | CHITOU | DataTable, EmptyState, + états chargement/erreur/vide |
| `feat/ds-pattern-poslayout` | CHITOU | Pattern caisse |
| `feat/ds-pattern-qrmenu` | CHITOU | Pattern menu QR |
| `feat/ds-pattern-mobilecheckout` | CHITOU | Parcours paiement |
| `docs/visual-identity-rules` | CHITOU | `rules/visual-identity.md` — critères de rejet Vision Critic |
| `feat/api-auth-rbac` | SERGE | Auth + rôles owner/cashier/kitchen/customer |
| `feat/api-core-schema` | SERGE | Modèle de données socle commun + migrations |
| `feat/api-tenants` | SERGE | Isolation multi-tenant — **livré** (GET/PATCH/POST `/tenants`, un jeton = un slug) |
| `feat/api-catalog` | SERGE | Produits / plats / prestations — **livré** |
| `feat/api-orders` | SERGE | Commande SKU+qty, montant serveur, isolation client — **livré** (offline file : ensuite) |
| `feat/api-crm` | SERGE | Clients par téléphone, historique, fidélité — **livré** |
| `feat/api-dashboard` | SERGE | Ventes du jour, panier moyen, tops, retards — **livré** |
| `feat/api-exports` | SERGE | Export CSV |
| `feat/pay-paymentprovider-interface` | SERGE | Interface `PaymentProvider` |
| `feat/pay-geniuspay-sandbox` | SERGE | `GeniusPayProvider` : `createTransaction` + `verify` (sandbox) |
| `feat/api-ledger` | SERGE | Ledger append-only + réconciliation quotidienne |
| `chore/infra-gates-policies` | SERGE | Règles des 6 gates (OPA) + politiques de permissions |
| `feat/bp-core` | partagé | Assemblage du socle commun des blueprints |
| `feat/bp-commerce` · `feat/bp-restaurant` · `feat/bp-services` | partagé | Modules spécifiques par vertical |

**Phase 2 — Automatisation IA (J31 → J60)**

| Branche | Qui | Contenu |
|---|---|---|
| `chore/llm-router-adapter` | SERGE+S | `packages/llm` : `generate()` / `stream()` |
| `chore/llm-prompt-cache-default` | S | Cache de prompts activé par défaut |
| `feat/agents-intent` | S | Intent Agent |
| `feat/agents-product-architect` | S | Product Architect Agent → `Blueprint JSON` |
| `chore/agents-eval-commerce` · `-restaurant` · `-services` | S | Jeux de prompts + scoring + check CI de régression |
| `feat/web-validation-audittrail` | S | Écran plan/coût/état live + audit trail |
| `feat/agents-code` | SERGE | Code Agent (OpenHands SDK) en sandbox |
| `feat/agents-security` | SERGE | Security Agent (SAST, deps, secrets, RBAC) |
| `feat/agents-qa` | SERGE | QA Agent (unitaires + Playwright) |
| `feat/agents-deployment` | SERGE | Deployment Agent (preview / release) |
| `feat/agents-payment` | SERGE | Payment Agent (sandbox, webhooks signés) |
| `feat/agents-observability` · `feat/agents-cost` | SERGE / S | Logs+métriques+alertes / budget+quotas |
| `feat/agents-vision-critic` | CHITOU | Vision Critic sur captures Playwright |
| `feat/ds-pattern-kitchenboard` | CHITOU | KDS (reçue / en préparation / prête) |
| `feat/ds-pattern-agenda-rdv` | CHITOU | Agenda de rendez-vous |
| `feat/ds-pattern-delivery` | CHITOU | Suivi de livraison |
| `chore/infra-cwv-gate` | CHITOU | Core Web Vitals bloquant en CI |
| `feat/wf-provision-tenant` | SERGE | Workflow Temporal de provisioning |
| `feat/wf-confirm-payment` | SERGE | Workflow webhook → `verify()` → ledger → WhatsApp |
| `feat/infra-preview-auto` | SERGE | Preview auto + capture après chaque génération |

**Phase 3 — Commercialisation (J61 → J90)**

| Branche | Qui | Contenu |
|---|---|---|
| `feat/web-cost-dashboard` | S | Coût IA/client, cloud, support, rétention J+30 |
| `chore/llm-quotas-tuning` | S | Ajustement crédits & plafonds sur coûts réels |
| `docs/phase2-vertical-decision` | S | Quel(s) vertical(aux) approfondir |
| `fix/ds-polish-highusage` | CHITOU | Polish : prise de commande, KDS, réco du soir |
| `feat/ds-whatsapp-daily-summary` | CHITOU | Mise en forme du résumé quotidien |
| `spike/ux-abtest-<sujet>` | CHITOU | 1 variante A/B documentée |
| `feat/wf-refund` | SERGE | Workflow remboursement total/partiel |
| `feat/wf-reconcile-daily` | SERGE | Job de réconciliation + alerte sur écart |
| `feat/wf-daily-summary-whatsapp` | SERGE | Envoi du résumé au gérant |
| `feat/api-csv-export` | SERGE | Export CSV libre-service (finalisation) |
| `chore/infra-alerting` | SERGE | Alertes paiement / base / déploiement |
| `chore/security-external-audit-fixes` | SERGE | Correctifs de l'audit externe |
| `feat/pay-geniuspay-production` | SERGE | Bascule prod — **après** audit + gate 6 |

---

## 6. Dépôts & open source sans perte de qualité

La consigne : réutiliser les briques qui existent déjà ([doc 06 §2](06-architecture-technique.md#2-repos-et-briques-open-source-fondamentales)) **sans** hériter de leur dette. Méthode : **on dépend des briques, on ne les fork pas, et on les isole toutes derrière une couche d'adaptation maison.**

### 6.1 — Structure des dossiers (arborescence complète du monorepo)

Un seul dépôt `afrosite/`. Gestion des paquets : **pnpm workspaces + Turborepo** (JS/TS) et **uv workspace** (Python). Une CI, des types partagés, des PR atomiques front + back.

```
afrosite/
├─ apps/
│  └─ web/                          # Next.js (App Router) — Souraka + CHITOU
│     ├─ app/
│     │  ├─ (marketing)/            # site vitrine afrosite (SSG)
│     │  ├─ (tenant)/[tenant]/      # mini-site public du client (SSR, SEO)
│     │  │  ├─ sitemap.ts           # sitemap PAR tenant (jamais global)
│     │  │  ├─ robots.ts
│     │  │  └─ opengraph-image.tsx
│     │  ├─ dashboard/              # espace gérant (commandes, caisse, CRM, réco)
│     │  ├─ studio/                 # prompt → blueprint, plan, coût, état live, audit trail
│     │  └─ api/                    # route handlers Next (BFF léger uniquement)
│     ├─ lib/                       # fetchers, auth client, i18n FR, offline queue
│     ├─ e2e/                       # specs Playwright (UI) + helpers captures
│     └─ package.json
│
├─ packages/
│  ├─ contracts/                    # ★ FRONTIÈRE — source unique — Souraka
│  │  ├─ src/blueprint.schema.ts    # Zod : Blueprint JSON (3 verticaux)
│  │  ├─ src/dto/                   # DTO API (requêtes/réponses)
│  │  ├─ src/events/                # types d'événements (paiement, commande, agent)
│  │  ├─ codegen/                   # génère les modèles Pydantic depuis Zod
│  │  └─ python/afrosite_contracts/ # sortie Pydantic consommée par services/*
│  ├─ design-system/                # CHITOU
│  │  ├─ src/foundations/           # colors, typography, spacing, shadows, motion
│  │  ├─ tokens/tokens.json
│  │  ├─ tokens/semantic-tokens.json
│  │  ├─ src/components/            # Button, Input, Card, DataTable, EmptyState,
│  │  │                            #   Money, PaymentStatus, OrderStatus, ...
│  │  ├─ src/patterns/              # POSLayout, KitchenBoard, QRMenu,
│  │  │                            #   MobileCheckout, RestaurantDashboard, AgendaRDV
│  │  └─ rules/                     # ux-principles, accessibility, responsive,
│  │                               #   visual-identity (critères de rejet Vision Critic)
│  ├─ blueprints/                   # partagé — 80 % éprouvé / 20 % généré
│  │  ├─ _core/                     # SOCLE COMMUN identique aux 3 (auth, catalogue,
│  │  │                            #   commande, CRM léger, dashboard, paiement, export)
│  │  ├─ commerce/                  # + stock simple, commande WhatsApp, facturation, livraison
│  │  ├─ restaurant/                # + menu QR, KDS, tables/emporter/livraison
│  │  └─ services/                  # + agenda RDV, devis, facture, rappels
│  ├─ llm/                          # SERGE + Souraka — couche d'adaptation LiteLLM
│  │  ├─ src/router.py              # generate() / stream() — SEULE porte vers les modèles
│  │  ├─ src/cache.py               # cache de prompts ACTIVÉ PAR DÉFAUT
│  │  └─ src/routing.py             # léger / puissant / spécialisé code / local
│  └─ telemetry/                    # SDK OpenTelemetry wrappé (traces, logs, métriques)
│
├─ services/
│  ├─ api/                          # SERGE — FastAPI
│  │  ├─ afrosite_api/
│  │  │  ├─ auth/                   # + RBAC : owner / cashier / kitchen / customer
│  │  │  ├─ tenants/                # isolation stricte multi-tenant
│  │  │  ├─ catalog/  orders/  crm/  dashboard/  exports/
│  │  │  ├─ payments/
│  │  │  │  ├─ provider.py          # interface PaymentProvider (contrat maison)
│  │  │  │  └─ providers/geniuspay.py
│  │  │  ├─ ledger/                 # append-only, immuable
│  │  │  └─ common/                 # repository pattern, idempotency, pagination
│  │  ├─ migrations/                # Alembic — toujours réversibles
│  │  └─ tests/
│  ├─ agents/                       # SERGE — LangGraph
│  │  ├─ runtime/                   # graphes internes (jamais langgraph nu dans le métier)
│  │  ├─ intent/  product_architect/  code/  security/  qa/
│  │  ├─ deployment/  payment/  observability/  cost/
│  │  ├─ tools/                     # liste blanche d'outils PAR agent
│  │  └─ eval/                      # harness : commerce/ restaurant/ services/ + run.py
│  └─ workflows/                    # SERGE — Temporal (argent + provisioning UNIQUEMENT)
│     ├─ provision_tenant/          # workflow.py + activities.py (idempotentes)
│     ├─ confirm_payment/
│     ├─ refund/
│     ├─ reconcile_daily/
│     └─ daily_summary_whatsapp/
│
├─ infra/
│  ├─ docker-compose.yml            # Postgres, Redis, MinIO, Temporal, api, web
│  ├─ coolify/                      # config déploiement (preview + prod)
│  ├─ observability/                # dashboards Grafana + règles Prometheus (versionnés)
│  ├─ opentofu/                     # IaC — Phase 2/3
│  └─ github-actions → ../.github/workflows/
│
├─ docs/                            # docs/01 → docs/11 (ce playbook)
│  └─ adr/                          # 0001-genius-pay-psp-primaire.md, ...
│
├─ .github/workflows/              # ci.yml, preview.yml, security.yml, smoke-thirdparty.yml
├─ THIRDPARTY.md                    # inventaire des briques OSS (§6.3 règle 2)
├─ turbo.json  ·  pnpm-workspace.yaml  ·  pyproject.toml (uv)
└─ README.md                        # golden path : une commande pour tout lancer
```

**Propriété par dossier :**

| Chemin | Propriétaire | Règle |
|---|---|---|
| `apps/web` | Souraka + CHITOU | Souraka = archi/routing/SSR/SEO · CHITOU = assemblage d'écrans depuis le design system |
| `packages/contracts` | Souraka | Modif = PR + accord Souraka. Zod et Pydantic dérivent d'**une** source. |
| `packages/design-system` | CHITOU | Aucune couleur/police en dur ailleurs dans le repo. |
| `packages/blueprints/_core` | partagé | Toute modif du socle se répercute **identiquement** sur les 3 verticaux (DoD §13.2). |
| `packages/blueprints/{commerce,restaurant,services}` | partagé | Seuls les modules spécifiques diffèrent. |
| `packages/llm` | SERGE + Souraka | Seule porte LLM : aucune app n'importe `ai`, `litellm` ni un SDK fournisseur directement. |
| `services/api` | SERGE | Repository pattern, multi-tenant strict, montants recalculés serveur. |
| `services/agents` | SERGE (impl.) · Souraka (prompts/eval) | Jeton + liste blanche d'outils par agent. |
| `services/workflows` | SERGE | Argent & provisioning **uniquement**. Logique dans des activities idempotentes. |
| `infra/` | SERGE | Pas de Kubernetes/Vault/GPU au MVP. |
| `docs/adr/` | partagé | Une décision d'archi = un ADR. |

### 6.2 — Les 10 briques prioritaires et leur isolation

| Brique | Rôle | Couche d'isolation maison | Cadence upgrade |
|---|---|---|---|
| `vercel/ai` + AI Gateway | Génération structurée, streaming, usage/coûts | `packages/llm` — `generateStructured` / `streamStructured` uniquement | Mensuelle, PR manuelle |
| `BerriAI/litellm` | Routeur multi-modèles interchangeable, fallback, coût | `packages/llm` via `AFROSITE_LLM_BACKEND=litellm` — aucune app n'importe litellm directement | Mensuelle, PR manuelle |
| `langchain-ai/langgraph` | Orchestration d'agents | `services/agents/runtime` — graphes définis en interne | Mensuelle, PR manuelle |
| `temporalio/temporal` | Workflows critiques (argent, provisioning) | `services/workflows` — activities maison, zéro logique métier dans le SDK | Trimestrielle, release stable |
| `OpenHands/software-agent-sdk` | Agent qui manipule le code | Wrappé dans le `Code Agent`, exécuté **uniquement** en sandbox Docker | Suivi, pas d'upgrade auto |
| `postgres/postgres` | Source de vérité, ledger, audit | Managé ; accès via repository pattern | LTS, patchs auto |
| `redis/redis` | Cache, files, rate limiting, verrous | Client centralisé `services/api/cache` | LTS, patchs auto |
| `minio/minio` | Objets S3 (assets, backups, exports) | Interface `ObjectStore` — swappable vers S3 réel | Trimestrielle |
| `microsoft/playwright` | Tests E2E + captures pour critique visuelle | Helpers `e2e/` ; mêmes captures consommées par le Vision Critic | Mensuelle |
| `open-telemetry/collector` | Traces, logs, métriques | SDK OTel derrière `packages/telemetry` | Trimestrielle |
| `prometheus` + `grafana` | Surveillance, alertes | Dashboards versionnés dans `infra/observability` | Trimestrielle |

### 6.3 — Les 8 règles d'hygiène des dépendances

1. **Jamais `latest`.** Lockfiles committés ; images Docker par *digest* `sha256:`.
2. **Un fichier `THIRDPARTY.md`.** Par brique : version, pourquoi, mainteneur interne nommé, cadence d'upgrade, checklist de test pré-upgrade, plan de sortie.
3. **Zéro fork du cœur.** Besoin non couvert → contribution amont ou ajout dans *notre* couche d'adaptation. Fork local = ADR + date de dé-fork obligatoires.
4. **Un smoke test maison par brique critique**, bloquant en CI : Temporal → un workflow paiement de bout en bout ; `packages/llm` → `check:llm` (appel structuré mocké + mesure du cache) ; LangGraph → `services/agents/check.py` (graphe interrompu puis repris) ; outils réels → `check_adapters.py` ; OpenHands → `check_openhands.py` (versions alignées, image épinglée par digest).
5. **Renovate/Dependabot en PR groupées hebdo.** Auto-merge autorisé *seulement* pour les patchs non critiques qui passent toute la CI. Jamais sur litellm, temporal, langgraph, SDK Genius Pay.
6. **Vendoring seulement pour un patch porté en amont** (`vendor/` + lien vers la PR upstream).
7. **Un `README` « golden path » par service** : une commande pour lancer en local, une pour les tests, une pour les migrations. Un nouveau contributeur démarre en < 15 min ou c'est un bug.
8. **Séparation stricte des rôles d'orchestration** : Temporal pour l'argent et le provisioning ; LangGraph pour le raisonnement d'agents. Jamais de logique de paiement dans un graphe d'agent.

> **Le vrai levier qualité** : `packages/contracts`. Le schéma `Blueprint JSON` y est défini une fois ; front (Zod) et back (Pydantic) en dérivent. Un validateur rejette tout JSON non conforme *avant* qu'un workflow démarre ([doc 06 §5](06-architecture-technique.md#5-pipeline-prompt--production)). Frontière typée et testée = front et back avancent en parallèle sans se casser.

---

## 7. Le pipeline prompt → production

Chaque étage a un propriétaire et une gate. Rien ne passe à l'étage suivant tant que la gate n'est pas verte ([doc 06 §4-5](06-architecture-technique.md#4-les-agents-du-pipeline), ajout Vision Critic [deep 04 §2B](../deeprecherche_important/04-application-a-afrosite.md#b-ajouter-une-boucle-de-critique-visuelle-par-capture-décran-pas-seulement-par-lecture-de-code)).

| # | Étage | Gate | Propriétaire |
|---|---|---|---|
| 01 | Prompt → `Blueprint JSON` (Intent + Product Architect) | **G1** : schéma conforme, budget IA sous plafond, pas de donnée sensible | Souraka |
| 02 | Génération dans une branche Git (Code Agent, sandbox) | **G2** : lint/typecheck, tests unitaires, build, zéro secret | SERGE |
| 03 | Sécurité (Security Agent : SAST, deps, secrets, RBAC, rate limit, CSRF/XSS/injection) | **G3** bloquante | SERGE |
| 04 | Paiement (Payment Agent : sandbox Genius Pay, webhooks signés, idempotency, montants serveur) | **G4** | SERGE |
| 05 | Tests (QA Agent : unitaires + Playwright E2E) | **G5** : migration testée sur copie, backup vérifié, rollback prêt | Souraka (A) · CHITOU/SERGE (R) |
| 06 | Preview déployée + capture d'écran automatique | — | SERGE |
| 07 | Vision Critic Agent : polish / cohérence / typographie vs critères écrits | Score ≥ seuil, sinon itération ciblée du Code Agent | CHITOU |
| 08 | Validation utilisateur (plan, coût estimé, état en direct, audit trail) | Accord explicite | Souraka |
| 09 | Production | **G6** : confirmation admin, déploiement progressif, monitoring actif, rollback auto | SERGE |

Streaming à chaque étage ; TTFT < 500 ms comme objectif perçu ([deep 01 §3](../deeprecherche_important/01-performance-et-vitesse.md#le-time-to-first-token-ttft-plutôt-que-le-débit-total)).

---

## 8. Système de prompts — pour aller très vite

**Principe.** Un prompt qui va vite est un prompt qui n'oblige pas l'IA à deviner. Il porte **tout** : contexte, objectif, fichiers exacts, contraintes, livrable attendu, **branche à créer**, Definition of Done, et ce qu'il ne faut **pas** faire. Un prompt vague coûte trois allers-retours ; un prompt complet coûte une passe.

**Règle d'équipe :**

1. Tout prompt commence par le **Bloc de contexte Afrosite** (§8.1), collé tel quel.
2. Tout prompt nomme la **branche** à créer ([§5.2](#52--convention-de-nommage)) et la **carte Notion**.
3. Tout prompt finit par la **Definition of Done** applicable (§13) et la section **Ne pas faire**.
4. Le prompt final utilisé est collé dans la carte Notion (propriété *Prompt utilisé*) et, s'il est réutilisable, dans la **Bibliothèque de prompts**.

### 8.0 — Mode opératoire d'une tâche (de la carte au merge)

Neuf étapes. On ne saute pas la 1 ni la 8.

1. **Cadrer la carte.** La carte Notion passe en *Prête* seulement si elle contient : objectif en une phrase, fichiers cibles exacts, contrat concerné, branche nommée, Gate cible, DoD copiée. Si un de ces éléments manque → elle reste en *Backlog*.
2. **Créer la branche.** `git switch -c <type>/<scope>-<slug>` depuis `main` à jour (`git fetch && git switch main && git pull`).
3. **Assembler le prompt.** Bloc de contexte (§8.1) + squelette (§8.2) rempli + le prompt de rôle correspondant (§8.3). Coller le **contenu réel** des contrats et des fichiers concernés dans le prompt — pas juste leurs chemins.
4. **Faire réfléchir l'IA avant de coder.** Terminer le prompt par : *« Avant d'écrire du code : liste tes hypothèses, les fichiers que tu vas toucher, et tes questions. Attends ma validation. »* On répond, puis on dit *« Vas-y. »* Cette passe supprime 80 % des allers-retours.
5. **Travailler en petits incréments.** Un diff par sous-problème, revu au fil de l'eau. On refuse un patch géant : on redemande découpé.
6. **Lancer les vérifications en local.** `pnpm turbo lint typecheck test build` (ou l'équivalent Python `uv run ...`). Rien ne part en PR rouge.
7. **Ouvrir la PR.** Titre en Conventional Commit, description = lien carte Notion + Gate cible + DoD cochée + captures si UI. Squash-merge visé.
8. **Revue par une autre personne** (prompt §8.4 « Revue de PR »). CHITOU relit tout ce qui est visuel ; SERGE relit tout ce qui touche argent, secrets, multi-tenant ; Souraka relit tout ce qui touche le contrat ou l'archi front.
9. **Merger, supprimer la branche, déplacer la carte en *Fait*.** Coller le prompt final dans la carte. S'il resservira → l'ajouter à la Bibliothèque de prompts.

**Instructions « à la pointe » — les 10 réflexes qui changent la vitesse et la qualité :**

- **Contexte complet, pas de résumé.** Colle le schéma, le fichier, l'erreur en entier. L'IA ne devine bien que ce qu'elle voit.
- **Une tâche = un objectif.** Deux objectifs dans un prompt = deux prompts.
- **Demander un plan d'abord, du code ensuite.** Toujours (étape 4).
- **Donner des exemples du repo.** « Suis le style de `services/api/orders/` » vaut mieux que « écris du code propre ».
- **Interdits explicites.** La section *Ne pas faire* évite les dérives (toucher à `main`, ajouter une dépendance, réinventer une couleur).
- **Cibles chiffrées.** « LCP ≤ 2,5 s », « couverture des 4 cas d'échec », pas « performant » ni « bien testé ».
- **Faire écrire les tests par l'IA, mais lire chaque test.** Un test qu'on ne comprend pas est un test faux.
- **Cause racine, jamais contournement.** Interdire « désactive le test » / « augmente le timeout ».
- **Boucler avec la sortie réelle.** Recoller la trace d'erreur, la capture d'écran, le résultat de gate — l'IA corrige sur des faits, pas sur des suppositions.
- **Capitaliser.** Un prompt qui a bien marché devient un modèle dans la Bibliothèque ; on ne réécrit pas deux fois le même.

### 8.1 — Bloc de contexte Afrosite (à coller en tête de CHAQUE prompt)

```
## CONTEXTE AFROSITE — ne jamais omettre
- Produit : plateforme AI-native de création + paiement Mobile Money + exploitation
  quotidienne pour TPE/PME au Bénin (UEMOA). Socle commun + 3 blueprints :
  Commerce, Restaurant, Services. Le socle est le produit, pas le vertical.
- Stack : Next.js + TypeScript (front) · FastAPI + PostgreSQL + Redis (back) ·
  LangGraph (agents) · Temporal (workflows argent/provisioning) · LiteLLM (routeur IA) ·
  Playwright (E2E) · Docker Compose + Coolify (déploiement) · GitHub Actions (CI).
- Monorepo : apps/web · packages/design-system · packages/blueprints ·
  packages/contracts · services/api · services/agents · services/workflows ·
  packages/llm · infra/ · docs/adr/.
- Règles non négociables :
  1. Un prompt n'exécute jamais une action risquée directement (workflow testable,
     réversible, observé ; l'humain valide les actions importantes).
  2. 80 % composants éprouvés / 20 % génération contrôlée.
  3. Afrosite ne détient JAMAIS de fonds. PSP = Genius Pay via la couche
     PaymentProvider. Ledger interne ≠ flux réels. Jamais de PAN/CVV stockés.
  4. La redirection navigateur ne prouve pas un paiement : webhook signé + verify()
     serveur. Idempotency key partout. Montants recalculés serveur.
  5. Streaming systématique de chaque étape vers l'UI.
  6. FCFA & français natifs. Jamais d'USD affiché au client final.
  7. Jamais de push généré sur main : branche + PR + CI + gates.
  8. Tokens sémantiques du design system, jamais de couleur/police en dur.
     Vert (#1F7A53) UNIQUEMENT pour le statut « paiement confirmé ».
  9. Offline-tolerant : file locale + synchro différée pour commande et caisse.
- Marque : Space Grotesk (titres, montants, stats — chiffres tabulaires, jamais
  d'italique) + IBM Plex Sans (interface, texte long). Terracotta #C1502E (CTA),
  Or #D89B3C (accent rare), Charbon #211B17, Sable #F3E7D8.
- Docs de référence : docs/01 → docs/10 + deeprecherche_important/. En cas de doute :
  demander, ne pas inventer.
```

### 8.2 — Squelette de prompt générique

```
[BLOC DE CONTEXTE AFROSITE]

## RÔLE
Tu es <ingénieur front | designer engineering | ingénieur backend> sur Afrosite,
en binôme avec <Souraka | CHITOU | SERGE>.

## OBJECTIF (1 phrase)
<quoi, et pourquoi maintenant>

## PÉRIMÈTRE
- Fichiers à créer / modifier : <chemins EXACTS>
- Contrats à respecter : <packages/contracts/... ou schéma collé ci-dessous>
- Dépend de : <PR / branche / carte Notion>
- Carte Notion : <lien ou id>

## CONTRAINTES
- Règles non négociables applicables : <liste ciblée>
- Perf / a11y / sécurité : <cibles chiffrées si pertinent>

## LIVRABLE
- <diff complet | fichiers | plan | tests>, prêt à ouvrir en PR
- Branche : <type>/<scope>-<slug>  (créée depuis main, à jour)
- Commits : Conventional Commits
- Mets à jour THIRDPARTY.md si tu ajoutes une dépendance

## DEFINITION OF DONE (playbook §13)
- <checklist copiée depuis §13.1 / §13.2 / §13.3>

## NE PAS FAIRE
- Toucher à main. Inventer un contrat non défini. Ajouter une couleur/police
  hors design system. Mettre de la logique de paiement dans un agent.
- <hors-périmètre explicite de cette tâche>
- Si une info manque : liste tes questions AVANT de coder.
```

### 8.3 — Prompts par rôle (bibliothèque)

<details>
<summary><b>Souraka — Étendre le contrat <code>Blueprint JSON</code></b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## RÔLE
Tu es ingénieur produit/plateforme, en binôme avec Souraka.

## OBJECTIF
Étendre le schéma Blueprint JSON pour couvrir <module: ex. kitchen_display> du
blueprint Restaurant, sans casser les blueprints Commerce et Services.

## PÉRIMÈTRE
- Fichiers : packages/contracts/src/blueprint.schema.ts (Zod) + génération Pydantic
- Référence : doc 06 §5 (contrat structuré + gates), doc 01 §5.1 (modules par blueprint)
- Carte Notion : <id>

## CONTRAINTES
- Le socle commun reste identique entre les 3 blueprints (doc 01 §9).
- Tout champ nouveau est optionnel OU a une valeur par défaut rétrocompatible.
- requires_confirmation doit lister toute action irréversible ajoutée.

## LIVRABLE
- Diff du schéma + tests de validation (cas conformes ET cas rejetés)
- Exemple de Blueprint JSON valide pour chaque blueprint
- Branche : chore/contracts-restaurant-kds
- Note de migration si un champ change de forme

## DEFINITION OF DONE (§13.1)
- typecheck OK · tests unitaires sur les cas rejetés · zéro secret
- Zod et Pydantic dérivent de la même source · exemples à jour

## NE PAS FAIRE
- Rendre un champ existant obligatoire. Dupliquer la définition front/back.
```
</details>

<details>
<summary><b>Souraka — Revue d'architecture front-end</b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## RÔLE
Tu es architecte front Next.js, en binôme avec Souraka. Tu proposes, tu ne merges pas.

## OBJECTIF
Passer en revue <PR / dossier> et dire si l'archi tient : SSR/SEO, data-fetching,
frontière avec packages/contracts, perf mobile 3G/4G.

## PÉRIMÈTRE
- Cible : apps/web/<...>
- Référence : doc 08 §2 (SEO natif : SSR, Metadata API, sitemap par tenant, JSON-LD,
  canonical), doc 06 §11 (Core Web Vitals : LCP ≤ 2,5 s, INP < 200 ms, CLS < 0,1)

## LIVRABLE
- Liste de constats classés bloquant / important / mineur, avec le fichier:ligne
- Pour chaque bloquant : le correctif concret
- Aucune modification de code, uniquement le rapport

## NE PAS FAIRE
- Réécrire la PR. Élargir le périmètre au backend.
```
</details>

<details>
<summary><b>Souraka — Construire / étendre l'eval harness des agents</b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## RÔLE
Tu es ingénieur eval/MLOps, en binôme avec Souraka.

## OBJECTIF
Ajouter au harness un jeu de <N> prompts réels du vertical <Commerce|Restaurant|
Services> et le scoring associé, pour détecter les régressions de prompt/modèle.

## PÉRIMÈTRE
- Fichiers : services/agents/eval/<vertical>/*.jsonl + eval/run.py
- Métriques à calculer : conformité Blueprint JSON, coût en crédits, temps
  prompt→preview, score Vision Critic, taux de passage des gates du 1er coup
- Référence : deep 03, deep 04 §2, doc 02 §5 (unit economics)

## LIVRABLE
- Le jeu de prompts + le rapport de baseline (valeurs actuelles)
- Un check CI qui échoue si un indicateur clé régresse au-delà d'un seuil
- Branche : chore/agents-eval-<vertical>

## NE PAS FAIRE
- Inventer des prompts : ils viennent des visites terrain. Marquer TODO si manquants.
```
</details>

<details>
<summary><b>CHITOU — Nouveau composant du design system</b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## RÔLE
Tu es designer engineering, en binôme avec CHITOU. Base technique : shadcn/ui
personnalisé pour porter l'identité Afrosite (doc 06 §11, doc 09).

## OBJECTIF
Créer le composant <Money | PaymentStatus | OrderStatus | DataTable | EmptyState>
dans le design system, utilisable par les 3 blueprints.

## PÉRIMÈTRE
- Fichiers : packages/design-system/src/components/<Nom>/*
- Tokens : n'utiliser QUE les tokens sémantiques de packages/design-system/tokens
- Référence : doc 09 §3 (palette, typo), §3.4 (interdits), §5 (checklist conformité)

## CONTRAINTES
- Space Grotesk pour les montants, chiffres tabulaires, jamais d'italique.
- Vert uniquement pour « paiement confirmé ». Ambre = en attente. Rouge = échec.
- Accessible : rôle ARIA correct, focus visible, contraste ≥ 4,5:1.
- Zéro couleur/px en dur : tout passe par un token.

## LIVRABLE
- Composant + stories/exemples (états : défaut, chargement, erreur, vide)
- Tests : rendu + accessibilité
- Branche : feat/ds-<nom>-component
- Entrée dans la doc du design system

## NE PAS FAIRE
- Dégradé violet/bleu, glassmorphism, carte à barre de couleur à gauche, émoji-icône.
- Réinventer une couleur : si un token manque, le proposer à CHITOU d'abord.
```
</details>

<details>
<summary><b>CHITOU — Nouveau pattern de blueprint</b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## RÔLE
Tu es designer engineering, en binôme avec CHITOU.

## OBJECTIF
Assembler le pattern <POSLayout | KitchenBoard/KDS | QRMenu | MobileCheckout |
RestaurantDashboard | AgendaRDV> à partir des composants existants du design system.

## PÉRIMÈTRE
- Fichiers : packages/design-system/src/patterns/<Nom>/*
- Données : props typées depuis packages/contracts (pas de type maison)
- Référence : doc 06 §11, doc 01 §5.1 (modules par blueprint)

## CONTRAINTES
- Priorité opérationnelle visible d'un coup d'œil (ce qui est en retard, en attente
  de paiement, à préparer). Utilisable sur mobile Android, réseau lent.
- États offline : file locale + bandeau « synchro en attente ».

## LIVRABLE
- Le pattern + un écran de démo alimenté par des données d'exemple réalistes
- Captures Playwright pour la boucle de critique visuelle
- Branche : feat/ds-pattern-<nom>

## NE PAS FAIRE
- Créer de nouveaux composants de base ici (les demander en amont).
```
</details>

<details>
<summary><b>CHITOU — Critique visuelle d'un écran (rôle Vision Critic)</b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## RÔLE
Tu es UI Critic. Tu REGARDES la capture d'écran fournie et tu évalues le rendu,
pas le code.

## ENTRÉE
- Capture(s) : <jointe(s)>
- Écran : <nom>, blueprint <vertical>, contexte d'usage <ex. caisse le soir>

## CRITÈRES (ordre de fréquence des défauts — deep 02 §2)
1. Polish visuel : espacement, alignement, raffinement
2. Cohérence : les composants se ressemblent-ils entre eux
3. Typographie : polices, tailles, lisibilité (accents français, petit écran)
+ Détecter et REJETER : dégradé violet/bleu, glassmorphism, carte à barre gauche,
  Inter/Roboto/Arial, émoji-icône, vert hors « paiement confirmé », montants en
  italique ou non tabulaires, dashboard sans priorité opérationnelle, contraste < 4,5:1.

## SORTIE
- Score /10 par critère + score global
- Liste des problèmes précis (zone + quoi + correction attendue)
- Verdict : PASSE (≥ seuil) ou ITÉRER (points exacts pour le Code Agent)

## NE PAS FAIRE
- Feedback vague type « améliore le design ». Chaque point est actionnable.
```
</details>

<details>
<summary><b>SERGE — Nouvel endpoint API + migration</b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## RÔLE
Tu es ingénieur backend FastAPI, en binôme avec SERGE.

## OBJECTIF
Créer l'endpoint <MÉTHODE /chemin> de <module>, avec sa migration et son RBAC.

## PÉRIMÈTRE
- Fichiers : services/api/<module>/{router,service,repository,schemas}.py
  + migration Alembic
- DTO : importés de packages/contracts (générés), jamais redéfinis
- Multi-tenant : toute requête filtrée par tenant_id ; jamais de fuite inter-tenant

## CONTRAINTES
- RBAC : rôles owner/cashier/kitchen/customer selon le blueprint
- Montants : recalculés serveur, jamais reçus du client
- Idempotency-Key acceptée sur les écritures sensibles
- Observabilité : trace OTel + log structuré (sans donnée personnelle en clair)
- Migration réversible, testée sur copie

## LIVRABLE
- Diff complet + tests (nominal, non autorisé, tenant croisé, idempotence)
- Branche : feat/api-<module>-<slug>
- THIRDPARTY.md mis à jour si nouvelle dépendance

## DEFINITION OF DONE (§13.1)
- lint/typecheck/build · tests · zéro secret · CodeQL/Semgrep sans alerte haute
- migration réversible testée

## NE PAS FAIRE
- Écrire « payé » sans verify() serveur. Stocker un secret. Toucher à main.
```
</details>

<details>
<summary><b>SERGE — Workflow Temporal (paiement / provisioning)</b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## RÔLE
Tu es ingénieur backend Temporal, en binôme avec SERGE.

## OBJECTIF
Implémenter le workflow <ex. ConfirmPaymentWorkflow> : de la réception du webhook
Genius Pay à l'écriture « payé » dans le ledger + notification WhatsApp.

## PÉRIMÈTRE
- Fichiers : services/workflows/<nom>/{workflow,activities}.py
- Le SDK Temporal ne contient AUCUNE logique métier : tout est dans des activities
  maison idempotentes.
- Référence : doc 06 §6 (architecture paiement), §5 (gate 4), §10 (système de confiance)

## CONTRAINTES
- Idempotent de bout en bout (rejeu du webhook, double livraison, retard).
- verify() serveur avant toute écriture « payé ».
- Retry avec backoff sur les appels PSP ; timeout explicite ; compensation définie.
- Ledger append-only : jamais d'UPDATE, seulement de nouvelles entrées.
- Tout est tracé dans l'audit trail (prompt/plan/outil/résultat/horodatage).

## LIVRABLE
- Workflow + activities + tests (succès, échec PSP, double webhook, webhook en retard,
  remboursement) sur environnement sandbox
- Smoke test de bout en bout ajouté à la CI
- Branche : feat/wf-<nom>

## NE PAS FAIRE
- Confirmer un paiement sur le seul retour de redirection navigateur.
- Mettre la logique dans le workflow plutôt que dans des activities.
```
</details>

<details>
<summary><b>SERGE — Intégration Genius Pay derrière <code>PaymentProvider</code></b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## RÔLE
Tu es ingénieur paiement, en binôme avec SERGE.

## OBJECTIF
Implémenter GeniusPayProvider (implémentation de l'interface PaymentProvider) en
SANDBOX : createTransaction, verify, handleWebhook, refund, reconcile.

## PÉRIMÈTRE
- Fichiers : services/api/payments/providers/geniuspay.py + tests + fixtures
- Interface : services/api/payments/provider.py (ne pas la modifier sans ADR)
- Doc Genius Pay : <lien interne / fichier> — mapper chaque méthode sur l'API réelle
- Référence : playbook §10, doc 06 §6

## CONTRAINTES
- Clés sandbox/prod en secret (variables Coolify), jamais en base, jamais loggées.
- Signature webhook vérifiée avec le secret Genius Pay ; payload non signé rejeté + loggé.
- Idempotency-Key sur createTransaction ; un rejeu renvoie la transaction existante.
- Montant pris depuis la commande serveur, pas depuis la requête.
- Aucun PAN/CVV nulle part (logs, base, traces, Sentry) — scrubbing vérifié.

## LIVRABLE
- L'implémentation + tests des 8 cas : succès, échec, expiration, double webhook,
  webhook en retard, remboursement total, remboursement partiel, écart de réconciliation
- Runbook « paiement bloqué » : diagnostic, contact Genius Pay, remboursement manuel
- Branche : feat/pay-geniuspay-sandbox

## NE PAS FAIRE
- Activer les clés PRODUCTION (interdit avant audit externe + gate 6 — playbook §14).
- Contourner l'interface PaymentProvider.
```
</details>

<details>
<summary><b>SERGE — Nouvel agent LangGraph</b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## RÔLE
Tu es ingénieur agents, en binôme avec SERGE.

## OBJECTIF
Implémenter l'agent <Intent | Product Architect | Code | Security | QA | Deployment |
Payment | Observability | Cost> selon le tableau doc 06 §4.

## PÉRIMÈTRE
- Fichiers : services/agents/<nom>/{graph,tools,prompts}.py
- LLM : via packages/llm uniquement (generate/stream), jamais litellm en direct
- Référence : doc 06 §4 (mission, sortie, "peut agir seul ?"), §9 (routage modèle)

## CONTRAINTES
- Jeton temporaire et limité + liste blanche d'outils pour cet agent.
- Toute entrée externe (web, PDF, user) = non fiable : jamais injectée dans un
  contexte à privilèges.
- Streaming du statut à chaque étape.
- L'agent respecte sa colonne "peut agir seul ?" : sinon, il s'arrête et demande
  validation.

## LIVRABLE
- Le graphe + outils + prompts + tests (nominal, échec outil, reprise après crash)
- Ajout au harness d'eval (§8.3, prompt Souraka)
- Branche : feat/agents-<nom>

## NE PAS FAIRE
- Donner à l'agent un accès plus large que sa liste blanche.
- Mettre de la logique de paiement ici (c'est un workflow Temporal).
```
</details>

### 8.4 — Prompts transverses

<details>
<summary><b>Revue de PR</b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## RÔLE
Tu es relecteur. Tu produis un rapport, tu ne modifies rien.

## ENTRÉE
- PR / diff : <lien ou collé>
- Definition of Done applicable : §13.<1|2|3>

## SORTIE
- Constats classés bloquant / important / mineur, avec fichier:ligne
- Vérifie explicitement : zéro secret, tokens sémantiques (pas de couleur en dur),
  multi-tenant sans fuite, montants recalculés serveur, migration réversible,
  tests présents, textes en français orientés résultat, PR < ~400 lignes
- Verdict : APPROUVÉ / CHANGEMENTS DEMANDÉS
```
</details>

<details>
<summary><b>Debug d'un test qui casse</b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## OBJECTIF
Le test <nom> échoue : <trace collée>. Trouver la cause racine, pas un contournement.

## ATTENDU
1. Hypothèse de cause racine + comment tu la confirmes
2. Le correctif minimal (diff)
3. Un test de non-régression si le cas n'était pas couvert
## NE PAS FAIRE
- Désactiver le test. Augmenter un timeout sans justification. Élargir le périmètre.
```
</details>

<details>
<summary><b>Écrire les tests manquants</b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## OBJECTIF
Couvrir <fichier/module> : chemins nominaux + cas limites + cas d'échec.

## ATTENDU
- Tests unitaires sur la logique ; E2E Playwright si un parcours utilisateur change
- Cas obligatoires : non autorisé, tenant croisé, idempotence, panne PSP (si paiement),
  mode offline (si commande/caisse)
- Branche : test/<scope>-<slug>
```
</details>

<details>
<summary><b>Rédiger un ADR</b></summary>

```
[BLOC DE CONTEXTE AFROSITE]

## OBJECTIF
Rédiger docs/adr/NNNN-<titre>.md pour la décision : <sujet>.

## FORMAT (court, 1 page max)
- Contexte : le problème, les contraintes
- Options envisagées : 2 à 4, avec le pour/contre de chacune
- Décision : laquelle, et pourquoi
- Conséquences : ce que ça implique, ce qu'on devra revisiter, docs à mettre à jour
```
</details>

### 8.5 — Anti-patterns de prompt (à bannir)

| Anti-pattern | Pourquoi c'est lent | À la place |
|---|---|---|
| « Fais-moi le module commandes » | L'IA invente le contrat, le schéma, les rôles | Coller le schéma `packages/contracts`, la liste des fichiers, les rôles RBAC |
| Pas de branche indiquée | Code posé n'importe où, PR impossible à cadrer | Nommer la branche `<type>/<scope>-<slug>` dans le prompt |
| Pas de « Ne pas faire » | L'IA élargit le périmètre, touche à `main`, ajoute des deps | Section **NE PAS FAIRE** systématique |
| Pas de DoD | On redécouvre les manques en revue | Coller la checklist §13 dans le prompt |
| Prompt sans le bloc de contexte | L'IA re-propose du violet/bleu, de l'USD, du CSR | Bloc §8.1 en tête, toujours |
| « Améliore le design » | Feedback non actionnable | Critères écrits du Vision Critic (§8.3) |

---

## 9. Plan 90 jours, par personne

Aligné sur le [doc 07](07-plan-execution-90-jours.md). Objectif : 5 pilotes à Cotonou (2 restaurant, 2 commerce, 1 service) utilisant Afrosite **tous les jours**, paiement réel, à J+90.

### Phase 1 — Fondation fiable · Jours 1 → 30

> But : le socle commun + 3 blueprints existent, testés, déployables. Aucune IA générative encore.

| Qui | Livrables | Branches |
|---|---|---|
| **Souraka** | Domaine + identité arrêtés · schéma `Blueprint JSON` v1 · archi front Next.js (SSR, Metadata API, sitemap par tenant — [doc 08 §2](08-seo-et-clonage-de-sites.md#2-exigences-techniques-à-intégrer-nativement-dans-chaque-blueprint)) · liste des 100 établissements cibles · plan d'instrumentation des coûts | `chore/contracts-blueprint-schema-v0` · `feat/web-skeleton-ssr` · `docs/cost-instrumentation-plan` · `docs/target-list-cotonou` |
| **CHITOU** | Design system v1 : foundations + tokens sémantiques + 12 composants de base · 3 patterns clés (POSLayout, QRMenu, MobileCheckout) · charte de critique visuelle écrite | `feat/ds-tokens` · `feat/ds-core-components` · `feat/ds-pattern-poslayout` · `feat/ds-pattern-qrmenu` · `feat/ds-pattern-mobilecheckout` · `docs/visual-identity-rules` |
| **SERGE** | Monorepo + CI (tests, CodeQL, scan secrets/deps, preview par PR) · PostgreSQL + sauvegardes quotidiennes testées + logs centralisés · socle API (auth/RBAC, catalogue, commande/réservation, CRM léger, dashboard) · **Genius Pay sandbox** derrière `PaymentProvider` · politiques de permissions + règles des 6 gates | `chore/infra-monorepo-bootstrap` · `chore/infra-github-actions` · `feat/api-auth-rbac` · `feat/api-core-schema` · `feat/api-catalog` · `feat/api-orders` · `feat/pay-paymentprovider-interface` · `feat/pay-geniuspay-sandbox` · `chore/infra-thirdparty-inventory` |

**Gate de sortie phase 1 :** les 3 blueprints partagent un socle *identique en code* (seuls les modules spécifiques diffèrent — [doc 01 §9](01-cahier-des-charges.md#9-critères-dacceptation-du-mvp)) ; une commande crée un tenant de démo fonctionnel ; un paiement sandbox est réconcilié automatiquement.

### Phase 2 — Automatisation IA · Jours 31 → 60

| Qui | Livrables | Branches |
|---|---|---|
| **Souraka** | Intent Agent + Product Architect Agent : prompt → `Blueprint JSON` validé · eval harness (30+ prompts réels par vertical, scoring auto) · écran de validation client + audit trail lisible · cache de prompts par défaut sur `packages/llm` · vente terrain : 15–25 visites/semaine | `feat/agents-intent` · `feat/agents-product-architect` · `chore/agents-eval-commerce` · `chore/agents-eval-restaurant` · `chore/agents-eval-services` · `feat/web-validation-audittrail` · `chore/llm-prompt-cache-default` |
| **CHITOU** | Vector Critic Agent branché sur les captures Playwright · itération design system → 3 blueprints « polis dès la sortie » · patterns restants (KitchenBoard/KDS, Agenda RDV, suivi livraison) · check Core Web Vitals intégré aux gates | `feat/agents-vision-critic` · `feat/ds-pattern-kitchenboard` · `feat/ds-pattern-agenda-rdv` · `feat/ds-pattern-delivery` · `chore/infra-cwv-gate` |
| **SERGE** | Blueprint → branche Git → génération contrôlée (Code Agent, sandbox) · Security Agent + correction auto avant merge · génération + exécution Playwright auto · preview auto après chaque génération · workflows Temporal : provisioning tenant, cycle de vie webhook paiement · installation des 5 pilotes en sandbox de paiement | `feat/agents-code` · `feat/agents-security` · `feat/agents-qa` · `feat/agents-deployment` · `feat/wf-provision-tenant` · `feat/wf-confirm-payment` · `feat/infra-preview-auto` |

**Gate de sortie phase 2 :** un prompt réel produit une preview fonctionnelle et « propre » en < 5 min sans intervention manuelle ; les 6 gates s'exécutent automatiquement ; usage quotidien mesuré chez au moins 3 pilotes en sandbox.

### Phase 3 — Commercialisation · Jours 61 → 90

| Qui | Livrables | Branches |
|---|---|---|
| **Souraka** | Mesure : coût IA/client, coût cloud, temps de support, rétention J+30 · ajustement crédits & plafonds sur coûts réels · vente des frais de lancement puis abonnement · ≥ 3 témoignages sur 5 pilotes · décision du/des vertical(aux) à approfondir | `feat/web-cost-dashboard` · `chore/llm-quotas-tuning` · `docs/phase2-vertical-decision` |
| **CHITOU** | Passe finale de polish sur les écrans à fort usage (prise de commande, KDS, réconciliation du soir) · résumé quotidien WhatsApp lisible · boucle d'apprentissage UX : 1 variante A/B documentée | `fix/ds-polish-highusage` · `feat/ds-whatsapp-daily-summary` · `spike/ux-abtest-<sujet>` |
| **SERGE** | Bascule des 5 pilotes en **production paiement réel** après tests webhooks + remboursement + réconciliation · activation Mobile Money par tenant validé · résumé quotidien WhatsApp au gérant · export CSV en libre-service · monitoring + alertes paiement/base/déploiement · **audit sécurité externe passé** | `feat/pay-geniuspay-production` · `feat/wf-daily-summary-whatsapp` · `feat/api-csv-export` · `chore/infra-alerting` · `chore/security-external-audit-fixes` |

**Décision de fin de phase ([doc 07](07-plan-execution-90-jours.md)) :** les 5 pilotes utilisent-ils Afrosite tous les jours ? Oui → répliquer le playbook commercial. Non → diagnostiquer avant d'ajouter la moindre fonctionnalité.

### À ne pas faire pendant ces 90 jours

- Ajouter un 4ᵉ blueprint avant d'avoir validé les 3 premiers.
- Activer une clé PSP en production avant d'avoir testé webhooks, échecs et remboursements en sandbox.
- Construire Kubernetes, Vault ou un cluster GPU.
- Donner un accès IA illimité sur l'offre gratuite.
- Pousser du code généré sur `main` sans branche + revue.

---

## 10. Paiement — Genius Pay

> **Décision d'équipe à consigner (ADR 0001).** Les [docs 03 §5](03-analyse-concurrentielle.md#5-concurrence-paiement--le-combat-le-plus-stratégique), [06](06-architecture-technique.md) et [10 §F](10-ressources-de-a-a-z.md#f--paiement-mobile-money-béninuemoa) nomment KKiaPay / FedaPay / CinetPay. **Décision :** Genius Pay devient le PSP *primaire* du MVP (clés API + doc en main). Il s'intègre derrière la couche `PaymentProvider` pour que FedaPay/KKiaPay restent des *fallback* activables (routage multi-PSP prévu en Phase 2 — [doc 01 §5.2](01-cahier-des-charges.md#52-phase-2-3-9-mois--approfondissement-et-nouveaux-verticaux)). **Action Souraka :** ouvrir l'ADR et mettre à jour docs 03 §5, 06 §5-6, 10 §F pour cohérence.

### 10.1 — Ce qui ne change pas, quel que soit le PSP

- Afrosite n'est jamais dépositaire de fonds. Orchestration au-dessus d'un acteur agréé BCEAO.
- Aucune donnée de carte (PAN/CVV) ne transite ou n'est stockée chez nous — champs/pages hébergés du PSP uniquement.
- La redirection navigateur ne prouve jamais le paiement. Seuls le webhook signé **et** la vérification serveur du statut le confirment.
- Ledger interne immuable, distinct des flux réels. Réconciliation quotidienne : encaissé par canal (cash, MoMo, carte), impayés.

### 10.2 — La couche `PaymentProvider` (contrat maison)

Toute la logique métier parle à cette interface, jamais au SDK Genius Pay directement. Changer de PSP = une seule implémentation à écrire.

| Méthode | Rôle | Garde-fous |
|---|---|---|
| `createTransaction(order, idemKey)` | Crée la transaction serveur, renvoie référence + handle de checkout | Montant recalculé serveur ; `idemKey` obligatoire ; devise XOF |
| `verify(reference)` | Interroge le PSP pour le statut réel | Appelé avant toute écriture « payé » ; jamais confiance au retour client |
| `handleWebhook(payload, signature)` | Vérifie la signature, normalise l'événement | Rejet si signature invalide ; rejeu idempotent ; horloge tolérante |
| `refund(reference, amount, reason)` | Remboursement total ou partiel | Confirmation admin explicite ; tracé dans l'audit trail |
| `reconcile(dateRange)` | Rapproche transactions PSP ↔ ledger interne | Job quotidien ; alerte si écart > 0 |

### 10.3 — Séquence d'un encaissement

1. Client valide le panier → **API Afrosite** crée une transaction serveur (montant recalculé, `idemKey`).
2. Redirection vers la page / le SDK sécurisé de **Genius Pay**.
3. Client paie (MTN MoMo / Moov Money). Le navigateur revient — statut affiché « en attente ».
4. Webhook signé Genius Pay → **workflow Temporal** : vérifie signature, appelle `verify()`, écrit dans le ledger.
5. Transaction marquée **paiement confirmé** · notification WhatsApp au gérant.
6. Job de réconciliation du soir : PSP ↔ ledger, tout écart lève une alerte.

### 10.4 — Checklist d'intégration (SERGE, avant Gate 4)

- [ ] Clés sandbox et production stockées en secret (jamais en base, jamais dans un prompt, jamais côté client).
- [ ] `createTransaction` recalcule le montant serveur ; le montant client est ignoré.
- [ ] `idemKey` unique par tentative ; un rejeu renvoie la transaction existante, ne recrée rien.
- [ ] Signature du webhook vérifiée avec le secret Genius Pay ; payload non signé rejeté et loggé.
- [ ] Webhook idempotent : recevoir deux fois le même événement ne double pas l'écriture ledger.
- [ ] Statut confirmé uniquement après `verify()` serveur — jamais sur le seul retour de redirection.
- [x] Cas testés en sandbox : succès, échec, expiration, double webhook, webhook en retard, remboursement total, remboursement partiel. → `pnpm check:pay`
- [x] Réconciliation quotidienne implémentée ; écart PSP/ledger → alerte. → `reconcile()` + écarts `pending`
- [ ] Aucune donnée PAN/CVV dans les logs, la base, les traces ou Sentry (scrubbing vérifié).
- [x] Runbook « paiement bloqué » écrit : diagnostic, contact Genius Pay, remboursement manuel. → `docs/runbook-paiement-bloque.md`
- [ ] Passage prod = approbation explicite ([doc 06](06-architecture-technique.md#gates-à-bloquer-automatiquement) gate 6) + audit externe passé (§14).

---

## 11. Design system & critique visuelle

Propriétaire : CHITOU. La qualité visuelle vient d'une **boucle générateur → critique** avec vision réelle du rendu ([deep 02](../deeprecherche_important/02-design-visuel-ia.md)), pas d'un meilleur prompt.

### 11.1 — Structure ([doc 06 §11](06-architecture-technique.md#11-design-system-et-direction-artistique))

```
/foundations   colors, typography, spacing, shadows, motion
/tokens        tokens.json, semantic-tokens.json   (ex. --status-payment-confirmed)
/components    Button, Input, Card, DataTable, EmptyState, PaymentStatus, OrderStatus, Money
/patterns      RestaurantDashboard, POSLayout, KitchenBoard, QRMenu, MobileCheckout
/rules         ux-principles.md, accessibility.md, responsive.md, visual-identity.md
```

### 11.2 — Les 4 agents de conception

Product Agent (besoin) · UX Agent (parcours) · Art Director Agent (palette, ton, contraintes) · UI Critic Agent (rejet). **Séparer la direction artistique de l'exécution** — les mélanger produit le « design IA générique ».

### 11.3 — Critères de rejet écrits ([doc 09 §3.4](09-branding-logo-positionnement.md#34-ce-que-la-marque-refuse-par-principe))

- Dégradé violet/bleu par défaut, glassmorphism décoratif, carte à barre de couleur à gauche.
- Polices hors marque (Inter, Roboto, Arial). Marque = Space Grotesk (titres, montants, stats) + IBM Plex Sans (interface, texte long).
- Émoji comme icône fonctionnelle. Icônes au trait, grille 24 px, trait 1,75 px.
- Vert utilisé ailleurs que pour le statut « paiement confirmé ».
- Montants pas en chiffres tabulaires, ou en italique.
- Dashboard sans priorité opérationnelle ; contraste < 4,5:1 ; cartes répétitives sans hiérarchie.
- Photo de banque d'images corporate au lieu d'une personne réelle en activité.

### 11.4 — La boucle ([deep 04 §2B](../deeprecherche_important/04-application-a-afrosite.md#b-ajouter-une-boucle-de-critique-visuelle-par-capture-décran-pas-seulement-par-lecture-de-code))

1. Code Agent génère l'écran **à partir du design system** (pas d'une page blanche).
2. Déploiement preview → capture d'écran automatique Playwright.
3. Vision Critic Agent lit l'image : polish visuel → cohérence → typographie (ordre de fréquence des défauts).
4. Score insuffisant → itération **ciblée** du Code Agent sur les points relevés.
5. Score OK → validation utilisateur.

Boucle d'apprentissage : mesurer temps de tâche, abandon, erreurs, questions support → hypothèse UX → variante → A/B → décision **documentée dans le design system**.

---

## 12. Data, coûts IA & recherche

Propriétaire : Souraka. La compétitivité IA d'Afrosite ne vient pas du modèle mais de l'ingénierie produit autour ([deep 04 §3](../deeprecherche_important/04-application-a-afrosite.md#3-ce-qui-reste-hors-de-portée--et-pourquoi-ce-nest-pas-grave)).

### 12.1 — Instrumenter dès le jour 1 ([doc 02 §5](02-business-model.md#5-unit-economics))

- Coût par génération / prompt (tokens IA), attribué au tenant.
- Coût stockage + bande passante par projet actif.
- Coût des environnements de preview.
- Coût SMS / WhatsApp / email par notification.
- Temps de support humain par ticket.
- Frais PSP — jamais absorbés sans refacturation transparente.

Cible : marge brute ≥ 70 %. Client Business à 15 000 FCFA/mois → coût variable direct ≤ 4 500–6 000 FCFA/mois. Au-delà : crédits additionnels, modèle plus léger, ou traitement asynchrone.

### 12.2 — Routage IA ([doc 06 §9](06-architecture-technique.md#9-système-de-réponse-rapide-routage-ia))

| Tâche | Classe de modèle |
|---|---|
| Classification d'intention, résumé, extraction, traduction, reformulation de menu | Modèle léger / peu coûteux |
| Architecture produit, plan complexe, débogage difficile, revue de code | Modèle puissant (raisonnement étendu activé) |
| Composants, migrations, tests, APIs, corrections | Modèle spécialisé code |
| Tâches répétitives + données sensibles (quand le volume le justifie) | Modèle local / open source |

Fallback via LiteLLM vers un second fournisseur ou un modèle local. Décodage spéculatif : souvent déjà activé côté API — le vérifier, pas le réimplémenter.

### 12.3 — Eval harness

- 30+ prompts réels par vertical (collectés en visites terrain), rejoués à chaque changement d'agent ou de modèle.
- Scoring : conformité du `Blueprint JSON`, coût en crédits, temps prompt → preview, score Vision Critic, taux de passage des gates du premier coup.
- Un changement de prompt/modèle qui fait régresser un indicateur clé est **bloqué comme une régression de code**.

### 12.4 — Cadence de recherche

Une demi-journée par semaine. Tenir à jour `deeprecherche_important/`. Toute info qui contredit une décision d'archi ouvre un ADR. Sujets ouverts : PI-SPI (BCEAO, paiements instantanés interopérables), SDK d'agents de code, coûts d'inférence, KYC/AML UEMOA.

---

## 13. Qualité — Definition of Done

### 13.1 — DoD d'une PR

- [ ] Lint + typecheck + build verts.
- [ ] Tests unitaires sur la logique ajoutée ; E2E si un parcours utilisateur change.
- [ ] Zéro secret (TruffleHog / scan CI). Aucune clé dans le code, les tests, les fixtures.
- [ ] CodeQL + Semgrep sans nouvelle alerte haute.
- [ ] Migration réversible et testée sur copie si le schéma change.
- [ ] Pas de couleur/police hors design system ; tokens sémantiques utilisés.
- [ ] Textes en français, orientés résultat, sans jargon ([voix doc 09 §4.5](09-branding-logo-positionnement.md#45-ton-de-marque-voix)).
- [ ] Relue par une autre personne. PR < ~400 lignes si possible.
- [ ] ADR joint si la PR change une décision d'architecture.

### 13.2 — DoD d'un blueprint

- [ ] Socle commun *identique en code* aux deux autres blueprints ; seuls les modules spécifiques diffèrent ([doc 01 §9](01-cahier-des-charges.md#9-critères-dacceptation-du-mvp)).
- [ ] SSR + Metadata API + sitemap par tenant + JSON-LD Schema.org + canonical auto ([doc 08 §2](08-seo-et-clonage-de-sites.md#2-exigences-techniques-à-intégrer-nativement-dans-chaque-blueprint)).
- [ ] Core Web Vitals : LCP ≤ 2,5 s, INP < 200 ms, CLS < 0,1 sur mobile 3G/4G.
- [ ] Mode dégradé testé : coupure réseau → file locale → synchro différée.
- [ ] Parcours paiement sandbox complet vert (les 8 cas du §10.4).
- [ ] Export CSV (transactions, clients, ventes) sans support technique.
- [ ] Résumé quotidien WhatsApp généré.
- [ ] Score Vision Critic au-dessus du seuil ; passe la [checklist de conformité charte (doc 09 §5)](09-branding-logo-positionnement.md#5-checklist-de-conformité--à-utiliser-avant-toute-publication-externe).

### 13.3 — Go-live d'un pilote

- [ ] Webhooks, remboursement et réconciliation testés en sandbox.
- [ ] Audit sécurité externe passé (au moins pour le périmètre paiement).
- [ ] Sauvegarde restaurée avec succès au moins une fois (pas seulement « le backup tourne »).
- [ ] Rollback répété à blanc.
- [ ] Monitoring + alertes paiement / base / déploiement actifs.
- [ ] Formation de l'équipe du client faite ; canal WhatsApp de support ouvert.
- [ ] Runbook incident accessible aux 3 membres.

---

## 14. Sécurité — responsabilités

Règles non négociables ([doc 06 §6](06-architecture-technique.md#6-sécurité--règles-non-négociables)) :

```
Prompt ≠ permission illimitée.      IA ≠ accès root.
Génération ≠ déploiement production. Succès du code ≠ sécurité validée.
Paiement initié ≠ paiement confirmé.
```

| Sujet | Propriétaire | Attendu |
|---|---|---|
| Secrets | SERGE | Aucun secret en base ni dans un prompt. Variables Coolify au MVP → Vault quand le volume le justifie. Rotation, révocation à la déconnexion. |
| Isolation des agents | SERGE | Jeton temporaire et limité par agent, liste blanche d'outils, sandbox Docker/Firecracker pour tout code généré. |
| Injection de prompt | Souraka | Toute donnée externe (web, PDF, email, utilisateur) = non fiable. Jamais injectée telle quelle dans un contexte à privilèges. |
| Confirmation humaine | SERGE | Obligatoire : déploiement prod, paiements live, emails massifs, suppression, changement d'accès. |
| Audit trail | SERGE | Complet : prompt, plan, outils exécutés, version de code, test, auteur, résultat, horodatage. |
| Scans CI | SERGE | SAST (CodeQL, Semgrep), scan dépendances, scan secrets (TruffleHog) à chaque déploiement. ZAP sur les previews. |
| Audit externe | Souraka (budget) | Audit tiers du périmètre paiement + auth **avant** l'activation des clés Genius Pay en production. |
| Conformité BCEAO | Souraka | Afrosite reste orchestrateur, jamais dépositaire de fonds. Ledger interne séparé des flux. Consentement + journalisation RGPD-like. |

Référentiel de base : [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) comme checklist minimale du MVP ([doc 10 §H](10-ressources-de-a-a-z.md#h--sécurité)).

---

## 15. Risques & propriétaire

| Risque | Signal d'alerte | Mitigation | Propr. |
|---|---|---|---|
| Coûts IA non gouvernés | Coût variable/client > 6 000 FCFA récurrent | Quotas, crédits, routage modèle léger, cache de prompts, tâches asynchrones | S |
| Dépendance à un seul PSP | Panne / lenteur Genius Pay | Couche `PaymentProvider` prête pour FedaPay/KKiaPay en fallback | SERGE |
| Effectif : pas de SRE/QA/MLOps dédié | Incident prod non couvert > 2 h | Infra légère (Coolify), QA outillée bloquante, audit externe, runbooks | SERGE |
| Dérive de périmètre (4ᵉ blueprint tôt) | Demande client / tentation interne | Règle 3 blueprints max ; tout vertical se valide d'abord sur le socle | S |
| Dette de fork open source | Un patch local sans date de dé-fork | `THIRDPARTY.md`, contribution amont, ADR obligatoire pour tout fork | SERGE |
| « Slop » visuel IA | Vision Critic sous le seuil de façon répétée | Critères de rejet écrits, Art Director distinct de l'exécution | CHITOU |
| Réseau instable côté client | Commandes perdues, caisse figée | Mode dégradé testé : file locale + synchro différée | SERGE |
| Rétention faible malgré la croissance | Usage quotidien < 5 j/7 chez un pilote | Diagnostiquer avant d'ajouter des fonctionnalités ([doc 07](07-plan-execution-90-jours.md)) | S |
| Changement réglementaire BCEAO | Communication BCEAO / PSP | Ne jamais détenir les fonds ; veille réglementaire hebdo | S |
| Concurrent « OS pour PME » entre en UEMOA francophone | Annonce Moniepoint/Orda ou Yoco/Dyner sur la zone | Vitesse d'implantation + moat distribution/paiement/données local | S |

---

## 16. Cette semaine — action par personne

Sept jours. À la fin : le dépôt existe, la CI tourne, le contrat de blueprint est écrit, le design system a démarré, Genius Pay répond en sandbox.

### Souraka — cadre & frontière

- [x] Ouvrir l'**ADR 0001** « Genius Pay = PSP primaire » + MAJ docs 03/06/10 (et 00/01/02).
- [ ] Créer l'espace **Notion** (4 bases : Board, ADR, Risques, Bibliothèque de prompts) et importer §3, §8, §15. *(hors dépôt — à faire dans Notion)*
- [x] Rédiger `packages/contracts` : schéma `Blueprint JSON` v0 (3 verticaux) + validateur Zod/Pydantic. → `chore/contracts-blueprint-schema-v0`
- [x] Poser le squelette `apps/web` (Next.js, SSR, Metadata API, `sitemap.ts` par tenant) + studio hackathon. → `feat/web-skeleton-ssr`
- [x] Eval harness agents (30+ prompts × 3 verticaux) : `pnpm eval:agents` dans `apps/web`.
- [x] Écrire le plan d'instrumentation des coûts. → `docs/cost-instrumentation-plan`
- [x] Commencer la liste des 100 établissements cibles. → `docs/target-list-cotonou`

### CHITOU — design system

- [ ] Créer `packages/design-system` : `tokens.json` + `semantic-tokens.json` depuis la [charte (doc 09 §3)](09-branding-logo-positionnement.md#3-le-branding--système-de-marque). → `feat/ds-tokens`
- [ ] Livrer 6 composants en code : Button, Input, Card, Money, PaymentStatus, OrderStatus. → `feat/ds-core-components`
- [ ] Écrire `/rules/visual-identity.md` : la liste des critères de rejet du Vision Critic. → `docs/visual-identity-rules`
- [ ] Maquette du pattern **MobileCheckout** (le parcours qui touche l'argent). → `feat/ds-pattern-mobilecheckout`

### SERGE — dépôt, CI, PSP sandbox

- [x] Initialiser le monorepo + `docker-compose` (Postgres, Redis, MinIO) + golden-path README. → `chore/infra-monorepo-bootstrap`
- [x] CI GitHub Actions : lint, typecheck, eval, `check:pay`, TruffleHog. (CodeQL + preview PR : ensuite.) → `chore/infra-github-actions`
- [x] Squelette `services/api` : `/health` + `POST /blueprints/validate` (Gate 1 Pydantic). Auth/RBAC + Postgres : ensuite. → `feat/api-core-schema`
- [x] Écrire l'interface `PaymentProvider` + `GeniusPayProvider` (`createTransaction` + `verify` en **sandbox**, fallback démo sans clés). → `feat/pay-paymentprovider-interface`, `feat/pay-geniuspay-sandbox`
- [x] Créer `THIRDPARTY.md` avec les 10 briques prioritaires, versions épinglées. → `chore/infra-thirdparty-inventory`

### Revue vendredi

Démo de trois choses : un tenant vide qui se crée, un composant `Money` rendu depuis les tokens, et un appel Genius Pay sandbox qui revient avec un statut. Si l'un des trois manque, c'est le sujet n°1 de la semaine suivante.

---

> **Playbook d'équipe Afrosite · v1.0 · 30 août 2026.** Dérivé des [docs 01 → 10](00-README.md) et de [`deeprecherche_important/`](../deeprecherche_important/00-README.md). Les documents numérotés font foi ; ce playbook les traduit en responsabilités. À mettre à jour à chaque fin de phase 90 jours.
