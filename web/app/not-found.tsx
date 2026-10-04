import { ButtonLink } from "@/components/ui/Button";

export default function NotFound() {
  return (
    <main className="bg-cream py-24 md:py-32">
      <div className="mx-auto max-w-xl px-5 text-center">
        <p className="text-sm font-semibold uppercase tracking-widest text-bark">
          Error 404
        </p>
        <h1 className="mt-3 text-4xl font-semibold md:text-5xl">
          Looks like this patch got missed
        </h1>
        <p className="mt-4 text-lg text-muted">
          The page you&apos;re looking for doesn&apos;t exist or has moved.
        </p>
        <div className="mt-8 flex flex-col justify-center gap-4 sm:flex-row">
          <ButtonLink href="/" size="lg">
            Back to home
          </ButtonLink>
          <ButtonLink href="/quote" variant="secondary" size="lg">
            Get a Free Quote
          </ButtonLink>
        </div>
      </div>
    </main>
  );
}
