# Politiques OPA — six gates Afrosite

Les règles G1 à G6 vivent dans `policies.rego`. La matrice rôle → route vit
dans `permissions.yaml`. OPA est la source de vérité exécutable ; la CI lance
un contrôle strict puis les tests Rego à chaque changement.

## Version vérifiée

`openpolicyagent/opa:1.20.2-static` a été vérifiée le 2026-09-10 :

```text
openpolicyagent/opa@sha256:bb245e9e36be0d0ed486c240b606c56be7aba96014a4a87895fed4ba7a6dfa8d
Version: 1.20.2
Rego Version: v1
```

Preuves : release GitHub officielle `v1.20.2` publiée le 2026-09-03, puis
`docker pull`, `docker image inspect` et `opa version`.

## Contrôle local

```bash
docker run --rm \
  -v "$PWD:/workspace" \
  -w /workspace \
  openpolicyagent/opa:1.20.2-static@sha256:bb245e9e36be0d0ed486c240b606c56be7aba96014a4a87895fed4ba7a6dfa8d \
  check --strict infra/gates

docker run --rm \
  -v "$PWD:/workspace" \
  -w /workspace \
  openpolicyagent/opa:1.20.2-static@sha256:bb245e9e36be0d0ed486c240b606c56be7aba96014a4a87895fed4ba7a6dfa8d \
  test infra/gates -v
```

La CI correspondante est `.github/workflows/gates.yml`. Aucun serveur OPA
longue durée n’est nécessaire : les politiques sont vérifiées directement avec
le binaire officiel conteneurisé.
