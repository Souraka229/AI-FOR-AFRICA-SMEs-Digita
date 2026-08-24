# Plan d'exécution 90 jours — Afrosite

Objectif de ces 90 jours : prouver que le socle commun + 3 blueprints (Commerce, Restaurant, Services) fonctionne réellement pour 5 clients pilotes à Cotonou, avec paiement Mobile Money en production, avant tout investissement supplémentaire.

## Jours 1 à 30 — La fondation fiable

- [ ] Choisir le nom de domaine et l'identité de marque « Afrosite » (`.app`, `.africa` ou équivalent).
- [ ] Construire le socle commun versionné : auth, catalogue, commande/réservation, CRM léger, dashboard (voir [doc 01 §5.1](01-cahier-des-charges.md#51-mvp--phase-1-0-3-mois)).
- [ ] Construire les 3 blueprints par-dessus le socle : Commerce, Restaurant, Services.
- [ ] Mettre en place GitHub Actions : tests, scans de secrets, CodeQL, revue de dépendances.
- [ ] Ajouter preview automatique par pull request.
- [ ] Ajouter PostgreSQL, sauvegardes quotidiennes, logs centralisés.
- [ ] Intégrer un PSP (KKiaPay ou FedaPay) **uniquement en sandbox**.
- [ ] Écrire les politiques de permissions et les règles d'approbation (gates — voir [doc 06 §5](06-architecture-technique.md#5-pipeline-prompt--production)).
- [ ] Démarrer la liste des 100 établissements cibles à Cotonou (mix commerce/restaurant/services).

## Jours 31 à 60 — L'automatisation IA

- [ ] Prompt → Blueprint JSON validé (schéma Zod/Pydantic).
- [ ] Blueprint → branche Git → génération contrôlée (Code Agent).
- [ ] Génération de tests et exécution Playwright automatique.
- [ ] Agent de sécurité et correction sur la branche avant merge.
- [ ] Preview déployée automatiquement après chaque génération.
- [ ] Écran de validation client + journal complet des actions (audit trail).
- [ ] Démarrer la vente terrain : 15 à 25 visites/semaine, viser les 5 premiers pilotes (voir [doc 05 §2](05-roadmap-leadership-afrique.md#2-les-cinq-premiers-clients)).
- [ ] Installer les premiers pilotes en sandbox de paiement, mesurer l'usage quotidien réel.

## Jours 61 à 90 — La commercialisation

- [ ] Passer les 5 pilotes en production (paiement réel), après tests de webhooks, remboursement et réconciliation.
- [ ] Activer le paiement Mobile Money en production pour chaque tenant validé.
- [ ] Mesurer : coût IA par client, coût cloud, temps de support, rétention à 30 jours.
- [ ] Ajuster les crédits et plafonds selon les coûts réels observés.
- [ ] Vendre les frais de lancement, puis l'abonnement récurrent (grille dans [doc 02 §3](02-business-model.md#3-grille-tarifaire)).
- [ ] Obtenir au moins 3 témoignages/recommandations parmi les 5 pilotes.
- [ ] Décider, sur la base des résultats réels, quel(s) vertical(aux) approfondir en priorité en Phase 2.

## Indicateurs à suivre dès le jour 1

| Indicateur | Pourquoi le suivre |
|---|---|
| Temps entre premier prompt et preview fonctionnelle | Valide la promesse « < 1 heure » du [cahier des charges](01-cahier-des-charges.md#3-objectifs-du-produit) |
| Coût IA/infra par client actif | Protège la marge brute cible de 70 % ([doc 02](02-business-model.md#5-unit-economics)) |
| Taux de réconciliation automatique des paiements | Doit tendre vers 100 % sans intervention manuelle |
| Usage quotidien par pilote | Signal le plus fiable de rétention future |
| Nombre de recommandations obtenues | Valide le canal de parrainage avant d'investir en acquisition payante |

## Ce qu'il ne faut pas faire pendant ces 90 jours

- Ne pas ajouter un 4ᵉ blueprint avant d'avoir validé les 3 premiers.
- Ne pas activer de clé PSP en production avant d'avoir testé webhooks, échecs et remboursements en sandbox.
- Ne pas construire Kubernetes, Vault ou un cluster GPU — hors de portée du besoin réel à ce stade.
- Ne pas donner un accès IA illimité sur l'offre gratuite.
- Ne pas pousser de code généré directement sur `main` sans passer par une branche + revue.

À l'issue de ces 90 jours, la décision à prendre est simple : les 5 pilotes utilisent-ils Afrosite **tous les jours** ? Si oui, répliquer le playbook commercial (Phase 2 du [doc 05](05-roadmap-leadership-afrique.md#4-stratégie-pour-devenir-leader-régional)). Si non, diagnostiquer avant d'ajouter la moindre fonctionnalité.
