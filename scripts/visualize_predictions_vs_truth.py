#!/usr/bin/env python3
"""Visualisasi ground truth berdampingan dengan prediksi model (BLOCK E).

Menghasilkan dua kelompok gambar dari split validasi:

- kelompok keberhasilan: citra yang memiliki minimal satu true positive dan
  tanpa false negative;
- kelompok kegagalan: citra dengan jumlah kesalahan terbanyak.

Aturan pemilihan dinyatakan eksplisit dan bersifat deterministik, sehingga
sampel tidak dipilih berdasarkan penampilan visual. Kelompok keberhasilan
merupakan ilustrasi kemampuan model, bukan representasi statistik dari
keseluruhan performa.

Prediksi dibaca dari artefak yang sudah tersimpan, tanpa inferensi ulang.

Penggunaan:
    python scripts/visualize_predictions_vs_truth.py
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.dataset.mapping import CANONICAL_CLASSES  # noqa: E402
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.metrics.detection import Detection, GroundTruthBox, compute_iou  # noqa: E402
from agridata.visualization.images import CLASS_COLORS  # noqa: E402

logger = logging.getLogger("agridata.scripts.visualize_predictions_vs_truth")

IOU_THRESHOLD = 0.5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bandingkan ground truth dengan prediksi model.")
    parser.add_argument("--split", default="valid")
    parser.add_argument("--prepared-dir", default=Path("data/prepared"), type=Path)
    parser.add_argument("--predictions", default=None, type=Path)
    parser.add_argument("--confidence-threshold", type=float, default=0.25)
    parser.add_argument("--num-examples", type=int, default=3)
    parser.add_argument(
        "--figures-dir", default=Path("artifacts/figures/final_submission"), type=Path
    )
    return parser.parse_args()


def draw_boxes(image_path: Path, boxes: list[tuple[str, tuple, float | None]]) -> Image.Image:
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    for class_name, (x, y, w, h), conf in boxes:
        color = CLASS_COLORS.get(class_name, "#ff0000")
        draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
        label = class_name if conf is None else f"{class_name} {conf:.2f}"
        draw.text((x + 3, max(y - 12, 2)), label, fill=color)
    return image


def main() -> int:
    setup_logging()
    args = parse_args()
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    predictions_path = args.predictions or Path(f"artifacts/predictions/predictions_{args.split}.json")
    with predictions_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    detections = [
        Detection(r["image_id"], r["class_id"], r["confidence"], tuple(r["bbox_xywh"]))
        for r in raw
        if r["confidence"] >= args.confidence_threshold
    ]

    with (args.prepared_dir / f"manifest_{args.split}.json").open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    images_by_id = {e["original_image_id"]: e for e in manifest}
    gt_by_image: dict[int, list[GroundTruthBox]] = defaultdict(list)
    for entry in manifest:
        for ann in entry["annotations"]:
            gt_by_image[entry["original_image_id"]].append(
                GroundTruthBox(entry["original_image_id"], ann["model_class_id"], tuple(ann["bbox_xywh"]))
            )

    det_by_image: dict[int, list[Detection]] = defaultdict(list)
    for det in detections:
        det_by_image[det.image_id].append(det)

    stats = {}
    for image_id, gts in gt_by_image.items():
        preds = sorted(det_by_image.get(image_id, []), key=lambda d: -d.confidence)
        unmatched = list(range(len(gts)))
        tp = 0
        fp = 0
        for pred in preds:
            best_idx, best_iou = None, 0.0
            for idx in unmatched:
                if gts[idx].class_id != pred.class_id:
                    continue
                iou = compute_iou(pred.bbox_xywh, gts[idx].bbox_xywh)
                if iou >= IOU_THRESHOLD and iou > best_iou:
                    best_idx, best_iou = idx, iou
            if best_idx is None:
                fp += 1
            else:
                unmatched.remove(best_idx)
                tp += 1
        stats[image_id] = {"tp": tp, "fp": fp, "fn": len(unmatched), "n_gt": len(gts)}

    success_ids = sorted(
        (i for i, s in stats.items() if s["tp"] >= 1 and s["fn"] == 0 and s["fp"] == 0),
        key=lambda i: (-stats[i]["tp"], i),
    )[: args.num_examples]

    failure_ids = sorted(
        (i for i, s in stats.items() if s["fn"] + s["fp"] > 0),
        key=lambda i: (-(stats[i]["fn"] + stats[i]["fp"]), i),
    )[: args.num_examples]

    images_dir = args.prepared_dir / args.split / "images"
    outputs = {"success": [], "failure": []}

    for label, ids in (("success", success_ids), ("failure", failure_ids)):
        if not ids:
            continue
        fig, axes = plt.subplots(len(ids), 2, figsize=(11, 5.2 * len(ids)))
        if len(ids) == 1:
            axes = [axes]
        for row, image_id in zip(axes, ids):
            entry = images_by_id[image_id]
            path = images_dir / Path(entry["file_name"]).name
            gt_boxes = [
                (CANONICAL_CLASSES[g.class_id], g.bbox_xywh, None) for g in gt_by_image[image_id]
            ]
            pred_boxes = [
                (CANONICAL_CLASSES[d.class_id], d.bbox_xywh, d.confidence)
                for d in sorted(det_by_image.get(image_id, []), key=lambda d: -d.confidence)
            ]
            row[0].imshow(draw_boxes(path, gt_boxes))
            row[0].set_title(f"Ground truth ({len(gt_boxes)} objek)", fontsize=10)
            row[0].axis("off")
            s = stats[image_id]
            row[1].imshow(draw_boxes(path, pred_boxes))
            row[1].set_title(
                f"Prediksi: TP={s['tp']} FP={s['fp']} FN={s['fn']}", fontsize=10
            )
            row[1].axis("off")
        title = (
            "Contoh prediksi benar (semua objek terdeteksi, tanpa false positive)"
            if label == "success"
            else "Contoh kegagalan (jumlah kesalahan terbanyak)"
        )
        fig.suptitle(title, y=1.0)
        fig.tight_layout()
        out = args.figures_dir / f"{label}_cases_{args.split}.png"
        fig.savefig(out, dpi=110, bbox_inches="tight")
        plt.close(fig)
        outputs[label] = [str(out)]
        logger.info("%s: %s", label, out)

    summary = {
        "split": args.split,
        "confidence_threshold": args.confidence_threshold,
        "iou_threshold": IOU_THRESHOLD,
        "selection_rule": {
            "success": "tp >= 1 dan fn == 0 dan fp == 0, diurutkan menurun berdasarkan jumlah tp lalu image_id",
            "failure": "fn + fp > 0, diurutkan menurun berdasarkan jumlah kesalahan lalu image_id",
        },
        "images_with_perfect_detection": sum(
            1 for s in stats.values() if s["tp"] >= 1 and s["fn"] == 0 and s["fp"] == 0
        ),
        "images_with_any_error": sum(1 for s in stats.values() if s["fn"] + s["fp"] > 0),
        "total_images_with_ground_truth": len(stats),
        "success_image_ids": success_ids,
        "failure_image_ids": failure_ids,
        "figures": outputs,
    }
    report_path = Path("artifacts/reports") / f"prediction_examples_{args.split}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Citra dengan deteksi sempurna : {summary['images_with_perfect_detection']} dari {len(stats)}")
    print(f"Citra dengan minimal satu error: {summary['images_with_any_error']} dari {len(stats)}")
    print(f"Laporan: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
