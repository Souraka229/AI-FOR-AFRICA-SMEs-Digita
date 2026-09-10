# Observabilité locale Afrosite

Stack réutilisée, sans réimplémentation :

- OpenTelemetry Collector reçoit traces, métriques et logs en OTLP ;
- Prometheus collecte les métriques internes du Collector et les métriques OTLP ;
- Grafana utilise automatiquement Prometheus comme source par défaut.

## Lancer

```bash
docker compose -f infra/docker-compose.yml up -d otel-collector prometheus grafana
python infra/observability/check_observability.py
```

| Service | URL locale | Usage |
|---|---|---|
| OTLP gRPC | `http://127.0.0.1:4317` | SDK OpenTelemetry |
| OTLP HTTP | `http://127.0.0.1:4318` | SDK et smoke |
| Collector health | `http://127.0.0.1:13133` | disponibilité |
| Prometheus | `http://127.0.0.1:9090` | métriques / requêtes PromQL |
| Grafana | `http://127.0.0.1:3001` | lecture anonyme locale, aucun compte admin |

Configuration standard à fournir aux services :

```text
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_SERVICE_NAME=afrosite-api
```

Dans un conteneur du même réseau Compose, remplacer `127.0.0.1` par
`otel-collector`.

## Vérifications réelles (2026-09-10)

Les tags et digests ont été vérifiés par `docker pull` puis
`docker image inspect` :

- `otel/opentelemetry-collector:0.160.0@sha256:e495787f07dbe432ce763ebaf5bc3d113850e9eee2250ade7a3da6a882d0d69a`
- `prom/prometheus:v3.14.0@sha256:5ce7540c3c00ef4ab0c9d2c995c6a5b9c421f44b4a115d97a2c7af3b1c21cbb0`
- `grafana/grafana:13.2.1@sha256:f772d434e8fab0049deb2b1b30abd43342bcfca1537614aa8d36080232cf4283`

`docker run ... components` a confirmé que cette distribution Collector
contient les receivers OTLP, processors `memory_limiter` / `batch`, exporters
Prometheus / debug et l’extension `health_check`.

## Smoke

Le smoke envoie une vraie métrique JSON via OTLP HTTP, puis vérifie :

1. le healthcheck du Collector ;
2. les deux cibles Prometheus à `UP` ;
3. la présence de `afrosite_afrosite_smoke_value` dans Prometheus ;
4. la connexion de Grafana à sa base.

Il ne dépend d’aucun SDK Python externe.

## Limites

- Les services applicatifs ne sont pas encore instrumentés : cette carte livre
  le backend OTLP prêt à recevoir leurs signaux.
- L’accès anonyme Grafana est strictement local. En preview/production,
  désactiver l’anonyme et fournir l’authentification via les variables secrètes
  Coolify.
- Aucune alerte de production n’est activée ici.
