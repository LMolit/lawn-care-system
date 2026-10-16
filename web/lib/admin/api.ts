import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ACCESS_COOKIE, apiUrl } from "./shared";

export { apiUrl };

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
