# Afrosite Web

Next.js 16 sert le site, le Studio et les previews multi‑tenant.

Depuis la racine :

```powershell
pnpm install
Copy-Item apps/web/.env.example apps/web/.env.local
pnpm --filter web dev
```

Pour une génération réelle en local, renseigner seulement
`AI_GATEWAY_API_KEY`. Sur Vercel, l’OIDC peut remplacer cette clé. Aucun
fallback regex ne s’active si le LLM est absent : le Studio affiche l’erreur.

Vérifications :

```powershell
pnpm --filter @afrosite/llm check
pnpm --filter web eval:agents
pnpm --filter web eval:llm
pnpm --filter web check:pay
pnpm --filter web test:e2e
```

Le Studio produit un Blueprint en streaming, applique Gate 1 puis attend une
approbation humaine avant de sauvegarder la preview. Production et paiements
live restent impossibles depuis ce flux.

## Vision Critic

Sur un serveur déjà lancé, l’audit visuel capture la preview en desktop et en
Pixel 7 puis demande une critique bloquante au modèle de raisonnement :

```powershell
pnpm --filter web vision cadjehoun-wax
```

Sortie non nulle si le score tombe sous 75 ou si une issue `high` existe. Le
script exige une clé LLM ; sa logique bloquante est couverte sans clé par
`pnpm --filter web eval:llm`.
