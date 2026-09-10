# Inventaire des briques open source — Afrosite

Source : [playbook §6.2](docs/11-playbook-equipe.md#62--les-10-briques-prioritaires-et-leur-isolation) · [doc 06](docs/06-architecture-technique.md).  
Règle : jamais `latest`. Isolation maison obligatoire. Fork du cœur = ADR + date de dé-fork.

PSP (hors cette liste de 10) : **Genius Pay** derrière `PaymentProvider` — [ADR 0001](docs/adr/0001-genius-pay-psp-primaire.md). Pas de SDK Genius dans le métier.

| # | Brique | Version épinglée | Pourquoi | Isolation maison | Mainteneur | Upgrade | Plan de sortie |
|---|---|---|---|---|---|---|---|
| 1 | LiteLLM | `1.99.0` (adaptateur prêt, proxy optionnel) | Routeur multi-modèles, fallback, coût | `packages/llm` — aucune app n’importe `litellm` | SERGE + Souraka | Mensuelle, PR manuelle | Remplacer le routeur, garder `generate/stream` |
| 2 | LangGraph | `1.2.11` | Agents stateful, reprise | `services/agents/runtime` | SERGE | Mensuelle, PR manuelle | Graphe maison au-dessus d’un autre runtime |
| 3 | Temporal | `1.28` server / SDK py `1.9` | Paiement + provisioning uniquement | `services/workflows` — zéro métier dans le SDK | SERGE | Trimestrielle, release stable | Worker simple (autorisé hackathon, [doc 12 §7](docs/12-pitch-hackathon.md#7-périmètre-de-build-pour-la-finale-1-semaine-réaliste)) |
| 4 | OpenHands software-agent-sdk | `1.44.1` · image `sha256:d98aabf…7ed6` | Code Agent sandbox | Wrappé dans le Code Agent, Docker only, dépôt jamais monté | SERGE | Sur besoin | Agent de code interne |
| 5 | PostgreSQL | `16.6` | Source de vérité, ledger, audit | Repository pattern (`services/api`) | SERGE | LTS, patchs | Autre Postgres managé, même SQL |
| 6 | Redis | `7.4` | Cache, files, rate limit, verrous | Client centralisé `services/api/cache` | SERGE | LTS, patchs | File en mémoire (dev) puis autre broker |
| 7 | MinIO | `RELEASE.2024-11-07T00-52-20Z` | Objets S3 (assets, backups) | Interface `ObjectStore` | SERGE | Trimestrielle | S3 / R2, même interface |
| 8 | Playwright | `1.55` (quand E2E branché) | E2E + captures Vision Critic | Helpers `e2e/` | Souraka (A) · CHITOU/SERGE | Mensuelle | Autre runner E2E, mêmes parcours |
| 9 | OpenTelemetry Collector | `0.122` (Phase 2) | Traces / logs / métriques | `packages/telemetry` | Souraka + SERGE | Trimestrielle | Export console au MVP |
| 10 | Prometheus + Grafana | `2.55` / `11.4` (Phase 2) | Surveillance, alertes | Dashboards dans `infra/observability` | SERGE | Trimestrielle | Alertes GitHub / e-mail d’abord |

## Déjà dans le repo (runtime hackathon)

| Brique | Version lock | Où | Note |
|---|---|---|---|
| Next.js | `16.3.4` | `apps/web` | Front + Server Actions (le « backend de poche ») |
| React | `19.2.8` | `apps/web` | |
| Zod | `3.25.76` | `packages/contracts` (workspace partagé avec `apps/web`) | Contrat Blueprint v0.1.0 + garde-fous de génération v0.1.0 (`generation-guardrails.json`, lu par TS **et** Python) |
| AI SDK | `6.0.280` | `packages/llm` | Adaptateur initial AI Gateway ; aucun import fournisseur dans les apps |
| Tailwind CSS | `4` | `apps/web` | Charte : terracotta / or / charbon / sable |
| FastAPI + Pydantic | `0.116.1` / `2.11.7` | `services/api` + `packages/contracts/python` | API + miroir du Zod |
| PyJWT | `2.10.1` | `services/api/auth` | JWT HS256 courts ; algorithme, audience et issuer imposés |
| httpx | `0.28.1` | `services/agents/runtime/adapters.py` | Seul client HTTP du graphe (Studio NDJSON + preview) ; testé via `MockTransport` |
| SQLAlchemy + Alembic | `2.0.52` / `1.19.1` | `services/api/migrations` | Schéma Postgres réversible ; pas d’ORM dans le métier HTTP |

## Comment on pilote (tokens / MCP — sans changer l’archi)

On n’ajoute **pas** d’outil hors playbook. On pilote ceux déjà décidés, s’il y a un token ou un CLI.

| Outil | Décidé dans | Pilotage aujourd’hui | Interdit |
|---|---|---|---|
| GitHub | playbook §5, §14 | `gh` (compte actif `Souraka229`) — CI, PR | Push direct sur `main` |
| Vercel | commodité preview (pas Coolify) | CLI `vercel` connecté — deploy / logs / env | Remplacer Genius Pay ou le contrat |
| Genius Pay | ADR 0001 | Variables `GENIUSPAY_*` sandbox (`pk_sandbox_` / `sbx_test_`) · MCP SSE `https://geniuspay.ci/api/mcp` | Clés `*_live_*` avant gate 6 · coller un secret dans `mcp.json` versionné |
| Docker | playbook §6 | `infra/docker-compose.yml` — Postgres / Redis / MinIO | Kubernetes, Vault, GPU |
| Coolify | doc 06 | Plus tard, quand on self-host | Pas un prérequis hackathon |

Checklist pré-upgrade (toute brique de la table des 10) :

1. Lire le changelog amont (breaking).
2. Smoke test maison vert (playbook §6.3 règle 4) — pour le paiement : parcours wax 24 500 FCFA.
3. `pnpm eval:agents` = 96/96.
4. PR dédiée, pas de groupement avec litellm / temporal / langgraph / Genius Pay.
