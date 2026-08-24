# Performance et rapidité — ce qui rend une IA réellement rapide

Trois couches distinctes déterminent la vitesse d'un système IA : le modèle lui-même, le système qui le sert (inférence), et l'application qui l'entoure. Empiler des optimisations sur les trois couches peut réduire le coût d'inférence de 80 % ou plus.

## 1. Couche modèle

### Mixture of Experts (MoE) — pourquoi tous les modèles de pointe l'utilisent en 2026

Un modèle dense active **tous** ses paramètres à chaque token — un modèle de 100 milliards de paramètres fait 100 milliards de multiplications même pour une question simple. Le MoE découpe le modèle en sous-réseaux spécialisés ("experts") et un routeur n'active qu'un petit sous-ensemble pertinent pour chaque token.

- Le modèle peut contenir beaucoup plus de paramètres (donc plus de connaissance) sans augmenter proportionnellement le calcul par token.
- Exemple concret : DeepSeek-R1 a 671 milliards de paramètres au total, mais n'en active que 37 milliards par token.
- Résultat : quasiment tous les modèles de pointe en 2026 sont construits en MoE, parce que cette architecture égale ou dépasse un modèle dense à coût de calcul équivalent.

### Quantization — réduire la précision sans perdre la qualité

Passer de FP16 à INT8 ou INT4 réduit la mémoire de 2 à 4× et le coût d'inférence d'environ 50 %, tout en conservant 95 à 99 % de la précision d'origine. Des techniques comme AWQ (Activation-aware Weight Quantization) et GPTQ préservent la qualité des poids sensibles tout en compressant agressivement le reste — near-FP16 quality à vitesse INT4.

### Décodage spéculatif — un petit modèle qui propose, un grand qui vérifie

Un modèle "brouillon" léger propose plusieurs tokens à l'avance ; le grand modèle les vérifie tous en parallèle au lieu de générer token par token. Gain observé : 1,5× à 3× de réduction de latence, sans perte de qualité, particulièrement efficace pour les applications sensibles à la latence.

### Cache KV — la mémoire qui explose avec le contexte

Le modèle doit stocker les paires clé-valeur de tous les tokens précédents pour générer le suivant ; cette mémoire grossit avec la longueur du contexte. Les avancées récentes compressent ce cache de manière agressive sans perte notable :
- **TurboQuant** (Google, 2026) compresse le cache KV à 3 bits avec une perte de précision mesurée comme nulle — 6× de réduction mémoire.
- **KIVI**, quantization 2-bit sans réglage fin nécessaire, réduit le pic mémoire de 2,6×.

## 2. Couche système d'inférence

- **Batching continu** et **PagedAttention** : servir plusieurs requêtes simultanément sans gaspiller de mémoire sur les séquences les plus courtes.
- **Matériel spécialisé vs GPU généraliste** : Llama 4 Scout sur du matériel d'inférence Cerebras dépasse 2 600 tokens de sortie par seconde — record vérifié indépendamment. Sur des GPU cloud standards, les meilleurs modèles plafonnent plutôt autour de 850–900 tokens/seconde. **Le matériel qui sert le modèle compte souvent plus que le modèle choisi.**
- Les modèles les plus rapides du marché ne sont généralement pas ceux qui dominent les classements de capacité — il y a un vrai compromis vitesse/intelligence à arbitrer selon la tâche.

## 3. Couche application — ce qui compte le plus pour l'utilisateur final

C'est la couche la plus actionnable, la moins chère à mettre en place, et celle que la recherche identifie comme ayant le plus gros effet sur la **vitesse perçue**.

### Streaming — le levier n°1

Une réponse qui n'apparaît qu'une fois complètement générée se sent lente, même si le temps total est identique à une réponse qui streame. Le principe : ne jamais attendre que le backend ait fini de générer tout le paragraphe avant d'afficher quelque chose. Dès que le premier mot apparaît en moins de 500 ms, la latence perçue tombe quasiment à zéro — même si la génération complète prend 8 secondes.

