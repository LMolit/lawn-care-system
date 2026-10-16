// Pure constants and helpers with no next/headers import, so both the
// server-side helpers and proxy.ts can use them.

export const ACCESS_COOKIE = "admin_at";
export const REFRESH_COOKIE = "admin_rt";

// The backend's access token lasts 30 minutes and the refresh token 30 days.
// The access cookie dies a minute early so a request never carries a token
// the backend has already rejected.
export const ACCESS_MAX_AGE = 29 * 60;
export const REFRESH_MAX_AGE = 30 * 24 * 60 * 60;

export function cookieOptions() {
  return {
    httpOnly: true, // JavaScript on the page can never read these
    // Safari refuses Secure cookies on http://localhost, so only in production
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
    path: "/admin", // the browser sends them to admin URLs only
  };
}

// Falls back to the public URL for local development, the same way
// lib/api/reviews.ts does. Read at call time, not import time, so tests can change it.
export function apiUrl() {
  return process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL;
}
