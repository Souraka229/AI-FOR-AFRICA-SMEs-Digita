# Application à Afrosite — ce qu'on prend de cette recherche

Cette recherche ne change pas l'architecture décidée dans [doc 06](../docs/06-architecture-technique.md) — elle la confirme et précise trois points à renforcer explicitement.

## 1. Ce qui est déjà bien positionné

| Décision déjà prise pour Afrosite | Confirmée par la recherche |
|---|---|
| Routeur multi-modèles (LiteLLM) avec modèle léger / puissant / spécialisé code | Correspond exactement au principe d'arbitrage vitesse/profondeur du [doc 03 §3](03-ce-qui-rend-une-ia-la-meilleure.md#3-le-raisonnement-étendu--arbitrer-vitesse-contre-profondeur) |
| Agent UI Critic qui rejette les tics visuels génériques | Correspond au pattern generator-critic documenté dans la recherche académique ([doc 02](02-design-visuel-ia.md#1-le-pattern-générateurcritique-generator-critic)) |
| 80 % de composants éprouvés (blueprints) / 20 % de génération IA contrôlée | Correspond à l'approche v0 (design system en entrée plutôt que page blanche) |
| Système de confiance : plan avant exécution, audit trail, rollback | Cohérent avec la légibilité mise en avant par l'IA constitutionnelle ([doc 03 §2](03-ce-qui-rend-une-ia-la-meilleure.md#la-légibilité-comme-propriété-de-fiabilité)) |

## 2. Trois ajouts concrets à faire au pipeline

### A. Rendre le streaming systématique, pas optionnel

Le [doc 06](../docs/06-architecture-technique.md) décrit le pipeline prompt→production mais ne précise pas la restitution en temps réel. À corriger : **chaque étape du pipeline (analyse, génération, tests, déploiement) doit streamer son statut vers l'interface utilisateur dès qu'elle démarre**, pas seulement à la fin. C'est le levier de vitesse perçue le moins cher et le plus efficace identifié dans cette recherche ([doc 01](01-performance-et-vitesse.md#streaming--le-levier-n1)) — et il est déjà à moitié prévu dans le "système de confiance" du doc 06 (« l'état en direct »). Il faut le rendre explicite comme exigence technique, pas seulement comme principe de confiance.

### B. Ajouter une boucle de critique visuelle par capture d'écran, pas seulement par lecture de code

Le pipeline actuel prévoit un `Security Agent` et un `QA Agent`, mais pas d'agent qui **regarde une image** du résultat rendu. La recherche montre que c'est précisément ce qui manque à un pipeline texte-seul pour détecter les problèmes de hiérarchie visuelle, d'alignement et de polish.

```text
Ajout recommandé au pipeline (doc 06 §5) :

... → Déploiement preview
    → Capture d'écran automatique (Playwright, déjà dans la stack)
    → Vision Critic Agent : lit la capture, évalue polish / cohérence / typographie
    → Si score insuffisant : nouvelle itération du Code Agent, ciblée sur les points relevés
    → Validation utilisateur
```

Playwright est déjà dans la stack MVP (voir [doc 06 §3](../docs/06-architecture-technique.md#3-stack-mvp-concrète)) — l'ajout ne demande pas de nouvel outil, seulement un agent supplémentaire qui consomme les captures qu'il produit déjà pour les tests.

### C. Activer le cache de prompts par défaut sur le routeur

LiteLLM supporte le cache de prompts des fournisseurs sous-jacents. À rendre explicite comme configuration par défaut plutôt que comme option : sur des tâches répétitives (reformulation de blueprint, génération de composants similaires entre tenants du même vertical), le gain de latence et de coût documenté (jusqu'à 90 % sur les requêtes en cache) est directement aligné avec l'objectif de marge brute ≥ 70 % du [doc 02 — Business model](../docs/02-business-model.md#5-unit-economics).

## 3. Ce qui reste hors de portée — et pourquoi ce n'est pas grave

Afrosite ne contrôle ni l'architecture des modèles (MoE, quantization) ni leur méthode d'entraînement (IA constitutionnelle, RLHF). Ce n'est pas une faiblesse à corriger : c'est exactement le principe déjà posé dans le [README du projet](../docs/00-README.md#principe-directeur-à-ne-jamais-perdre-de-vue) — réutiliser ce qui est commodité mondiale (ici, les modèles IA eux-mêmes), construire ce qui est spécifique et différenciant (l'orchestration, les blueprints, les boucles de critique, la couche de confiance).

**La compétitivité d'Afrosite sur l'IA ne viendra jamais du modèle utilisé — elle viendra de la qualité de l'ingénierie produit autour du modèle.** C'est la conclusion la plus solide de cette recherche, et elle est bonne nouvelle : ce sont exactement les décisions qu'une petite équipe peut contrôler sans budget d'entraînement de modèle.
