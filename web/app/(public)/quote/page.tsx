import type { Metadata } from "next";
import { QuoteForm } from "@/components/features/QuoteForm";
import { Card } from "@/components/ui/Card";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Get a Free Quote",
  description: `Request a free lawn care quote from ${site.name} in ${site.serviceArea}.`,
};

export default function QuotePage() {
  return (
    <main className="bg-cream py-14 md:py-20">
      <div className="mx-auto max-w-3xl px-5">
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-bark">
            Free quote
          </p>
          <h1 className="mt-3 text-4xl font-semibold md:text-5xl">
            Let&apos;s talk about your lawn
          </h1>
          <p className="mt-4 text-lg text-muted">
            Tell us a little about your property and we&apos;ll get back to you
            with a quote.
          </p>
        </div>

        <Card className="mt-10 p-6 sm:p-10 md:p-14">
          <QuoteForm />
        </Card>
      </div>
    </main>
  );
}
