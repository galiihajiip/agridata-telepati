#!/usr/bin/env python3
"""Analisis sensitivitas metrik lokal terhadap confidence threshold (BLOCK E).

Menggunakan prediksi mentah yang sudah dikumpulkan oleh `scripts/evaluate.py`
pada threshold pengumpulan yang sangat rendah, lalu menyaringnya kembali pada
berbagai threshold. Karena tidak ada inferensi ulang, hasil analisis ini
bersifat deterministik dan tidak terpengaruh nondeterminisme backend MPS yang
terdokumentasi pada project ini.

Threshold tidak pernah dipilih berdasarkan data uji. Seluruh analisis
dijalankan pada split validasi.

Penggunaan:
    python scripts/threshold_sensitivity.py
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.dataset.mapping import CANONICAL_CLASSES  # noqa: E402
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.metrics.detection import (  # noqa: E402
    Detection,
    GroundTruthBox,
    match_detections_to_ground_truth,
)
from agridata.visualization.distributions import plot_threshold_sensitivity  # noqa: E402

logger = logging.getLogger("agridata.scripts.threshold_sensitivity")

DEFAULT_THRESHOLDS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sensitivitas precision, recall, dan F1 terhadap threshold.")
    parser.add_argument("--split", default="valid", choices=["train", "valid"])
    parser.add_argument("--predictions", default=None, type=Path)
    parser.add_argument("--prepared-dir", default=Path("data/prepared"), type=Path)
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    parser.add_argument("--figures-dir", default=Path("artifacts/figures/final_submission"), type=Path)
    return parser.parse_args()


def load_ground_truth(manifest_path: Path) -> list[GroundTruthBox]:
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)
    return [
        GroundTruthBox(entry["original_image_id"], ann["model_class_id"], tuple(ann["bbox_xywh"]))
        for entry in manifest
        for ann in entry["annotations"]
    ]


def main() -> int:
    setup_logging()
    args = parse_args()

    predictions_path = args.predictions or Path(f"artifacts/predictions/predictions_{args.split}.json")
    if not predictions_path.exists():
        raise SystemExit(
            f"Prediksi tidak ditemukan pada {predictions_path}. "
            f"Jalankan scripts/evaluate.py --split {args.split} terlebih dahulu."
        )

    with predictions_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    detections = [
        Detection(r["image_id"], r["class_id"], r["confidence"], tuple(r["bbox_xywh"])) for r in raw
    ]
    ground_truths = load_ground_truth(args.prepared_dir / f"manifest_{args.split}.json")

    logger.info("Prediksi: %d | ground truth: %d", len(detections), len(ground_truths))

    rows = []
    for threshold in DEFAULT_THRESHOLDS:
        result = match_detections_to_ground_truth(
            detections, ground_truths, confidence_threshold=threshold, iou_threshold=args.iou_threshold
        )
        overall = result["overall"]
        rows.append({
            "threshold": threshold,
            "precision": overall.precision,
            "recall": overall.recall,
            "f1": overall.f1,
            "true_positives": overall.true_positives,
            "false_positives": overall.false_positives,
            "false_negatives": overall.false_negatives,
        })
        logger.info(
            "threshold=%.2f P=%.4f R=%.4f F1=%.4f", threshold, overall.precision, overall.recall, overall.f1
        )

    best = max(rows, key=lambda r: r["f1"])
    report = {
        "split": args.split,
        "iou_threshold": args.iou_threshold,
        "num_detections_collected": len(detections),
        "num_ground_truth_boxes": len(ground_truths),
        "predictions_artifact": str(predictions_path),
        "deterministic": True,
        "determinism_note": (
            "Dihitung ulang dari prediksi yang sudah tersimpan, tanpa inferensi ulang, "
            "sehingga tidak terpengaruh nondeterminisme backend MPS."
        ),
        "threshold_not_tuned_on_test": True,
        "rows": rows,
        "best_f1_row": best,
    }

    args.report_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.report_dir / f"threshold_sensitivity_{args.split}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    figure_path = plot_threshold_sensitivity(rows, args.figures_dir / f"threshold_sensitivity_{args.split}.png")

    print(f"\n{'Threshold':>10s} {'Precision':>10s} {'Recall':>9s} {'F1':>9s} {'TP':>7s} {'FP':>7s} {'FN':>7s}")
    for r in rows:
        print(
            f"{r['threshold']:10.2f} {r['precision']:10.4f} {r['recall']:9.4f} {r['f1']:9.4f} "
            f"{r['true_positives']:7d} {r['false_positives']:7d} {r['false_negatives']:7d}"
        )
    print(f"\nF1 tertinggi: {best['f1']:.4f} pada threshold {best['threshold']:.2f}")
    print(f"Laporan: {report_path}")
    print(f"Figur  : {figure_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
