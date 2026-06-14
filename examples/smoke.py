"""Live smoke test against https://ip-api.io.

Usage: IPAPI_API_KEY=... python3 examples/smoke.py
The API requires a key; without IPAPI_API_KEY this script skips.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ipapi_io import IpApiClient  # noqa: E402

api_key = os.environ.get("IPAPI_API_KEY")
if not api_key:
    print("SKIPPED: set IPAPI_API_KEY to run the live smoke test")
    sys.exit(0)

client = IpApiClient(api_key=api_key)

info = client.lookup("8.8.8.8")
assert info["ip"] == "8.8.8.8", info
print(f"lookup(8.8.8.8): {info['location']['country']} / {info.get('asn')}")

rl = client.rate_limit()
print(f"rate_limit: plan={rl.get('plan_id')} ip_api remaining={rl['ip_api']['remaining']}")

print("smoke OK")
