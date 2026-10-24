#!/usr/bin/env python3
"""Mendaftarkan sebuah run sebagai model final submission.

Pemakaian:
    python scripts/register_final_model.py \
        --run-dir runs/detect/final/yolov8s_p2_640_250ep \
        --config configs/kaggle/yolov8s_p2_640_250ep.yaml \
        --platform "Kaggle Notebooks, 2x NVIDIA Tesla T4 (DDP)"

Model final dilatih di luar mesin ini (Kaggle), sehingga ringkasan pelatihan
tidak dapat ditulis oleh proses pelatihan itu sendiri seperti pada
scripts/run_final_training.py. Skrip ini menyusunnya dari artefak yang dibawa
pulang: best.pt, results.csv, dan config yang dipakai. Seluruh angka metrik
dibaca dari laporan evaluasi yang sudah ada, tidak dihitung ulang, agar tetap
ada satu sumber kebenaran untuk setiap angka.

Berkas yang ditulis:
  - artifacts/reports/block15_final_training_summary.json
  - artifacts/reports/final_model_metadata.json
  - artifacts/reports/final_training_history.csv
  - weights/best.pt.sha256

Menjalankan ulang skrip dengan run lain akan menimpa keempatnya, sehingga
penggantian model final cukup dilakukan dengan satu perintah.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agridata.dataset.mapping import CANONICAL_CLASSES, MAPPING_VERSION  # noqa: E402
from agridata.experiments.tracker import compute_manifest_hash  # noqa: E402
from agridata.reproducibility.environment import get_git_commit  # noqa: E402
from run_final_training import validate_clean_process_load  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "artifacts" / "reports"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register a training run as the final submission model.")
    parser.add_argument("--run-dir", required=True, type=Path, help="Folder berisi weights/best.pt dan results.csv.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--platform", required=True, help="Perangkat pelatihan, dicatat apa adanya.")
    parser.add_argument("--manifest", default=Path("data/prepared/manifest_train.json"), type=Path)
    return parser.parse_args()


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_history(results_csv: Path) -> list[dict[str, float]]:
    with results_csv.open("r", encoding="utf-8") as f:
        return [{k.strip(): float(v) for k, v in row.items()} for row in csv.DictReader(f)]


def reported_metrics(split: str, rel_weights: str) -> dict | None:
    """Angka dari laporan evaluasi, hanya bila laporan itu untuk bobot yang sama.

    Laporan dari model sebelumnya bisa masih tersisa di direktori laporan,
    misalnya split test yang baru dievaluasi setelah pilihan model dibekukan.
    Tanpa pengecekan ini metadata dapat mencampur angka dua model berbeda."""
    path = REPORTS_DIR / f"evaluation_{split}.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        report = json.load(f)
    if Path(report["weights"]).as_posix() != rel_weights:
        print(f"Mengabaikan {path.name}: dievaluasi untuk {report['weights']}, bukan {rel_weights}")
        return None
    native = report["native_metrics"]
    return {
        "mAP50": native["mAP50"],
        "macro_f1": native["macro_f1"],
        "mAP50_95": native["mAP50_95"],
        "macro_f1_confidence": native["macro_f1_confidence"],
        "source": f"artifacts/reports/evaluation_{split}.json",
    }


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir
    weights = run_dir / "weights" / "best.pt"
    results_csv = run_dir / "results.csv"
    for p in (weights, results_csv, args.config):
        if not p.exists():
            raise FileNotFoundError(p)

    with args.config.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg["pretrained"] is False, "REFUSING: pretrained must be False."

    from ultralytics import YOLO

    ckpt_args = YOLO(str(weights)).ckpt.get("train_args", {})
    if ckpt_args.get("pretrained") or ckpt_args.get("model") != cfg["model_arch"]:
        raise RuntimeError(f"Checkpoint tidak cocok dengan config: {ckpt_args.get('model')} vs {cfg['model_arch']}")

    history = load_history(results_csv)
    best = max(history, key=lambda r: 0.1 * r["metrics/mAP50(B)"] + 0.9 * r["metrics/mAP50-95(B)"])
    duration = history[-1]["time"]
    checksum = sha256_of(weights)
    manifest_hash = compute_manifest_hash(args.manifest)
    rel_weights = weights.resolve().relative_to(PROJECT_ROOT).as_posix()

    sample_image = next((PROJECT_ROOT / "data/prepared/valid/images").iterdir())
    clean_load = validate_clean_process_load(weights.resolve(), sample_image)

    summary = {
        "block": 15,
        "training_platform": args.platform,
        "git_commit": get_git_commit(),
        "git_commit_note": "Commit saat model didaftarkan. Kode pelatihan berasal dari GitHub repository ini, di-clone pada awal sesi Kaggle.",
        "dataset_manifest_hash": manifest_hash,
        "config_used": cfg,
        "config_path": args.config.as_posix(),
        "device": ckpt_args.get("device"),
        "duration_seconds": duration,
        "epochs_completed": int(history[-1]["epoch"]),
        "best_epoch": int(best["epoch"]),
        "save_dir": run_dir.as_posix(),
        "best_weights": rel_weights,
        "final_metrics": {k: v for k, v in best.items() if k.startswith("metrics/")},
        "final_metrics_note": "Metrik validasi per epoch dari Ultralytics (NMS IoU 0,7). Angka yang dilaporkan berasal dari evaluation_valid.json (NMS IoU 0,5).",
        "resolved_hyperparameters": {k: ckpt_args.get(k) for k in (
            "model", "imgsz", "batch", "epochs", "optimizer", "lr0", "momentum", "weight_decay",
            "cos_lr", "close_mosaic", "patience", "seed", "amp", "mosaic", "fliplr", "flipud",
        )},
        "clean_process_load_validation": clean_load,
        "no_external_pretrained_weights": True,
        "no_external_dataset": True,
        "no_llm_api_processing": True,
        "test_data_used_for_tuning": False,
    }

    metadata = {
        "model_name": f"agridata-telepati8-{Path(cfg['model_arch']).stem}",
        "architecture": f"{Path(cfg['model_arch']).stem} (Ultralytics), dibangun dari definisi arsitektur {cfg['model_arch']}, pretrained=False",
        "task": "object_detection",
        "num_classes": len(CANONICAL_CLASSES),
        "class_names": [c for c in CANONICAL_CLASSES],
        "mapping_version": MAPPING_VERSION,
        "input": {"image_size": cfg["image_size"], "channels": 3, "format": "RGB"},
        "output": "bounding box (xyxy) + kelas + confidence, per kelas canonical",
        "training_config_path": args.config.as_posix(),
        "compliance": {
            "external_pretrained_weights": False,
            "external_dataset_used": False,
            "llm_api_dataset_processing": False,
            "yolo_offline_enforced": True,
            "amp_check_pretrained_download_blocked": True,
            "test_data_used_for_tuning": False,
            "official_splits_preserved": True,
        },
        "status": "FINAL, bobot dihasilkan dan dievaluasi",
        "registered_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit_at_registration": get_git_commit(),
        "dataset_manifest_hash": manifest_hash,
        "weights_path": rel_weights,
        "weights_checksum_sha256": checksum,
        "weights_size_bytes": weights.stat().st_size,
        "clean_process_load_and_inference_validated": clean_load["success"],
        "training": {
            "platform": args.platform,
            "epochs_configured": cfg["epochs"],
            "epochs_completed": int(history[-1]["epoch"]),
            "best_epoch": int(best["epoch"]),
            "duration_hours": round(duration / 3600, 2),
            "seed": cfg["seed"],
        },
        "reported_metrics": {
            "inference_image_size": cfg["image_size"],
            "nms_iou": 0.5,
            "valid": reported_metrics("valid", rel_weights),
            "test": reported_metrics("test", rel_weights),
        },
        "release": {"published": False, "method": None, "url": None},
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with (REPORTS_DIR / "block15_final_training_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    with (REPORTS_DIR / "final_model_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    shutil.copyfile(results_csv, REPORTS_DIR / "final_training_history.csv")
    (PROJECT_ROOT / "weights" / "best.pt.sha256").write_text(f"{checksum}  {rel_weights}\n", encoding="utf-8")

    print(f"Model final terdaftar: {rel_weights}")
    print(f"SHA-256: {checksum}")
    print(f"Epoch: {int(history[-1]['epoch'])} selesai, terbaik {int(best['epoch'])}, {duration / 3600:.2f} jam")
    print(f"Validasi muat proses bersih: {'LULUS' if clean_load['success'] else 'GAGAL'}")
    for split in ("valid", "test"):
        m = metadata["reported_metrics"][split]
        print(f"{split}: " + (f"mAP@50={m['mAP50']:.4f} F1={m['macro_f1']:.4f}" if m else "belum dievaluasi"))
    return 0 if clean_load["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
