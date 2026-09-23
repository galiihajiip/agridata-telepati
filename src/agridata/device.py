"""Deteksi perangkat komputasi dengan dukungan Apple Silicon dan fallback CPU.

Ketersediaan CUDA tidak pernah diasumsikan. Lingkungan audit kompetisi tidak
disebutkan spesifikasinya dan tidak boleh diandaikan sebagai Mac, sehingga jalur
CPU harus selalu dapat berjalan.
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
    yang dapat dipakai, sehingga pipeline selalu memiliki perangkat yang berfungsi.
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
