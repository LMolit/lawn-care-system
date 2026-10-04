import Image from "next/image";
import { site } from "@/lib/site";

export function PhotoBand() {
  return (
    <section className="relative isolate flex h-72 items-center justify-center overflow-hidden md:h-96">
      <Image
        src={site.images.band}
        alt=""
        fill
        sizes="100vw"
        className="-z-10 object-cover"
      />
      <div className="absolute inset-0 -z-10 bg-forest-dark/60" />
      <div className="px-5 text-center">
        <h2 className="text-3xl font-semibold !text-white md:text-5xl">
          Clean lines. Sharp edges. Every visit.
        </h2>
        <p className="mt-3 text-lg text-white/90">
          Proudly serving {site.serviceArea}
        </p>
      </div>
    </section>
  );
}
