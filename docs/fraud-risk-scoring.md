# Fraud detection & risk scoring

Collapse every signal — geolocation, proxy/VPN/Tor flags, datacenter hosting,
disposable email, syntax — into a single 0–100 risk score you can act on at sign-up,
checkout or login. Or pull the raw [IP reputation](https://ip-api.io/ip-reputation)
record when you want to build your own rules.

Powers the [fraud detection API](https://ip-api.io/fraud-detection-api),
[risk score](https://ip-api.io/risk-score) and
[IP reputation](https://ip-api.io/ip-reputation) products.

## `risk_score(ip=None)` — score an IP

Returns a `score` (0–100) and a human `risk_level`, plus the `factors` that drove it.
Omit the argument to score the caller's own IP.

```python
from ipapi_io import IpApiClient

client = IpApiClient(api_key="YOUR_API_KEY")

risk = client.risk_score("185.220.101.1")

print(risk["score"])                                  # 88
print(risk["risk_level"])                             # "high"
print(risk["factors"]["ip_factors"]["is_tor_node"])    # True
print(risk["factors"]["ip_factors"]["is_datacenter"])  # True

if risk["score"] >= 75:
    pass  # block, or send to manual review / step-up auth
```

### Response (`RiskScore`)

| Field | Type | Description |
|---|---|---|
| `score` | `int` | Risk score, 0 (safe) – 100 (high risk) |
| `risk_level` | `str` | Bucketed level, e.g. `"low"`, `"medium"`, `"high"` |
| `ip` | `str \| None` | Scored IP (when applicable) |
| `email` | `str \| None` | Scored email (when applicable) |
| `factors` | `dict` | `ip_factors` and/or `email_factors` |

`ip_factors`: `is_proxy`, `is_vpn`, `is_tor_node`, `is_spam`, `is_datacenter`,
`risk_contribution`.
`email_factors`: `is_disposable`, `is_valid_syntax`, `risk_contribution`.

## `email_risk_score(email)` — score an email

Same 0–100 scale, driven by email signals (disposable provider, invalid syntax).
Use it to grade leads or gate sign-ups by address quality.

```python
risk = client.email_risk_score("user@mailinator.com")

print(risk["score"], risk["risk_level"])                   # 90 "high"
print(risk["factors"]["email_factors"]["is_disposable"])   # True
```

## `ip_reputation(ip)` — raw reputation record

Returns the underlying reputation data for an IP as a plain dict — use it when you want
the source signals rather than a computed score.

```python
reputation = client.ip_reputation("185.220.101.1")
print(reputation)
```

## See also

- [IP geolocation & bulk lookup](ip-geolocation.md) — `suspicious_factors` per IP
- [VPN, proxy & Tor detection](vpn-proxy-tor.md) — the individual checks behind the score
- [Email validation & verification](email-validation.md) — deliverability before scoring
- Product pages: [Fraud detection](https://ip-api.io/fraud-detection-api) · [Risk score](https://ip-api.io/risk-score) · [IP reputation](https://ip-api.io/ip-reputation)
