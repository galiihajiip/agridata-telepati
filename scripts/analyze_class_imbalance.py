#!/usr/bin/env python3
"""Class imbalance diagnostics (Block 12).

Usage:
    python scripts/analyze_class_imbalance.py --dataset-root "<PATH>"

Reuses the Block 4 stats module (agridata.dataset.stats) for consistency
rather than recomputing counts a different way. Read-only against the raw
dataset. Reports instance/image counts, relative frequency, min/max
imbalance ratio, rare classes, and "visually difficult" classes (via median
bbox area — small objects are harder to localize, per the Block 4 finding
that disease-lesion classes have systematically smaller boxes than
whole-plant labels like Healthy).
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.dataset.mapping import CANONICAL_CLASSES  # noqa: E402
from agridata.dataset.stats import (  # noqa: E402
    class_image_counts,
    class_instance_counts,
    load_canonical_split,
)

DEFAULT_ANNOTATION_FILENAME = "_annotations.coco.json"
# A class is flagged "rare" if its instance count is below this fraction of
# the most common class's count. 20% is a round, documented threshold, not
# tuned to this dataset's specific numbers.
RARE_CLASS_THRESHOLD_FRACTION = 0.20
# A class is flagged "small-object / visually difficult" if its median bbox
# area is below this fraction of the largest class's median area.
SMALL_OBJECT_THRESHOLD_FRACTION = 0.10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Class imbalance diagnostics (read-only).")
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--split", default="train")
    parser.add_argument("--annotation-filename", default=DEFAULT_ANNOTATION_FILENAME)
    parser.add_argument("--output-dir", default=Path("artifacts/reports"), type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    split_data = load_canonical_split(args.dataset_root, args.split, args.annotation_filename)

    instance_counts = class_instance_counts(split_data)
    image_counts = class_image_counts(split_data)

    areas_by_class: dict[str, list[float]] = {}
    for ann in split_data.annotations:
        areas_by_class.setdefault(ann.canonical_class, []).append(ann.bbox[2] * ann.bbox[3])
    median_area = {cls: statistics.median(areas) for cls, areas in areas_by_class.items()}

    total_instances = sum(instance_counts.values())
    max_count = max(instance_counts.values())
    max_area = max(median_area.values())

    per_class = []
    for cls in CANONICAL_CLASSES:
        count = instance_counts.get(cls, 0)
        per_class.append({
            "canonical_class": cls,
            "instance_count": count,
            "image_count": image_counts.get(cls, 0),
            "relative_frequency_pct": round(100 * count / total_instances, 2) if total_instances else 0.0,
            "median_bbox_area_px2": round(median_area.get(cls, 0.0), 1),
            "is_rare": count < RARE_CLASS_THRESHOLD_FRACTION * max_count,
            "is_small_object": median_area.get(cls, 0.0) < SMALL_OBJECT_THRESHOLD_FRACTION * max_area,
        })

    min_count = min(instance_counts.values())
    imbalance_ratio = max_count / min_count if min_count else float("inf")

    rare_classes = [c["canonical_class"] for c in per_class if c["is_rare"]]
    small_object_classes = [c["canonical_class"] for c in per_class if c["is_small_object"]]

    report = {
        "split": args.split,
        "total_instances": total_instances,
        "num_classes": len(CANONICAL_CLASSES),
        "max_min_imbalance_ratio": round(imbalance_ratio, 2),
        "rare_class_threshold_fraction": RARE_CLASS_THRESHOLD_FRACTION,
        "small_object_threshold_fraction": SMALL_OBJECT_THRESHOLD_FRACTION,
        "rare_classes": rare_classes,
        "small_object_classes": small_object_classes,
        "per_class": per_class,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "class_imbalance_diagnostics.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    lines = [
        "# Class Imbalance Diagnostics (Block 12)",
        "",
        f"Split: `{args.split}` | Total instances: {total_instances} | Classes: {len(CANONICAL_CLASSES)}",
        f"Max/min instance-count imbalance ratio: **{imbalance_ratio:.1f}x**",
        "",
        f"Rare classes (< {RARE_CLASS_THRESHOLD_FRACTION*100:.0f}% of the most common class's count): **{rare_classes}**",
        f"Small-object / visually difficult classes (< {SMALL_OBJECT_THRESHOLD_FRACTION*100:.0f}% of the largest median bbox area): **{small_object_classes}**",
        "",
        "| Class | Instances | Images | % of total | Median bbox area (px²) | Rare | Small-object |",
        "|---|---:|---:|---:|---:|:---:|:---:|",
    ]
    for c in sorted(per_class, key=lambda c: -c["instance_count"]):
        lines.append(
            f"| {c['canonical_class']} | {c['instance_count']} | {c['image_count']} | "
            f"{c['relative_frequency_pct']} | {c['median_bbox_area_px2']} | "
            f"{'YES' if c['is_rare'] else ''} | {'YES' if c['is_small_object'] else ''} |"
        )
    md_path = args.output_dir / "class_imbalance_diagnostics.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nJSON: {json_path}")
    print(f"Markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
