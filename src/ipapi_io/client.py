from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional, Sequence

from .errors import (
    AuthenticationError,
    InvalidRequestError,
    IpApiError,
    RateLimitError,
    ServerError,
)
from .version import USER_AGENT

MAX_BATCH_SIZE = 100


def _quote(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def _header_int(headers: Any, name: str) -> Optional[int]:
    value = headers.get(name)
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


class IpApiClient:
    """Client for the ip-api.io IP intelligence and email validation API.

    Args:
        api_key: optional API key (free key at https://ip-api.io). Sent as the
            ``api_key`` query parameter. Anonymous requests work with IP-based limits.
        base_url: API origin, override for testing.
        timeout: per-request timeout in seconds.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://ip-api.io",
        timeout: float = 10.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # -- IP intelligence ----------------------------------------------------

    def lookup(self, ip: Optional[str] = None) -> Any:
        """Geolocation + threat intelligence for an IP (or the caller's IP)."""
        path = f"/api/v1/ip/{_quote(ip)}" if ip else "/api/v1/ip"
        return self._request("GET", path)

    def lookup_batch(self, ips: Sequence[str]) -> Any:
        """Look up to 100 IP addresses in a single request."""
        self._check_batch(ips, "ips")
        return self._request("POST", "/api/v1/ip/batch", body={"ips": list(ips)})

    def ip_reputation(self, ip: str) -> Any:
        return self._request("GET", f"/api/v1/ip-reputation/{_quote(ip)}")

    def tor_check(self, ip: str) -> Any:
        return self._request("GET", f"/api/v1/tor/{_quote(ip)}")

    def asn(self, ip: str) -> Any:
        return self._request("GET", f"/api/v1/asn/{_quote(ip)}")

    # -- Email validation ---------------------------------------------------

    def email_info(self, email: str) -> Any:
        """Syntax, disposability and MX analysis of an email address."""
        return self._request("GET", f"/api/v1/email/{_quote(email)}")

    def validate_email(self, email: str) -> Any:
        """Advanced validation including SMTP deliverability checks."""
        return self._request("GET", f"/api/v1/email/advanced/{_quote(email)}")

    def validate_email_batch(self, emails: Sequence[str]) -> Any:
        """Advanced-validate up to 100 email addresses in a single request."""
        self._check_batch(emails, "emails")
        return self._request(
            "POST", "/api/v1/email/advanced/batch", body={"emails": list(emails)}
        )

    # -- Risk scoring ---------------------------------------------------------

    def risk_score(self, ip: Optional[str] = None) -> Any:
        """Fraud risk score for an IP (or the caller's IP)."""
        path = f"/api/v1/risk-score/{_quote(ip)}" if ip else "/api/v1/risk-score"
        return self._request("GET", path)

    def email_risk_score(self, email: str) -> Any:
        return self._request("GET", f"/api/v1/risk-score/email/{_quote(email)}")

    # -- DNS & domains --------------------------------------------------------

    def whois(self, domain: str) -> Any:
        return self._request("GET", f"/api/v1/dns/whois/{_quote(domain)}")

    def reverse_dns(self, ip: str) -> Any:
        return self._request("GET", f"/api/v1/dns/reverse/{_quote(ip)}")

    def forward_dns(self, hostname: str) -> Any:
        return self._request("GET", f"/api/v1/dns/forward/{_quote(hostname)}")

    def mx_records(self, domain: str) -> Any:
        return self._request("GET", f"/api/v1/dns/mx/{_quote(domain)}")

    def domain_age(self, domain: str) -> Any:
        return self._request("GET", f"/api/v1/domain/age/{_quote(domain)}")

    def domain_age_batch(self, domains: Sequence[str]) -> Any:
        if not domains:
            raise ValueError("domains must not be empty")
        return self._request(
            "POST", "/api/v1/domain/age/batch", body={"domains": list(domains)}
        )

    # -- Account --------------------------------------------------------------

    def rate_limit(self) -> Any:
        return self._request("GET", "/api/v1/ratelimit")

    def usage_summary(self) -> Any:
        return self._request("GET", "/api/v1/usage/summary")

    # -- Internals ------------------------------------------------------------

    @staticmethod
    def _check_batch(items: Sequence[str], name: str) -> None:
        if not items:
            raise ValueError(f"{name} must not be empty")
        if len(items) > MAX_BATCH_SIZE:
            raise ValueError(f"{name} must contain at most {MAX_BATCH_SIZE} items")

    def _request(self, method: str, path: str, body: Any = None) -> Any:
        url = self.base_url + path
        if self.api_key:
            url += "?" + urllib.parse.urlencode({"api_key": self.api_key})
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = response.read()
        except urllib.error.HTTPError as exc:
            raise self._error_from(exc) from None
        return json.loads(payload) if payload else None

    @staticmethod
    def _error_from(exc: urllib.error.HTTPError) -> IpApiError:
        status = exc.code
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        message = ""
        try:
            parsed = json.loads(body)
            if isinstance(parsed, dict):
                message = parsed.get("message") or parsed.get("error") or ""
        except ValueError:
            message = body.strip()[:200]
        if not message:
            message = f"HTTP {status} from ip-api.io"
        if status in (401, 403):
            return AuthenticationError(message, status, body)
        if status == 429:
            return RateLimitError(
                message,
                status,
                body,
                limit=_header_int(exc.headers, "x-ratelimit-limit"),
                remaining=_header_int(exc.headers, "x-ratelimit-remaining"),
                reset=_header_int(exc.headers, "x-ratelimit-reset"),
            )
        if status in (400, 404, 422):
            return InvalidRequestError(message, status, body)
        if status >= 500:
            return ServerError(message, status, body)
        return IpApiError(message, status, body)
