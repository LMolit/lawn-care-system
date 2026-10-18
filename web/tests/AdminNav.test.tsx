import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const usePathname = vi.hoisted(() => vi.fn());
vi.mock("next/navigation", () => ({ usePathname }));

import { AdminNav } from "@/components/admin/AdminNav";

beforeEach(() => usePathname.mockReset());

describe("AdminNav", () => {
  it("marks the dashboard as current only on /admin itself", () => {
    usePathname.mockReturnValue("/admin");
    render(<AdminNav />);
    expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: "Reviews" })).not.toHaveAttribute(
      "aria-current",
    );
  });

  it("marks Reviews as current on its page", () => {
    usePathname.mockReturnValue("/admin/reviews");
    render(<AdminNav />);
    expect(screen.getByRole("link", { name: "Reviews" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: "Dashboard" })).not.toHaveAttribute(
      "aria-current",
    );
  });

  it("keeps Reviews current on pages beneath it", () => {
    usePathname.mockReturnValue("/admin/reviews/anything");
    render(<AdminNav />);
    expect(screen.getByRole("link", { name: "Reviews" })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });
});
