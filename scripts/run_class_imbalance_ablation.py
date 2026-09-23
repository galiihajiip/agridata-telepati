#!/usr/bin/env python3
"""Ablasi penanganan ketidakseimbangan kelas.

Usage:
    python scripts/run_class_imbalance_ablation.py

Compares baseline (natural class distribution) vs. targeted oversampling of
rare classes (Block 12's chosen mitigation strategy), holding EVERYTHING
else fixed, including total training image COUNT, not just a percentage,
so the comparison isolates the effect of rebalancing class representation
rather than confounding it with "the oversampled run just saw more data."

This is achieved by passing an integer `fraction` to Ultralytics (verified
via source: `ultralytics/data/base.py` uses an int fraction as an absolute
image count, not a percentage), applied to both the original 10,132-image
pool and the oversampled 15,352-entry pool alike.

Validation is the ORIGINAL, unmodified valid split in both cases (see
scripts/prepare_oversampled_train.py, val/test paths are identical files,
not copies). Per-class AP@0.5 is reported specifically for the rare classes
targeted by oversampling, not just the aggregate mAP@0.5, since the whole
point of this ablation is whether THEY improved, an aggregate-only view
could hide a rare-class win under common-class noise, or vice versa.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.dataset.mapping import CANONICAL_CLASSES, CANONICAL_ID_TO_NAME  # noqa: E402
from agridata.device import detect_device  # noqa: E402
from agridata.experiments.tracker import (  # noqa: E402
    ExperimentRecord,
    append_experiment,
    build_markdown_table,
    compute_manifest_hash,
    load_experiments,
)
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.reproducibility.environment import get_git_commit  # noqa: E402
from agridata.seed import set_global_seed  # noqa: E402
from agridata.training.train import run_training  # noqa: E402

logger = logging.getLogger("agridata.scripts.run_class_imbalance_ablation")

COMMON = dict(
    seed=42, model_arch="yolov8n.yaml", pretrained=False, device="auto", workers=2,
    image_size=320, batch_size=16, epochs=5, optimizer="AdamW", learning_rate=0.001,
    momentum=0.9, weight_decay=0.0005,
)
TRAIN_IMAGE_COUNT = 810  # matches Block 10/11's ~8%-of-10132 screening scale


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baseline vs. rare-class-oversampling ablation.")
    parser.add_argument("--baseline-data-yaml", default=Path("data/prepared/data.yaml"), type=Path)
    parser.add_argument("--oversampled-data-yaml", default=Path("data/prepared_oversampled/data.yaml"), type=Path)
    parser.add_argument("--manifest", default=Path("data/prepared/manifest_train.json"), type=Path)
    parser.add_argument("--rare-classes", nargs="+", required=True)
    parser.add_argument("--project", default=Path("runs/detect/class_imbalance"), type=Path)
    parser.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    parser.add_argument("--start-experiment-num", type=int, default=18)
    return parser.parse_args()


def run_one(experiment_id: str, label: str, data_yaml: Path, notes: str, project: Path, git_commit: str, manifest_hash: str) -> dict:
    device = detect_device()
    set_global_seed(COMMON["seed"])

    logger.info("=== Experiment %s (%s) ===", experiment_id, label)
    started_at = time.monotonic()
    result = run_training(
        model_arch=COMMON["model_arch"],
        data_yaml=data_yaml,
        output_project=project,
        run_name=experiment_id,
        image_size=COMMON["image_size"],
        batch_size=COMMON["batch_size"],
        epochs=COMMON["epochs"],
        device=device,
        seed=COMMON["seed"],
        workers=COMMON["workers"],
        fraction=TRAIN_IMAGE_COUNT,  # int -> absolute image count, not a percentage (verified via source)
        plots=False,
        validate=False,
        extra_train_kwargs={
            "optimizer": COMMON["optimizer"], "lr0": COMMON["learning_rate"],
            "momentum": COMMON["momentum"], "weight_decay": COMMON["weight_decay"],
        },
    )
    duration = time.monotonic() - started_at

    from ultralytics import YOLO

    model = YOLO(result["best_weights"])
    val_results = model.val(data=str(data_yaml), split="val", plots=False, verbose=False, device=device)

    per_class_ap50 = {}
    for idx, class_id in enumerate(val_results.box.ap_class_index):
        per_class_ap50[CANONICAL_ID_TO_NAME[int(class_id) + 1]] = float(val_results.box.ap50[idx])

    record = ExperimentRecord(
        experiment_id=experiment_id,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=git_commit,
        seed=COMMON["seed"],
        model_architecture=COMMON["model_arch"],
        pretrained=COMMON["pretrained"],
        dataset_manifest_hash=manifest_hash,
        image_size=COMMON["image_size"],
        batch_size=COMMON["batch_size"],
        epochs=COMMON["epochs"],
        optimizer=result["resolved_hyperparameters"]["optimizer"],
        learning_rate=result["resolved_hyperparameters"]["learning_rate"],
        weight_decay=result["resolved_hyperparameters"]["weight_decay"],
        scheduler=result["resolved_hyperparameters"]["scheduler"],
        augmentation_config=result["resolved_hyperparameters"]["augmentation"],
        device=device,
        best_val_map50=float(val_results.box.map50),
        best_val_f1=None,
        precision=float(val_results.box.mp),
        recall=float(val_results.box.mr),
        training_duration_seconds=duration,
        notes=notes,
        compliance_notes="No external pretrained weights. YOLO_OFFLINE enforced. Val/test data identical to Block 5's original, unmodified prepared directories.",
    )
    return {"label": label, "record": record, "per_class_ap50": per_class_ap50}


def build_report(baseline: dict, oversampled: dict, rare_classes: list[str]) -> str:
    lines = [
        "# Ablasi Mitigasi Ketidakseimbangan Kelas",
        "",
        f"Kedua eksekusi memakai JUMLAH citra latih yang identik ({TRAIN_IMAGE_COUNT}), yaitu jumlah "
        "absolut melalui `fraction` bertipe bilangan bulat, yang sudah diverifikasi lewat kode sumber "
        "bahwa nilainya bukan persentase. Satu-satunya perbedaan adalah apakah citra kelas minoritas "
        "digandakan di dalam kumpulan penyampelan. Seed sama, hyperparameter sama, dan data validasi "
        "sama, dengan berkas yang identik byte per byte pada kedua kasus.",
        "",
        f"Kelas minoritas yang menjadi sasaran oversampling, yaitu kelas dengan jumlah instance kurang "
        f"dari 20 persen kelas terbanyak menurut `artifacts/reports/class_imbalance_diagnostics.md`: "
        f"{rare_classes}",
        "",
        "## Hasil keseluruhan",
        "",
        "| Eksekusi | mAP@0.5 | Precision | Recall | Durasi (detik) |",
        "|---|---:|---:|---:|---:|",
        f"| baseline, distribusi alami | {baseline['record'].best_val_map50:.4f} | {baseline['record'].precision:.4f} | {baseline['record'].recall:.4f} | {baseline['record'].training_duration_seconds:.1f} |",
        f"| oversampled, kelas minoritas 3 kali | {oversampled['record'].best_val_map50:.4f} | {oversampled['record'].precision:.4f} | {oversampled['record'].recall:.4f} | {oversampled['record'].training_duration_seconds:.1f} |",
        "",
        "## AP@0.5 per kelas, khusus kelas minoritas, yang menjadi inti ablasi ini",
        "",
        "| Kelas | AP@0.5 baseline | AP@0.5 oversampled | Selisih |",
        "|---|---:|---:|---:|",
    ]
    for cls in rare_classes:
        b = baseline["per_class_ap50"].get(cls, 0.0)
        o = oversampled["per_class_ap50"].get(cls, 0.0)
        lines.append(f"| {cls} | {b:.4f} | {o:.4f} | {o - b:+.4f} |")

    lines += ["", "## AP@0.5 per kelas, seluruh kelas, untuk memastikan oversampling tidak merugikan kelas mayoritas", "", "| Kelas | AP@0.5 baseline | AP@0.5 oversampled | Selisih |", "|---|---:|---:|---:|"]
    for cls in CANONICAL_CLASSES:
        b = baseline["per_class_ap50"].get(cls, 0.0)
        o = oversampled["per_class_ap50"].get(cls, 0.0)
        marker = " (minoritas, disasar)" if cls in rare_classes else ""
        lines.append(f"| {cls}{marker} | {b:.4f} | {o:.4f} | {o - b:+.4f} |")

    rare_deltas = [oversampled["per_class_ap50"].get(c, 0.0) - baseline["per_class_ap50"].get(c, 0.0) for c in rare_classes]
    common_classes = [c for c in CANONICAL_CLASSES if c not in rare_classes]
    common_deltas = [oversampled["per_class_ap50"].get(c, 0.0) - baseline["per_class_ap50"].get(c, 0.0) for c in common_classes]
    avg_rare_delta = sum(rare_deltas) / len(rare_deltas) if rare_deltas else 0.0
    avg_common_delta = sum(common_deltas) / len(common_deltas) if common_deltas else 0.0

    lines += [
        "",
        "## Kesimpulan",
        "",
        f"Rata-rata selisih AP@0.5 pada kelas minoritas yang disasar: {avg_rare_delta:+.4f}",
        f"Rata-rata selisih AP@0.5 pada kelas mayoritas yang tidak disasar: {avg_common_delta:+.4f}",
        "",
    ]
    if avg_rare_delta > 0 and avg_rare_delta > avg_common_delta:
        verdict = (
            "Oversampling menunjukkan manfaat bersih yang terukur bagi kelas minoritas yang disasar pada "
            "skala penyaringan ini, tanpa disertai kerugian yang lebih besar pada kelas mayoritas. "
            "Layak dibawa sebagai kandidat konfigurasi final, tetapi TIDAK diadopsi secara otomatis, "
            "dan masih menunggu verifikasi ulang pada skala pelatihan penuh."
        )
    else:
        verdict = (
            "Oversampling TIDAK menunjukkan manfaat bersih yang jelas pada skala penyaringan ini, entah "
            "karena kelas minoritas tidak membaik, karena perbaikannya kalah oleh kerugian pada kelas "
            "mayoritas, atau keduanya sekaligus. Berdasarkan bukti ini, strategi tersebut TIDAK "
            "direkomendasikan untuk diadopsi. Pengujian ulang pada skala pelatihan penuh masih layak "
            "dipertimbangkan, karena efek ketidakseimbangan kelas dapat berperilaku berbeda dengan "
            "data dan epoch yang lebih banyak."
        )
    lines.append(verdict)
    return "\n".join(lines) + "\n"


def main() -> int:
    setup_logging()
    args = parse_args()

    git_commit = get_git_commit()
    manifest_hash = compute_manifest_hash(args.manifest)

    baseline = run_one(
        f"E{args.start_experiment_num:02d}", "baseline (natural distribution)",
        args.baseline_data_yaml, "Ablasi ketidakseimbangan kelas: baseline dengan distribusi kelas alami.",
        args.project, git_commit, manifest_hash,
    )
    append_experiment(baseline["record"])

    oversampled = run_one(
        f"E{args.start_experiment_num + 1:02d}", "oversampled (rare classes x3)",
        args.oversampled_data_yaml, f"Ablasi ketidakseimbangan kelas: kelas minoritas {args.rare_classes} di-oversample 3 kali.",
        args.project, git_commit, manifest_hash,
    )
    append_experiment(oversampled["record"])

    args.report_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(baseline, oversampled, args.rare_classes)
    (args.report_dir / "block12_class_imbalance_ablation.md").write_text(report, encoding="utf-8")

    all_records = load_experiments()
    (Path("artifacts/experiments") / "experiment_log.md").write_text(build_markdown_table(all_records), encoding="utf-8")

    print(report)
    print("Report: artifacts/reports/block12_class_imbalance_ablation.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
