import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Tabs } from "@/components/admin/Tabs";

const items = [
  {
    label: "Pending",
    href: "/admin/reviews?status=pending",
    count: 3,
    active: true,
  },
  {
    label: "Approved",
    href: "/admin/reviews?status=approved",
    count: 0,
    active: false,
  },
];

describe("Tabs", () => {
  it("renders each tab as a link with its count", () => {
    render(<Tabs label="Review status" items={items} />);
    const pending = screen.getByRole("link", { name: /pending/i });
    expect(pending).toHaveAttribute("href", "/admin/reviews?status=pending");
    expect(pending).toHaveTextContent("3");
  });

  it("shows a zero count instead of hiding it", () => {
    render(<Tabs label="Review status" items={items} />);
    expect(screen.getByRole("link", { name: /approved/i })).toHaveTextContent(
      "0",
    );
  });

  it("marks only the active tab as the current page", () => {
    render(<Tabs label="Review status" items={items} />);
    expect(screen.getByRole("link", { name: /pending/i })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: /approved/i })).not.toHaveAttribute(
      "aria-current",
    );
  });
});
