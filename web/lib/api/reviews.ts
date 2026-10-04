import type { paths } from "./schema";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const REVIEWS_PAGE_SIZE = 6;

// ---------- Reading reviews (home page + infinite scroll) ----------

export type ReviewsPage =
  paths["/api/v1/reviews"]["get"]["responses"]["200"]["content"]["application/json"];

export type Review = ReviewsPage["items"][number];

export async function fetchReviewsPage(page: number): Promise<ReviewsPage> {
  const res = await fetch(
    `${API_URL}/api/v1/reviews?page=${page}&page_size=${REVIEWS_PAGE_SIZE}`,
    { next: { revalidate: 60 } },
  );
  if (!res.ok) throw new Error(`Failed to load reviews (${res.status})`);
  return res.json();
}

// ---------- Submitting a review (review form) ----------

export type ReviewInput =
  paths["/api/v1/reviews"]["post"]["requestBody"]["content"]["application/json"];

export async function submitReview(review: ReviewInput) {
  const res = await fetch(`${API_URL}/api/v1/reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(review),
  });
  if (!res.ok) throw new Error(`Failed to submit review (${res.status})`);
  return res.json();
}
