# Afrosite — AI Company Builder (Monorepo)

> Socle d'infrastructure du monorepo Afrosite (PNPM + Turborepo pour JS/TS, `uv` pour Python).

## 🚀 Golden Path (Démarrage en < 10 minutes)

### Préréquis
- **Node.js** : v20.x (voir `.nvmrc`)
- **pnpm** : v9+ (`npm install -g pnpm`)
- **Python** : v3.12+ (voir `.python-version`)
- **uv** : gestionnaire Python rapide (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Docker & Docker Compose**

---

### 1. Cloner et configurer l'environnement

```bash
# Copier le fichier de variables d'environnement exemple
cp .env.example .env
```

### 2. Installer les dépendances JS/TS (Frontend & Packages)

```bash
pnpm install
```

### 3. Synchroniser les environnements & dépendances Python (Backend & Services)

```bash
# uv installe les venvs et les dépendances pour tous les services du workspace
uv sync
```

### 4. Démarrer l'infrastructure locale (PostgreSQL, Redis, MinIO)

```bash
docker compose up -d
```

### 5. Vérifier que tout fonctionne (< 10 min)

#### A. Statut de l'infrastructure Docker
```bash
docker compose ps
# postgres, redis et minio doivent afficher (healthy)
```

#### B. Tester le service FastAPI (services/api)
```bash
uv run --package afrosite-api uvicorn afrosite_api.main:app --reload --port 8000
# Sur un autre terminal :
curl http://localhost:8000/health
# Résultat attendu : {"status":"healthy","service":"api","timestamp":"..."}
```

#### C. Console MinIO
Accéder à [http://localhost:9001](http://localhost:9001) avec :
- User : `minioadmin`
- Password : `minioadmin`
- Le bucket `afrosite-assets` est prêt.

---

## 📁 Structure du Monorepo

```text
.
├── apps/
│   └── web/                # Next.js App Router (Frontend)
├── packages/
│   ├── contracts/          # Schémas Zod & DTOs partagés
│   ├── design-system/      # Foundations & tokens sémantiques Afrosite
│   └── llm/                # Couche d'adaptation LiteLLM (cache par défaut)
├── services/
│   ├── api/                # FastAPI backend (RBAC, tenants, catalog, orders)
│   ├── agents/             # LangGraph agent orchestration
│   └── workflows/          # Workflows durables Temporal
├── infra/                  # Documentation infra & configurations Docker
├── docker-compose.yml      # Infrastructure locale (Postgres, Redis, MinIO)
├── pnpm-workspace.yaml     # Configuration workspace PNPM
├── pyproject.toml          # Configuration workspace uv
└── turbo.json              # Configuration pipelines Turborepo
```

---

## 🛠️ Commandes de développement

```bash
# Lancer les linters & checks JS/TS
pnpm turbo lint typecheck

# Exécuter les tests Python
uv run pytest
```
