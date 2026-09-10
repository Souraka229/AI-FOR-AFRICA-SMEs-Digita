<div align="center">

<img src=".github/assets/header.svg" alt="Afrosite — décrivez votre activité, vendez et encaissez en Mobile Money, sans une ligne de code" width="100%">

<br><br>

<img alt="Statut" src="https://img.shields.io/badge/statut-pr%C3%A9--lancement-C1502E?style=for-the-badge">&nbsp;
<img alt="Marché" src="https://img.shields.io/badge/march%C3%A9-Cotonou%20%E2%86%92%20UEMOA-A2711F?style=for-the-badge">&nbsp;
<img alt="Paiement" src="https://img.shields.io/badge/paiement-Mobile%20Money-1F7A53?style=for-the-badge">&nbsp;
<img alt="Devise" src="https://img.shields.io/badge/devise-FCFA-211B17?style=for-the-badge">&nbsp;
<img alt="Documentation" src="https://img.shields.io/badge/docs-13%20documents-A2711F?style=for-the-badge">

<br><br>

### Afrosite ne génère pas un site de plus.

On transforme une activité informelle en **entreprise digitale opérable** :<br>
créer · encaisser en Mobile Money · piloter — sur un socle unique, décliné en **trois métiers**.<br>
Français natif. FCFA natif. Sans une ligne de code.

</div>

<img src=".github/assets/divider.svg" alt="" width="100%">

## Le problème → la réponse

Les TPE/PME africaines tournent avec WhatsApp, un cahier et Excel. Les créateurs d'apps par IA du marché ne parlent pas Mobile Money, facturent en dollars, et s'arrêtent au site vitrine.

| Aujourd'hui | Avec Afrosite |
|---|---|
| Commandes éparpillées sur WhatsApp | Prise de commande centralisée, en temps réel |
| Erreurs de caisse, monnaie approximative | Caisse reliée au catalogue, montants recalculés côté serveur |
| « Merci » comme seule preuve de paiement | Reçu signé, vérifié serveur, **réconcilié automatiquement** |
| Aucune vision des encaissements | Réconciliation du soir + résumé WhatsApp quotidien |
| Facturé en USD, interface anglaise | FCFA natif, français natif, pensé pour Android sur réseau lent |
| Un site vitrine, rien derrière | Catalogue, commandes, caisse, CRM, rapports — un vrai outil |

> **Le principe.** Un prompt ne déclenche jamais une action risquée directement. L'IA propose, des règles contrôlent, les tests vérifient, l'humain valide. Afrosite n'est **jamais** dépositaire des fonds — orchestrateur au-dessus d'un PSP agréé BCEAO.

<br>

<div align="center">
<img src=".github/assets/flow.svg" alt="Pipeline : prompt en langage naturel vers production, avec six garde-fous automatiques" width="100%">
</div>

<img src=".github/assets/divider.svg" alt="" width="100%">

## L'équipe

<table>
  <tr>
    <td align="center" width="33%">
      <img src=".github/assets/avatar-souraka.svg" width="168" alt="Souraka HAMIDA"><br>
      <b>Souraka&nbsp;HAMIDA</b><br>
      <sub>Product Lead · Front‑end · Data / Recherche</sub>
    </td>
    <td align="center" width="33%">
      <img src=".github/assets/avatar-chitou.svg" width="168" alt="CHITOU"><br>
      <b>CHITOU</b><br>
      <sub>Design Lead · Design System · Design Engineering</sub>
    </td>
    <td align="center" width="33%">
      <img src=".github/assets/avatar-serge.svg" width="168" alt="SERGE"><br>
      <b>SERGE</b><br>
      <sub>Backend · Infra · Paiement · Agents IA</sub>
    </td>
  </tr>
</table>

<details>
<summary><b>Qui possède quoi</b></summary>

<br>

**Souraka HAMIDA — Product Lead · Front‑end · Data / Recherche**
- Vision produit, backlog, priorisation, arbitrages de périmètre
- Contrat `Blueprint JSON` (`packages/contracts`) — la frontière typée front/back
- Architecture front‑end : Next.js, SSR, SEO natif par tenant
- Qualité des prompts & *eval harness* des agents
- Instrumentation des coûts IA/infra par client, unit economics
- Veille & recherche (`deeprecherche_important/`), go‑to‑market pilotes

