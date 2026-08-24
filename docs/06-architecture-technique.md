# Architecture technique — Afrosite

Principe directeur : un prompt ne doit **jamais** exécuter directement une action risquée. Il déclenche un workflow contrôlé, testable, réversible et observable. L'IA propose, les règles contrôlent, les tests vérifient, l'utilisateur valide les actions importantes.

## 1. Architecture cible (vue d'ensemble)

```text
PROMPT UTILISATEUR
       ↓
AI Gateway / Router
       ↓
Planner / Blueprint Agent
       ↓
Workflow durable + validations
       ↓
Agents spécialisés
 ├── Génération UI
 ├── Génération backend
 ├── Base de données
 ├── Tests / sécurité
 ├── Paiement
 └── Déploiement
       ↓
Sandbox d'exécution isolée
       ↓
CI/CD + infrastructure
       ↓
Monitoring + alertes + audit trail
       ↓
APPLICATION LIVRÉE
```

## 2. Repos et briques open source fondamentales

| Besoin | Repo / technologie | Pourquoi |
|---|---|---|
| Orchestration d'agents | `langchain-ai/langgraph` | Agents stateful, durables, reprise après échec, intervention humaine intégrée |
| Workflows critiques | `temporalio/temporal` | Fiabilité : paiements, provisioning, retry, récupération après crash, webhooks |
| Routage multi-modèles | `BerriAI/litellm` | API unique multi-fournisseurs, fallback, load balancing, suivi de dépense |
| Agent de code open source | `OpenHands/OpenHands` | Référence pour un agent qui écrit/exécute/corrige du code en environnement outillé |
| SDK agents de code | `OpenHands/software-agent-sdk` | Brique modulaire pour construire ses propres agents de développement |
| Observabilité | `open-telemetry/opentelemetry-collector` + `-operator` | Traces/logs/métriques standardisés, indépendants du fournisseur |
| Base de données | `postgres/postgres` | Source de vérité : utilisateurs, projets, permissions, ledger, audit trail |
| Cache et files | `redis/redis` | Sessions, cache, rate limiting, queues, verrous distribués |
| Stockage objet | `minio/minio` | S3-compatible, auto-hébergeable ou remplaçable |
| Déploiement d'apps | `coollabsio/coolify` ou `caprover/caprover` | PaaS self-hosted : déploiement Git, domaines, variables d'environnement |
| Conteneurs | `moby/moby` + Docker Compose | Reproductibilité et export des projets générés |
| Orchestration infra | `kubernetes/kubernetes` | À introduire seulement quand le volume le justifie |
| Infrastructure as Code | `opentofu/opentofu` | Provisionnement reproductible, alternative ouverte à Terraform |
| GitOps | `argoproj/argo-cd` | Déploiement contrôlé, versionné, réversible |
| Secrets | `hashicorp/vault` ou `external-secrets/external-secrets` | Jamais de clé IA/paiement en base ou dans les prompts |
| SSO / identités | `keycloak/keycloak` | OAuth/OIDC, rôles, MFA |
| Sécurité applicative | `zaproxy/zaproxy`, `semgrep/semgrep`, `trufflesecurity/trufflehog` | Détection de vulnérabilités, mauvaises pratiques, secrets exposés |
| Tests end-to-end | `microsoft/playwright` | Vérifie qu'un SaaS généré fonctionne réellement |
| Monitoring | `prometheus/prometheus` + `grafana/grafana` | Performance, latence, erreurs, disponibilité |
| Gestion d'incidents | `grafana/oncall` ou PagerDuty | Alerte sur défaillance paiement/base/déploiement |
| Contrôle de politiques | `open-policy-agent/opa` | Règles automatiques : pas de suppression/exposition/déploiement paiement sans validation |

### Les 10 repos à prioriser au démarrage

1. `BerriAI/litellm` — routeur multi-IA
2. `langchain-ai/langgraph` — orchestration des agents
3. `temporalio/temporal` — exécution fiable des tâches sensibles
4. `OpenHands/software-agent-sdk` — agents qui manipulent le code
5. `postgres/postgres` — données, permissions, audit, ledger
6. `redis/redis` — cache, queues, rate limiting
7. `minio/minio` — fichiers, backups, objets S3
8. `microsoft/playwright` — tests visibles d'une application générée
9. `open-telemetry/opentelemetry-collector` — traces, logs, métriques
10. `prometheus/prometheus` + `grafana/grafana` — surveillance et alertes

