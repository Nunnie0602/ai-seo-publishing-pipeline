"""Retry classification for LLM and WordPress HTTP clients."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from google.api_core import exceptions as google_exceptions
else:
    try:
        from google.api_core import exceptions as google_exceptions
    except ImportError:  # pragma: no cover
        google_exceptions = None  # type: ignore[assignment]

_LLM_NON_RETRYABLE_CODES = frozenset({400, 401, 403})
_LLM_RETRYABLE_CODES = frozenset({429, 500, 502, 503, 504})
_WP_RETRYABLE_STATUS = frozenset({502, 503, 504})


def _google_api_status_code(exc: Exception) -> int | None:
    if google_exceptions is None or not isinstance(exc, google_exceptions.GoogleAPIError):
        return None
    code = getattr(exc, "code", None)
    if isinstance(code, int):
        return code
    grpc_code = getattr(exc, "grpc_status_code", None)
    if isinstance(grpc_code, int):
        return grpc_code
    return None


def is_llm_retryable(exc: Exception) -> bool:
    """Timeout, rate limits, and 5xx are retryable; 400/401/403 are not."""
    if isinstance(exc, (TimeoutError, json.JSONDecodeError, ConnectionError, OSError)):
        return True

    if google_exceptions is not None:
        if isinstance(
            exc,
            (
                google_exceptions.DeadlineExceeded,
                google_exceptions.ResourceExhausted,
                google_exceptions.ServiceUnavailable,
                google_exceptions.InternalServerError,
                google_exceptions.TooManyRequests,
            ),
        ):
            return True

        status = _google_api_status_code(exc)
        if status in _LLM_NON_RETRYABLE_CODES:
            return False
        if status in _LLM_RETRYABLE_CODES:
            return True

        if isinstance(exc, google_exceptions.GoogleAPIError):
            lowered = str(exc).lower()
            if any(token in lowered for token in ("429", "quota", "rate limit", "503", "504")):
                return True
            if any(token in lowered for token in ("401", "400", "invalid api key", "permission denied")):
                return False

    return False


def is_wp_retryable(exc: Exception) -> bool:
    """Retry transient network failures and gateway errors only."""
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in _WP_RETRYABLE_STATUS
    return False
