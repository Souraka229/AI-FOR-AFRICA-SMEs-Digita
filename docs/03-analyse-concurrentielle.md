# Analyse concurrentielle — Afrosite

Afrosite n'affronte pas un concurrent unique, mais un ensemble d'acteurs qui couvrent chacun une partie de la vision : créer un outil, encaisser, opérer, fidéliser. La stratégie consiste à intégrer mieux qu'eux les besoins métier, l'IA, les paiements locaux et l'exploitation quotidienne d'une activité — sur plusieurs verticaux (commerce, restauration, services) construits sur un même socle.

## 1. Carte concurrentielle globale

| Catégorie | Acteurs | Ce qu'ils vendent | Menace pour Afrosite |
|---|---|---|---|
| AI app builders internationaux | Lovable, Bolt, Replit, v0, Base44 | Création d'applications par prompt, code, déploiement | Très forte sur la génération d'apps et l'UX |
| AI app builder africain | Gebeya Dala (+ Jitume, Jenga) | Création d'apps par langage naturel en langues africaines, CRM indépendants, marketplaces | Très forte — le concurrent africain le plus direct |
| No-code / low-code | Bubble, FlutterFlow, Softr, Glide, Adalo | Création visuelle de sites, web apps et apps mobiles | Forte pour entrepreneurs et agences déjà formés |
| Cloud / backend | AWS, GCP, Azure, Supabase, Firebase, Vercel, Render | Infrastructure, base de données, stockage, déploiement | Forte techniquement, faible pour les non-techniciens |
| Paiement africain | Genius Pay, KKiaPay, FedaPay, CinetPay, Paystack, Flutterwave, DusuPay | Encaissement Mobile Money, cartes, liens de paiement | Forte sur les rails de paiement — à intégrer, pas à concurrencer |
| Fintechs qui s'élargissent vers l'opérationnel | Moniepoint/Orda (Moniebook), Yoco/Dyner.ai | POS + paiement + comptabilité + IA pour commerces/restaurants | Stratégique — elles veulent devenir le système d'exploitation des PME |
| SaaS verticaux locaux | POS restaurants, e-commerce, ERP/CRM locaux | Résolution d'un problème métier précis | Forte sur le besoin immédiat |
| Agences / freelances | Agences web, développeurs locaux | Création sur mesure, accompagnement | Forte en proximité, faible en scalabilité |
| Suites globales | Odoo, Zoho, Microsoft 365/Copilot, Google Workspace/Gemini | ERP, CRM, productivité, IA | Élevée chez PME déjà structurées |
| Communication/CRM conversationnel | Wati, respond.io, Trengo | Boîte partagée WhatsApp, automatisation marketing | Élevée sur la communication — Afrosite doit ajouter opérations + paiement |

## 2. Concurrents directs : AI app builders

| Concurrent | Force principale | Faiblesse exploitable | Réponse Afrosite |
|---|---|---|---|
| **Lovable** | UX de création très forte | Pas de spécialisation Afrique francophone, coût USD, pas de Mobile Money natif | Apps prêtes à vendre en FCFA, Mobile Money, WhatsApp, templates locaux |
| **Bolt** | Génération rapide de prototypes | Peu adapté à l'exploitation complète d'une PME locale | Vendre un business qui encaisse et se pilote, pas juste du code |
| **Replit** | Agent IA, IDE, hébergement complet | Plus adapté aux développeurs qu'aux commerçants non techniques | Expérience sans code, guidée par métier |
| **v0 / Vercel** | Interfaces et écosystème développeur forts | Nécessite une équipe technique pour backend/paiement/sécurité | Blueprints complets : UI + DB + paiement + rôles + dashboard |
| **Base44** | Produit simple, hébergement inclus | Peu de profondeur régionale | Miser sur les flux métiers africains et la connectivité |
| **Gebeya Dala** | Marque africaine, multilingue (dont français), positionné « pour l'Afrique » | Profondeur opérationnelle (paiements UEMOA, POS, conformité, support terrain) à valider | Aller plus loin : pas seulement créer, mais opérer — paiement, CRM, workflow, données |

Les plans payants de Lovable, Bolt, v0 et Replit se situent couramment autour de 20 à 30 USD/mois avec une logique de crédits/usage — élevé et imprévisible pour une micro-entreprise qui facture en FCFA.

## 3. Concurrents indirects : le vrai statu quo

Le concurrent le plus massif n'est pas un produit, c'est une habitude :

