import type { Metadata } from "next";
import { ReviewModerationCard } from "@/components/admin/ReviewModerationCard";
import { Tabs } from "@/components/admin/Tabs";
import {
  REVIEW_STATUSES,
  REVIEW_STATUS_LABELS,
  fetchReviewCounts,
  fetchReviewsForModeration,
  type ReviewStatus,
} from "@/lib/admin/reviews";

export const metadata: Metadata = { title: "Reviews" };

const EMPTY_MESSAGE: Record<ReviewStatus, string> = {
  pending: "Nothing waiting. New reviews from your website show up here.",
  approved: "No reviews are showing on your website yet.",
  hidden: "No hidden reviews.",
};

// Anything unexpected in the URL falls back to the Pending tab.
function parseStatus(value: string | string[] | undefined): ReviewStatus {
  return REVIEW_STATUSES.find((s) => s === value) ?? "pending";
}

export default async function ReviewsPage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string | string[] }>;
}) {
  const status = parseStatus((await searchParams).status);
  const [counts, page] = await Promise.all([
    fetchReviewCounts(),
    fetchReviewsForModeration(status),
  ]);

  const tabs = REVIEW_STATUSES.map((s) => ({
    label: REVIEW_STATUS_LABELS[s],
    href: `/admin/reviews?status=${s}`,
    count: counts[s],
    active: s === status,
  }));

  return (
    <>
      <h1 className="text-3xl font-semibold">Reviews</h1>
      <p className="mt-2 max-w-prose text-muted">
        Customers leave reviews from your website. Approve the ones you want
        public and they appear on the site within about a minute. Hidden reviews
        are kept, never deleted, and you can approve them later.
      </p>

      <div className="mt-8">
        <Tabs label="Review status" items={tabs} />
      </div>

      {page.items.length === 0 ? (
        <p className="mt-8 text-muted">{EMPTY_MESSAGE[status]}</p>
      ) : (
        <>
          <ul className="mt-6 space-y-4">
            {page.items.map((review) => (
              <li key={review.id}>
                <ReviewModerationCard review={review} />
              </li>
            ))}
          </ul>
          {page.total > page.items.length && (
            <p className="mt-6 text-sm text-muted">
              Showing the newest {page.items.length} of {page.total}.
            </p>
          )}
        </>
      )}
    </>
  );
}
