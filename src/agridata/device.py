"""Compute device detection with Apple Silicon awareness and CPU fallback.

Never assumes CUDA is available (the competition audit environment is
unspecified and must not be assumed to be a Mac). CPU must always work.
"""

from __future__ import annotations

import logging
import platform

logger = logging.getLogger("agridata.device")


def is_apple_silicon() -> bool:
    """Return True if running on macOS with an ARM64 (Apple Silicon) CPU."""
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def detect_device() -> str:
    """Return the best available compute device string: 'cuda', 'mps', or 'cpu'.

    Falls back to 'cpu' whenever torch is not installed or no accelerator is
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
