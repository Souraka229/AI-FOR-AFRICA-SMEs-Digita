# Design visuel généré par IA — comment les meilleurs systèmes y arrivent

Générer une interface qui fonctionne est facile pour une IA en 2026. Générer une interface qui a du goût reste rare. La recherche et les produits qui y arrivent partagent un même principe : **le design n'est jamais produit en un seul passage** — il passe par une boucle de génération puis de critique, souvent avec une vision réelle du rendu (pas seulement du code).

## 1. Ce que font les leaders du marché

| Outil | Approche | Résultat observé |
|---|---|---|
| **v0 (Vercel)** | Comprend hiérarchie visuelle, espacement, esthétique moderne ; import direct depuis Figma avec lecture exacte des couleurs et tokens de design du fichier source | Composants "polis dès la sortie", parce qu'ils héritent d'un vrai design system plutôt que d'en inventer un |
| **Lovable** | A pivoté vers des produits "lovable" — la philosophie affichée : un logiciel généré par IA ne doit pas ressembler à un logiciel généré par IA. Fort accent sur les animations (Framer Motion), les palettes de couleurs sophistiquées, la gestion d'état complexe | Considéré en 2026 comme la référence pour l'esthétique "polie" par défaut |
| **Bolt** | Priorise le code fonctionnel sur l'esthétique — le rendu est souvent générique par défaut ; a introduit des workflows multi-agents (un agent base de données, un agent UI séparés) | Génération full-stack plus stable, mais design moins raffiné sans intervention |

Point commun observé dans la recherche de marché : la plupart de ces outils s'appuient sur Claude Sonnet comme modèle principal de génération, avec d'autres modèles (Gemini, o1) mobilisés pour des cas d'usage spécifiques — la qualité de design ne vient donc pas uniquement du modèle sous-jacent, mais de la couche produit construite autour.

## 2. Ce que montre la recherche académique

### Le pattern générateur/critique (generator-critic)

Le pattern le plus robuste identifié dans la littérature récente : un agent génère, un second agent **critique** le résultat selon des critères explicites, la boucle se répète jusqu'à un niveau de qualité acceptable — le même principe que ce que ce projet a déjà retenu pour Afrosite avec l'agent "UI Critic" (voir [doc 06 §11](../docs/06-architecture-technique.md#11-design-system-et-direction-artistique)).

### Le retour visuel, pas seulement le retour sur le code

Une avancée déterminante identifiée dans la recherche 2026 : un pipeline entièrement automatisé où un modèle vision-langage (VLM) observe une **capture d'écran rendue** de la page web générée et fournit un retour visuel — pas seulement une lecture du code source. Les critiques itératives améliorent la fidélité visuelle sur plusieurs modèles générateurs de code différents. Un système efficace pour les interfaces web doit être **multimodal** : analyser le code pour la complétude structurelle, ET analyser la représentation visuelle (captures d'écran) pour évaluer la hiérarchie visuelle et le niveau de finition global.

Catégories de critique identifiées par la recherche, par ordre de fréquence :
1. **Polish visuel** — espacement, alignement, raffinement
2. **Cohérence des éléments d'interface** — les composants se ressemblent-ils entre eux
3. **Typographie** — polices, tailles, lisibilité

### Boucle d'auto-QA visuelle

Le principe du "self-QA loop" : en capturant et évaluant la sortie visuelle plutôt que le texte brut seul, la boucle attrape des erreurs qu'une QA uniquement textuelle manquerait — un modèle capable de vision est utilisé spécifiquement pour la critique visuelle des rendus.

## 3. Les ingrédients concrets d'un bon système de design IA

En croisant produits et recherche, cinq ingrédients reviennent systématiquement :

1. **Un vrai design system en entrée, pas une page blanche.** v0 excelle en important les tokens Figma existants — l'IA personnalise un système déjà cohérent plutôt que d'en inventer un à chaque génération. Directement aligné avec l'approche blueprint d'Afrosite ([doc 06 §12](../docs/06-architecture-technique.md#12-premier-produit-technique-à-construire)) : 80 % de composants éprouvés, 20 % de génération contrôlée.
2. **Une boucle générateur → critique, jamais un seul passage.** Le premier résultat d'une IA est rarement le meilleur ; la qualité vient de l'itération automatisée, pas d'un meilleur prompt initial.
3. **Un critique qui voit une image, pas seulement du texte.** Un VLM qui regarde une capture d'écran détecte des problèmes (alignement, contraste, densité) qu'aucune analyse de code ne peut voir.
4. **Des critères de critique explicites et écrits**, pas un jugement flou du type "améliore le design". Les meilleurs systèmes listent des catégories précises (polish, cohérence, typographie) plutôt qu'un feedback générique.
5. **Séparer la décision de direction artistique de l'exécution.** Le rôle d'un agent "Art Director" (palette, ton, contraintes) est distinct du rôle d'un agent "UI Generator" (exécution) — mélanger les deux produit un résultat correct mais sans personnalité, le symptôme classique du "design IA générique".

## 4. Le piège à éviter : le "slop" visuel généré par IA

La littérature identifie un ensemble de tics visuels qui trahissent immédiatement une interface générée sans direction artistique : dégradés violet/bleu par défaut, glassmorphism décoratif, cartes avec une barre de couleur à gauche, polices surutilisées (Inter, Roboto, Arial), emoji utilisés comme icônes fonctionnelles. Un bon système de critique doit explicitement les détecter et les rejeter — c'est exactement le rôle donné à l'agent UI Critic dans l'architecture Afrosite, et la règle déjà appliquée dans la [charte graphique Afrosite](https://claude.ai/code/artifact/c98eb71b-f31c-408b-bd7f-4526bbc3e019).

**Sources :**
- [Lovable — Lovable vs Bolt vs v0](https://lovable.dev/guides/lovable-vs-bolt-vs-v0)
- [ToolJet Blog — Lovable vs Bolt vs V0 comparé en 2026](https://blog.tooljet.com/lovable-vs-bolt-vs-v0/)
- [GetMocha — Best AI App Builder 2026](https://getmocha.com/blog/best-ai-app-builder-2026)
- [arXiv — Vision-Guided Iterative Refinement for Frontend Code Generation](https://arxiv.org/pdf/2604.05839)
- [ACM CHI 2026 — Automating UI Optimization through Multi-Agentic Reasoning](https://dl.acm.org/doi/10.1145/3772318.3791444)
- [MindStudio — What Is the Self-QA Loop?](https://www.mindstudio.ai/blog/what-is-self-qa-loop-ai-agents)
- [arXiv — PerceptUI: LLM Agents as Human-Aligned Synthetic Users for UI/UX Evaluation](https://arxiv.org/html/2606.05697v1)
