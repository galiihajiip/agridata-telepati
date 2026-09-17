#!/usr/bin/env python3
"""Final compliant training run (Block 15).

Usage:
    python scripts/run_final_training.py --config configs/final_model_config.yaml

Executes the frozen configuration from Block 14 at full scale (fraction=1.0,
the entire prepared train set). Prints every disclosure the master spec
requires before training starts, trains, saves all artifacts, and validates
the resulting weights load and run inference from a completely clean
Python process (not just the training process that produced them).

Never touches test data. No external pretrained weights, no external
dataset, no LLM/API processing — enforced the same way as every prior
training block (YOLO_OFFLINE, architecture-only .yaml construction).
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.dataset.mapping import CANONICAL_CLASSES, CANONICAL_ID_TO_NAME, MAPPING_VERSION  # noqa: E402
from agridata.device import detect_device  # noqa: E402
from agridata.experiments.tracker import compute_manifest_hash  # noqa: E402
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.reproducibility.environment import capture_environment_snapshot, get_git_commit  # noqa: E402
from agridata.seed import set_global_seed  # noqa: E402
from agridata.training.train import run_training  # noqa: E402

logger = logging.getLogger("agridata.scripts.run_final_training")

AUGMENTATION_OVERRIDE_KEYS = {
    "hsv_h", "hsv_s", "hsv_v", "degrees", "translate", "scale", "shear",
    "perspective", "flipud", "fliplr", "mosaic", "mixup", "copy_paste",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Final compliant training run (full scale).")
    parser.add_argument("--config", default=Path("configs/final_model_config.yaml"), type=Path)
    parser.add_argument("--manifest", default=Path("data/prepared/manifest_train.json"), type=Path)
    parser.add_argument("--project", default=Path("runs/detect/final"), type=Path)
    parser.add_argument("--run-name", default="final_model")
    parser.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    return parser.parse_args()


def print_disclosures(cfg: dict, device: str, manifest_hash: str, git_commit: str) -> None:
    import torch
    import ultralytics

    print("=" * 70)
    print("BLOCK 15 — FINAL TRAINING RUN — PRE-TRAINING DISCLOSURES")
    print("=" * 70)
    print(f"1.  Git commit hash:        {git_commit}")
    print(f"2.  Python version:         {sys.version.split()[0]}")
    print(f"3.  Framework versions:     torch={torch.__version__}, ultralytics={ultralytics.__version__}")
    print(f"4.  Seed:                   {cfg['seed']}")
    print(f"5.  Dataset manifest hash:  {manifest_hash} (sha256 of manifest_train.json)")
    print(f"6.  Canonical class mapping (v{MAPPING_VERSION}, {len(CANONICAL_CLASSES)} classes):")
    for cid in sorted(CANONICAL_ID_TO_NAME):
        print(f"      model_class_id={cid - 1}: {CANONICAL_ID_TO_NAME[cid]}")
    print(f"7.  Model architecture:     {cfg['model_arch']} (architecture-only definition)")
    print(f"8.  Pretrained:             {cfg['pretrained']} (must be False)")
    print("9.  Hyperparameters:")
    for key in ("image_size", "batch_size", "epochs", "fraction", "optimizer", "learning_rate",
                "momentum", "weight_decay", "scheduler", "patience", "workers"):
        print(f"      {key}: {cfg.get(key)}")
    print(f"      augmentation overrides: {{k: cfg[k] for k in AUGMENTATION_OVERRIDE_KEYS if k in cfg}}"
          if False else f"      augmentation overrides: {({k: cfg[k] for k in AUGMENTATION_OVERRIDE_KEYS if k in cfg})}")
    print(f"10. Device:                 {device}")
    print(f"11. Output path:            {Path('runs/detect/final').resolve()}")
    print("=" * 70)
    assert cfg["pretrained"] is False, "REFUSING TO TRAIN: pretrained must be False."
    assert not cfg["model_arch"].endswith((".pt", ".pth", ".ckpt")), "REFUSING TO TRAIN: model_arch looks like a checkpoint."


def check_resources() -> dict:
    disk = shutil.disk_usage(".")
    return {"disk_free_gb": round(disk.free / (1024**3), 1), "disk_total_gb": round(disk.total / (1024**3), 1)}


def validate_clean_process_load(weights_path: Path, sample_image: Path) -> dict:
    """Load the checkpoint and run inference in a brand-new Python subprocess —
    not just the training process that produced it — to prove the artifact is
    genuinely portable and loadable independent of any in-memory state."""
    script = f"""
