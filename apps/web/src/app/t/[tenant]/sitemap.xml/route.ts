import { ALL_EXAMPLES } from "@afrosite/contracts";
import { ensureBlueprint } from "@/lib/demo/store";

export const dynamic = "force-dynamic";
export const dynamicParams = true;

export function generateStaticParams() {
  return ALL_EXAMPLES.map((item) => ({ tenant: item.tenant.slug }));
}

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ tenant: string }> },
) {
  const { tenant } = await params;
  const blueprint = ensureBlueprint(tenant);
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? "https://afrosite.app";
  const loc = `${base}/t/${blueprint.tenant.slug}`;
  const lastmod = new Date().toISOString();

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${loc}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}
