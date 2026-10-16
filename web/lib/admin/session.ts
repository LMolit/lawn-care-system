import { cookies } from "next/headers";
import {
  ACCESS_COOKIE,
  ACCESS_MAX_AGE,
  REFRESH_COOKIE,
  REFRESH_MAX_AGE,
  cookieOptions,
} from "./shared";

export { ACCESS_COOKIE, REFRESH_COOKIE };

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
