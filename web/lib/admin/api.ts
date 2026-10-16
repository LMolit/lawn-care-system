import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ACCESS_COOKIE } from "./session";

// Server-side only. Falls back to the public URL for local development,
// the same way lib/api/reviews.ts does. Read at call time, not import time,
// so tests can change it.
export function apiUrl() {
  return process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL;
}

// Every admin read and write goes through here. No session or a rejected
// token means back to the login page. Other statuses are the caller's to handle.
export async function adminFetch(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const token = (await cookies()).get(ACCESS_COOKIE)?.value;
  if (!token) redirect("/admin/login");

  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${token}`); // set last, so callers can't override it

  const res = await fetch(`${apiUrl()}${path}`, {
    ...init,
    headers,
    cache: "no-store", // admin data is private and must always be fresh
  });
  if (res.status === 401) redirect("/admin/login");
  return res;
}
