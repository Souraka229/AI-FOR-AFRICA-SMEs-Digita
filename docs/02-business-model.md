# Business Model — Afrosite (AI Company Builder Afrique)

## 1. Business Model Canvas

| Bloc | Contenu |
|---|---|
| **Proposition de valeur** | Transformer une intention économique en outil digital opérationnel — création + paiement Mobile Money + exploitation quotidienne, en français et en FCFA, sans compétence technique |
| **Segments clients** | TPE/commerçants, restaurants/food business, PME de services, agences digitales locales, startups/développeurs, institutions/ONG (voir priorisation ci-dessous) |
| **Canaux** | Vente terrain, WhatsApp Business, parrainage, partenaires de distribution, contenu local (voir [doc 05](05-roadmap-leadership-afrique.md)) |
| **Relation client** | Support humain WhatsApp, onboarding assisté, communauté de restaurateurs/commerçants, comptes gérés pour les clients Enterprise |
| **Ressources clés** | Blueprints métier versionnés, couche de paiement unifiée, données d'usage, réseau de distribution, équipe support |
| **Activités clés** | Maintenance des blueprints, orchestration IA, support client, réconciliation financière, sécurité/conformité |
| **Partenaires clés** | KKiaPay, FedaPay, CinetPay (paiement) ; agences locales ; incubateurs ; opérateurs télécoms ; associations de commerçants |
| **Structure de coûts** | Coûts IA (tokens/génération), infrastructure cloud, support client, acquisition terrain, salaires équipe |
| **Sources de revenus** | Abonnement logiciel + usage IA/infra + commission paiement/services (détail ci-dessous) |

## 2. Segments prioritaires

| Segment | Douleur principale | Offre à vendre | Priorité |
|---|---|---|---|
| TPE et commerçants | Faible digitalisation, dépendance WhatsApp/Excel | Boutique, catalogue, QR code, paiement Mobile Money | 1 |
| Restaurants et food business | Commandes dispersées, erreurs, peu de visibilité | POS léger, menu QR, commandes, livraison, fidélité, paiement | 1 |
| PME de services | Gestion manuelle clients/devis/factures | CRM, facturation, réservation, reporting | 1 |
| Agences digitales locales | Production lente, équipe technique limitée | White-label, génération d'apps, gestion multi-clients | 2 |
| Startups et développeurs | Coût cloud, time-to-market, intégrations paiement | SaaS Builder, API, code exportable, CI/CD | 2 |
| Institutions, ONG, incubateurs | Besoin de déployer vite des outils terrain | Portail, collecte de données, gestion de bénéficiaires | 3 |

## 3. Grille tarifaire

| Offre | Prix indicatif | Client | Inclus |
|---|---:|---|---|
| **Explorer** | 0 FCFA | Testeurs, micro-activités | 1 projet, templates limités, preview temporaire, crédits IA limités, aucun domaine personnalisé |
| **Starter** | 3 000–5 000 FCFA/mois | Commerçants, indépendants | 1 application, domaine partagé, quotas IA, support de base |
| **Business** | 10 000–20 000 FCFA/mois | Restaurants, PME structurées | Multi-utilisateurs, paiement, CRM, reporting, sauvegardes, support prioritaire |
| **SaaS Builder** | 25 000–60 000 FCFA/mois | Agences, startups, développeurs | Plusieurs projets, API, export, environnements preview, rôles, Git |
| **Enterprise** | Sur devis | Institutions, réseaux, franchises | SLA, SSO, déploiement dédié, conformité, intégrations sur mesure |

Pour un lancement de type « Afrosite Launch » (création sur mesure, tous verticaux confondus), ajouter des **frais de lancement** (25 000 à 150 000 FCFA selon complexité) afin de protéger la marge au moment où génération, paramétrage et support consomment le plus de ressources.

## 4. Les quatre revenus complémentaires

1. **Abonnement logiciel** — accès aux fonctionnalités, templates, dashboard, hébergement standard.
2. **Usage** — génération IA additionnelle, stockage au-delà du quota, SMS/WhatsApp, exports avancés, support premium.
3. **Paiement et services financiers** — commission d'orchestration transparente sur le paiement, facturation, réconciliation.
4. **Services premium** — onboarding, import de données, formation, personnalisation, intégrations sur mesure.

