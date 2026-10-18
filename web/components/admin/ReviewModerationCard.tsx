import { setReviewStatusAction } from "@/app/admin/(console)/reviews/actions";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { StarRating } from "@/components/ui/StarRating";
import { formatDate } from "@/lib/admin/format";
import {
  REVIEW_STATUS_LABELS,
  type ModerationReview,
  type ReviewStatus,
} from "@/lib/admin/reviews";
import { Badge } from "./Badge";

const statusTone = {
  pending: "warning",
  approved: "success",
  hidden: "neutral",
} as const;

function StatusButton({
  review,
  status,
  label,
  ariaLabel,
  variant = "secondary",
}: {
  review: ModerationReview;
  status: ReviewStatus;
  label: string;
  ariaLabel: string;
  variant?: "primary" | "secondary";
}) {
  return (
    <form action={setReviewStatusAction}>
      <input type="hidden" name="id" value={review.id} />
      <input type="hidden" name="status" value={status} />
      <Button type="submit" variant={variant} aria-label={ariaLabel}>
        {label}
      </Button>
    </form>
  );
}

export function ReviewModerationCard({ review }: { review: ModerationReview }) {
  const approve = (
    <StatusButton
      review={review}
      status="approved"
      label="Approve"
      ariaLabel={`Approve review from ${review.name}`}
      variant="primary"
    />
  );
  const hide = (
    <StatusButton
      review={review}
      status="hidden"
      label="Hide"
      ariaLabel={`Hide review from ${review.name}`}
    />
  );
  const backToPending = (
    <StatusButton
      review={review}
      status="pending"
      label="Back to pending"
      ariaLabel={`Move review from ${review.name} back to pending`}
    />
  );

  return (
    <Card className="p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <StarRating rating={review.rating} />
        <div className="flex items-center gap-3">
          <Badge tone={statusTone[review.status]}>
            {REVIEW_STATUS_LABELS[review.status]}
          </Badge>
          <span className="text-sm text-muted">
            {formatDate(review.created_at)}
          </span>
        </div>
      </div>

      {/* Rendered as plain text only. whitespace-pre-wrap keeps the customer's line breaks. */}
      {review.comment && (
        <blockquote className="mt-4 whitespace-pre-wrap break-words text-ink">
          {review.comment}
        </blockquote>
      )}
      <p className="mt-4 font-semibold text-forest-dark">{review.name}</p>

      <div className="mt-5 flex flex-wrap gap-3">
        {review.status === "pending" && (
          <>
            {approve}
            {hide}
          </>
        )}
        {review.status === "approved" && hide}
        {review.status === "hidden" && (
          <>
            {approve}
            {backToPending}
          </>
        )}
      </div>
    </Card>
  );
}