```text
WhatsApp + cahier + Excel + Mobile Money + Facebook + appels téléphoniques.
```

Pour beaucoup de PME, WhatsApp joue déjà le rôle de vitrine, support, canal de vente et outil de gestion. Afrosite doit donc démarrer là où la PME travaille déjà (WhatsApp-first), plutôt que d'exiger un changement d'habitude dès le premier jour.

## 4. Fintechs qui deviennent des systèmes d'exploitation — signal fort

| Cas | Ce qui s'est passé | Ce que ça signifie pour Afrosite |
|---|---|---|
| **Moniepoint / Orda → Moniebook** | Moniepoint a acquis Orda (POS Nigeria/Kenya) pour l'intégrer à Moniebook : POS, paiements, comptabilité, stocks, paiements fournisseurs, accès potentiel au crédit | Les fintechs veulent posséder l'opérationnel des PME, pas seulement le paiement — même logique qu'Afrosite, avec plus de moyens |
| **Yoco / Dyner.ai** | Yoco (Afrique du Sud) a acquis Dyner, OS IA pour restaurants/commerces indépendants, pour le connecter à son infra, sa force de vente et son réseau de 200 000+ marchands | Confirme la thèse : IA + paiement + opérations est la direction du marché, pas une idée isolée |

Ces acquisitions ne sont pas encore actives au Bénin/UEMOA francophone — c'est la fenêtre d'opportunité d'Afrosite pour s'implanter avant leur arrivée.

## 5. Concurrence paiement — le combat le plus stratégique

| Acteur | Couverture utile | Ce qu'il faut faire |
|---|---|---|
| **Genius Pay** *(primaire MVP — [ADR 0001](adr/0001-genius-pay-psp-primaire.md))* | Bénin (`MTN_MOMO_BEN`, `MOOV_BEN` via PawaPay) + plusieurs pays africains ; checkout hébergé ; webhooks HMAC-SHA256 | Intégrer **derrière** `PaymentProvider` en sandbox d'abord. Ne jamais appeler le SDK depuis le métier. |
| **KKiaPay** | Bénin, Côte d'Ivoire, Togo, Sénégal, Niger, Burkina Faso | Fallback Phase 2 — ne pas chercher à remplacer |
| **FedaPay** | Bénin, Côte d'Ivoire, Togo, Sénégal, Niger | Fallback Phase 2 — même interface `PaymentProvider` |
| **CinetPay** | 10+ pays francophones d'Afrique de l'Ouest/centrale | Expansion UEMOA / multi-pays |
| **Paystack / Flutterwave** | Nigeria + large couverture africaine | Référence produit, partenaire possible cross-border |
| **DusuPay** | 15+ pays francophones annoncés | À évaluer à l'expansion hors UEMOA |

**Principe** : Afrosite ne devient pas un PSP. Il construit une couche supérieure — routage entre PSP, gestion des webhooks/statuts/échecs, réconciliation quotidienne, facturation, reporting financier — connectée à des PSP déjà agréés BCEAO. Genius Pay est le premier implémenté ; changer de rail = une classe, pas une réécriture métier.

## 6. Matrice de différenciation

| Critère | Lovable/Bolt/Replit | Bubble/FlutterFlow | PSP locaux | Afrosite (cible) |
|---|---|---|---|---|
| Création par IA | Forte | Moyenne à forte | Faible | Forte et orientée métier |
| Paiements africains | Faible | Faible à moyenne | Très forte | Très forte via agrégation multi-PSP |
| Paiement en FCFA | Faible | Faible | Forte | Forte |
| Templates métier Afrique | Faible | Faible | Très faible | Très forte (3 blueprints dès le MVP) |
| Déploiement/infrastructure | Forte mais générique | Moyenne | Faible | Forte et simplifiée |
| Support francophone local | Faible | Faible | Moyenne à forte | Très forte |
| Contrôle / export code | Variable | Moyen à fort | Non applicable | Fort, par design |
| CRM, factures, commandes, opérations | Faible | À construire soi-même | Faible | Natif dans le socle commun |
| Rétention client | Moyenne | Moyenne | Forte sur paiement | Forte si le produit devient le système d'exploitation quotidien de la PME |

## 7. Analyse SWOT

