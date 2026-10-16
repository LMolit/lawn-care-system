import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// vi.hoisted: values the mock factories below need, created before the mocks run.
const mocks = vi.hoisted(() => ({
  setCookie: vi.fn(),
  requestHeaders: new Headers(),
  // Real redirect() throws to stop the function, so the fake does too.
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
}));

vi.mock("next/headers", () => ({
  cookies: async () => ({ set: mocks.setCookie, delete: vi.fn() }),
  headers: async () => mocks.requestHeaders,
}));
vi.mock("next/navigation", () => ({ redirect: mocks.redirect }));

import { loginAction } from "@/app/admin/login/actions";

const fetchMock = vi.fn();
const PASSWORD = "correct-horse-battery";

function form(email = "owner@example.com", password = PASSWORD) {
  const data = new FormData();
  data.set("email", email);
  data.set("password", password);
  return data;
}

function reply(
  body: unknown,
  status = 200,
  headers: Record<string, string> = {},
) {
  return new Response(JSON.stringify(body), { status, headers });
}

const TOKENS = {
  access_token: "ACCESS",
  refresh_token: "REFRESH",
  token_type: "bearer",
};

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
  vi.stubEnv("API_INTERNAL_URL", "http://backend.test");
  mocks.requestHeaders.delete("cf-connecting-ip");
  mocks.setCookie.mockClear();
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("loginAction", () => {
  it("stores both tokens in httpOnly cookies scoped to /admin, then redirects", async () => {
    fetchMock.mockResolvedValue(reply(TOKENS));
    await expect(loginAction({}, form())).rejects.toThrow(
      "NEXT_REDIRECT:/admin",
    );

    const expected = { httpOnly: true, sameSite: "lax", path: "/admin" };
    expect(mocks.setCookie).toHaveBeenCalledWith(
      "admin_at",
      "ACCESS",
      expect.objectContaining(expected),
    );
    expect(mocks.setCookie).toHaveBeenCalledWith(
      "admin_rt",
      "REFRESH",
      expect.objectContaining(expected),
    );
  });

  it("makes the access cookie expire before the token does", async () => {
    fetchMock.mockResolvedValue(reply(TOKENS));
    await expect(loginAction({}, form())).rejects.toThrow();
    const call = mocks.setCookie.mock.calls.find(
      ([name]) => name === "admin_at",
    );
    expect(call?.[2].maxAge).toBeLessThan(30 * 60); // the backend token lasts 30 minutes
  });

  it("marks cookies Secure in production only", async () => {
    fetchMock.mockImplementation(async () => reply(TOKENS));

    await expect(loginAction({}, form())).rejects.toThrow();
    expect(mocks.setCookie).toHaveBeenCalledWith(
      "admin_at",
      "ACCESS",
      expect.objectContaining({ secure: false }),
    );

    mocks.setCookie.mockClear();
    vi.stubEnv("NODE_ENV", "production");
    await expect(loginAction({}, form())).rejects.toThrow();
    expect(mocks.setCookie).toHaveBeenCalledWith(
      "admin_at",
      "ACCESS",
      expect.objectContaining({ secure: true }),
    );
  });

  it("calls the backend login endpoint with the credentials", async () => {
    fetchMock.mockResolvedValue(reply({ detail: "no" }, 401));
    await loginAction({}, form("owner@example.com"));
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("http://backend.test/api/v1/auth/login");
    expect(JSON.parse(init.body)).toEqual({
      email: "owner@example.com",
      password: PASSWORD,
    });
  });

  it("forwards the visitor's address so the backend rate-limits the right IP", async () => {
    mocks.requestHeaders.set("cf-connecting-ip", "203.0.113.7");
    fetchMock.mockResolvedValue(reply({ detail: "no" }, 401));
    await loginAction({}, form());
    expect(fetchMock.mock.calls[0][1].headers["CF-Connecting-IP"]).toBe(
      "203.0.113.7",
    );
  });

  it("says the same thing for any bad login and sets no cookies", async () => {
    fetchMock.mockResolvedValue(
      reply({ detail: "Incorrect email or password" }, 401),
    );
    const state = await loginAction({}, form());
    expect(state.error).toBe("Incorrect email or password.");
    expect(mocks.setCookie).not.toHaveBeenCalled();
  });

  it("tells the owner how long to wait when rate-limited", async () => {
    fetchMock.mockResolvedValue(
      reply({ error: "rate_limited" }, 429, { "Retry-After": "600" }),
    );
    const state = await loginAction({}, form());
    expect(state.error).toContain("10 minutes");
    expect(mocks.setCookie).not.toHaveBeenCalled();
  });

  it("returns a friendly error when the backend is unreachable", async () => {
    fetchMock.mockRejectedValue(new TypeError("fetch failed"));
    const state = await loginAction({}, form());
    expect(state.error).toMatch(/can't reach the server/i);
    expect(mocks.setCookie).not.toHaveBeenCalled();
  });

  it("never echoes a backend error body back (the 422 body contains the password)", async () => {
    fetchMock.mockResolvedValue(reply({ detail: [{ input: PASSWORD }] }, 422));
    const state = await loginAction({}, form());
    expect(state.error).toBeTruthy();
    expect(state.error).not.toContain(PASSWORD);
  });

  it("does not call the backend when a field is empty", async () => {
    const state = await loginAction({}, form("", ""));
    expect(state.error).toMatch(/enter your email and password/i);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
it("hands the typed email back on failure, never the password", async () => {
  fetchMock.mockResolvedValue(reply({ detail: "no" }, 401));
  const state = await loginAction({}, form("owner@example.com"));
  expect(state.email).toBe("owner@example.com");
  expect(JSON.stringify(state)).not.toContain(PASSWORD);
});
