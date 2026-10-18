import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/app/admin/(console)/reviews/actions", () => ({
  setReviewStatusAction: vi.fn(),
}));

import { ReviewModerationCard } from "@/components/admin/ReviewModerationCard";
import type { ModerationReview } from "@/lib/admin/reviews";

const review: ModerationReview = {
  id: "3f2b8c1e-6a4d-4e0b-9c57-1d2e3f4a5b6c",
  customer_id: null,
  name: "Jane Homeowner",
  rating: 4,
  comment: "Great work",
  status: "pending",
  created_at: "2026-10-14T03:30:00Z", // 10:30 PM on Oct 13 in Chicago
  updated_at: "2026-10-14T03:30:00Z",
};

describe("ReviewModerationCard", () => {
  it("shows who wrote it, the stars, and the comment", () => {
    render(<ReviewModerationCard review={review} />);
    expect(screen.getByText("Jane Homeowner")).toBeInTheDocument();
    expect(
      screen.getByRole("img", { name: "4 out of 5 stars" }),
    ).toBeInTheDocument();
    expect(screen.getByText(/Great work/)).toBeInTheDocument();
  });

  it("shows the date in Chicago time, not UTC", () => {
    render(<ReviewModerationCard review={review} />);
    expect(screen.getByText("Oct 13, 2026")).toBeInTheDocument();
  });

  it("offers Approve and Hide for a pending review", () => {
    render(<ReviewModerationCard review={review} />);
    expect(
      screen.getByRole("button", { name: /approve/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /hide/i })).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /pending/i }),
    ).not.toBeInTheDocument();
  });

  it("offers only Hide for an approved review", () => {
    render(<ReviewModerationCard review={{ ...review, status: "approved" }} />);
    expect(screen.getByRole("button", { name: /hide/i })).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /approve/i }),
    ).not.toBeInTheDocument();
  });

  it("lets a hidden review be approved or moved back to pending", () => {
    render(<ReviewModerationCard review={{ ...review, status: "hidden" }} />);
    expect(
      screen.getByRole("button", { name: /approve/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /back to pending/i }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /hide/i }),
    ).not.toBeInTheDocument();
  });

  it("sends the review id and the new status with each button", () => {
    render(<ReviewModerationCard review={review} />);
    const form = screen
      .getByRole("button", { name: /approve/i })
      .closest("form")!;
    expect(
      form.querySelector<HTMLInputElement>('input[name="id"]')!.value,
    ).toBe(review.id);
    expect(
      form.querySelector<HTMLInputElement>('input[name="status"]')!.value,
    ).toBe("approved");
  });

  it("shows markup in a comment as plain text instead of running it", () => {
    const comment = "<img src=x onerror=alert(1)>";
    const { container } = render(
      <ReviewModerationCard review={{ ...review, comment }} />,
    );
    expect(screen.getByText(comment, { exact: false })).toBeInTheDocument();
    expect(container.querySelector("img")).toBeNull();
  });

  it("copes with a review that has no comment", () => {
    render(<ReviewModerationCard review={{ ...review, comment: null }} />);
    expect(screen.getByText("Jane Homeowner")).toBeInTheDocument();
    expect(screen.queryByRole("blockquote")).not.toBeInTheDocument();
  });
});
