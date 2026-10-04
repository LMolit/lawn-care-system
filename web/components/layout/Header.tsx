import Image from "next/image";
import Link from "next/link";
import { Phone } from "lucide-react";
import { site } from "@/lib/site";
import { ButtonLink } from "@/components/ui/Button";
import { MobileMenu } from "./MobileMenu";

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-line bg-cream/90 backdrop-blur">
      <div className="mx-auto flex h-24 max-w-6xl items-center justify-between px-5">
        <Link href="/" className="flex items-center gap-3">
          <Image
            src="/logo.png"
            alt=""
            width={64}
            height={64}
            className="h-14 w-auto md:h-[4.5rem]"
            priority
          />
          <span className="font-display text-xl font-semibold text-forest-dark">
            {site.name}
          </span>
        </Link>

        <nav className="hidden items-center gap-8 lg:flex" aria-label="Main">
          {site.nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="font-medium text-ink transition hover:text-forest"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-5 lg:flex">
          <a
            href={site.phoneHref}
            className="flex items-center gap-2 font-semibold text-forest-dark hover:text-forest"
          >
            <Phone size={18} />
            {site.phone}
          </a>
          <ButtonLink href="/quote">Free Quote</ButtonLink>
        </div>

        <MobileMenu />
      </div>
    </header>
  );
}
