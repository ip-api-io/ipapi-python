# Domain age checker

Newly registered domains are a strong fraud and spam signal. `domain_age` returns how
long ago a domain was registered, derived from WHOIS data, so you can flag or block
domains created days ago.

Powers the [domain age checker](https://ip-api.io/domain-age-checker).

## `domain_age(domain)` — age of one domain

```python
from ipapi_io import IpApiClient

client = IpApiClient(api_key="YOUR_API_KEY")

age = client.domain_age("example.com")

print(age["is_valid"])           # True
print(age["registration_date"])  # "1995-08-14"
print(age["age_in_years"])       # 30
print(age["age_in_days"])        # 11000+

if (age["age_in_days"] or 10**9) < 30:
    pass  # treat brand-new domains as higher risk
```

### Response (`DomainAge`)

| Field | Type | Description |
|---|---|---|
| `domain` | `str` | The domain checked |
| `is_valid` | `bool` | Whether age could be determined |
| `registration_date` | `str \| None` | First registration date |
| `age_in_years` | `int \| None` | Age in whole years |
| `age_in_days` | `int \| None` | Age in days |
| `error` | `str \| None` | Reason when `is_valid` is false |

## `domain_age_batch(domains)` — many domains at once

Check a list of domains in one request (non-empty; raises `ValueError` if empty).

```python
batch = client.domain_age_batch([
    "example.com",
    "brand-new-domain.xyz",
])

for domain, age in batch["results"].items():
    print(domain, age["age_in_days"])
```

### Response (`BatchDomainAgeResponse`)
`results` — a dict mapping each domain to its `DomainAge`.

## See also

- [ASN & DNS lookups](asn-and-dns.md) — `whois` for the full registration record
- [Fraud detection & risk scoring](fraud-risk-scoring.md) — combine age with other signals
- Product page: [Domain age checker](https://ip-api.io/domain-age-checker)
- [Full tutorial on ip-api.io](https://ip-api.io/docs/sdk/python/domain-age)