import os
os.environ.setdefault("YOLO_OFFLINE", "1")
from ultralytics import YOLO
model = YOLO(r"{weights_path}")
results = model.predict(r"{sample_image}", verbose=False)
print("CLEAN_LOAD_OK", len(results[0].boxes))
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=120)
    success = result.returncode == 0 and "CLEAN_LOAD_OK" in result.stdout
    return {"success": success, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()[-2000:]}


def main() -> int:
    setup_logging()
    args = parse_args()

    with args.config.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    device = detect_device() if cfg["device"] == "auto" else cfg["device"]
    git_commit = get_git_commit()
    manifest_hash = compute_manifest_hash(args.manifest)

    resources = check_resources()
    logger.info("Resource re-check before final training: %s", resources)
    if resources["disk_free_gb"] < 5.0:
        raise RuntimeError(f"Refusing to start: only {resources['disk_free_gb']}GB free disk.")

    print_disclosures(cfg, device, manifest_hash, git_commit)
    set_global_seed(cfg["seed"])

    extra_kwargs = {
        "optimizer": cfg["optimizer"], "lr0": cfg["learning_rate"],
        "momentum": cfg["momentum"], "weight_decay": cfg["weight_decay"],
        "patience": cfg["patience"],
    }
    extra_kwargs.update({k: cfg[k] for k in AUGMENTATION_OVERRIDE_KEYS if k in cfg})

    started_at = datetime.now(timezone.utc)
    result = run_training(
        model_arch=cfg["model_arch"],
        data_yaml=Path(cfg["data_yaml"]),
        output_project=args.project,
        run_name=args.run_name,
        image_size=cfg["image_size"],
        batch_size=cfg["batch_size"],
        epochs=cfg["epochs"],
        device=device,
        seed=cfg["seed"],
        workers=cfg["workers"],
        fraction=cfg["fraction"],
        plots=True,
        validate=True,
        extra_train_kwargs=extra_kwargs,
    )
    finished_at = datetime.now(timezone.utc)
    duration = (finished_at - started_at).total_seconds()

    logger.info("Training complete in %.1fs. Validating clean-process load...", duration)
    sample_image = next((Path("data/prepared/valid/images")).iterdir())
    clean_load = validate_clean_process_load(Path(result["best_weights"]), sample_image)
    if not clean_load["success"]:
        logger.error("CLEAN PROCESS LOAD FAILED: %s", clean_load["stderr"])
    else:
        logger.info("Clean-process load and inference: SUCCESS (%s)", clean_load["stdout"])

    env_snapshot = capture_environment_snapshot()

    summary = {
        "block": 15,
        "git_commit": git_commit,
        "dataset_manifest_hash": manifest_hash,
        "config_used": cfg,
        "device": device,
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat(),
        "duration_seconds": duration,
        "save_dir": result["save_dir"],
        "best_weights": result["best_weights"],
        "last_weights": result["last_weights"],
        "final_metrics": result["metrics"],
        "resolved_hyperparameters": result["resolved_hyperparameters"],
        "clean_process_load_validation": clean_load,
        "environment_snapshot": env_snapshot,
        "no_external_pretrained_weights": True,
        "no_external_dataset": True,
        "no_llm_api_processing": True,
        "test_data_used_for_tuning": False,
    }

    args.report_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.report_dir / "block15_final_training_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nFinal training summary written to: {summary_path}")
    print(f"Best weights: {result['best_weights']}")
    print(f"Clean-process load validation: {'PASS' if clean_load['success'] else 'FAIL'}")
    return 0 if clean_load["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
