"""Official Python client for the ip-api.io IP intelligence API."""

from .client import MAX_BATCH_SIZE, IpApiClient
from .errors import (
    AuthenticationError,
    InvalidRequestError,
    IpApiError,
    RateLimitError,
    ServerError,
)
from .version import VERSION as __version__

__all__ = [
    "IpApiClient",
    "IpApiError",
    "AuthenticationError",
    "RateLimitError",
    "InvalidRequestError",
    "ServerError",
    "MAX_BATCH_SIZE",
    "__version__",
]
