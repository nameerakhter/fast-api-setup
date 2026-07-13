"""Simple in-memory rate limiter (Redis optional later). Skipped in development."""

from __future__ import annotations

import time
from collections import defaultdict, deque

from config import get_settings


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        settings = get_settings()
        if settings["app_env"] == "development":
            return True

        window_s = settings["rate_limit_window_ms"] / 1000.0
        limit = settings["rate_limit_max_requests"]
        now = time.monotonic()
        bucket = self._hits[key]
        while bucket and now - bucket[0] > window_s:
            bucket.popleft()
        if len(bucket) >= limit:
            return False
        bucket.append(now)
        return True


rate_limiter = InMemoryRateLimiter()
