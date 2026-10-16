// Server-side only. Falls back to the public URL for local development,
// the same way lib/api/reviews.ts does. Read at call time, not import time,
// so tests can change it.
export function apiUrl() {
  return process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL;
}
