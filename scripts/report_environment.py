#!/usr/bin/env python3
"""CLI to snapshot the current environment/version/git state (Block 8).

Usage:
    python scripts/report_environment.py

Writes artifacts/reports/environment_snapshot.json. Python/platform info,
resolved compute device, torch/CUDA/MPS availability, git commit + dirty
status, and full `pip freeze` output. Any script in this project can call
`agridata.reproducibility.environment.capture_environment_snapshot()`
directly instead of re-deriving this information.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.reproducibility.environment import capture_environment_snapshot  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Snapshot the current environment/version/git state.")
    parser.add_argument("--output", default=Path("artifacts/reports/environment_snapshot.json"), type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshot = capture_environment_snapshot()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    print(json.dumps(snapshot, indent=2))
    print(f"\nWritten to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
