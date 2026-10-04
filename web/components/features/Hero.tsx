import Image from "next/image";
import { MapPin, CalendarCheck, BadgeCheck } from "lucide-react";
import { site } from "@/lib/site";
import { ButtonLink } from "@/components/ui/Button";

const highlights = [
  { icon: BadgeCheck, label: "Free quotes" },
  { icon: MapPin, label: "Serving Batavia & nearby towns" },
  { icon: CalendarCheck, label: "Family-run and locally owned" },
];

export function Hero() {
  return (
    <section className="bg-linear-to-b from-cream to-[#eef3e8]">
      <div className="mx-auto flex max-w-4xl flex-col items-center px-5 py-16 text-center md:py-24">
        <div className="flex size-56 items-center justify-center rounded-full bg-white shadow-xl ring-1 ring-line md:size-72">
          <Image
            src="/logo.png"
            alt="Liberty Lawn Care mascot riding a green lawn mower"
            width={512}
            height={512}
            className="h-auto w-4/5"
            priority
          />
        </div>

        <p className="mt-10 text-sm font-semibold uppercase tracking-widest text-bark">
          Lawn care in Batavia, IL
        </p>

        <h1 className="mt-3 text-4xl font-semibold leading-tight md:text-6xl">
          For Life, Liberty and the{" "}
          <span className="text-forest">pursuit of a well kept lawn.</span>
        </h1>

        <p className="mt-6 max-w-2xl text-lg text-muted md:text-xl">
          {site.tagline} Mowing, aeration, cleanups, mulching, trimming, and
          fertilization from a local, family-run business.
        </p>

        <div className="mt-9 flex flex-col gap-4 sm:flex-row">
          <ButtonLink href="/quote" size="lg">
            Get a Free Quote
          </ButtonLink>
          <ButtonLink href="/#services" variant="secondary" size="lg">
            See Our Services
          </ButtonLink>
        </div>

        <ul className="mt-12 flex flex-col gap-4 text-ink sm:flex-row sm:gap-8">
          {highlights.map(({ icon: Icon, label }) => (
            <li
              key={label}
              className="flex items-center justify-center gap-2 font-medium"
            >
              <Icon size={20} className="text-forest" />
              {label}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
