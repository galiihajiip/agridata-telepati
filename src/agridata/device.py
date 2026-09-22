"""Deteksi perangkat komputasi dengan dukungan Apple Silicon dan fallback CPU.

Never assumes CUDA is available (the competition audit environment is
unspecified and must not be assumed to be a Mac). CPU must always work.
"""

from __future__ import annotations

import logging
import platform

logger = logging.getLogger("agridata.device")


def is_apple_silicon() -> bool:
    """Mengembalikan True bila berjalan pada macOS dengan prosesor ARM64 Apple Silicon."""
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def detect_device() -> str:
    """Mengembalikan perangkat komputasi terbaik yang tersedia: 'cuda', 'mps', atau 'cpu'.

    Jatuh kembali ke 'cpu' bila torch tidak terpasang atau tidak ada akselerator
    usable, so the pipeline always has a working device.
    """
    try:
        import torch
    except ImportError:
        logger.info("torch not installed; defaulting to CPU device string")
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"
    if is_apple_silicon() and torch.backends.mps.is_available():
        return "mps"
    return "cpu"
