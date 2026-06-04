"""
Logger for outbound Spring Boot hotel API calls.

All output goes exclusively to the rolling log file at:
  /Users/keshavdutta/Documents/speckit-workspace/logs/nextrip-api.log

Nothing is printed to the terminal.
"""

import time
from typing import Any

import httpx

from utils.file_logger import log_request_to_file, log_response_to_file, log_error_to_file


def log_request(
    method: str,
    url: str,
    body: Any,
    capability: str,
    correlation_id: str = "",
    headers: dict | None = None,
) -> float:
    """Record outbound request to the log file and return start timestamp."""
    start = time.time()
    log_request_to_file(
        method=method,
        url=url,
        body=body,
        capability=capability,
        correlation_id=correlation_id,
        headers=headers,
    )
    return start


def log_response(
    method: str,
    url: str,
    response: httpx.Response,
    start: float,
    capability: str,
) -> None:
    """Record full response to the log file."""
    elapsed_ms = (time.time() - start) * 1000
    status = response.status_code

    try:
        body = response.json()
    except Exception:
        body = response.text[:2000]

    log_response_to_file(
        method=method,
        url=url,
        status=status,
        response_body=body,
        elapsed_ms=elapsed_ms,
        capability=capability,
        response_headers=dict(response.headers),
    )


def log_error(
    method: str,
    url: str,
    error: Exception | str,
    start: float,
    capability: str,
    request_body: Any = None,
) -> None:
    """Record an unexpected error (e.g. network timeout) to the log file."""
    elapsed_ms = (time.time() - start) * 1000
    log_error_to_file(
        method=method,
        url=url,
        error=str(error),
        elapsed_ms=elapsed_ms,
        capability=capability,
        request_body=request_body,
    )
