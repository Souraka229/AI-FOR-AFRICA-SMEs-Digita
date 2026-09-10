# Regles visuelles Afrosite

Proprietaire: CHITOU. Toute UI (landing, builder, blueprint Commerce) passe par ces tokens. Aucune couleur ou police en dur hors de `packages/design-system`.

## Typographie

- Geist Sans: titres, UI, montants. Blanc sur fond sombre. `letter-spacing: var(--tracking-tight)` sur les titres.
- Newsreader: **un seul mot** d'accent par hero, italique, gris (`--text-accent-italic`). Jamais un paragraphe entier en Newsreader.
- Montants FCFA: Geist, chiffres tabulaires, jamais d'italique.
- Interdit: Inter, Roboto, Arial, une troisieme famille sans validation.

## Couleur

- CTA: terracotta uniquement (`--action-primary`).
- Vert: uniquement le statut "paiement confirme".
- Ambre: paiement en attente. Rouge: echec. Orange: commande urgente.
- Pas d'or. Pas de violet. Pas de degrade bleu/violet.

## Interdits (rejet Vision Critic)

- Tiret cadratin (caractere interdit dans toute copie produit).
- Emoji comme icone.
- Glassmorphism, degrade SaaS, carte a barre coloree a gauche.
- Motifs "ethniques" decoratifs.
- USD affiche au client.
- 3D dans la caisse, le catalogue, le checkout ou le dashboard. Le 3D n'entre que si CHITOU le place explicitement (landing seulement pour l'instant: aucun).

## Motion

- Landing: wordmark `afrosite` en contour (`-webkit-text-stroke`) + spotlight au survol.
- Produit: transitions courtes (120 a 180 ms), pas de spectacle.

## Voice

Clair, chaud, direct, oriente resultat. Une phrase, une idee.
