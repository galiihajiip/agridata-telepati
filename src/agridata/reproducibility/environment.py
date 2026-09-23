"""Utilitas perekam lingkungan, versi pustaka, dan status git.

Modul ini menyatukan logika yang sebelumnya tersebar dan terduplikasi di
scripts/prepare_dataset.py, scripts/train.py, dan scripts/evaluate.py, sehingga
ada satu sumber kebenaran tunggal mengenai apa saja yang perlu dicatat laporan
audit tentang kondisi mesin dan kode yang menghasilkannya.
"""

from __future__ import annotations

import platform
import subprocess
import sys
from typing import Any

from agridata.device import detect_device, is_apple_silicon


def get_git_commit() -> str | None:
    """Mengembalikan hash commit Git saat ini, atau None bila tidak tersedia."""
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_git_status() -> dict[str, Any]:
    """Mengembalikan status kebersihan working tree dan daftar berkas yang berubah.

    Working tree yang kotor saat laporan dibuat tetap dicatat, bukan
    disembunyikan. Auditor yang menjalankan ulang pipeline perlu tahu apakah
    artefaknya lahir dari kode yang persis terkomit atau dari suntingan lokal
    yang belum dikomit.
    """
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        changed_files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return {"clean": len(changed_files) == 0, "changed_files": changed_files}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"clean": None, "changed_files": [], "error": "not a git repository or git unavailable"}


def get_installed_packages() -> list[str]:
    """Return `pip freeze` output as a list of "package==version" strings."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=True
        )
        return sorted(line.strip() for line in result.stdout.splitlines() if line.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_device_info() -> dict[str, Any]:
    """Melaporkan perangkat komputasi terpilih beserta ketersediaan akselerator torch."""
    info: dict[str, Any] = {"resolved_device": detect_device(), "is_apple_silicon": is_apple_silicon()}
    try:
        import torch

        info["torch_version"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        info["mps_available"] = torch.backends.mps.is_available()
    except ImportError:
        info["torch_version"] = None
        info["cuda_available"] = None
        info["mps_available"] = None
    return info


def capture_environment_snapshot() -> dict[str, Any]:
    """Merekam seluruh informasi lingkungan dan kode yang dibutuhkan auditor.

    Cakupannya meliputi versi Python dan platform, versi dependensi, commit git
    beserta status kebersihan working tree, dan perangkat komputasi yang
    akhirnya dipakai."""
    return {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "platform": {
            "system": platform.system(),
            "machine": platform.machine(),
            "platform_string": platform.platform(),
        },
        "device": get_device_info(),
        "git_commit": get_git_commit(),
        "git_status": get_git_status(),
        "installed_packages": get_installed_packages(),
    }
