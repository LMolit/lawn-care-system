import { MessageSquareHeart } from "lucide-react";
import { fetchReviewsPage, type ReviewsPage } from "@/lib/api/reviews";
import { ReviewList } from "./ReviewList";
import { ButtonLink } from "@/components/ui/Button";

export async function Reviews() {
  let firstPage: ReviewsPage | null = null;
  try {
    firstPage = await fetchReviewsPage(1);
  } catch {
    // Backend unreachable: fall through to the empty state below
  }

  const hasReviews = firstPage !== null && firstPage.items.length > 0;

  return (
    <section id="reviews" className="scroll-mt-24 bg-cream py-20 md:py-28">
      <div className="mx-auto max-w-6xl px-5">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-bark">
            Reviews
          </p>
          <h2 className="mt-3 text-3xl font-semibold md:text-5xl">
            What our neighbors say
          </h2>
        </div>

        <div className="mt-14">
          {hasReviews ? (
            <ReviewList initialPage={firstPage!} />
          ) : (
            <div className="mx-auto flex max-w-md flex-col items-center text-center">
              <MessageSquareHeart size={44} className="text-forest" />
              <p className="mt-4 text-lg text-muted">
                Reviews are coming soon. Been happy with our work? We&apos;d
                love to hear about it.
              </p>
            </div>
          )}
        </div>

        <div className="mt-12 text-center">
          <ButtonLink href="/reviews/new" variant="secondary" size="lg">
            Leave a Review
          </ButtonLink>
        </div>
      </div>
    </section>
  );
}
