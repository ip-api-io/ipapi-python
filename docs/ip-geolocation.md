# IP geolocation & bulk lookup

Turn any IP address into geolocation, network and threat intelligence. A single
`lookup` returns the country, city, coordinates, timezone, ISP and ASN of an IP,
plus the `suspicious_factors` flags used for fraud screening (proxy, VPN, Tor,
datacenter, spam, crawler, threat).

Powers the [IP geolocation API](https://ip-api.io/what-is-my-ip) and the
[bulk IP lookup](https://ip-api.io/bulk-ip-lookup) product.

## `lookup(ip=None)` — geolocate one IP

Pass an IPv4/IPv6 address, or omit the argument to geolocate the caller's own IP.

```python
from ipapi_io import IpApiClient

client = IpApiClient(api_key="YOUR_API_KEY")

info = client.lookup("8.8.8.8")

print(info["ip"])                              # "8.8.8.8"
print(info["isp"])                             # "Google LLC"
print(info["location"]["country"])             # "United States"
print(info["location"]["city"])                # "Mountain View"
print(info["location"]["latitude"], info["location"]["longitude"])
print(info["location"]["timezone"])            # "America/Los_Angeles"
print(info["suspicious_factors"]["is_datacenter"])  # True
```

```python
# Geolocate the machine making the request
me = client.lookup()
print(me["ip"], me["location"]["country"])
```

### Response (`IpInfo`)

| Field | Type | Description |
|---|---|---|
| `ip` | `str` | The looked-up address |
| `isp` | `str \| None` | Internet service provider |
| `asn` | `str \| None` | Autonomous system the IP belongs to |
| `location` | `dict` | `country`, `country_code`, `city`, `latitude`, `longitude`, `zip`, `timezone`, `local_time`, `local_time_unix`, `is_daylight_savings` |
| `suspicious_factors` | `dict` | `is_proxy`, `is_vpn`, `is_tor_node`, `is_datacenter`, `is_spam`, `is_crawler`, `is_threat` |

> The `suspicious_factors` block is the fastest way to flag risky traffic in one call.
> For a single 0–100 score, see [Fraud detection & risk scoring](fraud-risk-scoring.md);
> for the individual checks, see [VPN, proxy & Tor detection](vpn-proxy-tor.md).

## `lookup_batch(ips)` — geolocate up to 100 IPs

Look up to 100 addresses in one request — ideal for enriching logs, sign-up events or
historical data without a round trip per IP. Raises `ValueError` if the list is empty
or longer than 100.

```python
batch = client.lookup_batch(["8.8.8.8", "1.1.1.1", "9.9.9.9"])

print(batch["total_processed"])     # 3
print(batch["successful_lookups"])  # 3
print(batch["failed_lookups"])      # 0

for ip, info in batch["results"].items():
    print(ip, info["location"]["country"], info["suspicious_factors"]["is_vpn"])
```

### Response (`BatchIpLookupResponse`)

| Field | Type | Description |
|---|---|---|
| `results` | `dict[str, IpInfo]` | Map of IP → info dict |
| `total_processed` | `int` | IPs received |
| `successful_lookups` | `int` | IPs resolved |
| `failed_lookups` | `int` | IPs that could not be resolved |

## See also

- [Fraud detection & risk scoring](fraud-risk-scoring.md) — turn the flags into a score
- [VPN, proxy & Tor detection](vpn-proxy-tor.md) — the individual threat checks
- [ASN & DNS lookups](asn-and-dns.md) — network ownership for an IP
- Product pages: [IP geolocation](https://ip-api.io/what-is-my-ip) · [Bulk IP lookup](https://ip-api.io/bulk-ip-lookup)
- [Full tutorial on ip-api.io](https://ip-api.io/docs/sdk/python/ip-geolocation)
