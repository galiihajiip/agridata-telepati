"""Penyiapan logging terstruktur untuk pipeline AgriData."""

from __future__ import annotations

import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Mengonfigurasi dan mengembalikan logger bersama 'agridata'.

    Aman dipanggil berkali-kali karena handler hanya dipasang sekali, sehingga
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
