#!/usr/bin/env python3
"""CLI for compliant baseline training (Block 6).

Usage:
    python scripts/train.py --config configs/experiments/baseline_smoke.yaml

This is a SMOKE TEST, not final training, see the config file's header
comment. No external pretrained weights are used; see
src/agridata/training/train.py for the enforced compliance checks.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.device import detect_device  # noqa: E402
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.reproducibility.environment import get_git_commit  # noqa: E402
from agridata.seed import set_global_seed  # noqa: E402
from agridata.training.train import run_training  # noqa: E402

logger = logging.getLogger("agridata.scripts.train")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compliant object-detection training (no external pretrained weights).")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--summary-dir", default=Path("artifacts/reports"), type=Path)
    return parser.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()

    with args.config.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    seed = cfg["seed"]
    set_global_seed(seed)
    device = detect_device() if cfg["device"] == "auto" else cfg["device"]

    logger.info("=== Compliant Baseline Training (Block 6) ===")
    logger.info("Git commit: %s", get_git_commit() or "unknown")
    logger.info("Seed: %d", seed)
    logger.info("Device: %s", device)
    logger.info("Model architecture: %s (pretrained=%s)", cfg["model_arch"], cfg["pretrained"])
    logger.info("Data config: %s", cfg["data_yaml"])
    logger.info("YOLO_OFFLINE enforced: any accidental network/download call will raise loudly.")

    started_at = datetime.now(timezone.utc)
    result = run_training(
        model_arch=cfg["model_arch"],
        data_yaml=Path(cfg["data_yaml"]),
        output_project=Path(cfg["project"]),
        run_name=cfg["name"],
        image_size=cfg["image_size"],
        batch_size=cfg["batch_size"],
        epochs=cfg["epochs"],
        device=device,
        seed=seed,
        workers=cfg.get("workers", 2),
        fraction=cfg.get("fraction", 1.0),
        plots=cfg.get("plots", False),
    )
    finished_at = datetime.now(timezone.utc)

    summary = {
        "block": 6,
        "git_commit": get_git_commit(),
        "seed": seed,
        "device": device,
        "model_arch": cfg["model_arch"],
        "pretrained": cfg["pretrained"],
        "data_yaml": cfg["data_yaml"],
        "image_size": cfg["image_size"],
        "batch_size": cfg["batch_size"],
        "epochs": cfg["epochs"],
        "fraction": cfg.get("fraction", 1.0),
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat(),
        "duration_seconds": (finished_at - started_at).total_seconds(),
        "save_dir": result["save_dir"],
        "best_weights": result["best_weights"],
        "last_weights": result["last_weights"],
        "final_metrics": result["metrics"],
        "resolved_hyperparameters": result["resolved_hyperparameters"],
        "yolo_offline_enforced": True,
    }

    args.summary_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.summary_dir / "block6_baseline_smoke_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"\nSummary written to: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
