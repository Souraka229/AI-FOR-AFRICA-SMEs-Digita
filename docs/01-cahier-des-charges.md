# Cahier des charges — Afrosite (AI Company Builder Afrique)

## 1. Contexte

Les TPE/PME africaines (commerçants, restaurants, artisans, services) restent majoritairement gérées via WhatsApp, Excel et cahier papier. Elles veulent se digitaliser mais sont mal servies par :
- les AI app builders internationaux (Lovable, Bolt, Replit, v0) : pas de paiement local, prix en USD, pas de support en français adapté au terrain ;
- le no-code classique (Bubble, FlutterFlow) : trop technique pour un commerçant non-initié ;
- les agences locales : peu scalables, qualité variable, délais longs ;
- les PSP seuls (KKiaPay, FedaPay, CinetPay) : bons pour encaisser, mais ne couvrent pas la création d'outil ni l'exploitation quotidienne.

## 2. Vision

Devenir la couche opérationnelle et financière des PME africaines : une plateforme où décrire son activité en langage naturel suffit à obtenir une application fonctionnelle, connectée aux paiements Mobile Money, exploitable et pilotable au quotidien — sans compétence technique et sans dépendance à une devise étrangère.

**Afrosite** est le nom du projet. Il ne se limite pas à un vertical unique : le MVP couvre dès le départ plusieurs profils de TPE/PME (commerce, restauration, services), construits sur un socle technique commun. C'est le socle — pas le vertical — qui est le vrai produit.

## 3. Objectifs du produit

| Objectif | Indicateur de succès |
|---|---|
| Réduire le temps de mise en ligne d'un outil métier | < 1 heure entre le premier prompt et une preview fonctionnelle |
| Permettre l'encaissement Mobile Money natif | 100 % des transactions réconciliées automatiquement |
| Garantir la confiance et la réversibilité | Export complet (code + données) disponible à tout moment |
| Rendre le produit utilisable sans développeur | 0 ligne de code requise pour le parcours standard |
| Valider plusieurs verticaux sur un socle unique | 3 blueprints métier en production dès le MVP, sans dupliquer l'infrastructure |
| Maîtriser les coûts IA/infra par client | Marge brute ≥ 70 % par client actif (voir [doc 02](02-business-model.md)) |

## 4. Utilisateurs cibles (personas)

| Persona | Profil | Besoin principal | Niveau technique | Priorité MVP |
|---|---|---|---|---|
| **Le commerçant** | Boutique physique + vente WhatsApp | Catalogue en ligne, commandes centralisées, paiement à distance | Faible | 1 |
| **Le restaurateur** | Maquis/fast-food/snack, 20–100 commandes/jour | Réduire les erreurs de commande, encaisser vite, suivre les ventes du jour | Nul à faible | 1 |
| **Le prestataire de service** | Salon, artisan, freelance | Prise de rendez-vous, devis, factures, relance client | Faible à moyen | 1 |
| **L'agence digitale locale** | Produit des sites/apps pour des clients | Produire plus vite, gérer plusieurs clients en marque blanche | Moyen à élevé | 2 |
| **Le développeur / la startup** | Veut lancer un SaaS rapidement | Code exportable, API, paiement intégré, déploiement | Élevé | 2 |

Contrairement à une approche mono-vertical, le MVP Afrosite sert **les trois personas prioritaires en parallèle** dès le premier lancement — voir justification dans [doc 03](03-analyse-concurrentielle.md) et [doc 05](05-roadmap-leadership-afrique.md). La raison : ces trois profils partagent un socle quasi identique (catalogue, commande, paiement, CRM léger, reporting) — seule l'habillage et deux ou trois modules spécifiques changent par vertical. Valider les trois en parallèle réduit le risque de construire une plateforme qui ne fonctionne que pour un seul métier.

## 5. Périmètre fonctionnel

### 5.1 MVP — Phase 1 (0–3 mois)

**Trois blueprints en production dès le lancement, sur un socle commun** : Commerce, Restaurant, Services.

#### Socle commun (partagé par les 3 blueprints)

| Module | Fonctionnalités incluses |
|---|---|
| Onboarding | Création de compte, description de l'activité en langage naturel, génération automatique du catalogue/menu/liste de services |
| Catalogue / offre | Produits, plats ou prestations avec prix, disponibilité, photos |
| Prise de commande / réservation | Panier ou créneau, notes spéciales, confirmation client |
| Paiement | Intégration Mobile Money (MTN MoMo, Moov Money) via un agrégateur (KKiaPay ou FedaPay) |
| Réconciliation | Vue quotidienne : encaissé par canal (cash, MoMo, carte), transactions impayées |
| CRM léger | Clients identifiés par numéro de téléphone, historique, compteur de fidélité |
| Dashboard | Ventes/activité du jour, panier moyen, top produits/services, éléments en retard |
| Notifications | Alertes WhatsApp au gérant (nouvelle commande/réservation, paiement confirmé) |
| Export | Export des données (transactions, clients, ventes) en CSV à tout moment |

#### Modules spécifiques par blueprint

| Blueprint | Modules additionnels |
|---|---|
| **Commerce** | Gestion de stock simple, commande via WhatsApp, facturation, suivi de livraison |
| **Restaurant** | Menu QR, écran cuisine (KDS) avec statuts (reçue / en préparation / prête), gestion des tables/à emporter/livraison |
| **Services** | Agenda de rendez-vous, devis, facture, rappels automatiques avant rendez-vous |

### 5.2 Phase 2 (3–9 mois) — Approfondissement et nouveaux verticaux

