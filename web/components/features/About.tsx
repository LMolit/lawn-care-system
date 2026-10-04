import Image from "next/image";
import { Check } from "lucide-react";
import { site } from "@/lib/site";
import { ButtonLink } from "@/components/ui/Button";

const values = [
  "Reliable, season after season",
  "Fair, honest pricing",
  "Attention to detail, down to the edges",
];

export function About() {
  return (
    <section id="about" className="scroll-mt-24 bg-surface py-20 md:py-28">
      <div className="mx-auto grid max-w-7xl items-center gap-16 px-5 lg:grid-cols-2">
        <div className="relative pb-16" style={{ position: "relative" }}>
          <div className="relative aspect-4/5 w-11/12 overflow-hidden rounded-2xl shadow-lg">
            <Image
              src={site.images.about[0]}
              alt="Liberty Lawn Care at work on a lawn"
              fill
              sizes="(min-width: 1024px) 50vw, 100vw"
              className="object-cover"
            />
          </div>
          <div
            className="aspect-square w-1/2 overflow-hidden rounded-2xl border-4 border-surface shadow-xl sm:w-3/5"
            style={{ position: "absolute", bottom: 0, right: 0 }}
          >
            <Image
              src={site.images.about[1]}
              alt="A freshly finished lawn"
              fill
              sizes="(min-width: 1024px) 30vw, 60vw"
              className="object-cover"
            />
          </div>
        </div>

        <div>
          <h2 className="mt-3 text-3xl font-semibold md:text-5xl">
            Welcome to {site.name}
          </h2>
          <p className="mt-5 text-lg text-muted">
            We are a family owned and operated lawn care company proudly serving{" "}
            {site.serviceArea}. Started in 2014 and passed down from one brother
            to the next, {site.name} takes pride in providing residential and
            commercial clients with quality workmanship and exceptional customer
            service.
          </p>
          <p className="mt-4 text-lg text-muted">
            From weekly mowing to seasonal cleanups, every lawn gets the same
            care and attention to detail. We work closely with you from your
            free quote to the finished job to make sure you&apos;re fully
            satisfied.
          </p>
          <p className="mt-4 text-lg text-muted">
            Whether you need mowing, aeration, mulching, trimming, or
            fertilization, we have everything you need to turn your yard into a
            lawn you&apos;re proud of. We server Batavie, Geneva, Aurora, and
            the surrounding areas. Contact us today for your free quote.
          </p>

          <ul className="mt-6 space-y-3">
            {values.map((value) => (
              <li key={value} className="flex items-start gap-3 font-medium">
                <Check size={22} className="mt-0.5 shrink-0 text-forest" />
                {value}
              </li>
            ))}
          </ul>

          <ButtonLink href="/quote" size="lg" className="mt-9">
            Get Your Free Quote
          </ButtonLink>
        </div>
      </div>
    </section>
  );
}
