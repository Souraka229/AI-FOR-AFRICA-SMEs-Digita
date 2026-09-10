# Pitch — Grok Bot Cotonou Hackathon (Cursor × Devs Days)

> Support de candidature, de présélection et de finale pour présenter **Afrosite**.
> Événement : Cursor Bénin × Club des Devs — 9 & 10 septembre 2026 (finale pendant les Devs Days).

## 0. Cadre de l'événement

| Phase | Format | Ce qu'on prépare |
|---|---|---|
| **Candidature** | Dossier + vidéo 2–5 min (+ GitHub, maquettes, démo) | §2 Fiche de candidature · §3 Script vidéo |
| **Présélection** | 10 équipes → entretien visio 10 min → 5 finalistes | §1 Accroche · §6 Q&A |
| **Finale** | Build intensif jusqu'à 1 semaine · pitch 5 min + 3 min Q&A · **démo fonctionnelle obligatoire** | §4 Pitch de finale · §5 Démo · §7 Périmètre · §8 Répartition |

**Critères du jury** : qualité technique du prototype · innovation & utilité · expérience utilisateur · **usage de Cursor** · qualité du pitch.

> ⚠️ Le texte officiel mélange « GrokBot » (une mention) et « Cursor » (partout ailleurs + critère de jury). Ce support mise sur **Cursor**. Si les organisateurs confirment GrokBot comme obligatoire, remplacer « Cursor » par « GrokBot + Cursor » dans la section outillage (§2, §6 Q12).

---

## 1. L'accroche (à connaître par cœur)

**Une phrase**

> « Afrosite : décrivez votre activité, repartez avec une application pour vendre et encaisser en Mobile Money — en français, en FCFA, sans une ligne de code. »

**30 secondes**

> « Au Bénin, la plupart des commerces, maquis et prestataires tournent avec WhatsApp, un cahier et Excel. Les créateurs d'apps par IA comme Lovable ou Bolt ne parlent pas Mobile Money, facturent en dollars, et ne gèrent pas l'exploitation quotidienne. Afrosite part de la description d'une activité et rend un outil complet — catalogue, commandes, caisse, paiement MTN MoMo et Moov Money, réconciliation, résumé WhatsApp — sur un socle unique décliné en trois métiers. Comme Cursor pour le code : l'IA propose, des règles contrôlent, les tests vérifient, l'humain valide. »

**Le positionnement, en une ligne**

> « On ne fait pas un générateur d'apps de plus. On construit le système d'exploitation quotidien d'une PME africaine : créer + encaisser + piloter. »

**La ligne qui résonne pour un jury Cursor**

> « Afrosite applique à la digitalisation des PME la même idée que Cursor applique au code : l'IA propose, des garde-fous contrôlent, l'humain valide. »

---

## 2. Fiche de candidature

### L'équipe — 3 personnes complémentaires

- **Souraka HAMIDA** — Product Lead, développeur front-end, data science & recherche. Vision, contrat de données, architecture front, mesure des coûts IA.
- **CHITOU** — Design Lead & design engineering. Design system, composants livrés en code, direction artistique, boucle de critique visuelle.
- **SERGE** — Backend, infrastructure, paiement, agents IA. API, base de données, intégration Mobile Money, orchestration des agents, CI/CD.

