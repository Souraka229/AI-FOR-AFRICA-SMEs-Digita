# Ressources de A à Z — tout ce qu'il faut pour construire Afrosite

Liste maîtresse de toutes les ressources externes nécessaires pour construire, sécuriser, déployer, payer et faire grandir Afrosite — organisée dans l'ordre où elles deviennent nécessaires, du cadrage légal à la croissance. Chaque entrée renvoie à une documentation officielle, pas à un tutoriel tiers.

## A — Cadrage légal & création d'entreprise (Bénin)

| Ressource | Lien | Pourquoi |
|---|---|---|
| **Guichet unique de création d'entreprise** | [monentreprise.bj](https://monentreprise.bj) | Enregistrer Afrosite en moins de 24h avec un dossier complet — plateforme officielle du gouvernement béninois |
| **APIEX** — Agence de Promotion des Investissements et des Exportations | [apiex.bj](https://apiex.bj) | Accompagnement gratuit aux formalités de création d'entreprise |
| **OHADA** — droit des affaires harmonisé | [ohada.org](https://www.ohada.org) | Le droit commercial et des sociétés applicable au Bénin et à toute la zone UEMOA/CEMAC |
| **ADPME Bénin** | [epme.adpme.bj](https://epme.adpme.bj/) | Plateforme d'appui aux PME béninoises — utile aussi comme futur canal de distribution partenaire |

## B — Réglementation paiement (BCEAO)

À lire avant d'intégrer le moindre PSP — détermine ce qu'Afrosite a le droit de faire (voir [doc 01 §7](01-cahier-des-charges.md#7-contraintes) et [doc 03 §8](03-analyse-concurrentielle.md#8-analyse-pestel)).

| Ressource | Lien | Pourquoi |
|---|---|---|
| **BCEAO — Réglementation des systèmes de paiement** | [bceao.int/fr/reglementations/reglementation-des-systemes-de-paiement](https://www.bceao.int/fr/reglementations/reglementation-des-systemes-de-paiement) | Le règlement n° 15/2002/CM/UEMOA — cadre légal des systèmes de paiement dans l'UEMOA |
| **BCEAO — Établissements de monnaie électronique** | [bceao.int/fr/documents/etablissements-de-monnaie-electronique](https://www.bceao.int/fr/documents/etablissements-de-monnaie-electronique) | Conditions d'agrément — confirme qu'Afrosite doit rester orchestrateur, jamais émetteur de monnaie électronique |
| **BCEAO — Guide du promoteur, demande d'agrément** | [bceao.int/fr/publications/demande-dagrement-ou-dautorisation](https://www.bceao.int/fr/publications/demande-dagrement-ou-dautorisation-en-qualite-detablissement-emetteur-de-monnaie) | À connaître même sans jamais avoir à le déposer soi-même — comprendre ce que nos PSP partenaires ont déjà obtenu |

## C — Orchestration IA & agents

Détail complet et priorisation dans [doc 06 §2](06-architecture-technique.md#2-repos-et-briques-open-source-fondamentales).

| Ressource | Lien | Pourquoi |
|---|---|---|
| **LiteLLM** | [docs.litellm.ai](https://docs.litellm.ai/) | Routeur multi-modèles, fallback, suivi de coût — la brique n°1 |
| **LangGraph** | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/) | Orchestration d'agents stateful avec reprise après échec |
| **Temporal** | [docs.temporal.io](https://docs.temporal.io/) | Exécution fiable des workflows longs et sensibles (paiement, provisioning) |
| **OpenHands** | [github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) | Référence d'agent de code open source à étudier |

## D — Backend & données

| Ressource | Lien | Pourquoi |
|---|---|---|
| **PostgreSQL** | [postgresql.org/docs](https://www.postgresql.org/docs/) | Source de vérité — utilisateurs, ledger, audit trail |
| **Redis** | [redis.io/docs](https://redis.io/docs/latest/) | Cache, queues, rate limiting |
| **MinIO** | [min.io/docs](https://min.io/docs/minio/linux/index.html) | Stockage objet S3-compatible auto-hébergeable |
| **FastAPI** | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) | Framework backend recommandé pour le MVP |
| **NestJS** | [docs.nestjs.com](https://docs.nestjs.com/) | Alternative backend structurée (TypeScript) |

## E — Frontend & design system

| Ressource | Lien | Pourquoi |
|---|---|---|
| **Next.js** | [nextjs.org/docs](https://nextjs.org/docs) | Framework frontend — SSR natif, Metadata API, base du SEO natif (voir [doc 08](08-seo-et-clonage-de-sites.md)) |
| **shadcn/ui** | [ui.shadcn.com/docs](https://ui.shadcn.com/docs) | Composants copiés dans le code (pas une dépendance), base du design system Afrosite |
| **Tailwind CSS** | [tailwindcss.com/docs](https://tailwindcss.com/docs) | Système de styles utilitaire sous-jacent à shadcn/ui |
| **Playwright** | [playwright.dev](https://playwright.dev/) | Tests end-to-end ET captures d'écran pour la boucle de critique visuelle (voir [deep research §2](../deeprecherche_important/02-design-visuel-ia.md)) |

## F — Paiement Mobile Money (Bénin/UEMOA)

Ordre de priorité d'intégration détaillé dans [doc 03 §5](03-analyse-concurrentielle.md#5-concurrence-paiement--le-combat-le-plus-stratégique).

| Ressource | Lien | Pourquoi |
|---|---|---|
| **Genius Pay — API marchand** | [geniuspay.ci/docs/api](https://geniuspay.ci/docs/api) | **PSP primaire du MVP** ([ADR 0001](adr/0001-genius-pay-psp-primaire.md)). Checkout hébergé, `X-API-Key` / `X-API-Secret`, Bénin `MTN_MOMO_BEN` / `MOOV_BEN`, webhooks HMAC-SHA256 (`X-Webhook-Signature` + `X-Webhook-Environment`). Sandbox : `pk_sandbox_` / `sk_sandbox_` / `whsec_sandbox_`. Payé = `data.status` `completed`. |
| **Genius Pay — Sandbox virtuel** | [geniuspay.ci/docs/sandbox](https://geniuspay.ci/docs/sandbox) | Scénarios `success` / `failure` / `timeout` / `pending` sans téléphone. Base `https://pay.genius.ci/sandbox/`, clé `sbx_test_…`, `POST /payments/initiate`. |
| **Genius Pay — MCP (IA)** | SSE `https://geniuspay.ci/api/mcp` | Lire `geniuspay://docs/api` et `inspect_recent_errors`. Auth `Authorization: Bearer pk_sandbox_…`. Modèle : [geniuspay-mcp.example.json](geniuspay-mcp.example.json). Jamais de clé live dans l’IDE. |
| **Genius Pay — SDKs** | [geniuspay.ci/docs/sdk](https://geniuspay.ci/docs/sdk) | Référence d'intégration. Le métier Afrosite n'importe **jamais** le SDK directement — seulement `GeniusPayProvider`. |
| **KKiaPay — Documentation** | [docs.kkiapay.me](https://docs.kkiapay.me/) | Fallback Phase 2 — agrégateur béninois, couverture Bénin/Côte d'Ivoire/Togo/Sénégal/Niger/Burkina Faso |
| **FedaPay — Documentation API** | [docs.fedapay.com/api-reference/introduction-en](https://docs.fedapay.com/api-reference/introduction-en) | Fallback Phase 2 — API REST, sandbox + production, MTN MoMo/Moov Money/Celtiis Cash côté Bénin |
| **CinetPay — Documentation** | [docs.cinetpay.com](https://docs.cinetpay.com/) | Couverture 10+ pays francophones — pertinent dès la Phase 2/expansion UEMOA |

## G — Déploiement & infrastructure

| Ressource | Lien | Pourquoi |
|---|---|---|
| **Docker** | [docs.docker.com](https://docs.docker.com/) | Conteneurisation — base de la reproductibilité et de l'export |
| **Coolify** | [coolify.io/docs](https://coolify.io/docs) | PaaS self-hosted — déploiement Git, domaines, variables d'environnement |
| **GitHub Actions** | [docs.github.com/en/actions](https://docs.github.com/en/actions) | CI/CD — tests, scans, déploiement preview automatique |
| **OpenTofu** | [opentofu.org/docs](https://opentofu.org/docs/) | Infrastructure as Code, alternative ouverte à Terraform — pour la Phase 2/3 |

## H — Sécurité

Gates détaillées dans [doc 06 §6](06-architecture-technique.md#6-sécurité--règles-non-négociables).

| Ressource | Lien | Pourquoi |
|---|---|---|
| **OWASP ASVS** | [owasp.org/www-project-application-security-verification-standard](https://owasp.org/www-project-application-security-verification-standard/) | Référentiel de contrôles de sécurité vérifiables — checklist de base pour le MVP |
| **GitHub CodeQL** | [codeql.github.com/docs](https://codeql.github.com/docs/) | Scan automatique de vulnérabilités, intégrable à GitHub Actions |
| **Semgrep** | [semgrep.dev/docs](https://semgrep.dev/docs/) | Analyse statique de code, mauvaises pratiques |
| **TruffleHog** | [github.com/trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) | Détection de secrets exposés dans le code |
| **HashiCorp Vault** | [developer.hashicorp.com/vault](https://developer.hashicorp.com/vault/docs) | Coffre-fort de secrets — à introduire dès que le volume le justifie |

## I — Observabilité & fiabilité

| Ressource | Lien | Pourquoi |
|---|---|---|
| **OpenTelemetry** | [opentelemetry.io/docs](https://opentelemetry.io/docs/) | Standard ouvert traces/logs/métriques |
| **Prometheus** | [prometheus.io/docs](https://prometheus.io/docs/) | Collecte de métriques |
| **Grafana** | [grafana.com/docs](https://grafana.com/docs/) | Dashboards de monitoring et alertes |
| **Sentry** | [docs.sentry.io](https://docs.sentry.io/) | Suivi d'erreurs applicatives en production |

## J — Email & communication client

Détail de l'architecture complet dans la conversation précédente sur les emails multi-tenant — repris ici comme index de ressources.

| Ressource | Lien | Pourquoi |
|---|---|---|
| **WhatsApp Business Platform (Cloud API)** | [developers.facebook.com/docs/whatsapp/cloud-api](https://developers.facebook.com/docs/whatsapp/cloud-api/) | Canal n°1 pour Afrosite — notifications, support, onboarding conversationnel |
| **Mailgun** | [documentation.mailgun.com](https://documentation.mailgun.com/) | Envoi + réception d'emails, Routes pour le routing par tenant |
| **AWS SES** | [docs.aws.amazon.com/ses](https://docs.aws.amazon.com/ses/latest/dg/Welcome.html) | Alternative la moins chère à grande échelle pour l'envoi/réception |
| **Resend** | [resend.com/docs](https://resend.com/docs) | API d'envoi simple pour un MVP rapide |

## K — Intégrations développeurs (Git)

Détail complet dans [doc 06 §8](06-architecture-technique.md#8-connexion-githubgitlab-et-push-de-code) — pertinent en Phase 3.

| Ressource | Lien | Pourquoi |
|---|---|---|
| **GitHub Apps — documentation** | [docs.github.com/en/apps](https://docs.github.com/en/apps) | Permissions granulaires, tokens courts — à utiliser plutôt qu'un OAuth App |
| **Octokit** | [github.com/octokit](https://github.com/octokit) | SDK officiel GitHub pour interagir avec l'API depuis le backend |
| **GitLab OAuth 2.0** | [docs.gitlab.com/api/oauth2](https://docs.gitlab.com/api/oauth2/) | Authentification et Project Access Tokens pour l'intégration GitLab |

## L — SEO & visibilité locale

Détail complet dans [doc 08](08-seo-et-clonage-de-sites.md).

| Ressource | Lien | Pourquoi |
|---|---|---|
| **Google Search Console** | [search.google.com/search-console](https://search.google.com/search-console/about) | Validation de l'indexation et des données structurées de chaque site tenant |
| **Google Business Profile** | [google.com/business](https://www.google.com/business/) | Le levier de visibilité local n°1 pour un commerçant — à automatiser pour chaque client Afrosite |
| **Schema.org** | [schema.org](https://schema.org/) | Référence des types de données structurées (`LocalBusiness`, `Restaurant`, `Product`) |
| **Rich Results Test** | [search.google.com/test/rich-results](https://search.google.com/test/rich-results) | Valider le JSON-LD injecté par chaque blueprint |

## M — Design — fabrication et inspiration

Détail complet dans la [charte graphique Afrosite](https://claude.ai/code/artifact/c98eb71b-f31c-408b-bd7f-4526bbc3e019) et [doc 09](09-branding-logo-positionnement.md).

| Ressource | Lien | Pourquoi |
|---|---|---|
| **Google Fonts** | [fonts.google.com](https://fonts.google.com/) | Hébergement de Space Grotesk et IBM Plex Sans, les deux polices de marque |
| **Mobbin** | [mobbin.com](https://mobbin.com/) | Bibliothèque de flux réels d'applications — pour étudier des parcours (paiement, onboarding), pas pour cloner |
| **Land-book** | [land-book.com](https://land-book.com/) | Référence de landing pages — utile pour la direction artistique des mini-sites vitrines |
| **Figma** | [figma.com](https://www.figma.com/) | Outil de maquettage — import direct des tokens dans v0/Next.js le cas échéant |

## N — Marketing & croissance terrain

Playbook complet dans [doc 05](05-roadmap-leadership-afrique.md).

| Ressource | Lien | Pourquoi |
|---|---|---|
| **WhatsApp Business App** | [business.whatsapp.com](https://business.whatsapp.com/) | Canal de qualification et de conversion n°1 (distinct de la Cloud API — usage manuel/PME) |
| **Meta Business Suite** | [business.facebook.com](https://business.facebook.com/) | Gestion des publicités Facebook/Instagram pour l'acquisition locale |
| **Google Business Profile** *(rappel)* | [google.com/business](https://www.google.com/business/) | Double usage : SEO local ET canal d'acquisition |

## O — Financement & incubation (Bénin/UEMOA)

| Ressource | Lien | Pourquoi |
|---|---|---|
| **BLO Lab** — incubateur tech Bénin | [blolab.bj/incubateur](https://blolab.bj/incubateur) | Accompagnement et réseau pour startups tech béninoises |
| **FAEN** — Fonds d'appui à l'entrepreneuriat numérique | via [ADPME](https://epme.adpme.bj/) | Financement dédié au numérique, intégré à l'écosystème national |
| **Digital Africa** | [digital-africa.co](https://digital-africa.co/) | Programmes de financement et de mise en réseau panafricains pour startups tech |

## P — Communautés & apprentissage continu

| Ressource | Lien | Pourquoi |
|---|---|---|
| **Y Combinator Startup School** | [startupschool.org](https://www.startupschool.org/) | Cours gratuit structuré sur la construction et la croissance d'une startup |
| **Indie Hackers** | [indiehackers.com](https://www.indiehackers.com/) | Communauté et retours d'expérience concrets sur les métriques SaaS/unit economics |
| **Deep research du projet** | [deeprecherche_important/](../deeprecherche_important/00-README.md) | Recherche déjà menée sur ce qui rend un système IA performant, rapide et visuellement excellent — à tenir à jour |

## Comment utiliser cette liste

Ne pas tout ouvrir aujourd'hui. L'ordre A → P correspond globalement à l'ordre où chaque ressource devient nécessaire dans le [plan d'exécution 90 jours](07-plan-execution-90-jours.md) : légal et paiement d'abord (A, B, F), stack technique ensuite (C à K), visibilité et croissance seulement une fois le socle stable (L à P). Revenir à ce document à chaque nouvelle phase plutôt que de tout consommer d'un coup.
