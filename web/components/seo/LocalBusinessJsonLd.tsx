import { site } from "@/lib/site";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export function LocalBusinessJsonLd() {
  const data = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    name: site.name,
    url: siteUrl,
    image: `${siteUrl}/opengraph-image`,
    telephone: site.phoneHref.replace("tel:", ""),
    description: `Lawn care services in ${site.serviceArea}.`,
    areaServed: site.areas.map((city) => ({
      "@type": "City",
      name: city,
    })),
    address: {
      "@type": "PostalAddress",
      addressLocality: "Batavia",
      addressRegion: "IL",
      addressCountry: "US",
    },
    makesOffer: site.services.map((service) => ({
      "@type": "Offer",
      itemOffered: { "@type": "Service", name: service.name },
    })),
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(data).replace(/</g, "\\u003c"),
      }}
    />
  );
}
