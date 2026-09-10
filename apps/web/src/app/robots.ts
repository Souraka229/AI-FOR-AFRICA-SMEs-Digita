import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  const isPreview = process.env.VERCEL_ENV === "preview";
  const host = process.env.NEXT_PUBLIC_SITE_URL ?? "https://afrosite.app";

  if (isPreview) {
    return {
      rules: { userAgent: "*", disallow: "/" },
      host,
    };
  }

  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/studio", "/dashboard", "/api/"],
      },
    ],
    sitemap: `${host}/sitemap.xml`,
    host,
  };
}
