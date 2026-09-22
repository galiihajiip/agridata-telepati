#!/usr/bin/env python3
"""Melanjutkan pelatihan resolusi 960 dari checkpoint terakhir.

Pelatihan resolusi 960 dijeda pada epoch tertentu agar GPU dapat dipakai untuk
finalisasi paket submission. Skrip ini melanjutkan pelatihan dari titik jeda
tersebut, bukan mengulang dari nol.

Cara kerja resume pada Ultralytics: berkas `last.pt` yang ditulis pada akhir
setiap epoch menyimpan bobot, state optimizer, EMA, jumlah update, dan
konfigurasi pelatihan. Selama pelatihan belum selesai secara normal,
checkpoint tersebut belum dilucuti state optimizernya sehingga masih dapat
dilanjutkan.

Catatan kepatuhan: melanjutkan pelatihan sendiri bukan penggunaan external
pretrained weights. Checkpoint berasal dari pelatihan project ini, dimulai
dari inisialisasi acak, dan tidak pernah memuat bobot dari sumber luar.

Penggunaan:
    python scripts/resume_training_960.py --dry-run     # periksa saja
    python scripts/resume_training_960.py               # lanjutkan pelatihan
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

from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.reproducibility.environment import capture_environment_snapshot, get_git_commit  # noqa: E402
from agridata.seed import set_global_seed  # noqa: E402

logger = logging.getLogger("agridata.scripts.resume_training_960")

DEFAULT_CHECKPOINT = Path("runs/detect/final/final_model_960/weights/last.pt")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Lanjutkan pelatihan 960 dari checkpoint terakhir.")
    p.add_argument("--checkpoint", default=DEFAULT_CHECKPOINT, type=Path)
    p.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    p.add_argument("--dry-run", action="store_true", help="Periksa kelayakan resume tanpa melatih.")
    return p.parse_args()


def inspect_checkpoint(path: Path) -> dict:
    """Membaca metadata checkpoint dan menilai apakah dapat dilanjutkan."""
    import torch

    if not path.exists():
        raise SystemExit(f"Checkpoint tidak ditemukan: {path}")

    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    train_args = ckpt.get("train_args", {}) or {}
    epoch = ckpt.get("epoch", -1)
    total = train_args.get("epochs")

    info = {
        "path": str(path),
        "epoch_terakhir_selesai": epoch,
        "epoch_berikutnya": epoch + 1,
        "total_epoch": total,
        "sisa_epoch": (total - (epoch + 1)) if isinstance(total, int) else None,
        "ada_optimizer_state": ckpt.get("optimizer") is not None,
        "ada_ema": ckpt.get("ema") is not None,
        "updates": ckpt.get("updates"),
        "best_fitness": ckpt.get("best_fitness"),
        "imgsz": train_args.get("imgsz"),
        "batch": train_args.get("batch"),
        "seed": train_args.get("seed"),
        "model": train_args.get("model"),
        "pretrained": train_args.get("pretrained"),
    }

    alasan = []
    if not info["ada_optimizer_state"]:
        alasan.append("state optimizer sudah dilucuti, pelatihan kemungkinan sudah selesai normal")
    if epoch < 0:
        alasan.append("epoch bernilai -1, menandakan checkpoint final yang sudah dilucuti")
    if isinstance(total, int) and epoch + 1 >= total:
        alasan.append(f"epoch berikutnya {epoch + 1} sudah mencapai total {total}")

    info["dapat_dilanjutkan"] = not alasan
    info["alasan_tidak_dapat_dilanjutkan"] = alasan
    return info


def main() -> int:
    setup_logging()
    args = parse_args()

    info = inspect_checkpoint(args.checkpoint)

    print("=" * 64)
    print("PEMERIKSAAN CHECKPOINT SEBELUM MELANJUTKAN PELATIHAN")
    print("=" * 64)
    print(f"  Checkpoint            : {info['path']}")
    print(f"  Epoch terakhir selesai: {info['epoch_terakhir_selesai']}")
    print(f"  Akan lanjut dari epoch: {info['epoch_berikutnya']}")
    print(f"  Total epoch           : {info['total_epoch']}")
    print(f"  Sisa epoch            : {info['sisa_epoch']}")
    print(f"  Ukuran citra          : {info['imgsz']}")
    print(f"  Batch                 : {info['batch']}")
    print(f"  Seed                  : {info['seed']}")
    print(f"  Arsitektur            : {info['model']}")
    print(f"  Pretrained            : {info['pretrained']} (harus False)")
    print(f"  State optimizer       : {'ada' if info['ada_optimizer_state'] else 'TIDAK ADA'}")
    print(f"  EMA                   : {'ada' if info['ada_ema'] else 'TIDAK ADA'}")
    print(f"  Jumlah update         : {info['updates']}")
    print(f"  Best fitness          : {info['best_fitness']}")
    print("=" * 64)

    if info["pretrained"]:
        raise SystemExit("MENOLAK MELANJUTKAN: train_args menunjukkan pretrained=True.")

    if not info["dapat_dilanjutkan"]:
        print("\nCheckpoint TIDAK dapat dilanjutkan:")
        for a in info["alasan_tidak_dapat_dilanjutkan"]:
            print(f"  - {a}")
        print("\nUntuk melatih ulang dari awal gunakan:")
        print("  python scripts/run_final_training.py --config configs/final_model_config_960.yaml \\")
        print("      --run-name final_model_960")
        return 1

    print("\nStatus: checkpoint dapat dilanjutkan.")

    if args.dry_run:
        print("Mode dry-run, pelatihan tidak dijalankan.")
        return 0

    set_global_seed(info["seed"] if isinstance(info["seed"], int) else 42)
    git_commit = get_git_commit()
    started = datetime.now(timezone.utc)

    logger.info("Melanjutkan pelatihan dari epoch %d menuju %d", info["epoch_berikutnya"], info["total_epoch"])

    from ultralytics import YOLO

    model = YOLO(str(args.checkpoint))
    results = model.train(resume=True)

    finished = datetime.now(timezone.utc)
    save_dir = Path(getattr(results, "save_dir", args.checkpoint.parent.parent))

    summary = {
        "jenis": "resume",
        "checkpoint_awal": str(args.checkpoint),
        "epoch_mulai": info["epoch_berikutnya"],
        "total_epoch": info["total_epoch"],
        "git_commit": git_commit,
        "dimulai_utc": started.isoformat(),
        "selesai_utc": finished.isoformat(),
        "durasi_detik": (finished - started).total_seconds(),
        "save_dir": str(save_dir),
        "environment": capture_environment_snapshot(),
        "tanpa_external_pretrained_weights": True,
        "tanpa_dataset_eksternal": True,
        "catatan": (
            "Pelatihan dilanjutkan dari checkpoint milik project ini sendiri. "
            "Checkpoint berasal dari pelatihan yang dimulai dari inisialisasi acak."
        ),
    }

    args.report_dir.mkdir(parents=True, exist_ok=True)
    out = args.report_dir / "training_960_resume_summary.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    history = save_dir / "results.csv"
    if history.exists():
        shutil.copyfile(history, args.report_dir / "training_960_history.csv")

    print(f"\nPelatihan selesai. Durasi {summary['durasi_detik'] / 3600:.2f} jam.")
    print(f"Ringkasan: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
