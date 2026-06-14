from __future__ import annotations

from typing import Optional


class IpApiError(Exception):
    """Base error for all ip-api.io client failures."""

    def __init__(self, message: str, status_code: Optional[int] = None, body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class AuthenticationError(IpApiError):
    """HTTP 401/403 — missing or invalid API key."""


class RateLimitError(IpApiError):
    """HTTP 429 — quota exhausted.

    Exposes the x-ratelimit-* response headers; ``reset`` is the unix
    timestamp when the quota renews. The client never retries.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 429,
        body: Optional[str] = None,
        limit: Optional[int] = None,
        remaining: Optional[int] = None,
        reset: Optional[int] = None,
    ):
        super().__init__(message, status_code, body)
        self.limit = limit
        self.remaining = remaining
        self.reset = reset


class InvalidRequestError(IpApiError):
    """HTTP 400/404/422 — malformed input or unknown resource."""


class ServerError(IpApiError):
    """HTTP 5xx — ip-api.io server-side failure."""
