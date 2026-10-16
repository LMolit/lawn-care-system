import { describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  del: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
}));

vi.mock("next/headers", () => ({
  cookies: async () => ({ delete: mocks.del, set: vi.fn() }),
}));
vi.mock("next/navigation", () => ({ redirect: mocks.redirect }));

import { logoutAction } from "@/app/admin/(console)/actions";

describe("logoutAction", () => {
  it("deletes both session cookies and returns to the login page", async () => {
    await expect(logoutAction()).rejects.toThrow("NEXT_REDIRECT:/admin/login");
    expect(mocks.del).toHaveBeenCalledWith({
      name: "admin_at",
      path: "/admin",
    });
    expect(mocks.del).toHaveBeenCalledWith({
      name: "admin_rt",
      path: "/admin",
    });
  });
});
