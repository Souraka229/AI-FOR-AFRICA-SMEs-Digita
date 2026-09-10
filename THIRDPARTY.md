# Third-Party Inventory — Afrosite

> Inventaire des 10 briques prioritaires ([playbook §6.2](docs/11-playbook-equipe.md)).
> Versions et digests ci-dessous ont été **vérifiés** le 2026-09-09 via `uv.lock` / PyPI / npm / `docker pull` + `docker image inspect` / GitHub Releases.
> Mainteneur interne : **SERGE**. Jamais de tag `latest` en prod.

## 1. BerriAI/litellm

| Champ | Valeur |
|---|---|
| Rôle | Routeur multi-modèles, fallback, suivi de coût |
| Isolation | `packages/llm` — aucune app n'importe `litellm` directement |
| Pin actuel | `litellm==1.99.0` (dans `uv.lock`) |
| Preuve | PyPI `litellm/1.99.0` (upload 2026-09-01) ; présent dans `uv.lock` |
| Cadence upgrade | Mensuelle, PR manuelle |
| Checklist pré-upgrade | `uv run pytest packages/llm` ; smoke `generate()` + fallback simulé |
| Plan de sortie | Remplacer l'adaptateur dans `packages/llm` sans toucher les services |

## 2. langchain-ai/langgraph

| Champ | Valeur |
|---|---|
| Rôle | Orchestration d'agents stateful |
| Isolation | `services/agents` — graphes définis en interne |
| Pin actuel | `langgraph==1.2.11` (dans `uv.lock`) |
| Preuve | PyPI `langgraph/1.2.11` (upload 2026-08-11) ; présent dans `uv.lock` |
| Cadence upgrade | Mensuelle, PR manuelle |
| Checklist pré-upgrade | Import package ; graphe minimal + reprise après échec |
| Plan de sortie | Réécrire le runtime agents derrière la même façade |

## 3. temporalio/temporal

| Champ | Valeur |
|---|---|
| Rôle | Workflows critiques (paiement, provisioning) |
| Isolation | `services/workflows` — logique métier dans activities maison |
| Pin serveur | `temporalio/server:1.31.2` @ `sha256:b5ecdb8282bededae2a10c36e8d862e27d0bc2d247fc73c5416025997ab4a1da` |
| Pin SDK Python | `temporalio==1.32.0` (dans `uv.lock`) |
| Preuve | `docker pull temporalio/server:1.31.2` + `docker image inspect` ; PyPI `temporalio/1.32.0` ; GitHub release `temporalio/temporal` tag `v1.31.2` |
| Cadence upgrade | Trimestrielle, release stable |
| Checklist pré-upgrade | Workflow paiement sandbox bout-en-bout ; retries ; replay |
| Plan de sortie | Activities stables ; swap runtime Temporal derrière `services/workflows` |
| Note | `temporalio/auto-setup:1.31.2` **n'existe pas** (manifest unknown) — ne pas l'utiliser |

## 4. OpenHands/software-agent-sdk

| Champ | Valeur |
|---|---|
| Rôle | Agent qui manipule le code (Code Agent) |
| Isolation | Wrappé dans le Code Agent, exécution **sandbox Docker uniquement** |
| Pin actuel | `openhands-sdk==1.46.0` (PyPI) / GitHub release `v1.46.0` |
| Preuve | PyPI `openhands-sdk` version `1.46.0` ; GitHub `OpenHands/software-agent-sdk` release `v1.46.0` (assets + `SHA256SUMS`) |
| Cadence upgrade | Suivi, pas d'upgrade auto |
| Checklist pré-upgrade | Exécution sandbox ; zéro accès secrets hôte ; tests Code Agent |
| Plan de sortie | Remplacer le SDK derrière la façade Code Agent |
| Statut repo | **Pas encore câblé** dans le monorepo — pin documenté pour la prochaine tâche agents |

## 5. postgres/postgres

| Champ | Valeur |
|---|---|
| Rôle | Source de vérité, ledger, audit |
| Isolation | Accès via repository pattern (`services/api`) |
| Pin actuel | `postgres:16-alpine` @ `sha256:cf78e76683b9ca8c5733cbbdce6c9262b45b6767934dd0a95e671f9a0fc20685` |
| Preuve | `docker pull` + `docker image inspect` (RepoTags `postgres:16-alpine`) ; pin dans `docker-compose.yml` |
| Cadence upgrade | LTS, patchs via PR |
| Checklist pré-upgrade | `docker compose up` healthy ; migrations ; backup/restore test |
| Plan de sortie | SQL standard + SQLAlchemy ; swap managed Postgres |

## 6. redis/redis

| Champ | Valeur |
|---|---|
| Rôle | Cache, files, rate limiting, verrous |
| Isolation | Client centralisé (à venir `services/api/cache`) |
| Pin actuel | `redis:7-alpine` @ `sha256:ff02b58f971e7d7d156a1267e283fcbbeee91773b6aa36c49dac28ecfe28eadf` |
| Preuve | `docker pull` + `docker image inspect` ; pin dans `docker-compose.yml` ; client Python `redis==8.1.0` dans `uv.lock` |
| Cadence upgrade | LTS, patchs via PR |
| Checklist pré-upgrade | Healthcheck compose ; SET/GET smoke ; rate-limit unit test |
| Plan de sortie | Interface cache maison |