**CHITOU — Design Lead · Design System · Design Engineering**
- Design system Afrosite : foundations, tokens sémantiques, composants livrés en code
- Patterns par blueprint : POSLayout, KitchenBoard, QRMenu, MobileCheckout…
- Direction artistique, rejet du « slop » IA, conformité charte de marque
- Boucle de critique visuelle : critères écrits, agent UI / Vision Critic
- Accessibilité & Core Web Vitals sur mobile Android / réseau lent

**SERGE — Backend · Infra · Paiement · Agents IA**
- API (FastAPI), modèle de données PostgreSQL, migrations, RBAC multi‑tenant
- Orchestration des agents (LangGraph), workflows durables (Temporal)
- Intégration Mobile Money derrière une couche `PaymentProvider` abstraite
- CI/CD (GitHub Actions), déploiement (Docker Compose + Coolify), sauvegardes
- Sécurité applicative (SAST, scans, 6 gates), ledger immuable, réconciliation

</details>

<img src=".github/assets/divider.svg" alt="" width="100%">

<div align="center">
<img src=".github/assets/metrics.svg" alt="Repères : moins d'une heure du prompt à la boutique en ligne, 100 % des paiements réconciliés, zéro ligne de code, marge brute cible d'au moins 70 %" width="100%">
</div>

## Trois métiers, un socle

Le socle commun — catalogue, commande, encaissement, CRM léger, dashboard — est **identique en code** entre les trois blueprints. Seuls les modules spécifiques changent.

| Commerce | Restaurant | Services |
|---|---|---|
| Boutique en ligne, commandes WhatsApp centralisées, facturation automatique | Menu QR, caisse, écran cuisine, livraison, fidélité | Rendez‑vous, devis, factures, rappels clients automatiques |
| `+` stock simple, suivi de livraison | `+` KDS, gestion des tables / à emporter | `+` agenda, relances avant rendez‑vous |

<img src=".github/assets/divider.svg" alt="" width="100%">

## Stack

<p>
<img alt="Next.js" src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white">
<img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white">
<img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
<img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
<img alt="Redis" src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white">
<img alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
<img alt="GitHub Actions" src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white">
</p>

`LangGraph` (agents) · `Temporal` (workflows argent / provisioning) · `packages/llm` (AI SDK + AI Gateway, LiteLLM interchangeable) · `Playwright` (E2E) · `Coolify` (déploiement).

### Golden path LLM contrôlé

`packages/llm` est l’unique porte vers les modèles : AI SDK + AI Gateway par
défaut, LiteLLM en backend interchangeable. Intent et Product Architect
produisent des objets Zod ; Gate 1 peut demander une seule réparation. Le
runtime LangGraph persiste le run et s’interrompt pour approbation humaine.
OpenHands ne travaille que dans Docker sur une copie éphémère et renvoie un
overlay ciblant `feature/generated-*` — jamais un push ni un paiement.

Les règles Security/QA vivent dans un seul fichier,
[`packages/contracts/generation-guardrails.json`](packages/contracts/generation-guardrails.json),
lu à la fois par `apps/web` et par `services/agents` : chemins interdits,
secrets, logique argent, déploiement production.

Décision complète : [ADR 0002](docs/adr/0002-llm-runtime-hybride.md).

