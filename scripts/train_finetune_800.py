#!/usr/bin/env python3
"""Progressive fine-tuning pada resolusi 800 menggunakan bobot model sendiri.

Skrip ini memulai pelatihan dari bobot 100 epoch (self-pretraining / progressive resizing),
BUKAN dari inisialisasi acak dan BUKAN dari external pretrained weights.

Kepatuhan:
- `pretrained=False` ditegakkan.
- `YOLO_OFFLINE=1` aktif.
- Inisialisasi bobot berasal dari pelatihan project ini sendiri.

Penggunaan:
    python scripts/train_finetune_800.py --dry-run
    python scripts/train_finetune_800.py
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("YOLO_OFFLINE", "1")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import yaml  # noqa: E402
from agridata.device import detect_device  # noqa: E402
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.reproducibility.environment import capture_environment_snapshot, get_git_commit  # noqa: E402
from agridata.seed import set_global_seed  # noqa: E402

logger = logging.getLogger("agridata.scripts.train_finetune_800")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Progressive fine-tuning 800px.")
    p.add_argument("--config", default=Path("configs/experiment_800_finetune.yaml"), type=Path)
    p.add_argument("--dry-run", action="store_true", help="Periksa konfigurasi dan bobot tanpa melatih.")
    return p.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()

    with args.config.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    weights_path = Path(cfg["initial_weights"])
    if not weights_path.exists():
        raise SystemExit(f"Bobot awal tidak ditemukan: {weights_path}")

    if cfg.get("pretrained", False):
        raise SystemExit("MENOLAK MELANJUTKAN: pretrained=True dilarang.")

    seed = cfg["seed"]
    set_global_seed(seed)
    device = detect_device() if cfg["device"] == "auto" else cfg["device"]

    print("=" * 64)
    print("PROGRESSIVE FINE-TUNING RESOLUSI 800")
    print("=" * 64)
    print(f"  Bobot inisialisasi : {weights_path}")
    print(f"  Resolusi citra     : {cfg['image_size']}")
    print(f"  Batch size         : {cfg['batch_size']}")
    print(f"  Epochs             : {cfg['epochs']}")
    print(f"  Learning rate      : {cfg['learning_rate']}")
    print(f"  Optimizer          : {cfg['optimizer']}")
    print(f"  Pretrained         : {cfg['pretrained']} (harus False)")
    print(f"  Device             : {device}")
    print("=" * 64)

    if args.dry_run:
        print("\nMode dry-run selesai. Konfigurasi valid.")
        return 0

    from ultralytics import YOLO

    model = YOLO(str(weights_path))

    started = datetime.now(timezone.utc)
    results = model.train(
        data=str(cfg["data_yaml"]),
        imgsz=cfg["image_size"],
        batch=cfg["batch_size"],
        epochs=cfg["epochs"],
        patience=cfg.get("patience", 8),
        lr0=cfg["learning_rate"],
        lrf=cfg.get("lr_factor", 0.01),
        optimizer=cfg["optimizer"],
        momentum=cfg.get("momentum", 0.9),
        weight_decay=cfg.get("weight_decay", 0.0005),
        project="runs/detect/final",
        name="model_800_finetune",
        device=device,
        seed=seed,
        workers=cfg.get("workers", 2),
        pretrained=False,
        flipud=cfg.get("flipud", 0.0),
        plots=True,
    )
    finished = datetime.now(timezone.utc)

    save_dir = Path(getattr(results, "save_dir", "runs/detect/final/model_800_finetune"))
    summary = {
        "model": "model_800_finetune",
        "initial_weights": str(weights_path),
        "image_size": cfg["image_size"],
        "epochs": cfg["epochs"],
        "batch_size": cfg["batch_size"],
        "git_commit": get_git_commit(),
        "dimulai_utc": started.isoformat(),
        "selesai_utc": finished.isoformat(),
        "durasi_detik": (finished - started).total_seconds(),
        "save_dir": str(save_dir),
        "best_weights": str(save_dir / "weights" / "best.pt"),
        "tanpa_external_pretrained_weights": True,
    }

    report_dir = Path("artifacts/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    summary_path = report_dir / "model_800_finetune_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    history = save_dir / "results.csv"
    if history.exists():
        shutil.copyfile(history, report_dir / "model_800_finetune_history.csv")

    print(f"\nPelatihan selesai. Ringkasan tersimpan di: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
