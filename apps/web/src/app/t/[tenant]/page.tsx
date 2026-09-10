import type { Metadata } from "next";
import { connection } from "next/server";
import { AppNav } from "@/components/app-nav";
import { TenantCheckout } from "@/components/tenant-checkout";
import { Money } from "@/components/money";
import { ALL_EXAMPLES, type Blueprint } from "@afrosite/contracts";
import { ensureBlueprint } from "@/lib/demo/store";

export const dynamic = "force-dynamic";
export const dynamicParams = true;

export function generateStaticParams() {
  return ALL_EXAMPLES.map((item) => ({ tenant: item.tenant.slug }));
}

function resolveBlueprint(slug: string): Blueprint {
  return ensureBlueprint(slug);
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ tenant: string }>;
}): Promise<Metadata> {
  const { tenant } = await params;
  const blueprint = resolveBlueprint(tenant);
  return {
    title: blueprint.seo.title,
    description: blueprint.seo.description,
    alternates: { canonical: `/t/${blueprint.tenant.slug}` },
    openGraph: {
      title: blueprint.seo.title,
      description: blueprint.seo.description,
      locale: "fr_FR",
    },
    twitter: {
      card: "summary",
      title: blueprint.seo.title,
      description: blueprint.seo.description,
    },
    robots: { index: false, follow: false },
  };
}

export default async function TenantPage({
  params,
}: {
  params: Promise<{ tenant: string }>;
}) {
  await connection();
  const { tenant } = await params;
  const blueprint = resolveBlueprint(tenant);

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": blueprint.seo.schema_org_type,
        name: blueprint.tenant.name,
        description: blueprint.seo.description,
        address: {
          "@type": "PostalAddress",
          addressLocality: `${blueprint.tenant.neighborhood}, ${blueprint.tenant.city}`,
          addressCountry: "BJ",
        },
        currenciesAccepted: "XOF",
        paymentAccepted: "Mobile Money",
      },
      {
        "@type": "ItemList",
        name: `Catalogue — ${blueprint.tenant.name}`,
        itemListElement: blueprint.catalog.map((item, index) => ({
          "@type": "ListItem",
          position: index + 1,
          item: {
            "@type": "Product",
            name: item.name,
            sku: item.sku,
            category: item.category,
            offers: {
              "@type": "Offer",
              price: item.price_xof,
              priceCurrency: "XOF",
              availability: item.available
                ? "https://schema.org/InStock"
                : "https://schema.org/OutOfStock",
            },
          },
        })),
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <AppNav current="boutique" tenantSlug={blueprint.tenant.slug} />
      <main className="mx-auto grid max-w-6xl gap-8 px-4 py-8 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.9fr)]">
        <section>
          <p className="text-sm text-muted-foreground">
            {blueprint.tenant.neighborhood}, {blueprint.tenant.city}
          </p>
          <h1 className="mt-1 font-heading text-4xl font-semibold tracking-tight">
            {blueprint.tenant.name}
          </h1>
          <p className="mt-2 max-w-xl text-muted-foreground">
            {blueprint.tenant.activity_description}
          </p>
          <ul className="mt-8 space-y-3">
            {blueprint.catalog.map((item) => (
              <li
                key={item.sku}
                className="flex items-center justify-between rounded-xl border border-border px-4 py-3"
              >
                <div>
                  <p className="font-medium">{item.name}</p>
                  <p className="text-xs text-muted-foreground">{item.category}</p>
                </div>
                <Money className="text-lg font-semibold" amountXof={item.price_xof} />
              </li>
            ))}
          </ul>
        </section>
        <TenantCheckout
          tenantSlug={blueprint.tenant.slug}
          items={blueprint.catalog.map((item) => ({
            sku: item.sku,
            name: item.name,
            price_xof: item.price_xof,
          }))}
        />
      </main>
    </>
  );
}