Arborescence complète du monorepo : [playbook §6.1](docs/11-playbook-equipe.md#61--structure-des-dossiers-arborescence-complète-du-monorepo).

<img src=".github/assets/divider.svg" alt="" width="100%">

## Documentation

| # | Document | Contenu |
|---|---|---|
| 00 | [Sommaire](docs/00-README.md) | Comment lire la documentation, principe directeur |
| 01 | [Cahier des charges](docs/01-cahier-des-charges.md) | Vision, périmètre, exigences, critères d'acceptation |
| 02 | [Business model](docs/02-business-model.md) | Canvas, pricing FCFA, unit economics |
| 03 | [Analyse concurrentielle](docs/03-analyse-concurrentielle.md) | Concurrents, SWOT, PESTEL |
| 04 | [Différenciation & positionnement](docs/04-differenciation-positionnement.md) | Le moat défendable, le message |
| 05 | [Roadmap leadership Afrique de l'Ouest](docs/05-roadmap-leadership-afrique.md) | Go‑to‑market, 5 premiers clients, expansion UEMOA |
| 06 | [Architecture technique](docs/06-architecture-technique.md) | Stack, repos open source, pipeline prompt→production, sécurité |
| 07 | [Plan d'exécution 90 jours](docs/07-plan-execution-90-jours.md) | Quoi faire, dans quel ordre |
| 08 | [SEO natif & clonage de sites](docs/08-seo-et-clonage-de-sites.md) | SEO technique, SEO local, garde‑fous légaux |
| 09 | [Branding, logo & positionnement](docs/09-branding-logo-positionnement.md) | Charte visuelle (version texte) |
| 10 | [Ressources de A à Z](docs/10-ressources-de-a-a-z.md) | Toutes les ressources externes, dans l'ordre d'usage |
| 11 | [Playbook d'équipe](docs/11-playbook-equipe.md) | Rôles, RACI, Kanban/Notion, structure des dossiers, branches Git, système de prompts, plan 90 jours |
| 12 | [Pitch — Hackathon Cursor × Devs Days](docs/12-pitch-hackathon.md) | Accroche, candidature, script vidéo, pitch de finale, Q&A jury, périmètre de build |
| 13 | [Guide solo Souraka + Serge](docs/13-guide-solo-souraka-serge.md) | Carte du code, état réel, feuille de route si une personne fait les deux |

<img src=".github/assets/divider.svg" alt="" width="100%">

## Feuille de route — 90 jours

| Phase | Jours | Objectif |
|---|---|---|
| **1 — Fondation fiable** | 1 → 30 | Socle commun + 3 blueprints, CI, PostgreSQL + sauvegardes, paiement **sandbox** |
| **2 — Automatisation IA** | 31 → 60 | Prompt → Blueprint JSON validé → génération contrôlée, 6 gates automatiques, preview auto |
| **3 — Commercialisation** | 61 → 90 | 5 pilotes à Cotonou en production, paiement réel, résumé WhatsApp, audit sécurité externe |

Décision de fin de phase : les 5 pilotes utilisent‑ils Afrosite **tous les jours** ? Sinon, diagnostiquer avant d'ajouter la moindre fonctionnalité.

<img src=".github/assets/divider.svg" alt="" width="100%">

## Golden path — lancer en local

L’app de démo (studio → boutique wax → caisse) :

```bash
cd apps/web
pnpm install
pnpm dev
# → http://localhost:3000/studio
# → http://localhost:3000/t/cadjehoun-wax   (24 500 FCFA)
# → http://localhost:3000/dashboard/cadjehoun-wax
```

Contrôles web : `pnpm --filter web eval:agents` · `pnpm --filter web eval:llm` ·
`pnpm --filter web check:contracts` · `pnpm --filter web check:pay` ·
`pnpm --filter @afrosite/llm check`.
Contrôles agents : `python check.py` · `python check_adapters.py` ·
`python check_openhands.py` dans [`services/agents`](services/agents/README.md).

Socle Docker (Postgres / Redis / MinIO, pas requis pour la démo) : [`infra/README.md`](infra/README.md).
Inventaire OSS : [`THIRDPARTY.md`](THIRDPARTY.md).
Si tu portes Souraka **et** Serge : [`docs/13-guide-solo-souraka-serge.md`](docs/13-guide-solo-souraka-serge.md).

Landing statique (optionnel) :

```bash
python -m http.server 5173 --directory landing
```

## Principes non négociables

- **Un prompt n'exécute jamais une action risquée** — workflow testable, réversible, observé.
- **80 % éprouvé / 20 % généré** — on personnalise des blueprints, on ne régénère pas de zéro.
- **Afrosite ne détient jamais de fonds** — orchestrateur au‑dessus d'un PSP agréé BCEAO.
- **La redirection navigateur ne prouve rien** — seul un webhook signé + `verify()` serveur confirme un paiement.
- **Réversibilité en un clic** — export intégral du code et des données, à tout moment.
- **3 blueprints maximum au MVP** — tout nouveau vertical se valide d'abord sur le socle.

<br>

<div align="center">
<img src=".github/assets/divider.svg" alt="" width="100%">
<br><br>
<sub><b>Conçu à Cotonou, Bénin</b>&nbsp;&nbsp;·&nbsp;&nbsp;FCFA&nbsp;&nbsp;·&nbsp;&nbsp;Mobile Money&nbsp;&nbsp;·&nbsp;&nbsp;Français&nbsp;&nbsp;·&nbsp;&nbsp;© 2026 Afrosite</sub>
</div>
