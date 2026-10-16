import { cookies } from "next/headers";

export const ACCESS_COOKIE = "admin_at";
export const REFRESH_COOKIE = "admin_rt";

// The backend's access token lasts 30 minutes and the refresh token 30 days.
// The access cookie dies a minute early so a request never carries a token
// the backend has already rejected.
const ACCESS_MAX_AGE = 29 * 60;
const REFRESH_MAX_AGE = 30 * 24 * 60 * 60;

function cookieOptions() {
  return {
    httpOnly: true, // JavaScript on the page can never read these
    // Safari refuses Secure cookies on http://localhost, so only in production
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
    path: "/admin", // the browser sends them to admin URLs only
  };
}

export async function setSessionCookies(tokens: {
  access_token: string;
  refresh_token: string;
}) {
  const store = await cookies();
  store.set(ACCESS_COOKIE, tokens.access_token, {
    ...cookieOptions(),
    maxAge: ACCESS_MAX_AGE,
  });
  store.set(REFRESH_COOKIE, tokens.refresh_token, {
    ...cookieOptions(),
    maxAge: REFRESH_MAX_AGE,
  });
}

export async function clearSessionCookies() {
  const store = await cookies();
  store.delete({ name: ACCESS_COOKIE, path: "/admin" });
  store.delete({ name: REFRESH_COOKIE, path: "/admin" });
}
