# AFROSITE — Documentation projet

> Plateforme AI-native de digitalisation, d'exploitation et de paiement pour les TPE/PME d'Afrique de l'Ouest (UEMOA), en commençant par le Bénin.

## Pitch en une phrase

**« Décrivez votre activité. En quelques minutes, obtenez une application prête à vendre, encaisser en Mobile Money, gérer vos clients et suivre votre business — le tout piloté par l'IA et exploitable sans compétence technique. »**

Contrairement à un lancement mono-vertical, **Afrosite démarre avec plusieurs blueprints métier en parallèle** (commerce, restauration, services) plutôt qu'un seul pilote isolé — voir la justification dans [doc 01 §5.1](01-cahier-des-charges.md#51-mvp--phase-1-0-3-mois). L'objectif reste de construire ensuite un **AI Company Builder** panafricain plus large.

## Comment lire cette documentation

Les documents sont numérotés dans l'ordre où ils doivent être lus/validés — chaque document s'appuie sur les décisions prises dans le précédent.

| # | Document | Contenu | Pour qui |
|---|---|---|---|
| 01 | [Cahier des charges](01-cahier-des-charges.md) | Vision, périmètre fonctionnel, exigences, critères d'acceptation | Équipe produit, développeurs, investisseurs |
| 02 | [Business model](02-business-model.md) | Business Model Canvas, pricing, unit economics, projections | Toi, investisseurs, associés |
| 03 | [Analyse concurrentielle](03-analyse-concurrentielle.md) | Carte des concurrents directs/indirects, SWOT, PESTEL | Toi, stratégie produit et levée de fonds |
| 04 | [Différenciation & positionnement](04-differenciation-positionnement.md) | Le moat défendable, le message, la matrice de différenciation | Marketing, vente, pitch investisseurs |
| 05 | [Roadmap vers le leadership Afrique de l'Ouest](05-roadmap-leadership-afrique.md) | Go-to-market, 5 premiers clients, canaux, expansion UEMOA | Toi, croissance, commercial |
| 06 | [Architecture technique](06-architecture-technique.md) | Stack, repos open source, pipeline prompt→production, sécurité | Développeurs, CTO |
| 07 | [Plan d'exécution 90 jours](07-plan-execution-90-jours.md) | Ce qu'il faut faire, dans quel ordre, dès demain | Toi, opérationnel |
| 08 | [SEO natif et clonage de sites](08-seo-et-clonage-de-sites.md) | SEO technique par défaut, SEO local (Google Business Profile), fonctionnalité de clonage/migration de site et ses garde-fous légaux | Développeurs, marketing, toi |
| 09 | [Branding, logo & positionnement](09-branding-logo-positionnement.md) | Règles d'usage du logo, système de marque (couleurs/typo/icônes), positionnement et voix — version texte de la charte visuelle | Toi, marketing, tout prestataire externe |
| 10 | [Ressources de A à Z](10-ressources-de-a-a-z.md) | Toutes les ressources externes nécessaires — légal, paiement, stack technique, SEO, design, marketing, financement — dans l'ordre où elles deviennent utiles | Toi, développeurs, toute nouvelle recrue |
| 11 | [Playbook d'équipe](11-playbook-equipe.md) | Rôles (Souraka / CHITOU / SERGE), RACI, méthode Kanban + Notion, structure des dossiers, liste maître des branches Git, système de prompts réutilisables, plan 90 jours par personne, intégration Genius Pay | Toute l'équipe, au quotidien |
| 12 | [Pitch — Hackathon Cursor × Devs Days](12-pitch-hackathon.md) | Accroche, fiche de candidature, script vidéo, pitch de finale slide par slide, déroulé de démo, Q&A jury, périmètre de build, répartition équipe | Toute l'équipe, pour l'événement du 9–10 sept. 2026 |

## Statut du projet

- **Phase actuelle** : Pré-lancement — validation multi-vertical (commerce, restauration, services), Bénin
- **Marché de départ** : Cotonou, zone dense (Cadjehoun / Fidjrossè), TPE/PME 20–100 transactions/jour
- **Devise et paiement** : FCFA, Mobile Money (MTN MoMo, Moov Money) via agrégateurs (KKiaPay, FedaPay, CinetPay)
- **Prochaine étape critique** : recruter les 5 premiers clients pilotes, un par profil prioritaire (voir [doc 05](05-roadmap-leadership-afrique.md#les-cinq-premiers-clients))

## Principe directeur (à ne jamais perdre de vue)

> Construire ce qui est spécifique à l'Afrique et difficile à reproduire — distribution, paiements locaux, templates métier, données opérationnelles, support, confiance.
> Réutiliser ce qui est commodité mondiale — Linux, PostgreSQL, Docker, S3, Git, OAuth, modèles IA.

Ne pas commencer par « posséder l'infrastructure ». Commencer par posséder la relation client, le workflow métier et la couche de paiement.
