export function MarketingJsonLd() {
  const data = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        name: "Afrosite",
        url: "https://afrosite.app",
        description:
          "Plateforme pour vendre, encaisser en Mobile Money et piloter une TPE au Bénin.",
        areaServed: "BJ",
        address: {
          "@type": "PostalAddress",
          addressLocality: "Cotonou",
          addressCountry: "BJ",
        },
      },
      {
        "@type": "SoftwareApplication",
        name: "Afrosite",
        applicationCategory: "BusinessApplication",
        operatingSystem: "Web",
        offers: {
          "@type": "Offer",
          priceCurrency: "XOF",
          price: "0",
        },
      },
    ],
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
