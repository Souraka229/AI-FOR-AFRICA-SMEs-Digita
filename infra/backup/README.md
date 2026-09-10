# Backups Postgres — dump et restauration prouvés

DoD go-live ([playbook §13.3](../../docs/11-playbook-equipe.md)) : une sauvegarde restaurée
avec succès au moins une fois, pas seulement « le backup tourne ».

Cet outil utilise **le client `pg_dump` / `pg_restore` du conteneur officiel**
`postgres:16.6` déjà épinglé dans `infra/docker-compose.yml`. Aucun binaire
inventé, aucun mot de passe journalisé.

## Contrôle local

Postgres doit être up :

```bash
docker compose -f infra/docker-compose.yml up -d postgres
python infra/backup/check_restore.py
```

Le smoke :

1. crée une table canari `_backup_canary` dans `afrosite` ;
2. dump au format custom (`pg_dump -Fc`) ;
3. restaure dans une base jetable `afrosite_restore_smoke` ;
4. vérifie que le canari est bien là ;
5. supprime la base jetable et le canari.

## Ce qui manque pour que ce soit opérationnel (prod / pilotes)

| Manque | Pourquoi ça bloque |
|---|---|
| Postgres **réel** (Coolify ou hébergeur), pas seulement Docker Desktop | Le script cible le service Compose `postgres` |
| Secret `DATABASE_URL` / mot de passe **hors** `docker-compose.yml` | Les identifiants `afrosite` / `afrosite_dev` sont du **dev local uniquement** |
| Job planifié (cron Coolify ou GitHub Actions) | Ici : smoke manuel / CI optionnelle, pas de rétention 7/30 jours |
| Stockage hors machine (MinIO / S3) | Le dump reste dans le conteneur le temps du test, puis est effacé |
| Restauration **à blanc** sur un environnement de secours | On restaure une base jetable locale, pas un failover |
| Merge de cette branche dans `main` | Tant que `main` est à #13, le runbook n’est pas sur la CI canonique |

**Hors périmètre volontaire :** Vault, snapshots disque, PITR. Le playbook
interdit Vault au MVP.
