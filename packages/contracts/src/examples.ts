import type { Blueprint } from "./blueprint.schema";
import { BLUEPRINT_SCHEMA_VERSION } from "./blueprint.schema";

const CORE = [
  "onboarding",
  "catalog",
  "orders",
  "payments",
  "reconciliation",
  "crm",
  "dashboard",
  "notifications",
  "exports",
] as const;

const CONFIRM = [
  "production_deploy",
  "payment_live_activation",
  "database_deletion",
] as const;

export const COMMERCE_EXAMPLE: Blueprint = {
  schema_version: BLUEPRINT_SCHEMA_VERSION,
  vertical: "commerce",
  project_type: "retail_storefront",
  country: "BJ",
  currency: "XOF",
  locale: "fr-BJ",
  tenant: {
    name: "Wax Cadjehoun",
    slug: "cadjehoun-wax",
    city: "Cotonou",
    neighborhood: "Cadjehoun",
    country: "BJ",
    activity_description:
      "Boutique de tissus wax à Cadjehoun, livraison quartier, paiement Mobile Money.",
  },
  roles: ["owner", "cashier", "customer"],
  modules: {
    core: [...CORE],
    extra: ["stock", "whatsapp_orders", "invoicing", "delivery"],
  },
  catalog: [
    {
      sku: "wax-cadjehoun-6y",
      name: "Pagne wax 6 yards — motif Cadjehoun",
      price_xof: 12500,
      category: "tissus",
      available: true,
      unit: "pièce",
    },
    {
      sku: "wax-fidjrosse-6y",
      name: "Pagne wax 6 yards — motif Fidjrossè",
      price_xof: 8000,
      category: "tissus",
      available: true,
      unit: "pièce",
    },
    {
      sku: "livraison-quartier",
      name: "Livraison quartier",
      price_xof: 4000,
      category: "livraison",
      available: true,
      unit: "course",
    },
  ],
  integrations: [
    {
      category: "payment",
      mode: "sandbox",
      provider_candidates: ["geniuspay", "fedapay", "kkiapay"],
    },
    {
      category: "whatsapp",
      mode: "sandbox",
      provider_candidates: ["meta_cloud_api"],
    },
  ],
  seo: {
    title: "Wax Cadjehoun — tissus wax à Cotonou",
    description:
      "Boutique de pagnes wax à Cadjehoun. Commandez et payez en MTN MoMo ou Moov Money.",
    schema_org_type: "Store",
  },
  security_level: "standard",
  deployment_target: "preview",
  estimated_cost_credits: 8,
  requires_confirmation: [...CONFIRM],
  gates: { budget_credits_max: 20, contains_sensitive_data: false },
};

export const RESTAURANT_EXAMPLE: Blueprint = {
  schema_version: BLUEPRINT_SCHEMA_VERSION,
  vertical: "restaurant",
  project_type: "restaurant_ordering_platform",
  country: "BJ",
  currency: "XOF",
  locale: "fr-BJ",
  tenant: {
    name: "Maquis Fidjrossè",
    slug: "maquis-fidjrosse",
    city: "Cotonou",
    neighborhood: "Fidjrossè",
    country: "BJ",
    activity_description:
      "Maquis à Fidjrossè, menu QR, à emporter, paiement Mobile Money.",
  },
  roles: ["owner", "cashier", "kitchen", "customer"],
  modules: {
    core: [...CORE],
    extra: ["qr_menu", "kitchen_display", "takeaway", "delivery"],
  },
  catalog: [
    {
      sku: "poisson-braise",
      name: "Poisson braisé",
      price_xof: 4500,
      category: "grillades",
      available: true,
    },
    {
      sku: "alloco-poulet",
      name: "Poulet + alloco",
      price_xof: 3500,
      category: "grillades",
      available: true,
    },
    {
      sku: "jus-bissap",
      name: "Jus bissap",
      price_xof: 500,
      category: "boissons",
      available: true,
    },
  ],
  integrations: [
    {
      category: "payment",
      mode: "sandbox",
      provider_candidates: ["geniuspay"],
    },
  ],
  seo: {
    title: "Maquis Fidjrossè — poisson braisé à Cotonou",
    description:
      "Menu QR, commande et paiement Mobile Money au maquis de Fidjrossè.",
    schema_org_type: "Restaurant",
  },
  security_level: "standard",
  deployment_target: "preview",
  estimated_cost_credits: 9,
  requires_confirmation: [...CONFIRM],
  gates: { budget_credits_max: 20, contains_sensitive_data: false },
};

export const SERVICES_EXAMPLE: Blueprint = {
  schema_version: BLUEPRINT_SCHEMA_VERSION,
  vertical: "services",
  project_type: "appointment_service",
  country: "BJ",
  currency: "XOF",
  locale: "fr-BJ",
  tenant: {
    name: "Salon Awa Cadjehoun",
    slug: "salon-awa-cadjehoun",
    city: "Cotonou",
    neighborhood: "Cadjehoun",
    country: "BJ",
    activity_description:
      "Salon de coiffure à Cadjehoun, rendez-vous et rappels WhatsApp.",
  },
  roles: ["owner", "staff", "customer"],
  modules: {
    core: [...CORE],
    extra: ["agenda", "quotes", "invoices", "reminders"],
  },
  catalog: [
    {
      sku: "tresses-medium",
      name: "Tresses moyennes",
      price_xof: 8000,
      category: "coiffure",
      available: true,
    },
    {
      sku: "locking",
      name: "Locking",
      price_xof: 12000,
      category: "coiffure",
      available: true,
    },
    {
      sku: "soin-capillaire",
      name: "Soin capillaire",
      price_xof: 4000,
      category: "soins",
      available: true,
    },
  ],
  integrations: [
    {
      category: "payment",
      mode: "sandbox",
      provider_candidates: ["geniuspay"],
    },
    {
      category: "whatsapp",
      mode: "sandbox",
      provider_candidates: ["meta_cloud_api"],
    },
  ],
  seo: {
    title: "Salon Awa Cadjehoun — tresses et soins",
    description:
      "Prenez rendez-vous, payez en Mobile Money, recevez un rappel WhatsApp.",
    schema_org_type: "ProfessionalService",
  },
  security_level: "standard",
  deployment_target: "preview",
  estimated_cost_credits: 7,
  requires_confirmation: [...CONFIRM],
  gates: { budget_credits_max: 20, contains_sensitive_data: false },
};

export const ALL_EXAMPLES: Blueprint[] = [
  COMMERCE_EXAMPLE,
  RESTAURANT_EXAMPLE,
  SERVICES_EXAMPLE,
];
