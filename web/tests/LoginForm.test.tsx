import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

const loginAction = vi.hoisted(() => vi.fn());
vi.mock("@/app/admin/login/actions", () => ({ loginAction }));

import { LoginForm } from "@/components/admin/LoginForm";

beforeEach(() => loginAction.mockReset());

async function signIn(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByLabelText(/email/i), "owner@example.com");
  await user.type(screen.getByLabelText(/password/i), "hunter2hunter2");
  await user.click(screen.getByRole("button", { name: /sign in/i }));
}

describe("LoginForm", () => {
  it("has labelled email and password fields", () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toHaveAttribute("type", "email");
    expect(screen.getByLabelText(/password/i)).toHaveAttribute(
      "type",
      "password",
    );
    expect(screen.getByRole("button", { name: /sign in/i })).toBeEnabled();
  });

  it("turns off auto-capitalization on the email (phone keyboards)", () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toHaveAttribute(
      "autocapitalize",
      "none",
    );
  });

  it("sends the typed values to the action", async () => {
    loginAction.mockResolvedValue({});
    render(<LoginForm />);
    await signIn(userEvent.setup());
    await waitFor(() => expect(loginAction).toHaveBeenCalledTimes(1));
    const formData = loginAction.mock.calls[0][1] as FormData;
    expect(formData.get("email")).toBe("owner@example.com");
    expect(formData.get("password")).toBe("hunter2hunter2");
  });

  it("shows the error the action returns, as an alert", async () => {
    loginAction.mockResolvedValue({ error: "Incorrect email or password." });
    render(<LoginForm />);
    await signIn(userEvent.setup());
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Incorrect email or password.",
    );
  });

  it("keeps the email but clears the password after a failed attempt", async () => {
    loginAction.mockResolvedValue({
      error: "Incorrect email or password.",
      email: "owner@example.com",
    });
    render(<LoginForm />);
    await signIn(userEvent.setup());
    await screen.findByRole("alert");
    await waitFor(() =>
      expect(screen.getByLabelText(/email/i)).toHaveValue("owner@example.com"),
    );
    expect(screen.getByLabelText(/password/i)).toHaveValue("");
  });
});
