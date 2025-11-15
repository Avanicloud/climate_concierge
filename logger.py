"""
Logging utilities for the Climate Concierge project.

Provides structured logging to both console and file sinks to aid in
debugging, observability, and reproducibility.
"""

from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

_LOGGER_CACHE: Dict[str, logging.Logger] = {}


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_logger(
    name: str,
    log_path: Path,
    enable_console: bool = True,
    level: str = "INFO",
) -> logging.Logger:
    """
    Return a configured logger instance.

    The logger writes JSON-formatted logs to `log_path` (rotated at ~1MB)
    and optionally streams human-readable logs to stdout.
    """

    cache_key = f"{name}:{log_path}"
    if cache_key in _LOGGER_CACHE:
        return _LOGGER_CACHE[cache_key]

    logger = logging.getLogger(cache_key)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    # File handler with JSON formatting
    _ensure_parent(log_path)
    file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3)
    file_handler.setFormatter(_JsonLogFormatter())
    logger.addHandler(file_handler)

    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(console_handler)

    _LOGGER_CACHE[cache_key] = logger
    return logger


class _JsonLogFormatter(logging.Formatter):
    """Minimal JSON formatter to keep logs structured."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if hasattr(record, "context"):
            payload["context"] = record.context
        return json.dumps(payload, ensure_ascii=False)


def log_event(
    logger: logging.Logger,
    message: str,
    *,
    level: str = "info",
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Helper to log with contextual metadata."""

    extra = {"context": context or {}}
    getattr(logger, level.lower(), logger.info)(message, extra=extra)

