"""Environment/version/git capture utilities (Block 8).

Consolidates logic that was previously duplicated ad hoc in
scripts/prepare_dataset.py, scripts/train.py, and scripts/evaluate.py, one
source of truth for "what does an audit report need to record about the
machine and code state that produced it."
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

    Working tree yang kotor saat laporan dibuat tetap dicatat, tidak disembunyikan,
    an auditor rerunning the pipeline needs to know if the artifact was
    produced from exactly the committed code or from local, uncommitted edits.
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
    """Merekam seluruh informasi lingkungan dan kode yang dibutuhkan auditor
    state that produced a given run: Python/platform, dependency versions,
    git commit + dirty status, and resolved compute device."""
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
