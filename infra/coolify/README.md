# Coolify — déploiement des previews

Coolify déploie **uniquement des previews**. La production reste derrière Gate 6
(confirmation admin explicite, playbook §14) et n'est pas câblée ici.

## Ce qui est vérifié

| Élément | Valeur | Preuve |
|---|---|---|
| Version Coolify | `v4.3.18` (publiée 2026-09-08) | `gh api repos/coollabsio/coolify/releases/latest` le 2026-09-10 |
| Endpoint de déploiement | `POST /api/v1/deploy?uuid=&pr=&force=` | `openapi.json` au tag `v4.3.18`, `operationId: deploy-by-tag-or-uuid` |
| Réponse | `{"deployments":[{"message","resource_uuid","deployment_uuid"}]}` | idem |
| Suivi | `GET /api/v1/deployments/{deployment_uuid}` → champ `status` | idem, schéma `ApplicationDeploymentQueue` |
| Authentification | `Authorization: Bearer <token>`, permission `deploy` | docs Coolify « API Authorization » |

**Non vérifié :** aucun digest d'image Coolify n'est épinglé ici — l'instance
s'auto-héberge hors du dépôt. Le déploiement n'a **pas** été exécuté contre une
instance réelle : il faut une instance Coolify et ses secrets pour le prouver.

## Secrets GitHub à créer

Aucun secret ne vit dans le dépôt. À déclarer dans *Settings → Secrets and
variables → Actions* :

| Secret | Rôle |
|---|---|
| `COOLIFY_URL` | Base de l'instance, en `https://` |
| `COOLIFY_API_TOKEN` | Jeton d'API, permission `deploy` seule (pas `root`) |
| `COOLIFY_PREVIEW_APP_UUID` | UUID de l'application de preview |
| `COOLIFY_PRODUCTION_APP_UUID` | Optionnel, mais recommandé : garde-fou qui fait échouer le job si l'UUID de preview pointe sur la prod |

Tant que les trois premiers sont absents, le job **ne casse pas la CI** : il
affiche `preview Coolify ignoree` et sort en 0.

## Utilisation

```bash
python infra/coolify/deploy_preview.py --pr 42 --wait
```

Options : `--pr` (déploiement de preview par PR), `--force` (rebuild sans
cache), `--wait` (attend un statut terminal, timeout borné à 600 s par défaut).

## Contrôle

```bash
python infra/coolify/check_deploy_preview.py
```

Le smoke rejoue le contrat HTTP sur un serveur local éphémère : déploiement
avec `pr`, suivi de statut, secrets absents, refus de l'UUID de production,
refus d'une URL non chiffrée, 401, et timeout borné. Aucun secret, aucune
instance Coolify requise.

## Garde-fous

- L'URL doit être `https`, sauf `127.0.0.1` / `localhost` pour les tests.
- Si `COOLIFY_PRODUCTION_APP_UUID` égale `COOLIFY_PREVIEW_APP_UUID`, le script refuse.
- Le workflow ne se déclenche que sur `pull_request` — jamais sur `main`.
- Le script ne journalise jamais le jeton.
