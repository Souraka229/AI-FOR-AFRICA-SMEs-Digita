# Plan d'instrumentation des coûts — Afrosite

Propriétaire : **Souraka HAMIDA**. Branche prévue : `docs/cost-instrumentation-plan`.

Objectif : savoir, **par tenant et par jour**, ce que coûte un client avant qu'il ne casse la marge brute cible de **≥ 70 %** ([doc 02 §5](02-business-model.md#5-unit-economics)). Un client Business à 15 000 FCFA/mois ne doit pas dépasser **4 500–6 000 FCFA** de coût variable direct.

On n'attend pas la Phase 3 pour mesurer. On pose les compteurs dès que le premier prompt tourne.

## 1. Ce qu'on mesure (et pourquoi)

| # | Métrique | Unité | Attribution | Seuil d'alerte |
|---|---|---|---|---|
| M1 | Coût tokens IA (prompt + completion + cache hit) | FCFA + crédits | `tenant_id`, `agent`, `model`, `vertical` | > 2 000 FCFA / tenant / 7 j |
| M2 | Nombre de générations / prompts | count | `tenant_id`, `agent` | > plafond de l'offre (Explorer/Starter) |
| M3 | Temps prompt → preview | secondes | `run_id`, `vertical` | > 300 s (cible produit : < 60 s perçus, < 5 min réels) |
| M4 | Coût stockage + bande passante | FCFA | `tenant_id` | > 800 FCFA / mois |
| M5 | Coût environnements preview | FCFA · heures | `pr_id` / `run_id` | preview > 24 h sans destroy |
| M6 | Coût WhatsApp / SMS / e-mail | FCFA | `tenant_id`, `channel` | > 400 FCFA / mois hors plan |
| M7 | Temps de support humain | minutes → FCFA | `tenant_id`, `ticket_id` | > 45 min / semaine / pilote |
| M8 | Frais PSP (Genius Pay) | FCFA | `tenant_id`, `psp_ref` | **jamais absorbés** — toujours refacturés |
| M9 | Taux de réconciliation auto | % | jour | < 100 % → alerte SERGE |
| M10 | Rétention d'usage | jours actifs / 7 | `tenant_id` | < 5 j/7 chez un pilote |

Crédit interne : **1 crédit ≈ coût d'un appel modèle léger**. Le Product Architect affiche `estimated_cost_credits` avant exécution (écran studio). Le Cost Agent (Phase 2) compare estimé vs réel.

## 2. Où ça se pose dans le code

Rien n'appelle LiteLLM en direct ([playbook §6](11-playbook-equipe.md#6-dépôts--open-source-sans-perte-de-qualité)). Toute génération passe par `packages/llm`.

```
packages/llm/src/router.py     → span OTel `afrosite.llm.generate`
                                 attributs : tenant_id, agent, model, credits, cache_hit
packages/telemetry             → export OTLP (Grafana / Tempo plus tard ; console au MVP)
services/workflows/*           → span par activity paiement / provisioning (coût PSP = M8)
apps/web/studio                → M3 (horloge navigateur + horodatage serveur)
apps/web (hackathon)           → `recordCost()` dans le store démo (`.demo/state.json`) + crédits studio / caisse
```

Attributs OpenTelemetry **obligatoires** sur chaque span IA :

```
afrosite.tenant_id
afrosite.agent            # intent | product_architect | code | …
afrosite.vertical
afrosite.model
afrosite.credits
afrosite.cache_hit        # true/false
afrosite.prompt_tokens
afrosite.completion_tokens
```

Aucun secret, aucun PAN, aucun prompt brut dans les attributs (risque d'injection + RGPD-like). Un hash du prompt suffit (`sha256` tronqué).

## 3. Dashboard (cible, puis hackathon)

**Cible Phase 3** — `feat/web-cost-dashboard` :

- Coût IA / client / 30 j
- Coût cloud (preview + bande passante)
- Minutes de support
- Rétention J+30
- Marge brute estimée vs 70 %

**Dès aujourd'hui (studio)** : chaque run affiche crédits estimés, gate 1 (plafond), et l'audit trail horodaté. C'est le germe du dashboard, pas un jouet.

## 4. Plafonds par offre ([doc 02 §3](02-business-model.md#3-grille-tarifaire))

| Offre | Crédits / mois | Preview | WhatsApp | Règle si dépassement |
|---|---:|---|---|---|
| Explorer | 20 | 1, 48 h | 0 | Stop génération + message clair |
| Starter | 80 | 1 stable | quota bas | Crédits additionnels |
| Business | 250 | 2 | inclus raisonnable | Modèle plus léger, puis asynchrone |
| SaaS Builder | 800 | N | facturé | Devis usage |

Le plan gratuit **n'a jamais** d'IA illimitée. Cache de prompts **activé par défaut** ([deep 04 §2C](../deeprecherche_important/04-application-a-afrosite.md#c-activer-le-cache-de-prompts-par-défaut-sur-le-routeur)).

## 5. Conversion FCFA (à recalibrer chaque vendredi)

Hypothèses de travail, pas des tarifs fournisseurs figés :

| Poste | Hypothèse J1 | Recalibrage |
|---|---|---|
| 1 k tokens modèle léger | ~ 2–4 FCFA | facture LiteLLM réelle |
| 1 k tokens modèle puissant | ~ 20–40 FCFA | idem |
| Preview Coolify / h | à mesurer semaine 2 | facture hébergeur |
| WhatsApp Cloud (template) | tarif Meta du mois | facture Meta |
| Support | 50 FCFA / minute (coût chargé équipe, ordre de grandeur) | temps réel saisi |

La revue hebdo du vendredi ([playbook §4.4](11-playbook-equipe.md#44--rituels-reliés-au-board)) lit **M1, M3, M8, M10**. Si M1 + M4 + M6 + M7 > 6 000 FCFA sur un Business : on baisse le modèle, on cache, ou on facture des crédits — on n'ajoute pas de feature.

## 6. Ce qu'on ne fait pas

- Pas de tableau Excel parallèle : si ce n'est pas dans le span / le ledger, ça n'existe pas.
- Pas de coût IA « moyen mondial » copié d'un blog : on mesure *nos* runs.
- Pas d'absorption silencieuse des frais Genius Pay.
- Pas de prompt utilisateur stocké en clair dans Grafana.

## 7. Livrable technique suivant

Quand `packages/llm` existe (binôme SERGE) : brancher le callback coût LiteLLM + ces attributs. Jusque-là, le studio hackathon écrit un `CostEstimate` dans l'audit trail à chaque run.
