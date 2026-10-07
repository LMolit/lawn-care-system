import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Request


class RateLimitError(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        self.message = "Too many requests. Please try again later."


_all_limiters: list["RateLimiter"] = []


class RateLimiter:
    """Allows max_requests per window_seconds for each key (usually an IP)."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()
        _all_limiters.append(self)

    def hit(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            if len(self._hits) > 10_000:
                self._prune(now)
            hits = self._hits[key]
            while hits and now - hits[0] >= self.window:
                hits.popleft()
            if len(hits) >= self.max_requests:
                raise RateLimitError(int(self.window - (now - hits[0])) + 1)
            hits.append(now)

    def _prune(self, now: float) -> None:
        stale = [
            k for k, h in self._hits.items() if not h or now - h[-1] >= self.window
        ]
        for k in stale:
            del self._hits[k]

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


def reset_all() -> None:
    for limiter in _all_limiters:
        limiter.reset()


def client_ip(request: Request) -> str:
    # In production every request arrives through the Cloudflare tunnel, which sets
    # CF-Connecting-IP to the real visitor address. The fallback is for local dev.
    return request.headers.get("cf-connecting-ip") or (
        request.client.host if request.client else "unknown"
    )


def limit(limiter: RateLimiter):
    def dependency(request: Request) -> None:
        limiter.hit(client_ip(request))

    return dependency


# The actual limits, in one place
login_limit = limit(RateLimiter(max_requests=10, window_seconds=900))  # 10 per 15 min
refresh_limit = limit(RateLimiter(max_requests=30, window_seconds=900))
lead_limit = limit(RateLimiter(max_requests=5, window_seconds=3600))  # 5 per hour
review_limit = limit(RateLimiter(max_requests=3, window_seconds=3600))  # 3 per hour
