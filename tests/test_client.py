import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from ipapi_io import (
    AuthenticationError,
    InvalidRequestError,
    IpApiClient,
    RateLimitError,
    ServerError,
)
from ipapi_io.version import USER_AGENT

# IpInfoV1Dto example from https://ip-api.io/openapi.json
IP_INFO_FIXTURE = {
    "ip": "203.0.113.195",
    "isp": "Comcast Cable Communications",
    "asn": "AS7922",
    "suspicious_factors": {
        "is_proxy": False,
        "is_tor_node": False,
        "is_spam": False,
        "is_crawler": False,
        "is_datacenter": True,
        "is_vpn": False,
        "is_threat": False,
    },
    "location": {
        "country": "United States",
        "country_code": "US",
        "city": "San Francisco",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "zip": "94105",
        "timezone": "America/Los_Angeles",
        "local_time": "2023-06-21T14:30:00-07:00",
        "local_time_unix": 1687385400,
        "is_daylight_savings": True,
    },
}


class _Handler(BaseHTTPRequestHandler):
    def _handle(self):
        srv = self.server
        srv.requests.append(
            {
                "method": self.command,
                "path": self.path,
                "headers": dict(self.headers),
                "body": self.rfile.read(int(self.headers.get("Content-Length", 0) or 0)),
            }
        )
        status, headers, body = srv.response
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = _handle

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    httpd = HTTPServer(("127.0.0.1", 0), _Handler)
    httpd.requests = []
    httpd.response = (200, {}, json.dumps(IP_INFO_FIXTURE).encode())
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd
    httpd.shutdown()


def _client(server, **kwargs):
    return IpApiClient(base_url=f"http://127.0.0.1:{server.server_address[1]}", **kwargs)


def test_lookup_parses_response_and_sends_user_agent(server):
    info = _client(server).lookup("203.0.113.195")
    assert info == IP_INFO_FIXTURE
    req = server.requests[0]
    assert req["method"] == "GET"
    assert req["path"] == "/api/v1/ip/203.0.113.195"
    assert req["headers"]["User-Agent"] == USER_AGENT
    assert "api_key" not in req["path"]


def test_api_key_sent_as_query_param(server):
    _client(server, api_key="secret123").lookup()
    assert server.requests[0]["path"] == "/api/v1/ip?api_key=secret123"


def test_email_path_is_url_encoded(server):
    server.response = (200, {}, b"{}")
    _client(server).validate_email("user+tag@example.com")
    assert server.requests[0]["path"] == "/api/v1/email/advanced/user%2Btag%40example.com"


def test_batch_post_sends_json_body(server):
    server.response = (200, {}, b'{"results": {}}')
    _client(server).lookup_batch(["8.8.8.8", "1.1.1.1"])
    req = server.requests[0]
    assert req["method"] == "POST"
    assert req["path"] == "/api/v1/ip/batch"
    assert json.loads(req["body"]) == {"ips": ["8.8.8.8", "1.1.1.1"]}
    assert req["headers"]["Content-Type"] == "application/json"


def test_batch_size_validation():
    client = IpApiClient()
    with pytest.raises(ValueError):
        client.lookup_batch([])
    with pytest.raises(ValueError):
        client.lookup_batch(["1.1.1.1"] * 101)
    with pytest.raises(ValueError):
        client.validate_email_batch([])


def test_429_raises_rate_limit_error_with_headers(server):
    server.response = (
        429,
        {
            "x-ratelimit-limit": "1000",
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": "1718200000",
        },
        b'{"message": "Rate limit exceeded"}',
    )
    with pytest.raises(RateLimitError) as exc_info:
        _client(server).lookup("8.8.8.8")
    err = exc_info.value
    assert err.status_code == 429
    assert err.limit == 1000
    assert err.remaining == 0
    assert err.reset == 1718200000
    assert "Rate limit exceeded" in str(err)


def test_401_raises_authentication_error(server):
    server.response = (401, {}, b'{"error": "Invalid API key"}')
    with pytest.raises(AuthenticationError) as exc_info:
        _client(server, api_key="bad").lookup()
    assert exc_info.value.status_code == 401


def test_400_raises_invalid_request_error(server):
    server.response = (400, {}, b'{"message": "Invalid IP address"}')
    with pytest.raises(InvalidRequestError):
        _client(server).lookup("not-an-ip")


def test_500_raises_server_error(server):
    server.response = (500, {}, b"{}")
    with pytest.raises(ServerError):
        _client(server).lookup()
