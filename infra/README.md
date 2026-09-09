# Infrastructure — Afrosite

## Services gérés via Docker Compose (Développement local)

- **PostgreSQL 16** (port 5432) : Base relationnelle principale
- **Redis 7** (port 6379) : Cache & file de messages
- **MinIO** (ports 9000 & 9001) : Stockage d'objets S3 compatible (bucket `afrosite-assets` initialisé)

## Commandes utiles

```bash
# Lancer les services d'infrastructure
docker compose up -d

# Vérifier la santé des conteneurs
docker compose ps

# Stopper et nettoyer les volumes
docker compose down -v
```
