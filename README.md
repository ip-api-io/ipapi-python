# ip-api-io — Official Python client for [ip-api.io](https://ip-api.io)

[![PyPI](https://img.shields.io/pypi/v/ip-api-io)](https://pypi.org/project/ip-api-io/)
[![test](https://github.com/ip-api-io/ipapi-python/actions/workflows/test.yml/badge.svg)](https://github.com/ip-api-io/ipapi-python/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

The official Python client for the [ip-api.io](https://ip-api.io) IP intelligence
platform. One client covers [IP geolocation](https://ip-api.io/what-is-my-ip),
[email validation](https://ip-api.io/email-validation) and [verification](https://ip-api.io/email-verification-api)
(syntax, MX, SMTP deliverability), [fraud detection](https://ip-api.io/fraud-detection-api)
and [risk scoring](https://ip-api.io/risk-score),
[VPN](https://ip-api.io/vpn-detection-api)/[proxy](https://ip-api.io/proxy-detection-api)/[Tor detection](https://ip-api.io/tor-detection),
[disposable email detection](https://ip-api.io/disposable-email-checker), [ASN lookup](https://ip-api.io/asn-lookup),
[WHOIS](https://ip-api.io/whois-lookup), [reverse DNS](https://ip-api.io/reverse-dns-lookup),
[MX records](https://ip-api.io/mx-record-lookup) and [domain age](https://ip-api.io/domain-age-checker).

Zero dependencies — pure standard library.

## Install

```bash
pip install ip-api-io
```

## Quickstart

```python
from ipapi_io import IpApiClient

client = IpApiClient(api_key="YOUR_API_KEY")  # free key at https://ip-api.io

# Where is this IP, and is it risky?
info = client.lookup("8.8.8.8")
print(info["location"]["country"])            # "United States"
print(info["suspicious_factors"]["is_vpn"])   # False

risk = client.risk_score("8.8.8.8")
print(risk["score"], risk["risk_level"])      # 0 "low"

email = client.validate_email("user@example.com")
print(email["reachable"], email["disposable"]) # "yes" False
```

An API key is required — the API rejects keyless requests with `401`. Sign up at
[ip-api.io](https://ip-api.io) for a free key.

## Documentation

Each guide documents the methods for one capability, with runnable examples and a link
to the matching ip-api.io product page:

- **[IP geolocation & bulk lookup](docs/ip-geolocation.md)** — `lookup`, `lookup_batch`
- **[Email validation & verification](docs/email-validation.md)** — `email_info`, `validate_email`, `validate_email_batch`
- **[Fraud detection & risk scoring](docs/fraud-risk-scoring.md)** — `risk_score`, `email_risk_score`, `ip_reputation`
- **[VPN, proxy & Tor detection](docs/vpn-proxy-tor.md)** — `tor_check`, `suspicious_factors`
- **[ASN & DNS lookups](docs/asn-and-dns.md)** — `asn`, `whois`, `reverse_dns`, `forward_dns`, `mx_records`
- **[Domain age checker](docs/domain-age.md)** — `domain_age`, `domain_age_batch`
- **[Errors, rate limits & usage](docs/error-handling.md)** — exception types, `rate_limit`, `usage_summary`

## Methods

Every method maps to one ip-api.io endpoint and its product page:

| Method | Endpoint | Product page |
|---|---|---|
| `lookup(ip=None)` | `GET /api/v1/ip[/{ip}]` | [IP geolocation](https://ip-api.io/what-is-my-ip) |
| `lookup_batch(ips)` | `POST /api/v1/ip/batch` (≤100 IPs) | [Bulk IP lookup](https://ip-api.io/bulk-ip-lookup) |
| `email_info(email)` | `GET /api/v1/email/{email}` | [Email validation](https://ip-api.io/email-validation) |
| `validate_email(email)` | `GET /api/v1/email/advanced/{email}` | [Advanced email validation](https://ip-api.io/advanced-email-validation) |
| `validate_email_batch(emails)` | `POST /api/v1/email/advanced/batch` (≤100) | [Email list cleaning](https://ip-api.io/email-list-cleaning) |
| `risk_score(ip=None)` | `GET /api/v1/risk-score[/{ip}]` | [Risk score](https://ip-api.io/risk-score) |
| `email_risk_score(email)` | `GET /api/v1/risk-score/email/{email}` | [Fraud detection](https://ip-api.io/fraud-detection-api) |
| `ip_reputation(ip)` | `GET /api/v1/ip-reputation/{ip}` | [IP reputation](https://ip-api.io/ip-reputation) |
| `tor_check(ip)` | `GET /api/v1/tor/{ip}` | [Tor detection](https://ip-api.io/tor-detection) |
| `asn(ip)` | `GET /api/v1/asn/{ip}` | [ASN lookup](https://ip-api.io/asn-lookup) |
| `whois(domain)` | `GET /api/v1/dns/whois/{domain}` | [WHOIS lookup](https://ip-api.io/whois-lookup) |
| `reverse_dns(ip)` | `GET /api/v1/dns/reverse/{ip}` | [Reverse DNS](https://ip-api.io/reverse-dns-lookup) |
| `forward_dns(hostname)` | `GET /api/v1/dns/forward/{hostname}` | — |
| `mx_records(domain)` | `GET /api/v1/dns/mx/{domain}` | [MX record lookup](https://ip-api.io/mx-record-lookup) |
| `domain_age(domain)` | `GET /api/v1/domain/age/{domain}` | [Domain age checker](https://ip-api.io/domain-age-checker) |
| `domain_age_batch(domains)` | `POST /api/v1/domain/age/batch` | [Domain age checker](https://ip-api.io/domain-age-checker) |
| `rate_limit()` | `GET /api/v1/ratelimit` | — |
| `usage_summary()` | `GET /api/v1/usage/summary` | — |

All methods return parsed JSON as plain dicts. `ipapi_io.types` ships `TypedDict`
definitions for editor autocompletion.

## Error handling

The client raises typed exceptions and **never retries** — on `429`,
`RateLimitError.reset` tells you when your quota renews:

```python
from ipapi_io import IpApiClient, RateLimitError, AuthenticationError

client = IpApiClient(api_key="YOUR_API_KEY")
try:
    client.lookup("8.8.8.8")
except RateLimitError as e:
    print(f"limit={e.limit} remaining={e.remaining} resets_at={e.reset}")
except AuthenticationError:
    print("invalid API key")
```

See [docs/error-handling.md](docs/error-handling.md) for the full exception taxonomy.

## Links

- Website: https://ip-api.io
- API reference: https://ip-api.io/api-docs.html
- OpenAPI spec: https://ip-api.io/openapi.json
- Get a free API key: https://ip-api.io

---

`ip-api-io` is the official client for [ip-api.io](https://ip-api.io).
It is not affiliated with ip-api.com or ipapi.com.
