import { NextResponse, type NextRequest } from "next/server";
import {
  ACCESS_COOKIE,
  ACCESS_MAX_AGE,
  REFRESH_COOKIE,
  apiUrl,
  cookieOptions,
} from "@/lib/admin/shared";

const LOGIN_PATH = "/admin/login";

// Sends the visitor to the login page. Cookies are cleared only when the backend
// said the refresh token is no good (401). A network error or a 5xx says nothing
// about the cookies, so they stay and a later visit can recover.
function toLogin(request: NextRequest, clearCookies: boolean) {
  const response = NextResponse.redirect(new URL(LOGIN_PATH, request.url));
  if (clearCookies) {
    response.cookies.delete({ name: ACCESS_COOKIE, path: "/admin" });
    response.cookies.delete({ name: REFRESH_COOKIE, path: "/admin" });
  }
  return response;
}

// A convenience in front of the real gate. This only checks that cookies EXIST;
// it can't verify a token (that needs the JWT secret, which the web container
// must never have). adminFetch and the backend make the actual decision.
export async function proxy(request: NextRequest) {
  if (request.nextUrl.pathname === LOGIN_PATH) return NextResponse.next();
  if (request.cookies.get(ACCESS_COOKIE)) return NextResponse.next();

  const refreshToken = request.cookies.get(REFRESH_COOKIE)?.value;
  if (!refreshToken) return toLogin(request, false);

  // Same reason as the login action: this call doesn't pass through Cloudflare,
  // so hand the backend the real visitor's address for its rate limit.
  const visitorIp = request.headers.get("cf-connecting-ip");

  let res: Response;
  try {
    res = await fetch(`${apiUrl()}/api/v1/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(visitorIp ? { "CF-Connecting-IP": visitorIp } : {}),
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: "no-store",
    });
  } catch {
    return toLogin(request, false);
  }
  if (!res.ok) return toLogin(request, res.status === 401);

  let accessToken: string | undefined;
  try {
    accessToken = (await res.json()).access_token;
  } catch {
    accessToken = undefined;
  }
  if (!accessToken) return toLogin(request, false);

  // The page about to render is part of THIS request, which doesn't have the new
  // token yet, so put it on the request as well as sending it to the browser.
  request.cookies.set(ACCESS_COOKIE, accessToken);
  const response = NextResponse.next({ request });
  response.cookies.set(ACCESS_COOKIE, accessToken, {
    ...cookieOptions(),
    maxAge: ACCESS_MAX_AGE,
  });
  return response;
}

export const config = { matcher: ["/admin/:path*"] };
