import { beforeEach, describe, expect, it, vi } from "vitest";

const adminFetch = vi.hoisted(() => vi.fn());
vi.mock("@/lib/admin/api", () => ({ adminFetch }));

import {
  fetchReviewCounts,
  fetchReviewsForModeration,
  updateReviewStatus,
} from "@/lib/admin/reviews";

const ID = "3f2b8c1e-6a4d-4e0b-9c57-1d2e3f4a5b6c";

function reply(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status });
}

beforeEach(() => adminFetch.mockReset());

describe("review helpers", () => {
  it("loads the counts for the tab badges", async () => {
    adminFetch.mockResolvedValue(reply({ pending: 2, approved: 5, hidden: 1 }));
    expect(await fetchReviewCounts()).toEqual({
      pending: 2,
      approved: 5,
      hidden: 1,
    });
    expect(adminFetch).toHaveBeenCalledWith("/api/v1/reviews/admin/counts");
  });

  it("asks the backend for one status at a time", async () => {
    adminFetch.mockResolvedValue(
      reply({ items: [], total: 0, page: 1, page_size: 50 }),
    );
    await fetchReviewsForModeration("hidden");
    const url = adminFetch.mock.calls[0][0] as string;
    expect(url).toContain("/api/v1/reviews/admin?");
    expect(url).toContain("status=hidden");
    expect(url).toContain("page_size=50");
  });

  it("changes a review's status with a PATCH", async () => {
    adminFetch.mockResolvedValue(reply({ id: ID, status: "approved" }));
    await updateReviewStatus(ID, "approved");
    const [url, init] = adminFetch.mock.calls[0];
    expect(url).toBe(`/api/v1/reviews/${ID}`);
    expect(init.method).toBe("PATCH");
    expect(JSON.parse(init.body)).toEqual({ status: "approved" });
  });

  it("fails loudly without leaking the response body", async () => {
    adminFetch.mockResolvedValue(reply({ detail: "internal details" }, 500));
    const error = await fetchReviewCounts().catch((e: Error) => e);
    expect(error).toBeInstanceOf(Error);
    expect((error as Error).message).toContain("500");
    expect((error as Error).message).not.toContain("internal details");
  });
});
