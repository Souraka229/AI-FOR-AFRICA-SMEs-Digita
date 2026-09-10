import type { Vertical } from "@afrosite/contracts";

export type EvalCase = {
  id: string;
  prompt: string;
  expected: Vertical;
  mustSlug?: string;
  mustPass: boolean;
};

function pack(
  vertical: Vertical,
  prompts: string[],
  extras: Partial<EvalCase>[] = [],
): EvalCase[] {
  return prompts.map((prompt, index) => ({
    id: `${vertical}-${String(index + 1).padStart(2, "0")}`,
    prompt,
    expected: vertical,
    mustPass: true,
    ...extras[index],
  }));
}

const COMMERCE = pack("commerce", [
  "boutique de tissus wax à Cadjehoun, livraison quartier, paiement Mobile Money",
  "magasin de pagnes wax à Dantokpa, stock simple, paiement Moov Money",
  "boutique cosmétique à Haie Vive, vente au détail, Mobile Money",
  "épicerie de quartier à Godomey, dépôt boissons, paiement MTN MoMo",
  "quincaillerie à Akpakpa, vente de pièces, livraison possible",
  "boutique de wax à Houéyiho, catalogue pagnes, encaissement Mobile Money",
  "magasin de tissus à Cotonou Cadjehoun, stock et facture",
  "vente de pagnes wax à Fidjrossè, livraison quartier",
  "boutique de chaussures à Akogbato, stock, paiement Mobile Money",
  "dépôt de boissons à Godomey, vente en gros et détail",
  "épicerie Cadjehoun, produits de première nécessité, MTN MoMo",
  "magasin cosmétique Fidjrossè, vente au comptoir",
  "boutique wax Dantokpa, pagne 6 yards, livraison moto",
  "vente de tissus wax Haie Vive, catalogue et stock",
  "quincaillerie Houéyiho, vis et outils, paiement Mobile Money",
  "boutique de sacs et wax à Akpakpa",
  "épicerie Akogbato, dépôt riz et huile",
  "magasin de pagnes à Cotonou, vente et stock",
  "boutique wax Cadjehoun motif traditionnel, livraison quartier",
  "vente de cosmétique naturelle à Haie Vive",
  "dépôt alimentaire Godomey, Mobile Money accepté",
  "boutique de tissus à Tokpa, stock pagnes",
  "magasin wax Fidjrossè, commande WhatsApp",
  "épicerie de nuit Cadjehoun, vente et caisse",
  "quincaillerie Godomey, catalogue pièces",
  "boutique pagne wax Akpakpa, livraison quartier",
  "vente de wax et accessoires Haie Vive",
  "magasin alimentaire Houéyiho, stock et caisse",
  "boutique de tissus wax Cotonou, paiement Mobile Money",
  "épicerie Dantokpa, dépôt et vente au détail",
  "magasin cosmétique Cadjehoun, stock simple",
  "boutique wax Akogbato, pagnes et livraison",
]);

COMMERCE[0].mustSlug = "cadjehoun-wax";
COMMERCE[0].id = "commerce-demo-cadjehoun";

const RESTAURANT = pack("restaurant", [
  "maquis à Fidjrossè, menu QR, à emporter, paiement MTN MoMo",
  "restaurant de poisson braisé à Cadjehoun, menu et caisse",
  "snack grillades à Haie Vive, plat du jour, Mobile Money",
  "resto à emporter Godomey, cuisine béninoise, QR menu",
  "maquis Akpakpa, poisson et alloco, paiement Moov",
  "restaurant Fidjrossè, kds cuisine, à emporter",
  "snack Cadjehoun, fast-food local, menu QR",
  "maquis Houéyiho, grillades, paiement Mobile Money",
  "restaurant de brochettes Akogbato, plat et boisson",
  "resto Dantokpa, cuisine de rue, caisse",
  "maquis Godomey, menu QR et à emporter",
  "restaurant Haie Vive, poisson braisé, KDS",
  "snack Fidjrossè, plat du midi, Mobile Money",
  "maquis Cadjehoun, grill et jus bissap",
  "restaurant Akpakpa, menu QR, livraison plats",
  "resto Houéyiho, cuisine locale, caisse",
  "maquis Akogbato, poisson braisé, à emporter",
  "snack Godomey, fast food, paiement MTN MoMo",
  "restaurant Dantokpa, plat et menu",
  "maquis Haie Vive, grillades et kds",
  "resto Cadjehoun, menu QR, Mobile Money",
  "snack Akpakpa, cuisine rapide, caisse",
  "maquis Tokpa, poisson et alloco",
  "restaurant Fidjrossè, à emporter uniquement",
  "snack Houéyiho, plat du jour, QR menu",
  "maquis Godomey, grill et boissons",
  "restaurant Akogbato, cuisine béninoise, caisse",
  "resto Haie Vive, menu et paiement Mobile Money",
  "maquis Cadjehoun, kds et à emporter",
  "snack Dantokpa, fast-food, Moov Money",
  "restaurant Akpakpa, poisson braisé, menu QR",
  "maquis Fidjrossè plage, grillades, paiement Mobile Money",
]);

RESTAURANT[0].id = "restaurant-demo-fidjrosse";

const SERVICES = pack("services", [
  "salon de coiffure à Cadjehoun, rendez-vous et rappels WhatsApp",
  "salon de tresses à Fidjrossè, agenda et devis",
  "barbier à Haie Vive, rdv WhatsApp, paiement Mobile Money",
  "salon de manucure Godomey, rendez-vous clients",
  "couturière à Akpakpa, devis et facture",
  "plombier Cadjehoun, prestataire, devis urgent",
  "pressing Houéyiho, dépôt vêtements, rappels",
  "mécanique moto Akogbato, devis et rdv",
  "salon locking Dantokpa, agenda, WhatsApp",
  "coiffure homme Fidjrossè, rendez-vous",
  "salon Awa Cadjehoun, tresses et soins",
  "manucure Haie Vive, rdv et rappels",
  "artisan couturier Godomey, devis sur mesure",
  "salon de coiffure Akpakpa, locking et tresses",
  "barbier Cadjehoun, rdv WhatsApp",
  "pressing Fidjrossè, prestataire quartier",
  "salon manucure Houéyiho, agenda",
  "plombier Haie Vive, devis et facture",
  "mécanique auto Godomey, rendez-vous atelier",
  "coiffure tresses Akogbato, rappels WhatsApp",
  "salon barbier Dantokpa, rdv",
  "couture traditionnelle Cadjehoun, devis",
  "salon de soins Fidjrossè, agenda",
  "pressing Akpakpa, dépôt et retrait",
  "manucure Godomey, rendez-vous WhatsApp",
  "salon locking Haie Vive, rdv",
  "artisan plombier Houéyiho, devis",
  "coiffure dame Cadjehoun, tresses, agenda",
  "barbier Akogbato, prestataire, Mobile Money",
  "salon de coiffure Godomey, rappels clients",
  "mécanique moto Fidjrossè, devis",
  "salon manucure Cadjehoun, rdv et facture",
]);

SERVICES[0].id = "services-demo-cadjehoun";

export const MUST_PASS_IDS = [
  "commerce-demo-cadjehoun",
  "restaurant-demo-fidjrosse",
  "services-demo-cadjehoun",
] as const;

export const EVAL_CASES: EvalCase[] = [...COMMERCE, ...RESTAURANT, ...SERVICES];