| Forces | Faiblesses |
|---|---|
| Vision intégrée : création, déploiement, exploitation, facturation, paiement | Produit large : risque de construire trop de couches trop tôt |
| Expertise locale en fintech, paiement, opérations métier | Ressources techniques/financières probablement inférieures aux plateformes mondiales |
| Connaissance des besoins africains : Mobile Money, WhatsApp, FCFA, support humain | Coûts IA/cloud difficiles à prévoir si les usages ne sont pas gouvernés |
| Expérience française et contextualisée | Support utilisateur important pour une clientèle non technique |
| Approche anti-lock-in : export code, données, Docker, documentation | L'exportabilité peut réduire la rétention si le service géré n'apporte pas assez de valeur |
| Marché UEMOA avec monnaie commune et interopérabilité croissante (PI-SPI) | Dépendance persistante aux APIs opérateurs, PSP, cloud, modèles IA |

| Opportunités | Menaces |
|---|---|
| Digitalisation rapide des TPE/PME, recherche de solutions abordables | Lovable, Replit, Bolt, Google peuvent baisser leurs prix rapidement |
| Expansion de l'IA générative et du low-code (50 % des nouvelles apps low-code/no-code dès 2025 selon les estimations sectorielles) | Guerre des prix, banalisation de la génération de code |
| Paiements interopérables UEMOA via PI-SPI (lancé septembre 2025 par la BCEAO) | Évolutions réglementaires, exigences KYC/AML |
| Marchés verticaux insuffisamment servis : restaurants, commerces, écoles, logistique, microfinance | Instabilité ou indisponibilité des APIs Mobile Money/PSP |
| Vente B2B2C via agences, incubateurs, opérateurs télécoms, banques | Cybersécurité, fraude, pertes de données, incidents de paiement |
| Demande de souveraineté des données et d'hébergement régional | Coût infrastructure GPU, pénurie de profils DevOps/sécurité/IA |
| Fintechs (Moniepoint/Orda, Yoco/Dyner) qui valident le modèle « OS pour PME » sans encore couvrir l'UEMOA francophone | Ces mêmes fintechs peuvent entrer sur le marché UEMOA francophone plus vite que prévu |

## 8. Analyse PESTEL

| Facteur | Impact | Réponse stratégique |
|---|---|---|
| **Politique** | Soutien croissant des gouvernements africains à la transformation numérique et aux fintechs | S'aligner avec incubateurs, agences nationales du numérique, programmes PME |
| **Économique** | Pouvoir d'achat limité, sensibilité au prix, coûts d'infrastructure facturés en USD | Tarification FCFA, freemium limité, paiement mensuel, contrôle strict de la consommation IA |
| **Social** | Forte adoption WhatsApp/Mobile Money/commerce informel, compétences numériques inégales | UX conversationnelle en français, onboarding assisté, support WhatsApp |
| **Technologique** | Croissance IA/cloud/low-code/paiements instantanés, mais Internet et énergie irréguliers | Architecture offline-tolerant, apps légères, files de messages, sauvegardes, multi-fournisseurs |
| **Environnemental** | GPU/data centers énergivores, coupures pouvant affecter l'hébergement local | Optimiser les modèles, mesurer le coût par action, éviter l'auto-hébergement prématuré de gros modèles |
| **Légal** | Paiement encadré par la BCEAO, protection des données, cybersécurité | Ne pas détenir les fonds, s'appuyer sur des PSP agréés, séparer le ledger interne des flux financiers, consentement/journalisation |

Dans l'UEMOA, une entreprise proposant des services de paiement doit être autorisée selon les conditions fixées par la BCEAO — Afrosite doit rester une couche technique/orchestration connectée à des acteurs agréés, jamais un substitut à une banque ou un établissement de paiement.

## 9. Les vrais concurrents à court terme (à ne pas sous-estimer)

1. **L'inertie** — le commerçant continue avec cahier, Excel, WhatsApp, cash.
2. **L'agence locale** — crée un site ou un menu QR en une semaine à prix négocié.
3. **Le PSP seul** — un simple lien de paiement suffit parfois.
4. **Le logiciel générique** — Odoo, un POS importé, une solution piratée.
5. **La marketplace/livraison** — apporte des commandes mais capture les données et la marge.
6. **Les fintechs qui s'élargissent** — modèle Moniepoint/Orda ou Yoco/Dyner.

Vendre un **résultat économique clair**, pas une promesse technologique : « Afrosite augmente vos ventes directes, réduit les erreurs, accélère l'encaissement et vous donne une vision réelle de votre activité. »

Voir la traduction de cette analyse en avantage défendable dans [doc 04 — Différenciation & positionnement](04-differenciation-positionnement.md).
