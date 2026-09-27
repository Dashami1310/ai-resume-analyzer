"""Minimal application logging configuration."""

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure standard logging without recording user-submitted resume text."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )