# Email validation & verification

Check whether an email address is real, deliverable and safe to accept — before it
ever enters your database. The SDK exposes three levels: a fast syntax/MX/disposable
check, full SMTP verification, and a batch endpoint for cleaning whole lists.

Powers [email validation](https://ip-api.io/email-validation),
[advanced email validation](https://ip-api.io/advanced-email-validation),
[email verification](https://ip-api.io/email-verification-api),
[disposable email detection](https://ip-api.io/disposable-email-checker) and
[email list cleaning](https://ip-api.io/email-list-cleaning).

## `email_info(email)` — fast syntax, MX & disposable check

A lightweight check (no SMTP probe): validates syntax, confirms the domain has MX
records, and flags disposable/throwaway providers. Use it inline on sign-up forms.

```python
from ipapi_io import IpApiClient

client = IpApiClient(api_key="YOUR_API_KEY")

info = client.email_info("user@example.com")

print(info["syntax"]["is_valid"])    # True
print(info["is_disposable"])         # False
print(info["has_mx_records"])        # True
print(info["mx_records"][0]["hostname"])
```

### Response (`EmailInfo`)

| Field | Type | Description |
|---|---|---|
| `email` | `str` | The address checked |
| `is_disposable` | `bool` | Throwaway / temporary provider |
| `has_mx_records` | `bool` | Domain can receive mail |
| `mx_records` | `list` | Each: `priority`, `hostname`, `ttl` |
| `syntax` | `dict` | `is_valid`, `domain`, `username`, `error_reasons` |

## `validate_email(email)` — full SMTP deliverability

Advanced verification that connects to the mail server to confirm the mailbox is
deliverable, and adds role-account, free-provider, catch-all and Gravatar signals.
Use it before sending important mail or accepting a paying customer.

```python
result = client.validate_email("user@example.com")

print(result["reachable"])             # "yes" | "no" | "unknown"
print(result["smtp"]["deliverable"])   # True
print(result["smtp"]["catch_all"])     # False
print(result["disposable"])            # False
print(result["role_account"])          # False  (e.g. info@, support@)
print(result["free"])                  # False  (e.g. gmail.com)
print(result.get("suggestion"))        # typo fix, e.g. "user@gmail.com"
```

### Response (`AdvancedEmailValidation`)

| Field | Type | Description |
|---|---|---|
| `email` | `str` | The address checked |
| `reachable` | `str` | `"yes"`, `"no"` or `"unknown"` |
| `syntax` | `dict` | `username`, `domain`, `valid` |
| `smtp` | `dict \| None` | `host_exists`, `deliverable`, `full_inbox`, `catch_all`, `disabled` |
| `gravatar` | `dict \| None` | `has_gravatar`, `gravatar_url` |
| `suggestion` | `str` | Suggested correction for a likely typo |
| `disposable` | `bool` | Throwaway provider |
| `role_account` | `bool` | Role address (info@, sales@, …) |
| `free` | `bool` | Free webmail provider |
| `has_mx_records` | `bool` | Domain can receive mail |

## `validate_email_batch(emails)` — clean a list (≤100)

Advanced-validate up to 100 addresses in one request — the building block for
[email list cleaning](https://ip-api.io/email-list-cleaning). Raises `ValueError`
if the list is empty or longer than 100.

```python
batch = client.validate_email_batch([
    "user@example.com",
    "fake@mailinator.com",
    "info@example.org",
])

print(batch["totalProcessed"])          # 3
print(batch["successfulValidations"])   # 3

for email, result in batch["results"].items():
    print(email, result["reachable"], result["disposable"])
```

### Response (`BatchEmailValidationResponse`)

| Field | Type | Description |
|---|---|---|
| `results` | `dict[str, AdvancedEmailValidation]` | Map of email → result |
| `totalProcessed` | `int` | Emails received |
| `successfulValidations` | `int` | Emails validated |
| `failedValidations` | `int` | Emails that errored |

## See also

- [Fraud detection & risk scoring](fraud-risk-scoring.md) — `email_risk_score` for a 0–100 score
- [ASN & DNS lookups](asn-and-dns.md) — `mx_records` to inspect a domain's mail servers
- Product pages: [Email validation](https://ip-api.io/email-validation) · [Advanced validation](https://ip-api.io/advanced-email-validation) · [Email verification API](https://ip-api.io/email-verification-api) · [Disposable email checker](https://ip-api.io/disposable-email-checker) · [Email list cleaning](https://ip-api.io/email-list-cleaning)
