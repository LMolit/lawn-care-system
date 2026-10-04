import Image from "next/image";
import Link from "next/link";
import { Phone, MapPin } from "lucide-react";
import { site } from "@/lib/site";

export function Footer() {
  return (
    <footer className="bg-forest-dark text-cream/80">
      <div className="mx-auto grid max-w-6xl gap-10 px-5 py-14 md:grid-cols-3">
        <div>
          <div className="flex items-center gap-3">
            <Image
              src="/logo.png"
              alt=""
              width={64}
              height={64}
              className="h-12 w-auto rounded-lg bg-cream p-1"
            />
            <span className="font-display text-xl font-semibold text-white">
              {site.name}
            </span>
          </div>
          <p className="mt-4 max-w-xs">{site.tagline}</p>
        </div>

        <div>
          <h2 className="font-display text-lg font-semibold !text-white">
            Services
          </h2>
          <ul className="mt-4 space-y-2">
            {site.services.map((service) => (
              <li key={service.name}>{service.name}</li>
            ))}
          </ul>
        </div>

        <div>
          <h2 className="font-display text-lg font-semibold !text-white">
            Get in touch
          </h2>
          <ul className="mt-4 space-y-3">
            <li className="flex items-center gap-2">
              <Phone size={18} className="text-gold" />
              <a href={site.phoneHref} className="hover:text-white">
                {site.phone}
              </a>
            </li>
            <li className="flex items-start gap-2">
              <MapPin size={18} className="mt-0.5 shrink-0 text-gold" />
              <span>Serving {site.areas.join(", ")}</span>
            </li>
            <li>
              <Link
                href="/quote"
                className="font-semibold text-gold hover:underline"
              >
                Request a free quote →
              </Link>
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-white/10 py-5 text-center text-sm">
        © {new Date().getFullYear()} {site.name}. All rights reserved.
      </div>
    </footer>
  );
}
