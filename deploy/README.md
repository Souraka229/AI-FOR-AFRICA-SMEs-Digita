# Afrosite — runbook de déploiement national

Ce dossier décrit le passage contrôlé de la branche `integration/2026-09-lancement-pilote` vers un environnement de production destiné aux PME du Bénin puis à l’expansion UEMOA. Le dépôt est **production-ready côté code et CI**, mais le go-live national reste conditionné par la mise en place des éléments externes listés dans la section des prérequis.

## Architecture de référence

Le service web Next.js sert le Studio, les boutiques, le dashboard et les webhooks entrants. FastAPI porte l’authentification, le catalogue, les commandes et le ledger lorsque `AFROSITE_API_URL` est configuré. PostgreSQL est la source de vérité persistante, Redis sert aux tâches et verrous, et le PSP Mobile Money reste responsable des fonds et de la conformité financière.

## Prérequis obligatoires avant ouverture publique

| Domaine | Exigence | Preuve attendue |
|---|---|---|
| Hébergement | Deux services déployables avec TLS, sauvegardes et logs | URL web/API, certificat, accès opérateur |
| Données | PostgreSQL managé, migrations appliquées, sauvegarde restaurée en test | journal de migration et test de restauration |
| Secrets | Secrets injectés par le gestionnaire de secrets, jamais dans Git | inventaire signé sans valeur secrète |
| Paiement | Contrat PSP validé, compte marchand et webhook HTTPS vérifié | transaction sandbox puis validation de production |
| Sécurité | Domaine, HSTS, contrôle d’accès, rotation et astreinte | checklist sécurité signée |
| Exploitation | SLO, alertes, procédure incident et rollback | runbook testé par une seconde personne |
| Marché | CGU, politique de confidentialité, support client et procédure de litige | liens publiés et contacts vérifiés |

## Configuration production

Copier `apps/web/.env.production.example` dans le gestionnaire de secrets de l’hébergeur. Pour l’API, partir de `services/api/.env.example`, remplacer les valeurs de démonstration et fournir au minimum `AFROSITE_AUTH_SECRET`, `AFROSITE_AUTH_BOOTSTRAP_KEY` et `DATABASE_URL`.

`AFROSITE_ENV=production` active deux protections : la sonde `/api/health` renvoie `503` si l’API ou la clé Studio manque, et le web refuse de sélectionner silencieusement le `DemoPaymentProvider`. Une production sans paiement ou API configuré doit donc échouer tôt plutôt que paraître opérationnelle.

Les clés PSP live ne doivent jamais être placées dans le navigateur. Le webhook doit pointer vers `https://app.<domaine>/api/pay/webhook`, être signé, horodaté et testé avec un rejeu invalide. Une redirection navigateur n’est jamais une preuve de paiement.

## Séquence de déploiement

1. Ouvrir une Pull Request de la branche d’intégration vers `main`.
2. Attendre CI, sécurité, CodeQL, E2E Playwright, tests Python, Ruff et Mypy au vert.
3. Appliquer les migrations PostgreSQL sur une copie de préproduction.
4. Déployer le web et l’API en préproduction avec des secrets sandbox.
5. Vérifier `/api/health`, `/health`, `/studio`, `/refs`, une boutique tenant, le dashboard et le webhook sandbox.
6. Réaliser un test de restauration PostgreSQL et conserver le résultat.
7. Programmer une fenêtre de mise en production avec une personne de relève.
8. Déployer avec migration forward-only, puis exécuter le smoke test public.
9. Activer progressivement les premiers tenants et surveiller erreurs, latence, paiements et files.
10. Après stabilisation, promouvoir le domaine national et annoncer le support.

## Smoke test après déploiement

```bash
WEB_URL=https://app.example.bj
API_URL=https://api.example.bj

curl --fail-with-body "$WEB_URL/api/health"
curl --fail-with-body "$API_URL/health"
curl --fail-with-body "$WEB_URL/"
curl --fail-with-body "$WEB_URL/studio"
curl --fail-with-body "$WEB_URL/t/cadjehoun-wax"
curl --fail-with-body "$WEB_URL/dashboard/cadjehoun-wax"
```

Le test de paiement doit utiliser une clé sandbox et un montant de test documenté. Ne jamais simuler un succès live en modifiant directement le ledger.

## Rollback

Le rollback applicatif consiste à redéployer l’image précédente et à conserver la base dans son schéma courant. Les migrations destructives sont interdites ; toute suppression de colonne passe par une phase de dépréciation. En cas de doute sur un paiement, suspendre les nouveaux encaissements, conserver les webhooks bruts, comparer le ledger local au PSP, puis ouvrir un incident financier.

## Limites actuelles à lever avant le go-live national

Le dépôt ne contient pas de domaine, de compte hébergeur, de compte marchand PSP live, de gestionnaire de secrets ni de politique légale validée. Ces éléments nécessitent une coordination et des accès externes ; ils ne doivent pas être inventés ou committés dans le dépôt. Tant qu’ils ne sont pas fournis et vérifiés, la branche est prête pour **préproduction nationale**, pas pour déclarer le service officiellement ouvert au public.
