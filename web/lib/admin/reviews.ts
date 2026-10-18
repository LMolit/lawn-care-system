import type { paths } from "@/lib/api/schema";
import { adminFetch } from "./api";

export type ModerationPage =
  paths["/api/v1/reviews/admin"]["get"]["responses"]["200"]["content"]["application/json"];
export type ModerationReview = ModerationPage["items"][number];
export type ReviewStatus = ModerationReview["status"];
export type ReviewCounts =
  paths["/api/v1/reviews/admin/counts"]["get"]["responses"]["200"]["content"]["application/json"];

// `satisfies` makes the compiler complain if this list drifts from the backend's.
export const REVIEW_STATUSES = [
  "pending",
  "approved",
  "hidden",
] as const satisfies readonly ReviewStatus[];

export const REVIEW_STATUS_LABELS: Record<ReviewStatus, string> = {
  pending: "Pending",
  approved: "Approved",
  hidden: "Hidden",
};

export const MODERATION_PAGE_SIZE = 50;

// None of these include the response body in an error: FastAPI's 422 echoes the input.

export async function fetchReviewCounts(): Promise<ReviewCounts> {
  const res = await adminFetch("/api/v1/reviews/admin/counts");
  if (!res.ok) throw new Error(`Failed to load review counts (${res.status})`);
  return res.json();
}

export async function fetchReviewsForModeration(
  status: ReviewStatus,
): Promise<ModerationPage> {
  const params = new URLSearchParams({
    status,
    page: "1",
    page_size: String(MODERATION_PAGE_SIZE),
  });
  const res = await adminFetch(`/api/v1/reviews/admin?${params}`);
  if (!res.ok) throw new Error(`Failed to load reviews (${res.status})`);
  return res.json();
}

export async function updateReviewStatus(id: string, status: ReviewStatus) {
  const res = await adminFetch(`/api/v1/reviews/${encodeURIComponent(id)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error(`Failed to update review (${res.status})`);
  return res.json();
}