Ne pas introduire Kubernetes, Argo CD, Vault et un cluster GPU avant que l'usage le justifie. Pour les premiers centaines de clients : Docker bien géré + PostgreSQL managé + sauvegardes testées + observabilité sérieuse apportent plus de fiabilité qu'un Kubernetes mal administré.

## 3. Stack MVP concrète

```text
Frontend       : Next.js + TypeScript
Backend        : FastAPI ou NestJS
Base           : PostgreSQL
Cache/queue    : Redis
Fichiers       : MinIO / fournisseur S3
IA             : LiteLLM + modèles externes + modèles open source plus tard
Agents         : LangGraph
Tâches durables: Temporal
Code agent     : OpenHands SDK, sous sandbox
Déploiement MVP: Docker Compose + Coolify
CI/CD          : GitHub Actions
Tests          : Playwright + pytest / Vitest
Observabilité  : OpenTelemetry + Grafana + Prometheus
Erreurs        : Sentry
Paiements      : KKiaPay / FedaPay / CinetPay selon pays
Auth           : Clerk au MVP, puis Keycloak si auto-hébergement souhaité
```

## 4. Les agents du pipeline

| Agent | Mission | Sortie | Peut agir seul ? |
|---|---|---|---|
| Intent Agent | Comprend et normalise le prompt | JSON de besoin produit | Oui |
| Product Architect | Transforme le besoin en modules et flux | Blueprint versionné | Oui, mais pas de déploiement |
| Code Agent | Génère ou modifie le code | Pull Request Git | Oui, uniquement dans une branche |
| Database Agent | Propose migrations et index | Migration versionnée | Oui en preview ; validation requise en production |
| Security Agent | Vérifie accès, secrets, injections, dépendances, rôles | Rapport bloquant ou validé | Oui |
| QA Agent | Crée et lance tests unitaires et E2E | Rapport de tests | Oui |
| Deployment Agent | Crée preview, prépare release, déploie | Preview ou release | Preview : oui ; production : approbation obligatoire |
| Payment Agent | Configure le checkout et les webhooks | Connexion PSP testée | Sandbox : oui ; clés live : approbation obligatoire |
| Observability Agent | Ajoute logs, métriques, alertes | Dashboard + alertes | Oui |
| Cost Agent | Calcule le coût IA/cloud/usage | Budget, quotas, alertes | Oui |

## 5. Pipeline prompt → production

```text
Prompt
  → Blueprint structuré JSON
  → Validation de schéma
  → Génération dans une branche Git
  → Scan de secrets et sécurité
  → Tests unitaires
  → Tests Playwright
  → Déploiement preview
  → Validation utilisateur
  → Déploiement production
  → Monitoring et rollback
```

### Contrat structuré (exemple)

```json
{
  "project_type": "restaurant_ordering_platform",
  "country": "BJ",
  "currency": "XOF",
  "roles": ["owner", "cashier", "kitchen", "customer"],
  "modules": ["qr_menu", "cart", "orders", "kitchen_display", "payments", "daily_reporting"],
  "integrations": [
    { "category": "payment", "mode": "sandbox", "provider_candidates": ["kkiapay", "fedapay"] }
  ],
  "security_level": "standard",
  "deployment_target": "preview",
  "estimated_cost_credits": 8,
  "requires_confirmation": ["production_deploy", "payment_live_activation", "database_deletion"]
}
```

Un validateur (Zod/Pydantic) rejette tout JSON non conforme avant que le moindre workflow ne démarre.

### Gates à bloquer automatiquement

```text
GATE 1 — Blueprint : JSON conforme, budget IA sous plafond, pas de données sensibles dans le prompt
GATE 2 — Qualité code : lint/typecheck, tests unitaires, build, aucun secret dans Git
GATE 3 — Sécurité : SAST, scan dépendances, scan secrets, RBAC vérifié, rate limiting, CSRF/XSS/injection contrôlés
GATE 4 — Paiement : sandbox, webhooks signés vérifiés, idempotency key, montants recalculés serveur, aucune donnée carte stockée
GATE 5 — Préproduction : migration testée sur copie, tests Playwright, backup vérifié, rollback prêt
GATE 6 — Production : confirmation explicite admin, déploiement progressif, monitoring actif, rollback automatique
```

