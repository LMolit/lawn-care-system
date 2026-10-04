import type { Metadata } from "next";
import { Fraunces, DM_Sans } from "next/font/google";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { QueryProvider } from "@/components/providers/QueryProvider";
import "./globals.css";
import { site } from "@/lib/site";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  display: "swap",
});

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
  display: "swap",
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";
const defaultTitle = "Liberty Lawn Care | Lawn Care in Batavia, IL";
const description =
  "Reliable lawn care in Batavia, Illinois and the surrounding area: mowing, aeration, seasonal cleanups, mulching, trimming, and fertilization.";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: defaultTitle,
    template: `%s | ${site.name}`,
  },
  description,
  openGraph: {
    type: "website",
    siteName: site.name,
    locale: "en_US",
    title: defaultTitle,
    description,
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      data-scroll-behavior="smooth"
      className={`${fraunces.variable} ${dmSans.variable}`}
    >
      <body className="flex min-h-screen flex-col">
        <QueryProvider>
          <Header />
          <div className="flex-1">{children}</div>
          <Footer />
        </QueryProvider>
      </body>
    </html>
  );
}
