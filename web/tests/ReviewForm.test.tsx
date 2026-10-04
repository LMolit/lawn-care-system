import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import { ReviewForm } from "@/components/features/ReviewForm";
import { submitReview } from "@/lib/api/reviews";
import { renderWithProviders } from "./utils";

vi.mock("@/lib/api/reviews", () => ({ submitReview: vi.fn() }));
const submitReviewMock = vi.mocked(submitReview);

beforeEach(() => {
  submitReviewMock.mockReset();
  submitReviewMock.mockResolvedValue({});
});

const submitButton = () =>
  screen.getByRole("button", { name: /submit my review/i });
const star = (n: number) =>
  screen.getByRole("radio", { name: new RegExp(`^${n} out of 5`) });

describe("ReviewForm", () => {
  it("requires a star rating and a name", async () => {
    const { user } = renderWithProviders(<ReviewForm />);

    await user.click(submitButton());

    expect(
      await screen.findByText("Please choose a star rating"),
    ).toBeInTheDocument();
    expect(screen.getByText("Please enter your name")).toBeInTheDocument();
    expect(submitReviewMock).not.toHaveBeenCalled();
  });

  it("selects a rating when a star is clicked", async () => {
    const { user } = renderWithProviders(<ReviewForm />);

    await user.click(star(4));

    expect(star(4)).toBeChecked();
    expect(star(5)).not.toBeChecked();
  });

  it("submits with just a rating and name, and explains approval", async () => {
    const { user } = renderWithProviders(<ReviewForm />);

    await user.click(star(4));
    await user.type(screen.getByLabelText(/your name/i), "Jane S.");
    await user.click(submitButton());

    expect(await screen.findByText(/once it.s approved/i)).toBeInTheDocument();
    expect(submitReviewMock.mock.calls[0][0]).toEqual({
      name: "Jane S.",
      rating: 4,
    });
  });

  it("includes the comment when one is written", async () => {
    const { user } = renderWithProviders(<ReviewForm />);

    await user.click(star(5));
    await user.type(screen.getByLabelText(/your name/i), "Jane S.");
    await user.type(screen.getByLabelText(/your review/i), "Great work!");
    await user.click(submitButton());

    expect(await screen.findByText(/once it.s approved/i)).toBeInTheDocument();
    expect(submitReviewMock.mock.calls[0][0]).toEqual({
      name: "Jane S.",
      rating: 5,
      comment: "Great work!",
    });
  });

  it("shows an error banner when the server request fails", async () => {
    submitReviewMock.mockRejectedValue(new Error("boom"));
    const { user } = renderWithProviders(<ReviewForm />);

    await user.click(star(3));
    await user.type(screen.getByLabelText(/your name/i), "Jane S.");
    await user.click(submitButton());

    expect(
      await screen.findByText(/something went wrong/i),
    ).toBeInTheDocument();
  });

  it("pretends to succeed but sends nothing when the honeypot is filled", async () => {
    const { user } = renderWithProviders(<ReviewForm />);

    await user.click(star(5));
    await user.type(screen.getByLabelText(/your name/i), "Spam Bot");
    await user.type(screen.getByLabelText(/leave this field empty/i), "gotcha");
    await user.click(submitButton());

    expect(await screen.findByText(/once it.s approved/i)).toBeInTheDocument();
    expect(submitReviewMock).not.toHaveBeenCalled();
  });
});