**Règle non négociable** : le plan gratuit ne doit jamais donner un accès illimité à une IA coûteuse. Utiliser crédits, limites de génération, modèles légers pour les tâches basiques, et validation avant toute action coûteuse.

## 5. Unit economics

```text
Marge brute = revenu abonnement + revenu usage + revenu services − coûts variables
```

**Objectif : marge brute ≥ 70 %.**

Exemple — client Business à 15 000 FCFA/mois : le coût variable direct (IA, infra, support) ne doit pas dépasser régulièrement 4 500–6 000 FCFA/mois. Au-delà, basculer l'usage excédentaire vers des crédits additionnels, un modèle IA plus léger, ou une tâche différée (traitement asynchrone plutôt qu'en temps réel).

Coûts variables à instrumenter dès le MVP :
- coût par génération/prompt (tokens IA) ;
- coût de stockage et bande passante par projet actif ;
- coût des environnements de preview ;
- coût SMS/WhatsApp/email par notification ;
- coût de support (temps humain par ticket) ;
- frais PSP (à ne jamais absorber sans les refacturer en transparence).

## 6. Taille de marché — approche pragmatique

| Niveau | Définition | Hypothèse indicative |
|---|---|---|
| **TAM** | Entrepreneurs, TPE/PME et créateurs d'applications d'Afrique francophone | Plusieurs millions de structures économiques |
| **SAM** | PME digitalisables au Bénin puis UEMOA, nécessitant présence digitale, paiement ou automatisation | Centaines de milliers d'organisations à moyen terme |
| **SOM à 3 ans** | Clients atteignables par vente directe, partenaires et communauté | 1 000 à 5 000 clients payants — objectif crédible si le produit trouve son segment |

**Illustration économique** : 2 000 clients actifs × 10 000 FCFA/mois de revenu moyen = 20 millions FCFA/mois de revenu récurrent, soit environ 240 millions FCFA/an avant frais de transaction et revenus d'usage. La viabilité dépend fortement de la maîtrise des coûts IA, du support et de l'acquisition.

## 7. Objectifs de croissance par horizon

| Horizon | Objectif clients actifs | Condition |
|---|---|---|
| 0–3 mois | 5 pilotes payants ou engagés | Produit stable, usage quotidien, feedback intense |
| 3–6 mois | 20–50 restaurants/commerces actifs | Onboarding rapide, premiers témoignages, churn faible |
| 6–12 mois | 100–250 clients actifs | Réseau de partenaires, paiement fiable, playbook commercial |
| 12–24 mois | 500–1 500 clients actifs | Réplication dans 2–3 marchés, équipe support/distribution |
| 24–36 mois | 3 000+ clients actifs | Plateforme multi-verticale, API paiement, agents IA, partenaires régionaux |

La métrique la plus importante n'est pas la croissance brute mais la **rétention** : une croissance rapide avec 20 % de churn mensuel est un piège. L'objectif est un usage quotidien qui rend le coût de changement élevé.

## 8. Pourquoi le Bénin et l'UEMOA

- Les paiements digitaux reposent fortement sur le Mobile Money (MTN MoMo, Moov Money, Wave).
- Des agrégateurs locaux (FedaPay, KKiaPay, FeexPay) prouvent déjà l'existence d'un marché pour l'infrastructure fintech locale.
- La BCEAO a lancé en septembre 2025 la plateforme de paiements instantanés interopérables **PI-SPI**, ouvrant la voie à des services de paiement plus intégrés au niveau régional — une opportunité structurelle pour une couche applicative construite dessus.

## 9. Risques financiers à surveiller

| Risque | Mitigation |
|---|---|
| Coûts IA imprévisibles si l'usage n'est pas gouverné | Quotas, crédits, routage vers modèles légers, cache de réponses |
| Dépendance à un seul PSP | Couche de routage multi-PSP dès la Phase 2 |
| Support trop coûteux pour une clientèle non technique | Onboarding en libre-service progressif + documentation vidéo + FAQ WhatsApp automatisée |
| Export du code réduisant la rétention | La valeur doit venir du service géré (paiement, support, données), pas du verrouillage |
| Change de réglementation paiement (BCEAO) | Ne jamais détenir les fonds ; rester couche d'orchestration au-dessus de PSP agréés |
