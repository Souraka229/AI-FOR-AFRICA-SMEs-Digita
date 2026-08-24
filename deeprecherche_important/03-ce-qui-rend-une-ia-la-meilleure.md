# Ce qui rend une IA "la meilleure" — architecture, entraînement, raisonnement

Être "le meilleur" en IA en 2026 ne se résume pas à un seul score de benchmark. Trois décisions indépendantes déterminent ce qu'un modèle peut faire, à quelle vitesse, et avec quelle fiabilité.

## 1. L'architecture détermine la capacité par unité de calcul

Voir le détail complet dans [doc 01](01-performance-et-vitesse.md#1-couche-modèle). Le point clé pour ce document : la quasi-totalité des modèles de pointe en 2026 utilisent une architecture **Mixture of Experts (MoE)**, parce qu'elle découple la capacité totale du modèle (combien il "sait") du coût de calcul par token (combien ça coûte de répondre). C'est ce qui permet à un modèle d'être à la fois très capable ET économiquement servable à grande échelle.

## 2. La méthode d'entraînement détermine la fiabilité du jugement

C'est le facteur le moins visible dans les benchmarks de vitesse, mais le plus déterminant pour la confiance qu'on peut accorder à un système IA en production.

### L'IA constitutionnelle (Anthropic)

Approche qui utilise un ensemble écrit de principes pour guider le comportement du modèle, réduisant la dépendance à la notation humaine à chaque étape. Le modèle est entraîné à **critiquer et réviser ses propres réponses** selon ces principes explicites, plutôt que d'inférer des valeurs uniquement à partir de préférences humaines notées a posteriori.

En janvier 2026, Anthropic a publié une nouvelle constitution pour Claude marquant un changement de philosophie : d'une liste de règles vers une **explication du raisonnement** — le document n'indique plus seulement quoi faire, mais pourquoi, avec l'objectif explicite de permettre au modèle de généraliser à des situations qu'aucune règle spécifique n'aurait anticipées. Une hiérarchie à quatre niveaux de priorité structure les arbitrages : sécurité, éthique, conformité, puis utilité.

**Pourquoi c'est pertinent au-delà de la sécurité** : un modèle entraîné à critiquer ses propres réponses selon des principes explicites est structurellement mieux équipé pour les boucles de génération/critique décrites dans le [doc 02](02-design-visuel-ia.md) — la capacité d'auto-critique n'est pas qu'une propriété de sécurité, c'est aussi une propriété de qualité produit.

### La légibilité comme propriété de fiabilité

Un point souligné par la recherche : quand un modèle entraîné par IA constitutionnelle se comporte d'une certaine façon, il existe un document écrit qui prétend expliquer pourquoi. Que ce document reflète fidèlement le comportement réel du modèle est une question qui peut être examinée et débattue — ce qui est beaucoup plus difficile quand les valeurs sont implicites dans un processus d'entraînement purement statistique. Cette légibilité est elle-même une propriété utile : elle permet d'auditer, de corriger et d'expliquer le comportement d'un système IA en production — un enjeu direct pour la confiance client d'Afrosite (voir [doc 06 §10](../docs/06-architecture-technique.md#10-système-de-confiance--ce-que-lutilisateur-doit-toujours-voir)).

## 3. Le raisonnement étendu — arbitrer vitesse contre profondeur

Un modèle qui "réfléchit" plus longtemps avant de répondre (chain-of-thought étendu, plusieurs passes de réflexion) produit généralement de meilleures réponses sur les tâches complexes, au prix d'une latence plus élevée. La recherche sur l'arbitrage qualité/coût/vitesse en réflexion à l'inférence ("inference-time LLM reflection") montre qu'il existe un point d'équilibre : au-delà d'un certain nombre de passes de réflexion, le gain de qualité marginal ne justifie plus le coût de latence additionnel.

**Implication pratique** : ce n'est pas la même architecture de raisonnement qui doit être utilisée pour "reformuler un menu" que pour "concevoir l'architecture complète d'une application" — exactement le principe déjà retenu dans le routeur IA à plusieurs niveaux d'Afrosite ([doc 06 §9](../docs/06-architecture-technique.md#9-système-de-réponse-rapide-routage-ia)).

## 4. Synthèse — les trois familles de décisions ne se remplacent pas

| Décision | Ce qu'elle améliore | Qui la contrôle |
|---|---|---|
| Architecture (MoE, quantization) | Le rapport capacité/coût de calcul | Le fournisseur de modèle — hors de portée d'Afrosite |
| Méthode d'entraînement (constitutionnelle, RLHF) | La fiabilité du jugement et la capacité d'auto-critique | Le fournisseur de modèle — hors de portée d'Afrosite |
| Raisonnement étendu | La qualité sur les tâches complexes, au prix de la latence | Configurable côté produit — Afrosite peut choisir quand l'activer |
| Ingénierie produit (streaming, cache, boucles critique/vision) | La vitesse perçue et la qualité visuelle du résultat livré | **Entièrement contrôlable par Afrosite** |

**Le point le plus important pour ce projet** : les deux premières familles de décisions sont prises par les laboratoires IA (Anthropic, OpenAI, Google) — Afrosite les consomme via LiteLLM sans les contrôler directement. Mais les deux dernières — quand utiliser le raisonnement étendu, et comment structurer les boucles de génération/critique visuelle — sont exactement les décisions qu'Afrosite prend déjà dans son architecture (voir [doc 04 — application à Afrosite](04-application-a-afrosite.md)).

**Sources :**
- [Anthropic — Claude's new Constitution](https://anthropic.com/news/claude-new-constitution)
- [BISI — Claude's New Constitution: AI Alignment, Ethics, and the Future of Model Governance](https://bisi.org.uk/reports/claudes-new-constitution-ai-alignment-ethics-and-the-future-of-model-governance)
- [TDWI — Constitutional AI: How Anthropic Trains Models Using Written Principles](https://tdwi.org/blogs/ai-101/2026/05/constitutional-ai.aspx)
- [Oxford AI Ethics — Claude's new Constitution: two evaluative continua](https://www.oxford-aiethics.ox.ac.uk/blog/claudes-new-constitution-two-evaluative-continua)
- [arXiv — Finding the Sweet Spot: Trading Quality, Cost, and Speed During Inference-Time LLM Reflection](https://arxiv.org/pdf/2510.20653)
- [BuildFastWithAI — Mixture of Experts explained (2026)](https://www.buildfastwithai.com/blogs/mixture-of-experts-moe-explained)
