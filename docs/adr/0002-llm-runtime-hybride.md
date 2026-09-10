# ADR 0002 — Runtime LLM hybride

- Statut : accepté
- Date : 2026-09-10
- Décideurs : Souraka + SERGE

## Contexte

Le studio hackathon analyse aujourd’hui les prompts par expressions régulières et
clone trois exemples. Afrosite doit réellement générer le Blueprint et les
personnalisations avec un LLM, tout en restant indépendant d’un fournisseur.

Le playbook cible LiteLLM, LangGraph et OpenHands. Le runtime actuel est une
application Next.js déployable sur Vercel : imposer tout le plan de contrôle
avant le premier appel LLM retarderait inutilement la preuve produit.

## Décision

1. `packages/llm` est l’unique porte LLM du code TypeScript.
2. L’adaptateur initial utilise AI SDK et AI Gateway. Les modèles sont choisis
   par capacité (`light`, `reasoning`, `code`), jamais par le métier.
3. LiteLLM reste un backend interchangeable via son API OpenAI-compatible. Il
   devient le routeur central lors du self-hosting ou du multi-fournisseur
   avancé.
4. LangGraph est réservé aux runs persistants multi-étapes avec reprise et
   approbation humaine. Un simple Blueprint ne nécessite pas de graphe.
5. OpenHands exécute le Code Agent uniquement dans une sandbox Docker.
6. Les règles sensibles restent déterministes : secrets, BJ, XOF, budget,
   preview, RBAC et paiement confirmé uniquement après `verify()` serveur.

## Conséquences

- Changer de routeur ne modifie pas les agents : seuls les adaptateurs changent.
- Aucun import direct d’un SDK fournisseur hors `packages/llm`.
- Aucun fallback silencieux vers le pipeline regex en production.
- Les appels live sont facultatifs en CI ; les faux providers sont injectés.
- Le cache de prompts est activé par défaut. `AFROSITE_LLM_PROMPT_CACHE=0` le coupe.
- Temporal reste réservé à l’argent et au provisioning, jamais au raisonnement.
