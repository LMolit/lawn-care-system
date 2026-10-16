"use server";

import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { z } from "zod";
import { apiUrl } from "@/lib/admin/api";
import { setSessionCookies } from "@/lib/admin/session";

// `email` is handed back with every error so the form can refill the box.
// The password is never returned.
export type LoginState = { error?: string; email?: string };

// Same length caps as the backend, so oversized input never leaves the server.
const loginSchema = z.object({
  email: z.string().trim().min(1).max(254),
  password: z.string().min(1).max(1024),
});

export async function loginAction(
  _previous: LoginState,
  formData: FormData,
): Promise<LoginState> {
  const email = String(formData.get("email") ?? "").slice(0, 254);
  const fail = (error: string): LoginState => ({ error, email });

  const parsed = loginSchema.safeParse({
    email: formData.get("email"),
    password: formData.get("password"),
  });
  if (!parsed.success) return fail("Enter your email and password.");

  // The backend rate-limits per visitor IP. This request comes from our web
  // server, not through Cloudflare, so pass the real visitor's address along.
  // (Only trustworthy because all real traffic arrives through Cloudflare.)
  const visitorIp = (await headers()).get("cf-connecting-ip");

  let res: Response;
  try {
    res = await fetch(`${apiUrl()}/api/v1/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(visitorIp ? { "CF-Connecting-IP": visitorIp } : {}),
      },
      body: JSON.stringify(parsed.data),
      cache: "no-store",
    });
  } catch {
    return fail("Can't reach the server right now. Try again in a minute.");
  }

  if (res.status === 429) {
    const seconds = Number(res.headers.get("retry-after")) || 900;
    const minutes = Math.max(1, Math.ceil(seconds / 60));
    return fail(
      `Too many attempts. Try again in ${minutes} minute${minutes === 1 ? "" : "s"}.`,
    );
  }
  if (res.status === 401) return fail("Incorrect email or password.");
  // Never read or log the body of an error response: FastAPI's 422 echoes the input.
  if (!res.ok) return fail("Something went wrong. Try again in a minute.");

  await setSessionCookies(await res.json());

  // redirect() works by throwing, so it must stay outside any try/catch.
  redirect("/admin");
}
