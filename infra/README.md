# Infra locale — golden path

Une commande pour le socle (Postgres, Redis, MinIO). L’app hackathon se lance à part.

## Prérequis

- Docker Desktop
- Node 20+ et pnpm 10 (`apps/web/package.json`)

## Lancer le socle

```bash
docker compose -f infra/docker-compose.yml up -d
```

| Service | URL / port | Identifiants (dev seulement) |
|---|---|---|
| PostgreSQL | `localhost:5432` | `afrosite` / `afrosite_dev` · base `afrosite` |
| Redis | `localhost:6379` | — |
| MinIO API | `http://localhost:9000` | `afrosite` / `afrosite_dev_minio` |
| MinIO console | `http://localhost:9001` | idem |

Arrêt : `docker compose -f infra/docker-compose.yml down`  
Reset volumes : `docker compose -f infra/docker-compose.yml down -v`

## Lancer l’app (démo pitch)

Le paiement simulé **n’a pas besoin** de Docker. Depuis `apps/web` :

```bash
pnpm install
pnpm dev
```

Puis : `/studio` → `/t/cadjehoun-wax` (24 500 FCFA) → `/dashboard/cadjehoun-wax`.

Contrôles :

```bash
pnpm eval:agents
pnpm check:contracts
pnpm check:pay
npx tsc --noEmit
```

## API + Next ensemble

```bash
# terminal 1 — déjà fait si les conteneurs tournent
docker compose -f infra/docker-compose.yml up -d

# terminal 2
cd services/api
set DATABASE_URL=postgresql://afrosite:afrosite_dev@127.0.0.1:5432/afrosite
uvicorn main:app --reload --port 8000

# terminal 3
cd apps/web
# dans .env.local : AFROSITE_API_URL=http://127.0.0.1:8000
pnpm dev
```

Sans `AFROSITE_API_URL`, Next reste sur le store fichier (démo wax intacte).

Schéma Postgres : Alembic (`services/api`), pas les SQL historiques.

```bash
cd services/api
set DATABASE_URL=postgresql://afrosite:afrosite_dev@127.0.0.1:5432/afrosite
python -m alembic upgrade head
```

## Previews Coolify

Le déploiement des previews est déclenché en CI par
[`infra/coolify/deploy_preview.py`](coolify/deploy_preview.py). Voir
[`infra/coolify/README.md`](coolify/README.md) pour les secrets à créer et les
garde-fous. Sans secrets, la CI n’échoue pas : le job est simplement ignoré.

## Variables paiement (sandbox uniquement)

Copier `apps/web/.env.example` vers `apps/web/.env.local`.  
Sans clés Genius Pay, le `DemoPaymentProvider` garde la démo verte.  
Clés `pk_live_` / `sk_live_` / `whsec_live_` : **refusées** (gate 6 + audit).
