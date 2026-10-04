import type { MetadataRoute } from "next";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: siteUrl, changeFrequency: "weekly", priority: 1 },
    { url: `${siteUrl}/quote`, changeFrequency: "yearly", priority: 0.8 },
    { url: `${siteUrl}/reviews/new`, changeFrequency: "yearly", priority: 0.4 },
  ];
}
