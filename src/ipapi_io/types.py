"""Zero-cost TypedDict definitions for ip-api.io responses.

These mirror the schemas in https://ip-api.io/openapi.json. They exist purely
for editor/type-checker support — the client returns plain dicts.
"""
from __future__ import annotations

from typing import Dict, List, Optional, TypedDict


class SuspiciousFactors(TypedDict):
    is_proxy: bool
    is_tor_node: bool
    is_spam: bool
    is_crawler: bool
    is_datacenter: bool
    is_vpn: bool
    is_threat: bool


class Location(TypedDict):
    country: Optional[str]
    country_code: Optional[str]
    city: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    zip: Optional[str]
    timezone: Optional[str]
    local_time: Optional[str]
    local_time_unix: Optional[int]
    is_daylight_savings: Optional[bool]


class IpInfo(TypedDict):
    ip: str
    isp: Optional[str]
    asn: Optional[str]
    suspicious_factors: SuspiciousFactors
    location: Location


class BatchIpLookupResponse(TypedDict):
    results: Dict[str, IpInfo]
    total_processed: int
    successful_lookups: int
    failed_lookups: int


class MxRecord(TypedDict):
    priority: int
    hostname: str
    ttl: int


class EmailSyntax(TypedDict):
    domain: Optional[str]
    username: Optional[str]
    is_valid: bool
    error_reasons: List[str]


class EmailInfo(TypedDict):
    email: str
    is_disposable: bool
    has_mx_records: bool
    mx_records: List[MxRecord]
    syntax: EmailSyntax


class AdvancedSyntax(TypedDict):
    username: str
    domain: str
    valid: bool


class AdvancedSmtp(TypedDict):
    host_exists: bool
    full_inbox: bool
    catch_all: bool
    deliverable: bool
    disabled: bool


class AdvancedGravatar(TypedDict):
    has_gravatar: bool
    gravatar_url: str


class AdvancedEmailValidation(TypedDict, total=False):
    email: str
    reachable: str
    syntax: AdvancedSyntax
    smtp: Optional[AdvancedSmtp]
    gravatar: Optional[AdvancedGravatar]
    suggestion: str
    disposable: bool
    role_account: bool
    free: bool
    has_mx_records: bool


class IpFactors(TypedDict):
    is_proxy: bool
    is_tor_node: bool
    is_spam: bool
    is_vpn: bool
    is_datacenter: bool
    risk_contribution: float


class EmailFactors(TypedDict):
    is_disposable: bool
    is_valid_syntax: bool
    risk_contribution: float


class RiskScoreFactors(TypedDict, total=False):
    ip_factors: Optional[IpFactors]
    email_factors: Optional[EmailFactors]


class RiskScore(TypedDict, total=False):
    score: float
    risk_level: str
    ip: Optional[str]
    email: Optional[str]
    factors: RiskScoreFactors


class TorDetection(TypedDict):
    ip: str
    is_tor: bool
    tor_node_count: int


class AsnLookup(TypedDict, total=False):
    ip: str
    asn: Optional[int]
    organization: Optional[str]
    network: Optional[str]
    is_datacenter: bool
    country: Optional[str]
    country_code: Optional[str]


class DomainAge(TypedDict, total=False):
    domain: str
    is_valid: bool
    registration_date: Optional[str]
    age_in_years: Optional[int]
    age_in_days: Optional[int]
    error: Optional[str]


class WhoisRegistrar(TypedDict, total=False):
    name: Optional[str]
    url: Optional[str]
    iana_id: Optional[str]


class WhoisStatus(TypedDict):
    code: str
    humanized: str


class Whois(TypedDict, total=False):
    domain: str
    registrar: Optional[WhoisRegistrar]
    registered_on: Optional[str]
    expires_on: Optional[str]
    updated_on: Optional[str]
    name_servers: List[str]
    status: List[WhoisStatus]
    raw: str
    error: Optional[str]


class ReverseDns(TypedDict, total=False):
    ip: str
    hostname: Optional[str]
    ptr_record: Optional[str]
    ttl: Optional[int]


class ForwardLookupRecord(TypedDict):
    type: str
    address: str
    ttl: int


class ForwardDns(TypedDict):
    hostname: str
    addresses: List[ForwardLookupRecord]


class MxLookup(TypedDict):
    domain: str
    mx_records: List[MxRecord]


class ApiLimitInfo(TypedDict):
    limit: int
    remaining: int
    used: int
    usage_percent: float


class RateLimitInfo(TypedDict, total=False):
    plan_id: str
    plan_name: Optional[str]
    ip_api: ApiLimitInfo
    email_api: ApiLimitInfo
    interval_seconds: int
    next_renewal_date: Optional[str]
    status: Optional[str]
