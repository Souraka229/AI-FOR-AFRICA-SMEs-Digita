# SEO natif et clonage de sites — Afrosite

Deux fonctionnalités à fort potentiel de différenciation, à condition de bien poser les garde-fous techniques et légaux avant de les construire.

## 1. Pourquoi le SEO doit être un argument de vente, pas une option

La quasi-totalité des sites générés par les concurrents (Lovable, Bolt, Bubble) sortent avec un SEO médiocre par défaut : rendu côté client sans SSR, pas de sitemap, pas de données structurées. Pour un commerçant africain, c'est justement ce qui décide s'il apparaît ou non quand un client cherche « restaurant Cadjehoun » ou « boutique wax Cotonou » sur Google. **Un SEO excellent par défaut, sans configuration côté client, est un avantage concret et vendable** — pas un détail technique.

## 2. Exigences techniques à intégrer nativement dans chaque blueprint

Avec Next.js (déjà dans la stack, voir [doc 06](06-architecture-technique.md#3-stack-mvp-concrète)), tout ceci est natif à condition de l'imposer dans le blueprint dès la génération — pas en option activable plus tard :

| Exigence | Implémentation |
|---|---|
| **Rendu SSR/SSG** | Pages publiques (menu, catalogue, mini-site) rendues côté serveur — jamais de contenu clé uniquement en client-side rendering |
| **Metadata API** | Titre, description, Open Graph et Twitter Card générés automatiquement à partir du profil business, co-localisés avec chaque route |
| **Sitemap dynamique** | Généré via route handler qui interroge la base (pas un fichier XML statique), avec `lastmod` exact ; scinder par type de contenu si le site grossit |
| **robots.txt** | Généré automatiquement, adapté par environnement (bloquer l'indexation des previews/sandbox) |
| **Données structurées (JSON-LD)** | Schema.org `LocalBusiness`, `Restaurant`, `Product`, `Menu`, `Review` selon le blueprint — injecté côté serveur pour être présent dans le HTML initial, pas ajouté après exécution JS |
| **Canonical tags** | Auto-référencés sur chaque route pour éviter le contenu dupliqué (paramètres d'URL, slash final, variantes) |
| **Core Web Vitals** | Cibles : LCP ≤ 2,5 s, INP < 200 ms, CLS < 0,1 — critiques sur les réseaux mobiles africains (voir [doc 06 §11](06-architecture-technique.md#11-design-system-et-direction-artistique)) |
| **Validation continue** | Rich Results Test + Search Console branchés dès le déploiement production, alerte si un schema casse après un déploiement |

Ces éléments doivent faire partie des **gates de qualité** du pipeline ([doc 06 §5](06-architecture-technique.md#gates-à-bloquer-automatiquement)) : un site sans metadata correcte ni sitemap ne devrait pas passer en production.

## 3. SEO local — la vraie bataille pour les TPE africaines

Le SEO qui compte le plus pour un commerçant local n'est pas le classement organique classique, c'est le **local pack** (les 3 résultats avec carte affichés en haut de Google).

- **Google Business Profile** est la source de leads locale la plus puissante quand elle est bien tenue : informations complètes, catégorie exacte, photos, cohérence stricte du nom/adresse/téléphone (NAP) sur tous les canaux, avis clients actifs — un profil avec 20 avis authentiques surclasse presque toujours un profil avec 2 avis.
- **WhatsApp comme canal de contact direct** est désormais intégrable au profil Google : le client peut écrire sur WhatsApp sans quitter l'app qu'il utilise déjà — cohérent avec le positionnement WhatsApp-first d'Afrosite (voir [doc 04 §4](04-differenciation-positionnement.md#4-les-cinq-couches-du-positionnement-défendable)).
- **L'activité continue compte** : un profil qui publie régulièrement (nouveaux produits, promos, photos) garde mieux sa visibilité qu'un profil qui reste silencieux.

**Ce qu'Afrosite doit automatiser pour chaque client** :
1. Génération assistée de la fiche Google Business Profile à partir du profil business déjà saisi (pas de re-saisie).
2. Rappel automatique (WhatsApp) pour demander un avis après une commande/prestation réussie.
3. Publication automatique d'un post Google à chaque nouveau produit/plat/service ajouté au catalogue.
4. Vérification de cohérence NAP entre le mini-site Afrosite, WhatsApp Business et Google Business Profile.

## 4. Architecture SEO en environnement multi-tenant

Chaque client Afrosite a son propre mini-site (sous-domaine ou domaine personnalisé). Mal géré, un environnement multi-tenant crée des conflits de contenu dupliqué qui diluent le classement de tous les sites clients à la fois.

**Règles à appliquer dès l'architecture** :
- Isolation stricte : les déclarations canoniques d'un site tenant ne pointent **jamais** vers le domaine marketing d'Afrosite, et inversement — un canonical croisé entre sous-domaines est géré de façon incohérente par Google.
- `noindex` systématique sur tout contenu tenant qui dupliquerait le site marketing (pages de démonstration, templates non personnalisés).
- Un sitemap **par tenant**, jamais un sitemap global mélangeant tous les clients.
- Domaine personnalisé en option payante (Phase 2/3) : un client qui passe de `boutique.afrosite.app` à `www.laboutique.com` doit pouvoir migrer son historique SEO sans tout perdre (redirections 301 propres, pas de contenu dupliqué entre les deux).

## 5. Fonctionnalité « cloner un site web »

### 5.1 Comment ça marche techniquement

L'approche standard des outils IA (Open Lovable, skills « website-clone » via Firecrawl) suit ce pipeline :

```text
URL fournie par l'utilisateur
        ↓
Scraper (Firecrawl ou équivalent) : rendu JS, extraction HTML propre,
markdown, screenshot, métadonnées
        ↓
Analyse par un modèle (structure, sections, palette, typographie)
        ↓
Reconstruction en composants du design system Afrosite
        (pas une copie pixel-perfect du code source)
        ↓
Remplacement du contenu (textes, images, logo, coordonnées)
par les données réelles du client
        ↓
Preview générée dans un blueprint Afrosite
```

Deux approches techniques possibles :
- **Scraping + reconstruction structurée** (Firecrawl) : plus fiable, extrait le contenu et la structure sémantique.
- **Screenshot-to-code** (vision) : approximatif — les détails (polices, espacements, composants) dérivent souvent de l'original.

Pour Afrosite, la première approche est préférable car elle s'intègre nativement au pipeline blueprint déjà en place (Product Architect Agent → Code Agent, voir [doc 06 §4](06-architecture-technique.md#4-les-agents-du-pipeline)) plutôt que de générer du code libre non structuré.

### 5.2 Garde-fous légaux — à traiter avant tout développement

Cloner un site n'est pas illégal en soi, mais la frontière entre « inspiration » et « contrefaçon » est fine :

| Autorisé sans risque | Interdit / à risque |
|---|---|
| Reproduire une structure, une mise en page générale, un pattern de design | Copier textes, photos, logos, identité de marque d'un site qu'on ne possède pas |
| Cloner **son propre ancien site** pour migrer vers Afrosite | Cloner le site d'un concurrent pour le republier ou l'usurper |
| S'inspirer d'un site de référence puis remplacer entièrement contenu et assets | Reproduire un site protégeant explicitement le scraping dans ses CGU |

Conséquences en cas d'infraction : notifications de retrait, mises en demeure, réclamations DMCA ou de marque — potentiellement bien plus coûteuses que d'écrire un contenu original. Beaucoup de sites interdisent explicitement le scraping/la reproduction dans leurs conditions d'utilisation.

### 5.3 Recommandation produit — comment positionner la fonctionnalité sans risque

Ne pas vendre « clonez n'importe quel site » tel quel. Positionner plutôt deux usages légitimes et vendables :

1. **« Migrez votre site existant vers Afrosite »** — le client fournit l'URL de **son propre site** (ou confirme en être propriétaire) ; Afrosite en extrait la structure et le contenu et reconstruit l'équivalent dans un blueprint Afrosite, avec paiement Mobile Money et opérations ajoutés. Cas d'usage clair, zéro risque légal, forte valeur (« gardez votre site, gagnez le reste »).
2. **« Inspirez-vous d'une référence »** — le client montre un site qu'il aime (pas forcément le sien) ; Afrosite en extrait uniquement la structure/le style (mise en page, palette, ton) et **remplace systématiquement tout le contenu** (textes, images, marque) par les données réelles du client. Jamais de republication du contenu original.

Garde-fous techniques à implémenter :
- Case à cocher obligatoire : « Je confirme être propriétaire de ce site ou disposer de son consentement » avant tout clonage de type 1.
- Filtrage automatique : blocage si l'URL correspond à un domaine à forte notoriété (grandes marques, concurrents directs identifiés) pour le mode « inspiration ».
- Remplacement systématique et automatique des assets protégés (logos, photos, textes de marque) — jamais conservés tels quels dans le mode inspiration.
- Traçabilité : log de l'URL source, de la confirmation de propriété, et de la date, dans l'audit trail (cohérent avec [doc 06 §10](06-architecture-technique.md#10-système-de-confiance--ce-que-lutilisateur-doit-toujours-voir)).

## 6. Priorisation

| Fonctionnalité | Phase recommandée | Pourquoi |
|---|---|---|
| SEO natif (SSR, metadata, sitemap, JSON-LD, Core Web Vitals) | **MVP — non négociable** | Fait partie de la promesse de base, coût d'implémentation faible avec Next.js, différenciateur immédiat |
| Automatisation Google Business Profile + rappel avis | **MVP ou Phase 2 rapprochée** | Impact direct sur l'acquisition client du commerçant, forte valeur perçue |
| Migration de site existant (« clonez votre site ») | **Phase 2** | Fonctionnalité d'acquisition puissante pour convertir des commerçants qui ont déjà un site basique mais aucune opération dessus |
| Mode « inspiration » (clonage de référence tierce) | **Phase 3, avec garde-fous validés** | Valeur réelle mais risque légal à cadrer précisément avant tout développement — ne pas se précipiter |

**Sources :**
- [Pagepro — Next.js SEO Guide 2026](https://pagepro.co/blog/nextjs-seo/)
- [DevKit Market — Next.js SEO Checklist 2026](https://www.devkitmarket.com/blog/nextjs-seo-checklist-2026)
- [StackNotice — Next.js 15 SEO metadata/sitemap/structured data](https://stacknotice.com/blog/nextjs-seo-guide-2026)
- [Firecrawl — Open Lovable Tutorial (clone a website)](https://www.firecrawl.dev/blog/open-lovable-tutorial)
- [Firecrawl — website design clone skill](https://mcpservers.org/agent-skills/firecrawl/firecrawl-website-design-clone)
- [Webxloo — Cloned Website Guide: Risks, Legal Issues & Uses](https://webxloo.com/blog/cloned-website-understanding-the-benefits-pitfalls-and-critical-legal-issues-2025-guide.html)
- [PropSaaS Growth — Fix SaaS Canonical Conflicts](https://propsaasgrowth.com/blog/saas-canonical-conflicts/)
- [RankLayer — Subdomain SEO](https://www.ranklayer.app/blog/en/subdomain-seo)
- [klientsolutech — Google Business Profile Local SEO Guide 2026](https://klientsolutech.com/google-business-profile-seo-guide/)
- [BigRedSEO — Google Business Profile In 2026](https://www.bigredseo.com/google-business-profile-local-seo/)