Effets du streaming :
- change la perception de vitesse ;
- construit la confiance dans le résultat (l'utilisateur voit que "ça travaille") ;
- permet d'interrompre une mauvaise réponse tôt, avant la fin de la génération.

### Cache de prompts (prompt caching)

Le cache sémantique est l'un des plus gros gains de latence perçue disponibles. Anthropic et OpenAI rapportent tous deux des réductions de latence et de coût de 50 à 90 % grâce au cache de prompts — une réduction de coût API de 41 à 80 % et une amélioration du time-to-first-token (TTFT) de 13 à 31 %. Un cache hit réduit nettement le TTFT, ce qui améliore la réactivité perçue même quand le temps de génération total reste similaire.

### Le time-to-first-token (TTFT) plutôt que le débit total

En pratique, ce que l'utilisateur remarque le plus n'est pas le débit (tokens/seconde) mais le **délai avant le premier signe de vie**. Un système qui optimise pour un TTFT bas plutôt que pour un débit brut élevé produit une expérience perçue comme plus rapide, à coût d'infrastructure souvent inférieur.

## Tableau récapitulatif — impact vs effort d'implémentation

| Technique | Gain typique | Effort pour Afrosite |
|---|---|---|
| Streaming des réponses IA | Latence perçue → quasi 0 dès 500 ms | Faible — changement côté frontend/API |
| Cache de prompts | -50 à -90 % latence/coût sur requêtes répétées | Faible — activable au niveau du routeur LiteLLM |
| Routage vers un modèle léger pour les tâches simples | Coût et latence réduits, pas de perte perçue | Déjà prévu dans [doc 06 §9](../docs/06-architecture-technique.md#9-système-de-réponse-rapide-routage-ia) |
| Décodage spéculatif | 1,5–3× plus rapide | Dépend du fournisseur IA (souvent déjà activé côté API) |
| Quantization / MoE | Coût et vitesse d'inférence | Hors de portée — décision du fournisseur de modèle, pas d'Afrosite |

**Conclusion pour Afrosite** : les deux leviers les plus rentables ne demandent pas de changer de fournisseur IA ni d'investir dans du matériel spécialisé — c'est le **streaming systématique** et le **cache de prompts**, déjà cohérents avec le principe "système de réponse rapide" du [doc 06](../docs/06-architecture-technique.md#9-système-de-réponse-rapide-routage-ia).

**Sources :**
- [Fastio — Fastest AI in 2026: Speed Benchmarks](https://fast.io/resources/fastest-ai-2026/)
- [ModelGrep — Fastest LLMs by tokens per second (Aug. 2026)](https://modelgrep.com/best/fastest)
- [Morph — LLM Inference Optimization 2026](https://www.morphllm.com/llm-inference-optimization)
- [Google Cloud Blog — Five techniques for efficient LLM inference](https://cloud.google.com/blog/topics/developers-practitioners/five-techniques-to-reach-the-efficient-frontier-of-llm-inference)
- [MyEngineeringPath — Inference Optimization: Quantization, Distillation & Speed](https://myengineeringpath.dev/genai-engineer/inference-optimization/)
- [BuildFastWithAI — Mixture of Experts explained (2026)](https://www.buildfastwithai.com/blogs/mixture-of-experts-moe-explained)
- [TensorOps — LLM Mixture of Experts, 2026 field guide](https://tensorops.ai/blog/what-is-mixture-of-experts-llm)
- [Redis Blog — Streaming LLM Responses: Make Your AI App Feel Fast](https://redis.io/blog/streaming-llm-responses/)
- [Techademy — AI Latency Patterns: Caching, Streaming & Pre-fetching](https://www.techademy.com/ai-latency-patterns-caching-streaming)
- [SystemDR — Prompt Caching Strategies](https://systemdr.systemdrd.com/p/prompt-caching-strategies-reducing)
