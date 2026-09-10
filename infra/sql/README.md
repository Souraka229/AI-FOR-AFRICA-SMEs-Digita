# SQL historique

`001_init.sql` et `002_catalog_orders.sql` documentent le prototype initial.
Ils ne sont plus exécutés automatiquement par Docker.

Depuis `feat/api-core-schema`, la source de vérité est :

`services/api/migrations/versions/`

Toute évolution du schéma passe par une nouvelle révision Alembic avec
`upgrade()` et `downgrade()`. Ne pas modifier une migration déjà appliquée.