## 7. minio/minio

| Champ | Valeur |
|---|---|
| Rôle | Objets S3 (assets, backups, exports) |
| Isolation | Interface `ObjectStore` (à venir) — swappable S3 |
| Pin serveur | `minio/minio:RELEASE.2025-09-07T16-13-09Z` @ `sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e` |
| Pin client mc | `minio/mc:RELEASE.2025-08-13T08-35-41Z` @ `sha256:a7fe349ef4bd8521fb8497f55c6042871b2ae640607cf99d9bede5e9bdf11727` |
| Preuve | `docker pull` + `docker image inspect` ; pins dans `docker-compose.yml` |
| Cadence upgrade | Trimestrielle |
| Checklist pré-upgrade | Bucket init ; put/get objet ; console :9001 |
| Plan de sortie | Swap vers S3/R2 via `ObjectStore` |

## 8. microsoft/playwright

| Champ | Valeur |
|---|---|
| Rôle | Tests E2E + captures Vision Critic |
| Isolation | Helpers `e2e/` (à venir) |
| Pin actuel | `@playwright/test@1.63.0` / `playwright@1.63.0` (npm) |
| Preuve | npm registry `playwright/1.63.0` et `@playwright/test/1.63.0` ; GitHub `microsoft/playwright` release `v1.63.0` |
| Cadence upgrade | Mensuelle |
| Checklist pré-upgrade | `pnpm exec playwright install` ; smoke E2E ; captures inchangées |
| Plan de sortie | Remplacer runner E2E en gardant les helpers de capture |
| Statut repo | **Pas encore ajouté** au lockfile JS — pin documenté |

## 9. open-telemetry/opentelemetry-collector

| Champ | Valeur |
|---|---|
| Rôle | Traces, logs, métriques |
| Isolation | Backend OTLP dans `infra/observability` ; SDK applicatif derrière `packages/telemetry` (à venir) |
| Pin actuel | `otel/opentelemetry-collector:0.160.0` @ `sha256:e495787f07dbe432ce763ebaf5bc3d113850e9eee2250ade7a3da6a882d0d69a` |
| Preuve | GitHub `open-telemetry/opentelemetry-collector-releases` latest `v0.160.0` ; `docker pull` + `inspect` |
| Cadence upgrade | Trimestrielle |
| Checklist pré-upgrade | Collector démarre ; reçoit une span de smoke |
| Plan de sortie | Export OTLP standard vers autre backend |
| Statut repo | **Câblé dans Compose** — receiver OTLP, métriques Prometheus, healthcheck ; SDK applicatif à venir |

## 10. prometheus + grafana

| Champ | Valeur |
|---|---|
| Rôle | Surveillance, alertes |
| Isolation | Configs et provisioning Grafana versionnés dans `infra/observability` |
| Pin Prometheus | `prom/prometheus:v3.14.0` @ `sha256:5ce7540c3c00ef4ab0c9d2c995c6a5b9c421f44b4a115d97a2c7af3b1c21cbb0` |
| Pin Grafana | `grafana/grafana:13.2.1` @ `sha256:f772d434e8fab0049deb2b1b30abd43342bcfca1537614aa8d36080232cf4283` |
| Preuve | GitHub releases `prometheus/prometheus` `v3.14.0`, `grafana/grafana` `v13.2.1` ; `docker pull` + `inspect` |
| Cadence upgrade | Trimestrielle |
| Checklist pré-upgrade | Targets UP ; dashboard smoke ; alerte test |
| Plan de sortie | Dashboards as code ; remote_write vers autre stack |
| Statut repo | **Câblé dans Compose** — deux cibles Prometheus et datasource Grafana provisionnée |

## Hygiène

- Lockfiles commités (`uv.lock`, `pnpm-lock.yaml`).
- Images runtime locales (Postgres/Redis/MinIO) épinglées par digest dans `docker-compose.yml`.
- Auto-merge Dependabot/Renovate **interdit** sur litellm, temporal, langgraph, SDK Genius Pay ([§6.3](docs/11-playbook-equipe.md)).
- Toute brique absente du monorepo est marquée « pas encore câblée » — ne pas inventer un digest non vérifié.

## Câblé dans le Studio (JS) — génération LLM contrôlée

| Brique | Version lock | Où | Note |
|---|---|---|---|
| AI SDK | `6.0.280` | `packages/llm` (TypeScript) | Porte unique `generateStructured` / `streamStructured` ; AI Gateway par défaut, LiteLLM interchangeable |
| Next.js | `16.3.4` | `apps/web` | Studio, preview tenant, paiement sandbox |
| Zod | `3.25.76` | `packages/contracts` | Blueprint v0.1.0 + `generation-guardrails.json` (TS et Python) |
| Playwright | `1.55.0` | `apps/web` | E2E desktop + Pixel 7 ; pin npm distinct du pin documenté §8 en attente d’alignement |
| OpenHands SDK | `1.44.1` · image `sha256:d98aabf…7ed6` | `services/agents/runtime/code_agent.py` | Docker only, digest épinglé, jamais `latest` |
