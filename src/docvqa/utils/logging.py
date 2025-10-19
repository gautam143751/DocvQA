from __future__ import annotations

"""Logging utilities for DocVQA CLI."""

import logging
from typing import Literal

import structlog


def configure_logging(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO") -> None:
    """Configure structlog and standard logging for the CLI."""

    logging.basicConfig(level=getattr(logging, level), format="%(message)s")
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
            if level == "DEBUG"
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level)),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """Return a structlog logger."""

    return structlog.get_logger(name)


__all__ = ["configure_logging", "get_logger"]
