import { Card } from "@/components/ui/Card";
import { StarRating } from "@/components/ui/StarRating";
import type { Review } from "@/lib/api/reviews";

export function ReviewCard({ review }: { review: Review }) {
  return (
    <Card className="flex h-full flex-col p-6">
      <StarRating rating={review.rating} />
      {review.comment && (
        <blockquote className="mt-4 flex-1 text-ink">
          &ldquo;{review.comment}&rdquo;
        </blockquote>
      )}
      <p className="mt-5 font-semibold text-forest-dark">{review.name}</p>
    </Card>
  );
}
