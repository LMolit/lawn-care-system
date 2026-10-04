import Image from "next/image";
import { site } from "@/lib/site";
import { Card } from "@/components/ui/Card";
import { ButtonLink } from "@/components/ui/Button";

export function Services() {
  return (
    <section id="services" className="scroll-mt-24 bg-cream py-20 md:py-28">
      <div className="mx-auto max-w-6xl px-5">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-bark">
            What we do
          </p>
          <h2 className="mt-3 text-3xl font-semibold md:text-5xl">
            Everything your lawn needs, year-round
          </h2>
          <p className="mt-4 text-lg text-muted">
            From weekly mowing to seasonal projects, one local business handles
            it all.
          </p>
        </div>

        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {site.services.map((service) => (
            <Card
              key={service.name}
              className="group overflow-hidden transition duration-200 hover:-translate-y-1 hover:shadow-md"
            >
              <div className="relative aspect-4/3 overflow-hidden">
                <Image
                  src={service.image}
                  alt={`${service.name} by ${site.name}`}
                  fill
                  sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
                  className="object-cover transition duration-500 group-hover:scale-105"
                />
              </div>
              <div className="p-6">
                <h3 className="text-xl font-semibold">{service.name}</h3>
                <p className="mt-2 text-muted">{service.description}</p>
              </div>
            </Card>
          ))}
        </div>

        <div className="mt-12 text-center">
          <ButtonLink href="/quote" size="lg">
            Get a Free Quote
          </ButtonLink>
        </div>
      </div>
    </section>
  );
}
