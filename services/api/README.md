# services/api — golden path

```bash
cd services/api
python -m pip install -r requirements.txt
python check.py
# schéma Postgres (base jetable) :
#   DATABASE_URL=postgresql://afrosite:afrosite_dev@127.0.0.1:5432/afrosite_migration_test
#   python check_migrations.py
uvicorn main:app --reload --port 8000
# GET  http://localhost:8000/health
# POST http://localhost:8000/blueprints/validate
```

- `main.py` — `/health` · Gate 1 · auth/RBAC · ledger
- Auth : JWT HS256 court (1 h max), `iss` + `aud` + `exp` requis, algorithme fixé côté serveur.
- RBAC : `owner`, `cashier`, `kitchen`, `customer` ; toute route tenant vérifie aussi le slug du jeton.
- Ledger : mémoire par défaut. `DATABASE_URL` → Postgres via **Alembic** (`alembic upgrade head`)
- Paiement : ancien header `X-Afrosite-Role` encore isolé dans ce module ; migration vers JWT lors de la reprise paiement.
- Catalogue : `GET/PUT/PATCH /tenants/{slug}/catalog` — prix XOF serveur, écriture owner
- Commandes : `POST /tenants/{slug}/orders` — SKU + qty, montant recalculé, idempotence
  (statut `placed` / `cancelled` ; pas de « payé » sans verify)
- CRM : `PUT/GET /tenants/{slug}/crm/customers/{phone}` — téléphone Bénin, historique, fidélité
  (caisse : `crm:write` ; client : 403 ; montant visite pris sur la commande, jamais le corps)
- Dashboard : `GET /tenants/{slug}/dashboard` — jour Africa/Porto-Novo ; activité ≠ encaissé
  (`collected_xof` seulement après `verify()` ; jamais le mot « payé »)
- Exports CSV (owner) : `GET /exports/ventes.csv` · `GET /exports/transactions.csv` ·
  `GET /exports/clients.csv` — isolation tenant, jamais de mot de passe

## Auth locale

Copier `.env.example` vers `.env` sans versionner ce dernier, puis générer deux
valeurs aléatoires d'au moins 32 octets. L'endpoint d'amorçage n'est utilisable
que si `AFROSITE_AUTH_BOOTSTRAP_KEY` existe et il retourne 404 en production.

```bash
POST /auth/token                         # header X-Afrosite-Bootstrap-Key
GET  /auth/me                            # Authorization: Bearer <token>
GET  /tenants/{tenant_slug}/access       # identité + permissions, tenant isolé
GET  /tenants/{tenant_slug}              # fiche établissement (même slug que le jeton)
PATCH /tenants/{tenant_slug}             # owner uniquement
POST /tenants                            # amorçage local, jamais en production
```

`AFROSITE_AUTH_SECRET` reste serveur uniquement. Aucun jeton ni secret dans les
logs, le navigateur ou le dépôt.

## Schéma (Alembic)

Source de vérité : `migrations/versions/`. Plus d’init Docker SQL.

```bash
docker compose -f ../../infra/docker-compose.yml up -d postgres
# base jetable pour tester upgrade/downgrade
# CREATE DATABASE afrosite_migration_test;
set DATABASE_URL=postgresql://afrosite:afrosite_dev@127.0.0.1:5432/afrosite_migration_test
python check_migrations.py
```

Appliquer sur la base locale `afrosite` (une fois, après dump éventuel) :

```bash
set DATABASE_URL=postgresql://afrosite:afrosite_dev@127.0.0.1:5432/afrosite
python -m alembic upgrade head
```