Francophones, terrain de Cotonou, Mobile Money au quotidien. Documentation projet déjà rédigée : cahier des charges, architecture, business model, go-to-market, [playbook d'équipe](11-playbook-equipe.md).

### Le projet — Afrosite

Plateforme AI-native de digitalisation, d'encaissement et d'exploitation pour les TPE/PME d'Afrique de l'Ouest, en commençant par le Bénin. On décrit son activité en langage naturel ; l'IA personnalise un **blueprint métier éprouvé** (Commerce, Restaurant, Services) plutôt que de générer une app de zéro — 80 % de composants testés, 20 % de génération contrôlée. Paiement Mobile Money natif via un PSP agréé BCEAO ; Afrosite n'est **jamais** dépositaire des fonds. Export du code et des données à tout moment. Détails : [doc 01](01-cahier-des-charges.md), [doc 06](06-architecture-technique.md).

### La motivation

Les fintechs qui deviennent le « système d'exploitation des PME » (Moniepoint/Orda au Nigéria, Yoco/Dyner en Afrique du Sud) valident la thèse — mais **aucune ne couvre encore l'UEMOA francophone**. La BCEAO a lancé les paiements instantanés interopérables (PI-SPI) en septembre 2025. La fenêtre est ouverte maintenant, pour une équipe locale qui connaît le terrain. Le hackathon nous force à livrer un prototype de bout en bout et à le confronter à un jury et à la communauté.

### Comment on utilise Cursor

- **Monorepo + frontière typée** : un paquet `contracts` définit le schéma « Blueprint JSON » une seule fois ; front et back en dérivent. Cursor travaille contre un contrat, pas contre du vide.
- **Système de prompts discipliné** ([playbook §8](11-playbook-equipe.md#8-système-de-prompts--pour-aller-très-vite)) : chaque tâche donnée à Cursor porte un *bloc de contexte* (produit, stack, règles non négociables, charte), le nom de la branche, et la *Definition of Done*. On fait produire le plan avant le code.
- **Cursor génère** les composants du design system, les endpoints API + migrations, les tests Playwright ; des **gates automatiques** (lint, typecheck, tests, scan de secrets, sécurité) valident avant merge. Jamais de code généré poussé sur `main` sans revue.
- Résultat : une équipe de 3 tient le rythme d'une équipe plus grande, sans perdre la qualité. **Démontrable en direct.**

---

## 3. Script de la vidéo de candidature (2–5 min → cible 3 min)

**[0:00–0:25 — Souraka, à l'écran]**
> « Je suis Souraka. Avec CHITOU au design et SERGE au backend, on construit Afrosite. À Cotonou, un commerçant sur deux gère ses ventes avec WhatsApp et un cahier. Il veut se digitaliser, mais les outils d'IA du marché ne parlent pas Mobile Money, facturent en dollars, et s'arrêtent au site vitrine. »

**[0:25–0:55 — voix off + capture de la landing puis du produit]**
> « Afrosite part d'une phrase : "je tiens une boutique de tissus à Cadjehoun". En quelques minutes, on obtient un catalogue, un mini-site, la prise de commande, la caisse et le paiement Mobile Money. Pas une page blanche : un blueprint métier déjà testé que l'IA personnalise. »

**[0:55–1:40 — démo écran, la séquence de vente]**
> « Voici une commande de 24 500 FCFA passée depuis le mini-site. Le client paie avec MTN MoMo. Le paiement est vérifié côté serveur — pas juste une redirection — puis confirmé. Le client reçoit son reçu sur WhatsApp, la commerçante est notifiée. Le soir, le tableau de bord montre l'encaissé par espèces, Mobile Money et carte, et envoie un résumé WhatsApp. »

**[1:40–2:15 — SERGE, sur l'architecture + Cursor]**
> « Techniquement : Next.js, FastAPI, PostgreSQL, des agents orchestrés, un pipeline prompt → production avec six garde-fous automatiques. On construit tout dans Cursor, avec un système de prompts qui embarque le contexte, la branche et les critères de qualité à chaque tâche. L'IA propose, les règles contrôlent, l'humain valide. »

**[2:15–2:45 — CHITOU, sur le design + le terrain]**
> « Le design est pensé pour un téléphone Android sur réseau lent : la caisse et les commandes fonctionnent hors connexion puis se synchronisent. Français natif, FCFA natif, jamais de devise étrangère affichée au client. »

**[2:45–3:00 — Souraka, clôture]**
> « Après le hackathon : cinq établissements pilotes à Cotonou en 90 jours. Notre objectif ici : sortir un prototype de bout en bout et le confronter à vous. Merci. »

**À joindre** : le dépôt GitHub (monorepo + docs), la landing en ligne, les maquettes du design system.

---

## 4. Pitch de finale — 5 minutes, slide par slide

| # | Slide | Ce qu'on dit (≈ durée) |
|---|---|---|
| 1 | **Titre** — logo Afrosite + « Vendez, encaissez, pilotez — sans code » + les 3 noms | 10 s |
| 2 | **Le problème** — photo d'un comptoir : WhatsApp + cahier + Mobile Money éparpillés | « Commandes perdues, erreurs de caisse, aucune vision des encaissements. » 30 s |
| 3 | **Pourquoi les outils actuels échouent ici** — Lovable/Bolt/v0 : pas de Mobile Money, USD, site vitrine seulement ; no-code : trop technique ; agences : pas scalables | 30 s |
| 4 | **Afrosite** — le schéma : phrase → blueprint → mini-site + commandes + caisse + paiement + dashboard | 40 s |
| 5 | **DÉMO EN DIRECT** (voir §5) | 2 min |
| 6 | **Comment c'est fait** — 80/20, pipeline à 6 gates, agents, audit trail, « construit dans Cursor avec un système de prompts » | 30 s |
| 7 | **Le moat** — distribution terrain · paiement local · templates métier · données d'usage · réversibilité. Moniepoint/Yoco valident la thèse, pas encore en UEMOA francophone | 30 s |
| 8 | **Marché & modèle** — Cotonou → UEMOA · abonnement FCFA 3–20k/mois + commission paiement transparente · marge brute cible ≥ 70 % | 20 s |
| 9 | **Après le hackathon** — 5 pilotes Cotonou en 90 jours, un par métier · demande : mentorat paiement + mise en relation commerçants | 20 s |
| 10 | **Merci** — QR vers la démo + le dépôt | — |

---

## 5. Déroulé de la démo en direct (2 min) — **obligatoire, à répéter 5 fois**

1. **(20 s)** Dans `/studio`, on tape : *« boutique de tissus wax à Cadjehoun, livraison quartier, paiement Mobile Money »*. On lance.
2. **(25 s)** L'agent produit le **blueprint Commerce** : catalogue (3 produits avec prix), mini-site, prise de commande. On ouvre la preview.
3. **(25 s)** Depuis le mini-site, un client ajoute au panier → **24 500 FCFA** → paiement **MTN MoMo (sandbox)**.
4. **(20 s)** Webhook signé → **vérification serveur** → statut **« paiement confirmé »** → **reçu WhatsApp** au client + notif à la commerçante.
5. **(20 s)** Dashboard : **réconciliation du soir** (espèces / MoMo / carte) + bouton **résumé WhatsApp**.
6. **(10 s)** Bonus Cursor : on montre dans Cursor un composant du design system généré avec notre **bloc de prompt** qui passe les gates lint + tests.

**Plan B (si le live casse)** : vidéo pré-enregistrée de la même séquence (même environnement sandbox), lancée en 3 s. Toujours l'avoir ouverte dans un onglet.

---

## 6. Q&A — questions probables du jury + réponses courtes

1. **Différence avec Lovable / Bolt / v0 ?** — Eux génèrent du code. Nous vendons l'**exploitation quotidienne + le paiement local** : Mobile Money natif, FCFA, français, blueprints métier testés, support humain, réversibilité.
2. **Et Gebeya Dala (concurrent africain) ?** — Eux créent des apps. Nous **opérons** l'activité : paiement UEMOA, caisse, réconciliation, CRM, workflow.
3. **Vous êtes un PSP ? Et la BCEAO ?** — Non. **Jamais dépositaire des fonds.** Orchestrateur au-dessus de PSP agréés BCEAO. Registre interne séparé des flux réels.
4. **Modèle économique ?** — Abonnement FCFA (3 000–20 000/mois) + usage + **commission d'orchestration transparente** sur le paiement + services. Marge brute cible ≥ 70 % ([doc 02](02-business-model.md)).
5. **Acquisition clients ?** — Vente terrain dans une zone dense de Cotonou, programme **Founding 5**, parrainage, partenaires (agences, imprimeurs QR, PSP), WhatsApp ([doc 05](05-roadmap-leadership-afrique.md)).
6. **Qu'est-ce qui empêche un géant de copier ?** — Le moat n'est pas le modèle IA : distribution physique, intégration paiement locale, templates terrain, données d'usage, confiance. Fenêtre : les fintechs « OS pour PME » ne sont pas encore en UEMOA francophone.
7. **Coûts IA / marge ?** — Routeur multi-modèles (léger / puissant / code), **cache de prompts**, quotas et crédits, 80 % de composants éprouvés. Chaque action IA est trackée par client.
8. **Qualité et sécurité du code généré ?** — Pipeline à **6 gates** (schéma, qualité, sécurité SAST, paiement, préprod, prod), sandbox d'exécution, jamais de push sur `main`, audit trail complet, boucle de critique visuelle ([doc 06 §5](06-architecture-technique.md#5-pipeline-prompt--production)).
9. **Réseau instable ?** — File locale + synchro différée pour la commande et la caisse.
10. **Traction ?** — Pré-lancement. Objectif hackathon : prototype de bout en bout. Ensuite : 5 pilotes Cotonou en 90 jours.
11. **Pourquoi vous ?** — Équipe complète (produit/front/data, design system, backend/paiement/agents), terrain de Cotonou, francophone, Mobile Money au quotidien.
12. **Usage de Cursor, concrètement ?** — Monorepo, `contracts` comme frontière typée, système de prompts (contexte + branche + DoD dans chaque prompt), Cursor génère composants/endpoints/tests, les gates valident. Démontré en direct.

---

## 7. Périmètre de build pour la finale (1 semaine, réaliste)

**On livre**

- **1 seul blueprint** (Commerce) de bout en bout — pas les 3.
- Prompt → **Blueprint JSON validé** (schéma Zod/Pydantic) → preview : catalogue + prise de commande + mini-site.
- **Paiement sandbox** (Genius Pay ou FedaPay) : `createTransaction` + webhook signé + `verify` serveur + statut « payé ».
- **Dashboard minimal** : réconciliation du jour + **résumé WhatsApp** (Twilio / Meta sandbox, ou simulé proprement).
- **2 agents** : Intent + Product Architect. Code Agent léger si le temps le permet.
- **Déploiement preview automatique** + audit trail visible.

**On coupe (assumé)** : les 3 blueprints, multi-PSP, offline complet, SEO complet, Temporal complet (un simple worker suffit), Keycloak, marketplace.

---

## 8. Répartition pour le hackathon

| Qui | Pendant le build | Le jour J |
|---|---|---|
| **Souraka** | Pipeline prompt → blueprint (agents Intent + Product Architect), écran de démo, coordination | Porte le pitch (slides 1–4, 6–10) |
| **CHITOU** | Design system minimal + UI blueprint Commerce (catalogue, commande, dashboard, mini-site) + montage de la vidéo | Pilote la **démo en direct** (écran) |
| **SERGE** | API socle + paiement sandbox (`createTransaction` / webhook / `verify`) + registre + déploiement preview + résumé WhatsApp | Répond aux questions techniques (Q&A 3, 7, 8, 12) |

---

## 9. Checklist J-1

- [ ] Démo répétée 5 fois de bout en bout, chronométrée sous 2 min.
- [ ] Vidéo de secours enregistrée et ouverte dans un onglet.
- [ ] Environnement sandbox paiement testé le matin même (clés, webhooks).
- [ ] Slides exportées en PDF (pas de dépendance réseau).
- [ ] QR code vers la démo + le dépôt, imprimé et sur la dernière slide.
- [ ] Rôles de prise de parole répartis et minutés.
- [ ] Connexion de secours (partage 4G) prête.
