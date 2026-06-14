# Errors, rate limits & usage

The client maps every HTTP failure to a typed exception and **never retries** — you
stay in control of back-off. It also exposes your current quota so you can throttle
before you hit a limit.

## Exception taxonomy

Every exception extends `IpApiError`, which carries `status_code` and the raw response
`body`. Catch the specific subclass you care about:

| Exception | HTTP status | Meaning |
|---|---|---|
| `AuthenticationError` | 401, 403 | Missing or invalid API key |
| `RateLimitError` | 429 | Quota exhausted (see below) |
| `InvalidRequestError` | 400, 404, 422 | Malformed input or unknown resource |
| `ServerError` | 5xx | ip-api.io server-side failure |
| `IpApiError` | other | Base / fallback |

```python
from ipapi_io import (
    IpApiClient,
    IpApiError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    ServerError,
)

client = IpApiClient(api_key="YOUR_API_KEY")

try:
    info = client.lookup("8.8.8.8")
    print(info["location"]["country"])
except RateLimitError as e:
    print(f"quota hit — resets at {e.reset}")
except AuthenticationError:
    print("check your API key")
except InvalidRequestError as e:
    print("bad request:", e)
except ServerError:
    print("ip-api.io is having trouble, try later")
except IpApiError as e:
    print(f"error {e.status_code}: {e}")
```

Transport failures (DNS, connection, timeout) surface as the standard library's
`urllib.error.URLError` / `socket.timeout`, not an `IpApiError`.

## Rate limits

On HTTP 429 the client raises `RateLimitError`, parsed from the `x-ratelimit-*`
response headers. Because the client never retries, **`reset` tells you when to**:

```python
import time

try:
    client.lookup("8.8.8.8")
except RateLimitError as e:
    print(e.limit)      # your quota for the window
    print(e.remaining)  # requests left (0 here)
    print(e.reset)      # unix timestamp when quota renews
    wait = (e.reset or 0) - time.time()
    # schedule a retry after `wait` seconds instead of hammering the API
```

## `rate_limit()` — check quota proactively

Read your current limits without triggering a 429, so you can throttle in advance.

```python
rl = client.rate_limit()

print(rl["plan_name"])
print(rl["ip_api"]["remaining"], "/", rl["ip_api"]["limit"])
print(rl["email_api"]["usage_percent"], "% used")
print(rl["next_renewal_date"])
```

`RateLimitInfo`: `plan_id`, `plan_name`, `ip_api` and `email_api`
(`limit`, `remaining`, `used`, `usage_percent`), `interval_seconds`,
`next_renewal_date`, `status`.

## `usage_summary()` — account usage

Aggregate usage for the current period — handy for dashboards and internal alerts.

```python
usage = client.usage_summary()

print(usage["totalRequests"], usage["successfulRequests"])
print(usage["rateLimitedRequests"], usage["quotaConsumed"])
print(usage["periodStart"], "→", usage["periodEnd"])
```

`UsageSummary`: `apiKey`, `apiType`, `periodStart`, `periodEnd`, `totalRequests`,
`successfulRequests`, `rateLimitedRequests`, `quotaConsumed`, `batchOperations`,
`avgRequestDurationMs`.

## See also

- [IP geolocation & bulk lookup](ip-geolocation.md) — the most common call
- API reference: https://ip-api.io/api-docs.html
- Get a free API key: https://ip-api.io
