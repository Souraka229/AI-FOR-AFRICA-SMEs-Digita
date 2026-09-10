import { z } from "zod";

/** Schéma Blueprint JSON v0 — source unique front (Zod) / back (Pydantic miroir). */
export const BLUEPRINT_SCHEMA_VERSION = "0.1.0" as const;

export const VerticalSchema = z.enum(["commerce", "restaurant", "services"]);
export type Vertical = z.infer<typeof VerticalSchema>;

export const RoleSchema = z.enum([
  "owner",
  "cashier",
  "kitchen",
  "customer",
  "staff",
]);
export type Role = z.infer<typeof RoleSchema>;

export const CoreModuleSchema = z.enum([
  "onboarding",
  "catalog",
  "orders",
  "payments",
  "reconciliation",
  "crm",
  "dashboard",
  "notifications",
  "exports",
]);

export const CommerceExtraModuleSchema = z.enum([
  "stock",
  "whatsapp_orders",
  "invoicing",
  "delivery",
]);

export const RestaurantExtraModuleSchema = z.enum([
  "qr_menu",
  "kitchen_display",
  "tables",
  "takeaway",
  "delivery",
]);

export const ServicesExtraModuleSchema = z.enum([
  "agenda",
  "quotes",
  "invoices",
  "reminders",
]);

export const ExtraModuleSchema = z.union([
  CommerceExtraModuleSchema,
  RestaurantExtraModuleSchema,
  ServicesExtraModuleSchema,
]);

export const PaymentProviderIdSchema = z.enum([
  "geniuspay",
  "fedapay",
  "kkiapay",
  "cinetpay",
]);

export const IntegrationSchema = z.object({
  category: z.enum(["payment", "whatsapp", "sms", "email"]),
  mode: z.enum(["sandbox", "production"]),
  provider_candidates: z.array(z.string()).min(1),
});

export const CatalogItemSchema = z.object({
  sku: z.string().min(1),
  name: z.string().min(1),
  price_xof: z.number().int().nonnegative(),
  category: z.string().min(1),
  available: z.boolean(),
  unit: z.string().optional(),
});

export const TenantSchema = z.object({
  name: z.string().min(2),
  slug: z
    .string()
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, "slug kebab-case ascii"),
  city: z.string().min(2),
  neighborhood: z.string().min(1),
  country: z.literal("BJ"),
  phone: z.string().optional(),
  activity_description: z.string().min(8),
});

export const SeoSchema = z.object({
  title: z.string().min(8).max(70),
  description: z.string().min(20).max(170),
  schema_org_type: z.enum([
    "LocalBusiness",
    "Store",
    "Restaurant",
    "ProfessionalService",
  ]),
});

export const ConfirmationActionSchema = z.enum([
  "production_deploy",
  "payment_live_activation",
  "database_deletion",
  "mass_email",
  "access_change",
]);

export const BlueprintDraftSchema = z.object({
    schema_version: z.literal(BLUEPRINT_SCHEMA_VERSION),
    vertical: VerticalSchema,
    project_type: z.string().min(4),
    country: z.literal("BJ"),
    currency: z.literal("XOF"),
    locale: z.literal("fr-BJ"),
    tenant: TenantSchema,
    roles: z.array(RoleSchema).min(2),
    modules: z.object({
      core: z.array(CoreModuleSchema).min(5),
      extra: z.array(ExtraModuleSchema),
    }),
    catalog: z.array(CatalogItemSchema).min(1).max(40),
    integrations: z.array(IntegrationSchema).min(1),
    seo: SeoSchema,
    security_level: z.enum(["standard", "elevated"]),
    deployment_target: z.enum(["preview", "production"]),
    estimated_cost_credits: z.number().int().nonnegative().max(100),
    requires_confirmation: z.array(ConfirmationActionSchema).min(3),
    gates: z.object({
      budget_credits_max: z.number().int().positive(),
      contains_sensitive_data: z.boolean(),
    }),
  });

export const BlueprintSchema = BlueprintDraftSchema.superRefine((value, ctx) => {
    if (value.estimated_cost_credits > value.gates.budget_credits_max) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["estimated_cost_credits"],
        message: "budget IA au-dessus du plafond (gate 1)",
      });
    }
    if (value.gates.contains_sensitive_data) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["gates", "contains_sensitive_data"],
        message: "données sensibles détectées dans le prompt (gate 1)",
      });
    }
    if (value.currency !== "XOF" || value.country !== "BJ") {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["currency"],
        message: "MVP Bénin : BJ / XOF uniquement",
      });
    }
    if (
      value.vertical === "restaurant" &&
      !value.roles.includes("kitchen")
    ) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["roles"],
        message: "le blueprint restaurant exige le rôle kitchen",
      });
    }
  });

export type Blueprint = z.infer<typeof BlueprintSchema>;

export const IntentSchema = z.object({
  raw_prompt: z.string().min(8),
  vertical: VerticalSchema,
  confidence: z.number().min(0).max(1),
  city: z.string(),
  neighborhood: z.string(),
  wants_mobile_money: z.boolean(),
  wants_delivery: z.boolean(),
  wants_whatsapp: z.boolean(),
  activity_summary: z.string(),
  suggested_name: z.string(),
  flags: z.array(z.string()),
});
export type Intent = z.infer<typeof IntentSchema>;

export const Gate1ResultSchema = z.object({
  passed: z.boolean(),
  errors: z.array(z.string()),
  credits: z.number().int().nonnegative(),
  budget_credits_max: z.number().int().positive(),
});
export type Gate1Result = z.infer<typeof Gate1ResultSchema>;

export const VisionCritiqueSchema = z.object({
  passed: z.boolean(),
  score: z.number().int().min(0).max(100),
  summary: z.string().min(8).max(500),
  issues: z.array(
    z.object({
      severity: z.enum(["low", "medium", "high"]),
      component: z.string().min(1),
      description: z.string().min(4),
      suggestion: z.string().min(4),
    }),
  ).max(20),
});
export type VisionCritique = z.infer<typeof VisionCritiqueSchema>;

export function parseBlueprint(input: unknown): Blueprint {
  return BlueprintSchema.parse(input);
}

export function safeParseBlueprint(input: unknown) {
  return BlueprintSchema.safeParse(input);
}
