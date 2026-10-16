import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { config, proxy } from "@/proxy";

const fetchMock = vi.fn();

function request(
  path: string,
  cookies: Record<string, string> = {},
  headers: Record<string, string> = {},
) {
  const cookie = Object.entries(cookies)
    .map(([name, value]) => `${name}=${value}`)
    .join("; ");
  return new NextRequest(`http://localhost:3000${path}`, {
    headers: { ...(cookie ? { cookie } : {}), ...headers },
  });
}

function reply(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status });
}

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
  vi.stubEnv("API_INTERNAL_URL", "http://backend.test");
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("proxy", () => {
  it("lets a request with a session cookie through without calling the backend", async () => {
    const response = await proxy(request("/admin", { admin_at: "ACCESS" }));
    expect(response.status).toBe(200);
    expect(response.headers.get("location")).toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("never interferes with the login page, even with only a refresh cookie", async () => {
    const response = await proxy(
      request("/admin/login", { admin_rt: "REFRESH" }),
    );
    expect(response.status).toBe(200);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("sends visitors with no cookies to the login page", async () => {
    const response = await proxy(request("/admin/customers"));
    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe(
      "http://localhost:3000/admin/login",
    );
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("quietly gets a new access token when only the refresh cookie is left", async () => {
    fetchMock.mockResolvedValue(
      reply({ access_token: "NEW", token_type: "bearer" }),
    );
    const response = await proxy(request("/admin", { admin_rt: "REFRESH" }));

    expect(response.headers.get("location")).toBeNull(); // not redirected
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("http://backend.test/api/v1/auth/refresh");
    expect(JSON.parse(init.body)).toEqual({ refresh_token: "REFRESH" });

    const setCookie = response.headers.get("set-cookie") ?? "";
    expect(setCookie).toContain("admin_at=NEW");
    expect(setCookie).toContain("HttpOnly");
    expect(setCookie).toContain("Path=/admin");
  });

  it("forwards the visitor's address so the backend rate-limits the right IP", async () => {
    fetchMock.mockResolvedValue(reply({ access_token: "NEW" }));
    await proxy(
      request(
        "/admin",
        { admin_rt: "REFRESH" },
        { "cf-connecting-ip": "203.0.113.7" },
      ),
    );
    expect(fetchMock.mock.calls[0][1].headers["CF-Connecting-IP"]).toBe(
      "203.0.113.7",
    );
  });

  it("clears both cookies when the backend rejects the refresh token", async () => {
    fetchMock.mockResolvedValue(
      reply({ detail: "Token has been revoked" }, 401),
    );
    const response = await proxy(request("/admin", { admin_rt: "REFRESH" }));

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe(
      "http://localhost:3000/admin/login",
    );
    const setCookie = response.headers.get("set-cookie") ?? "";
    expect(setCookie).toMatch(/admin_at=;/);
    expect(setCookie).toMatch(/admin_rt=;/);
  });

  it("keeps the cookies when the backend can't be reached", async () => {
    fetchMock.mockRejectedValue(new TypeError("fetch failed"));
    const response = await proxy(request("/admin", { admin_rt: "REFRESH" }));
    expect(response.status).toBe(307);
    expect(response.headers.get("set-cookie")).toBeNull();
  });

  it("keeps the cookies when the backend has a server error", async () => {
    fetchMock.mockResolvedValue(reply({}, 500));
    const response = await proxy(request("/admin", { admin_rt: "REFRESH" }));
    expect(response.status).toBe(307);
    expect(response.headers.get("set-cookie")).toBeNull();
  });

  it("only runs for admin URLs", () => {
    expect(config.matcher).toEqual(["/admin/:path*"]);
  });
});
