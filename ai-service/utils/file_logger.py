"""
Rolling file logger for all outbound Spring Boot API calls.

Writes to /Users/keshavdutta/Documents/speckit-workspace/logs/nextrip-api.log
(an external directory outside the project tree) with a RotatingFileHandler:
  - Max size : 2 000 KB (2 048 000 bytes)
  - Backups  : 5  → maximum ~12 MB retained on disk

Each line is a JSON record so logs can be ingested by any log viewer.

Schema
------
{
  "timestamp": "2026-05-25T20:28:13.847+05:30",   # ISO-8601 local time
  "level":     "INFO" | "ERROR",
  "type":      "REQUEST" | "RESPONSE" | "ERROR",
  "capability": "AutoSuggest",
  "method":    "POST",
  "url":       "https://...",
  "correlation_id": "...",            # present on requests only
  "request_body":   {...},            # present on REQUEST records
  "request_headers": {...},           # present on REQUEST records (auth masked)
  "response_status": 200,             # present on RESPONSE / ERROR records
  "response_headers": {...},          # present on RESPONSE records
  "response_body":  {...},            # present on RESPONSE / ERROR records
  "elapsed_ms":     143,              # present on RESPONSE / ERROR records
  "error":          "..."             # present on ERROR records
}
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

# ─── Constants ───────────────────────────────────────────────────────────────
# External log directory — lives outside the project tree so log files are
# never accidentally committed and don't clutter the source tree.
_LOG_DIR   = Path("/Users/keshavdutta/Documents/speckit-workspace/logs")
_LOG_FILE  = _LOG_DIR / "nextrip-api.log"
_MAX_BYTES = 2_048_000   # 2 000 KB
_BACKUPS   = 5           # keep 5 rotated files → ~12 MB max on disk

# Capabilities whose response bodies are logged in full (small / essential payloads).
# All other capabilities have their response body truncated to _BODY_PREVIEW_CHARS.
_FULL_RESPONSE_CAPABILITIES = {"TOKEN", "AUTOSUGGEST"}
_BODY_PREVIEW_CHARS = 100

# ─── Logger setup (runs once at import) ──────────────────────────────────────
_log_dir_created = False

def _get_file_logger() -> logging.Logger:
    """Return (and lazily create) the rotating-file logger."""
    global _log_dir_created
    logger = logging.getLogger("nextrip.api_file")
    if logger.handlers:
        return logger

    # Make sure logs/ directory exists
    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        _log_dir_created = True
    except OSError:
        # Filesystem is read-only or something unexpected — degrade gracefully
        return logger

    handler = RotatingFileHandler(
        filename=str(_LOG_FILE),
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUPS,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False   # do not bubble up to root logger (keeps terminal clean)
    return logger


def _now_iso() -> str:
    """Return current local time as ISO-8601 with offset, e.g. 2026-05-25T20:28:13.847+05:30."""
    now = datetime.now(tz=timezone.utc).astimezone()
    return now.isoformat(timespec="milliseconds")


def _safe_json(obj: Any) -> Any:
    """Return obj if JSON-serialisable, else its repr."""
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        return repr(obj)


def _mask_auth(value: str) -> str:
    """Show 'Bearer <first20chars>...' so the token is identifiable but not exposed."""
    if value.lower().startswith("bearer "):
        token = value[7:]
        return f"Bearer {token[:20]}... ({len(token)} chars)"
    return value[:20] + "..." if len(value) > 20 else value


def _sanitise_headers(headers: dict) -> dict:
    return {
        k: (_mask_auth(v) if k.lower() == "authorization" else v)
        for k, v in headers.items()
    }


def _truncate_body(body: Any, capability: str) -> Any:
    """
    Return *body* unchanged for TOKEN / AUTOSUGGEST responses (small, fully useful).
    For all other capabilities serialise to a string and keep only the first
    _BODY_PREVIEW_CHARS characters so the log file stays readable.
    """
    if capability.upper() in _FULL_RESPONSE_CAPABILITIES:
        return _safe_json(body)
    # Serialise then slice
    try:
        text = json.dumps(body, default=str, ensure_ascii=False)
    except Exception:
        text = repr(body)
    if len(text) <= _BODY_PREVIEW_CHARS:
        return body   # already short enough — store as-is
    return text[:_BODY_PREVIEW_CHARS] + f"… [truncated, full length {len(text)} chars]"


def _write(record: dict) -> None:
    """Serialise *record* as a single JSON line and hand it to the file handler."""
    logger = _get_file_logger()
    if not logger.handlers:
        return  # silently skip if we couldn't create the file
    try:
        line = json.dumps(record, default=str, ensure_ascii=False)
        logger.info(line)
    except Exception:
        pass  # never crash the caller


# ─── Public API ──────────────────────────────────────────────────────────────

def log_request_to_file(
    method: str,
    url: str,
    body: Any,
    capability: str,
    correlation_id: str = "",
    headers: dict | None = None,
) -> None:
    """Write a REQUEST record to the rolling log file."""
    record: dict[str, Any] = {
        "timestamp":      _now_iso(),
        "level":          "INFO",
        "type":           "REQUEST",
        "capability":     capability,
        "method":         method.upper(),
        "url":            url,
        "request_body":   _safe_json(body),
    }
    if correlation_id:
        record["correlation_id"] = correlation_id
    if headers:
        record["request_headers"] = _sanitise_headers(dict(headers))
    _write(record)


def log_response_to_file(
    method: str,
    url: str,
    status: int,
    response_body: Any,
    elapsed_ms: float,
    capability: str,
    response_headers: dict | None = None,
) -> None:
    """Write a RESPONSE record to the rolling log file.

    Response body is stored in full only for TOKEN and AUTOSUGGEST.
    All other capabilities are truncated to the first 100 characters.
    """
    record: dict[str, Any] = {
        "timestamp":       _now_iso(),
        "level":           "INFO" if status < 400 else "ERROR",
        "type":            "RESPONSE",
        "capability":      capability,
        "method":          method.upper(),
        "url":             url,
        "response_status": status,
        "response_body":   _truncate_body(response_body, capability),
        "elapsed_ms":      round(elapsed_ms, 1),
    }
    if response_headers:
        record["response_headers"] = dict(response_headers)
    _write(record)


def log_error_to_file(
    method: str,
    url: str,
    error: str,
    elapsed_ms: float,
    capability: str,
    request_body: Any = None,
) -> None:
    """Write an ERROR record (e.g. network timeout, unexpected exception) to the log file."""
    record: dict[str, Any] = {
        "timestamp":   _now_iso(),
        "level":       "ERROR",
        "type":        "ERROR",
        "capability":  capability,
        "method":      method.upper(),
        "url":         url,
        "error":       error,
        "elapsed_ms":  round(elapsed_ms, 1),
    }
    if request_body is not None:
        record["request_body"] = _safe_json(request_body)
    _write(record)
