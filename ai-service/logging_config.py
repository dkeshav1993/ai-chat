"""
Centralised logging configuration for NexTrip AI Service.

Terminal: uvicorn.error only (startup/shutdown banners).
File:     everything else -> rolling log at
          /Users/keshavdutta/Documents/speckit-workspace/logs/nextrip-api.log
          (max 2 000 KB, 5 backups)
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog

_LOG_DIR   = Path("/Users/keshavdutta/Documents/speckit-workspace/logs")
_LOG_FILE  = _LOG_DIR / "nextrip-api.log"
_MAX_BYTES = 2_048_000
_BACKUPS   = 5


def configure_logging() -> None:
    """
    Call once at application startup (main.py, before anything else).

    Result:
    - uvicorn.error  -> stderr/terminal  (startup banner, shutdown notice)
    - uvicorn.access -> log file         (per-request lines, too noisy for terminal)
    - All structlog / app loggers -> log file
    - Root logger stdout handler removed
    """
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=str(_LOG_FILE),
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUPS,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging.Formatter("%(levelname)s:     %(message)s"))
    console_handler.setLevel(logging.INFO)

    # Root logger -> file only
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)
    root.addHandler(file_handler)
    root.setLevel(logging.DEBUG)

    # uvicorn.error -> terminal (startup/shutdown banners)
    uv_error = logging.getLogger("uvicorn.error")
    for h in uv_error.handlers[:]:
        uv_error.removeHandler(h)
    uv_error.addHandler(console_handler)
    uv_error.propagate = False

    # uvicorn (general) + uvicorn.access -> file only
    for name in ("uvicorn", "uvicorn.access", "fastapi", "asyncio"):
        lg = logging.getLogger(name)
        for h in lg.handlers[:]:
            lg.removeHandler(h)
        lg.addHandler(file_handler)
        lg.propagate = False

    # Strip any remaining StreamHandlers on stdout/stderr from third-party libs
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name == "uvicorn.error":
            continue
        lg = logging.getLogger(name)
        for h in lg.handlers[:]:
            if isinstance(h, logging.StreamHandler) and h.stream in (sys.stdout, sys.stderr):
                lg.removeHandler(h)

    # structlog: JSON -> stdlib -> file
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso", utc=False),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
