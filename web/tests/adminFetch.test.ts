import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  cookieValue: undefined as string | undefined,
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
}));

vi.mock("next/headers", () => ({
  cookies: async () => ({
    get: (name: string) =>
      name === "admin_at" && mocks.cookieValue
        ? { value: mocks.cookieValue }
        : undefined,
  }),
}));
vi.mock("next/navigation", () => ({ redirect: mocks.redirect }));

import { adminFetch } from "@/lib/admin/api";

const fetchMock = vi.fn();

beforeEach(() => {
  mocks.cookieValue = "TOKEN";
  fetchMock.mockReset();
  fetchMock.mockResolvedValue(new Response("{}", { status: 200 }));
  vi.stubGlobal("fetch", fetchMock);
  vi.stubEnv("API_INTERNAL_URL", "http://backend.test");
});

describe("adminFetch", () => {
  it("sends the visitor to the login page when there is no session cookie", async () => {
    mocks.cookieValue = undefined;
    await expect(adminFetch("/api/v1/auth/me")).rejects.toThrow(
      "NEXT_REDIRECT:/admin/login",
    );
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("calls the backend with the bearer token and never caches", async () => {
    await adminFetch("/api/v1/auth/me");
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("http://backend.test/api/v1/auth/me");
    expect(init.headers.get("Authorization")).toBe("Bearer TOKEN");
    expect(init.cache).toBe("no-store");
  });

  it("does not let a caller override the Authorization header", async () => {
    await adminFetch("/api/v1/auth/me", {
      headers: { Authorization: "Bearer evil" },
    });
    expect(fetchMock.mock.calls[0][1].headers.get("Authorization")).toBe(
      "Bearer TOKEN",
    );
  });

  it("sends the visitor to the login page when the backend says 401", async () => {
    fetchMock.mockResolvedValue(new Response("{}", { status: 401 }));
    await expect(adminFetch("/api/v1/auth/me")).rejects.toThrow(
      "NEXT_REDIRECT:/admin/login",
    );
  });

  it("hands other statuses back to the caller", async () => {
    fetchMock.mockResolvedValue(new Response("{}", { status: 404 }));
    const res = await adminFetch("/api/v1/leads/nope");
    expect(res.status).toBe(404);
  });
});