- Blueprints additionnels : salon de beauté avancé, école/centre de formation, clinique/pharmacie légère, agence/livraison.
- Moteur de workflow/automatisation (ex. relance client inactif après 30 jours).
- Paiement multi-PSP avec routage automatique (KKiaPay, FedaPay, CinetPay).
- Marketplace de modules additionnels.
- Emails automatiques par tenant (`admin@boutique.afrosite.app`) — voir [doc 06 §7](06-architecture-technique.md#7-emails-automatiques-par-tenant).

### 5.3 Phase 3 (9–18 mois) — SaaS Builder ouvert

- Génération de SaaS B2B générique (comptes, organisations, rôles, abonnements, API).
- Connexion GitHub/GitLab et export/push de code réel — voir [doc 06 §8](06-architecture-technique.md#8-connexion-githubgitlab-et-push-de-code).
- API publique et environnements preview à la demande.
- Offre white-label pour agences.

### 5.4 Hors périmètre (explicitement exclu du MVP)

- Auto-hébergement de modèles IA propriétaires.
- Développement d'un PSP propre (détention de fonds) — la plateforme reste orchestrateur au-dessus de PSP agréés.
- Kubernetes, service mesh, multi-cloud actif — reporté à la phase où le volume le justifie.
- Génération de code totalement libre sans blueprint (trop risqué en sécurité/qualité au démarrage).
- Marketplace publique de plugins tiers.
- Plus de 3 blueprints simultanés au lancement (mieux vaut 3 verticaux solides que 6 verticaux fragiles).

## 6. Exigences non fonctionnelles

| Catégorie | Exigence |
|---|---|
| **Performance** | Preview générée en < 5 minutes pour un blueprint standard ; dashboard chargé en < 2 s sur réseau mobile 3G/4G |
| **Disponibilité** | SLA cible 99,5 % pour les fonctions critiques (paiement, prise de commande/réservation) dès la sortie du pilote |
| **Résilience réseau** | Prise de commande et caisse fonctionnelles en mode dégradé (file d'attente locale, synchronisation différée) |
| **Sécurité** | Aucune donnée de carte stockée en interne (délégué au PSP) ; secrets en coffre-fort (Vault) ; scans automatiques (SAST, dépendances, secrets) à chaque déploiement |
| **Conformité** | Alignement avec les exigences BCEAO sur les prestataires de paiement (la plateforme n'est jamais dépositaire de fonds) ; consentement et traçabilité RGPD-like sur les données personnelles |
| **Langue** | Français natif dès le MVP ; langues locales en roadmap Phase 3 |
| **Réversibilité** | Export intégral (code, base de données, assets, configuration) disponible en un clic |
| **Observabilité** | Traces, logs et métriques centralisés (OpenTelemetry) sur chaque application déployée |
| **Coût maîtrisé** | Chaque action IA a un coût tracké ; quotas et crédits appliqués sur les offres gratuites/starter |

## 7. Contraintes

- **Budget** : ressources limitées au démarrage → priorité aux briques open source et managées plutôt qu'à l'infrastructure propriétaire.
- **Réglementaire** : la plateforme ne doit jamais se substituer à un établissement de paiement agréé BCEAO ; elle route vers des PSP agréés.
- **Connectivité** : conception « offline-tolerant » — réseau instable et coupures fréquentes à anticiper.
- **Devise** : tarification et comptabilité natives en FCFA, jamais en USD affiché au client final.
- **Support** : cible non technique → onboarding assisté et support humain WhatsApp indispensables, pas seulement un chatbot.
- **Discipline de portée** : 3 blueprints maximum au MVP — tout nouveau vertical demandé doit d'abord être validé sur le socle commun avant de justifier un module dédié.

## 8. Livrables attendus par phase

| Phase | Livrable |
|---|---|
| MVP | Socle commun + 3 blueprints (Commerce, Restaurant, Services) en production, 5 clients pilotes répartis sur les 3 profils, paiement Mobile Money en production |
| Phase 2 | 2 à 4 blueprints additionnels, workflow/automatisation, multi-PSP, 50+ clients actifs |
| Phase 3 | SaaS Builder ouvert aux agences/développeurs, API publique, export de code, 500+ clients actifs |

## 9. Critères d'acceptation du MVP

- [ ] Un utilisateur (commerçant, restaurateur ou prestataire) peut décrire son activité en langage naturel et obtenir un outil fonctionnel en moins d'une heure, sur le blueprint correspondant.
- [ ] Une commande ou réservation passée par le client final est visible en temps réel côté gérant (dashboard ou écran cuisine selon le blueprint).
- [ ] Un paiement Mobile Money (MTN MoMo ou Moov Money) est initié, confirmé par webhook signé, et réconcilié sans intervention manuelle.
- [ ] Le gérant reçoit un résumé quotidien de son activité via WhatsApp.
- [ ] Les données peuvent être exportées en CSV sans support technique.
- [ ] Le produit reste utilisable (mode dégradé) en cas de coupure réseau ponctuelle.
- [ ] Aucun secret (clé API, token PSP) n'est visible côté client ou dans les logs.
- [ ] Le socle commun (auth, catalogue, paiement, CRM, dashboard) est identique en code entre les 3 blueprints — seuls les modules spécifiques diffèrent.

## 10. Glossaire

| Terme | Définition |
|---|---|
| **Blueprint** | Modèle d'application pré-conçu, testé et sécurisé, que l'IA personnalise plutôt que de générer de zéro |
| **PSP** | Prestataire de Services de Paiement (KKiaPay, FedaPay, CinetPay…) |
| **KDS** | Kitchen Display System — écran cuisine affichant les commandes |
| **UEMOA** | Union Économique et Monétaire Ouest-Africaine (zone FCFA) |
| **Tenant** | Une entreprise cliente utilisant la plateforme, avec son propre espace isolé |
| **Ledger** | Registre interne des transactions financières, distinct des flux réels gérés par le PSP |
