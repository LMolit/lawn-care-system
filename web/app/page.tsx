import { Hero } from "@/components/features/Hero";
import { PhotoBand } from "@/components/features/PhotoBand";
import { Services } from "@/components/features/Services";
import { About } from "@/components/features/About";
import { Reviews } from "@/components/features/Reviews";
import { LocalBusinessJsonLd } from "@/components/seo/LocalBusinessJsonLd";

export default function HomePage() {
  return (
    <main>
      <LocalBusinessJsonLd />
      <Hero />
      <PhotoBand />
      <Services />
      <About />
      <Reviews />
    </main>
  );
}