## 6. Sécurité — règles non négociables

```text
Prompt ≠ permission illimitée.
IA ≠ accès root.
Génération ≠ déploiement production.
Succès du code ≠ sécurité validée.
Paiement initié ≠ paiement confirmé.
```

Sécurité spécifique aux agents IA :
- Aucun secret dans le contexte LLM.
- Permissions minimales : chaque agent reçoit un jeton temporaire et limité.
- Liste blanche d'outils autorisés par agent.
- Toute donnée externe (web, PDF, email, utilisateur) traitée comme **non fiable** (risque d'injection de prompt).
- Sandbox Docker/Firecracker pour exécuter le code généré.
- Confirmation humaine pour : déploiement prod, paiements live, emails massifs, suppression, changement d'accès.
- Audit trail complet : prompt, plan, outils exécutés, version de code, test, auteur, résultat, horodatage.

### Architecture paiement

```text
Client
   ↓
Checkout Afrosite
   ↓
API Afrosite crée une transaction serveur
   ↓
PSP : KKiaPay / FedaPay / CinetPay
   ↓
Page / SDK sécurisé du PSP
   ↓
Webhook signé vers le backend Afrosite
   ↓
Vérification du statut côté serveur
   ↓
Ledger interne immuable
   ↓
Transaction marquée "payée"
```

**Règle vitale** : la redirection du navigateur n'est jamais la preuve finale de paiement — seul le webhook signé et/ou la vérification serveur du PSP confirme le paiement. Afrosite ne stocke jamais de données de carte (PAN/CVV) : ces données restent dans l'infrastructure PCI DSS du PSP via ses pages/champs hébergés.

## 7. Emails automatiques par tenant

Objectif : donner à chaque client l'impression d'une adresse dédiée (`admin@boutiquedupain.afrosite.app`) sans gérer un vrai serveur mail par tenant.

| Modèle | Fonctionnement | Complexité |
|---|---|---|
| **A. Adressage virtuel (recommandé)** | `admin+boutiquedupain@afrosite.app` en interne, affiché comme `admin@boutiquedupain.afrosite.app` en façade | Faible |
| **B. Sous-domaine réel** | Vraie adresse par sous-domaine, nécessite MX/DKIM par tenant ou wildcard + Email Worker | Élevée — réservé aux tenants premium/domaines personnalisés |

**Réception (inbound)** : Mailgun Routes (parsing JSON), Postmark Inbound (fiabilité transactionnelle), ou AWS SES + S3 + Lambda (le moins cher à grande échelle).

**Envoi (outbound)** : domaine dédié type `mg.afrosite.app` avec SPF/DKIM/DMARC automatisés (Mailgun génère 2 CNAME DKIM, rotation automatique tous les 120 jours) ; alternative simple : Resend.

```text
1. Un client écrit à admin+boutiquedupain@afrosite.app
2. Le fournisseur reçoit → webhook vers le backend
3. Le backend résout le tenant "boutiquedupain" depuis le suffixe
4. Le message est stocké dans le CRM du tenant (PostgreSQL)
5. Le gérant est notifié via WhatsApp/app
6. Il répond depuis le dashboard → envoi via l'ESP avec
   From affiché : admin@boutiquedupain.afrosite.app
```

## 8. Connexion GitHub/GitLab et push de code

Réservé à la Phase 3 (SaaS Builder ouvert), mais l'architecture doit être anticipée.

- **GitHub : privilégier une GitHub App, jamais un OAuth App** — permissions granulaires par dépôt, tokens d'installation courts (1h) et renouvelés automatiquement, identité propre qui survit au départ de l'installateur, webhooks centralisés.
- **GitLab** : OAuth 2.0 + Project Access Tokens scopés à un seul projet, expiration configurable.
- **Push du code généré** : toujours dans une sandbox Docker, via `simple-git` (wrapper autour du vrai binaire git) plutôt qu'`isomorphic-git` côté serveur (plus simple, plus performant, pas de contrainte same-origin).
- **Jamais de push direct sur `main`** : toujours branche dédiée (`feature/generated-<id>`) + Pull Request automatique + CI (lint, tests, scan sécurité) avant merge, humain ou automatisé selon les gates.
- **Sécurité des tokens** : jamais de Personal Access Token en clair, chiffrement au repos (Vault/KMS), rotation automatique, révocation immédiate à la déconnexion, log de chaque push (qui, quoi, branche, commit SHA).

```text
Agent de code génère les fichiers en sandbox
        ↓
git init / add / commit (simple-git)
        ↓
git remote add origin https://x-access-token:<installation_token>@github.com/user/repo.git
        ↓
git push origin feature/generated-<id>
        ↓
Ouverture automatique d'une Pull Request
        ↓
CI : lint, tests, scan sécurité
        ↓
Validation utilisateur → merge
```

## 9. Système de réponse rapide (routage IA)

```text
Demande utilisateur
       ↓
Classification rapide et règles
       ↓
Modèle léger / peu coûteux
       ├── Question simple → réponse directe
       ├── Création d'un écran → générateur UI
       ├── Création de projet → planner puissant
       ├── Paiement → workflow réglementé
       └── Action à risque → demande de confirmation
```

- **Modèle léger** : classification d'intention, résumé, extraction, traduction, assistance basique.
- **Modèle puissant** : architecture produit, plan complexe, débogage difficile, revue de code.
- **Modèle spécialisé code** : composants, migrations, tests, APIs, corrections.
- **Modèle local/open source** : tâches répétitives et données sensibles, quand le volume le justifie.
- **Fallback** : LiteLLM route vers un second fournisseur ou un modèle local en cas d'échec.

## 10. Système de confiance — ce que l'utilisateur doit toujours voir

- Le plan avant l'exécution.
- Le coût estimé (crédits IA, hébergement, SMS, stockage, paiement).
- L'état en direct (analyse, génération, test, déploiement, succès/échec).
- Un historique complet (qui a demandé quoi, quel agent a agi, quel fichier a changé, quel paiement a été reçu).
- Un bouton rollback.
- Une exportation complète (code, données, fichiers, documentation).
- Des sauvegardes avec fréquence claire, restauration testée, statut visible.
- Une confirmation explicite pour toute action irréversible.

## 11. Design system et direction artistique

Ne pas générer d'interface générique. Donner à l'IA une direction artistique, des contraintes métier, une bibliothèque de composants propriétaire et un processus de critique.

```text
/design-system
  /foundations   (colors, typography, spacing, shadows, motion)
  /tokens        (tokens.json, semantic-tokens.json)
  /components    (Button, Input, Card, DataTable, EmptyState, PaymentStatus, OrderStatus, Money)
  /patterns      (RestaurantDashboard, POSLayout, KitchenBoard, QRMenu, MobileCheckout)
  /rules         (ux-principles.md, accessibility.md, responsive.md, visual-identity.md)
```

- Utiliser des **tokens sémantiques** (`--status-payment-confirmed`) plutôt que des couleurs directes.
- Base technique : shadcn/ui, personnalisée pour porter l'identité Afrosite (tons chauds, énergie africaine moderne — pas le violet/bleu générique des SaaS).
- Quatre agents de conception : Product Agent, UX Agent, Art Director Agent, UI Critic Agent — ce dernier rejette explicitement gradients décoratifs inutiles, cartes répétitives, contraste insuffisant, dashboards sans priorité opérationnelle.
- Boucle d'apprentissage : mesurer temps de tâche, taux d'abandon, erreurs, questions support → hypothèse UX → nouvelle variante → A/B test → décision documentée dans le design system.
- Performance mobile : LCP ≤ 2,5 s, INP < 200 ms, CLS < 0,1 (repères Core Web Vitals), images WebP/AVIF compressées, mode offline/file d'attente pour les actions critiques.

## 12. Premier produit technique à construire

Au lieu de « construire n'importe quel SaaS », construire un générateur contrôlé de **3 blueprints** (voir [doc 01 §5.1](01-cahier-des-charges.md#51-mvp--phase-1-0-3-mois)) : Commerce, Restaurant, Services — chacun versionné, testé et sécurisé, personnalisé par l'IA mais jamais réinventé à chaque prompt.

Résultat recherché : **80 % de composants éprouvés, 20 % de génération IA contrôlée** — c'est ce qui permet d'obtenir simultanément qualité, vitesse, maîtrise des coûts et confiance.
