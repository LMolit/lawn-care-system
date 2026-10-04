"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X, Phone } from "lucide-react";
import { site } from "@/lib/site";
import { ButtonLink } from "@/components/ui/Button";

export function MobileMenu() {
  const [open, setOpen] = useState(false);

  return (
    <div className="lg:hidden">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        aria-label={open ? "Close menu" : "Open menu"}
        className="rounded-lg p-2 text-forest-dark hover:bg-forest/10"
      >
        {open ? <X size={26} /> : <Menu size={26} />}
      </button>

      {open && (
        <div className="absolute left-0 right-0 top-full border-b border-line bg-cream px-5 pb-6 pt-2 shadow-lg">
          <nav className="flex flex-col" aria-label="Mobile">
            {site.nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className="border-b border-line py-4 text-lg font-medium text-forest-dark"
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="mt-5 flex flex-col gap-3">
            <ButtonLink href="/quote" size="lg" onClick={() => setOpen(false)}>
              Get a Free Quote
            </ButtonLink>
            <ButtonLink href={site.phoneHref} variant="secondary" size="lg">
              <Phone size={18} /> {site.phone}
            </ButtonLink>
          </div>
        </div>
      )}
    </div>
  );
}
