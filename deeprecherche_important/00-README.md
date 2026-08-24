# Deep research — comment les IA de pointe deviennent les meilleures (performance, design visuel, rapidité)

Recherche approfondie (août 2026) sur ce que font réellement les systèmes d'IA de pointe — modèles de langage, agents de code, générateurs d'interfaces — pour se distinguer sur trois axes : la performance/qualité globale, la qualité du design visuel produit, et la rapidité perçue et réelle. Objectif : comprendre les mécanismes concrets, pas le marketing, pour pouvoir les appliquer à l'architecture IA d'[Afrosite](../docs/06-architecture-technique.md).

## Sommaire

| # | Document | Contenu |
|---|---|---|
| 01 | [Performance et rapidité](01-performance-et-vitesse.md) | Les techniques d'inférence qui rendent une IA rapide : décodage spéculatif, quantization, cache KV, MoE, streaming, cache de prompts |
| 02 | [Design visuel généré par IA](02-design-visuel-ia.md) | Comment v0, Lovable, Bolt et la recherche académique obtiennent un design de qualité — boucles critique/génération, retour visuel, tokens de design |
| 03 | [Ce qui rend une IA "la meilleure"](03-ce-qui-rend-une-ia-la-meilleure.md) | Architecture (MoE), méthode d'entraînement (IA constitutionnelle), raisonnement étendu — ce qui différencie les laboratoires de pointe |
| 04 | [Application à Afrosite](04-application-a-afrosite.md) | Ce qu'on prend concrètement de cette recherche pour le pipeline IA d'Afrosite |

## Constat central

Il n'existe pas un seul levier qui rend une IA "la meilleure". Trois familles de décisions, indépendantes les unes des autres, se combinent :

```text
ARCHITECTURE           →  combien de calcul par token, quelle capacité de raisonnement
                           (Mixture of Experts, décodage spéculatif, quantization)

MÉTHODE D'ENTRAÎNEMENT  →  quelle qualité de jugement, quelle fiabilité du comportement
                           (IA constitutionnelle, RLHF, raisonnement étendu)

INGÉNIERIE PRODUIT      →  ce que l'utilisateur perçoit réellement
                           (streaming, cache, boucles de critique visuelle, design tokens)
```

Le point le plus contre-intuitif de cette recherche : **la vitesse perçue par l'utilisateur dépend presque autant de l'ingénierie produit (streaming, cache, time-to-first-token) que de la puissance brute du modèle.** Un modèle plus lent en tokens/seconde mais qui streame dès 500 ms se sent plus rapide qu'un modèle plus rapide qui répond d'un bloc après 3 secondes. C'est directement actionnable pour Afrosite sans dépendre d'un fournisseur IA plus puissant.
