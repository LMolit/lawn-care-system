import type { Metadata } from "next";
import { ReviewForm } from "@/components/features/ReviewForm";
import { Card } from "@/components/ui/Card";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Leave a Review",
  description: `Share your experience with ${site.name}.`,
};

export default function NewReviewPage() {
  return (
    <main className="bg-cream py-14 md:py-20">
      <div className="mx-auto max-w-3xl px-5">
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-bark">
            Reviews
          </p>
          <h1 className="mt-3 text-4xl font-semibold md:text-5xl">
            How did we do?
          </h1>
          <p className="mt-4 text-lg text-muted">
            Your feedback helps your neighbors choose a lawn care company they
            can trust.
          </p>
        </div>

        <Card className="mt-10 p-6 sm:p-10 md:p-14">
          <ReviewForm />
        </Card>
      </div>
    </main>
  );
}
