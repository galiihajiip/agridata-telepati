"""Structured logging setup for the AgriData pipeline."""

from __future__ import annotations

import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return the shared 'agridata' logger.

    Safe to call multiple times: handlers are only attached once so repeated
    calls (e.g. across notebook cells) do not duplicate log lines.
    """
    logger = logging.getLogger("agridata")
    if logger.handlers:
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
