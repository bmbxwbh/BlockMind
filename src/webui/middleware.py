"""WebUI middleware — rate limiting and request logging.

Uses only stdlib (dict + timestamps) for rate limiting.  No third-party
packages required.
"""

import logging
import time
from collections import defaultdict
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("blockmind.webui.middleware")

# ---------------------------------------------------------------------------
# Rate Limiter (stdlib only — dict + timestamps)
# ---------------------------------------------------------------------------

# Per-client (IP) sliding-window counters:  {key: [timestamps …]}
_rate_store: dict[str, list[float]] = defaultdict(list)

# Limits per path prefix
_LIMITS: list[tuple[str, int]] = [
    ("/api/login", 10),   # 10 req / 60 s
]
_DEFAULT_LIMIT = 60       # 60 req / 60 s for everything else
_WINDOW = 60.0            # seconds


def _get_limit(path: str) -> int:
    for prefix, limit in _LIMITS:
        if path.startswith(prefix):
            return limit
    return _DEFAULT_LIMIT


def _clean_old(key: str, now: float) -> None:
    cutoff = now - _WINDOW
    _rate_store[key] = [t for t in _rate_store[key] if t > cutoff]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory sliding-window rate limiter."""

    async def dispatch(self, request: Request, call_next: Callable):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        key = f"{client_ip}:{path}"
        now = time.time()
        limit = _get_limit(path)

        _clean_old(key, now)

        if len(_rate_store[key]) >= limit:
            logger.warning("Rate limit exceeded for %s on %s (%d/%d)", client_ip, path, len(_rate_store[key]), limit)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests", "retry_after": int(_WINDOW)},
            )

        _rate_store[key].append(now)
        return await call_next(request)


# ---------------------------------------------------------------------------
# Request Logging Middleware
# ---------------------------------------------------------------------------

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs method, path, status code and duration in ms for every request."""

    async def dispatch(self, request: Request, call_next: Callable):
        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)
        logger.info(
            "%s %s → %s (%.2f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
