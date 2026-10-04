import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import { QuoteForm } from "@/components/features/QuoteForm";
import { submitLead } from "@/lib/api/leads";
import { renderWithProviders } from "./utils";

// Replace the real network call with a fake we control
vi.mock("@/lib/api/leads", () => ({ submitLead: vi.fn() }));
const submitLeadMock = vi.mocked(submitLead);

beforeEach(() => {
  submitLeadMock.mockReset();
  submitLeadMock.mockResolvedValue({});
});

const submitButton = () =>
  screen.getByRole("button", { name: /get my free quote/i });

describe("QuoteForm", () => {
  it("shows errors for the required fields when submitted empty", async () => {
    const { user } = renderWithProviders(<QuoteForm />);

    await user.click(submitButton());

    expect(
      await screen.findByText("Please enter your name"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Please enter your property address"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/please fix the highlighted fields/i),
    ).toBeInTheDocument();
    expect(submitLeadMock).not.toHaveBeenCalled();
  });

  it("requires a phone number or an email", async () => {
    const { user } = renderWithProviders(<QuoteForm />);

    await user.type(screen.getByLabelText(/your name/i), "Jane Smith");
    await user.type(screen.getByLabelText(/property address/i), "12 Main St");
    await user.click(submitButton());

    expect(
      await screen.findByText(/phone number or an email/i),
    ).toBeInTheDocument();
    expect(submitLeadMock).not.toHaveBeenCalled();
  });

  it("blocks letters and formats the phone number as you type", async () => {
    const { user } = renderWithProviders(<QuoteForm />);
    const phone = screen.getByLabelText(/phone/i);

    await user.type(phone, "abc");
    expect(phone).toHaveValue("");

    await user.type(phone, "6305550123");
    expect(phone).toHaveValue("(630) 555-0123");
  });

  it("rejects an incomplete phone number", async () => {
    const { user } = renderWithProviders(<QuoteForm />);

    await user.type(screen.getByLabelText(/your name/i), "Jane Smith");
    await user.type(screen.getByLabelText(/property address/i), "12 Main St");
    await user.type(screen.getByLabelText(/phone/i), "63055");
    await user.click(submitButton());

    expect(
      await screen.findByText(/full 10-digit phone number/i),
    ).toBeInTheDocument();
    expect(submitLeadMock).not.toHaveBeenCalled();
  });

  it("rejects a malformed email", async () => {
    const { user } = renderWithProviders(<QuoteForm />);

    await user.type(screen.getByLabelText(/your name/i), "Jane Smith");
    await user.type(screen.getByLabelText(/property address/i), "12 Main St");
    await user.type(screen.getByLabelText(/email/i), "abc");
    await user.click(submitButton());

    expect(
      await screen.findByText(/email doesn't look right/i),
    ).toBeInTheDocument();
    expect(submitLeadMock).not.toHaveBeenCalled();
  });

  it("submits a valid form and shows the success message", async () => {
    const { user } = renderWithProviders(<QuoteForm />);

    await user.type(screen.getByLabelText(/your name/i), "Jane Smith");
    await user.type(screen.getByLabelText(/phone/i), "6305550123");
    await user.type(screen.getByLabelText(/property address/i), "12 Main St");
    await user.click(submitButton());

    expect(await screen.findByText(/we got your request/i)).toBeInTheDocument();
    expect(submitLeadMock).toHaveBeenCalledTimes(1);
    // Blank email and message are left out of the payload
    expect(submitLeadMock.mock.calls[0][0]).toEqual({
      name: "Jane Smith",
      address: "12 Main St",
      phone: "(630) 555-0123",
    });
  });

  it("shows an error banner when the server request fails", async () => {
    submitLeadMock.mockRejectedValue(new Error("boom"));
    const { user } = renderWithProviders(<QuoteForm />);

    await user.type(screen.getByLabelText(/your name/i), "Jane Smith");
    await user.type(screen.getByLabelText(/email/i), "jane@example.com");
    await user.type(screen.getByLabelText(/property address/i), "12 Main St");
    await user.click(submitButton());

    expect(
      await screen.findByText(/something went wrong/i),
    ).toBeInTheDocument();
    expect(screen.queryByText(/we got your request/i)).not.toBeInTheDocument();
  });

  it("pretends to succeed but sends nothing when the honeypot is filled", async () => {
    const { user } = renderWithProviders(<QuoteForm />);

    await user.type(screen.getByLabelText(/your name/i), "Spam Bot");
    await user.type(screen.getByLabelText(/email/i), "bot@example.com");
    await user.type(screen.getByLabelText(/property address/i), "1 Spam Ln");
    await user.type(screen.getByLabelText(/leave this field empty/i), "gotcha");
    await user.click(submitButton());

    expect(await screen.findByText(/we got your request/i)).toBeInTheDocument();
    expect(submitLeadMock).not.toHaveBeenCalled();
  });
});
