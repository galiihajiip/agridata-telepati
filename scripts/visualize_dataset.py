#!/usr/bin/env python3
"""CLI for dataset EDA and visual annotation sanity-checking (Block 4).

Usage:
    python scripts/visualize_dataset.py --dataset-root "<PATH>" \
        --output-dir artifacts/figures --num-samples 8 --seed 42

Read-only with respect to the raw dataset. Applies the Block 3 canonical
mapping when loading annotations (fails loudly on any unmapped raw
category — same behavior as the rest of the pipeline). Sampling is
deterministic (seeded) so repeated runs pick the same images.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.dataset.stats import (  # noqa: E402
    SplitData,
    annotations_per_image,
    bbox_dimensions,
    class_image_counts,
    class_instance_counts,
    image_dimensions,
    load_canonical_split,
)
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.seed import set_global_seed  # noqa: E402
from agridata.visualization.distributions import (  # noqa: E402
    plot_bbox_size_distribution,
    plot_class_counts,
    plot_image_dimension_distribution,
)
from agridata.visualization.images import save_annotated_sample  # noqa: E402

DEFAULT_ANNOTATION_FILENAME = "_annotations.coco.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dataset EDA and annotation visualization (read-only).")
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("artifacts/figures"), type=Path)
    parser.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    parser.add_argument("--audit-report", default=Path("artifacts/audit/dataset_audit_report.json"), type=Path)
    parser.add_argument("--num-samples", type=int, default=8, help="Random annotated samples to save per split.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--splits", nargs="+", default=["train", "valid"])
    parser.add_argument("--annotation-filename", default=DEFAULT_ANNOTATION_FILENAME)
    return parser.parse_args()


def per_class_bbox_areas(split_data: SplitData) -> dict[str, list[float]]:
    areas: dict[str, list[float]] = {}
    for ann in split_data.annotations:
        areas.setdefault(ann.canonical_class, []).append(ann.bbox[2] * ann.bbox[3])
    return areas


def find_suspicious_example(audit_report_path: Path, split: str) -> dict | None:
    """Pull one 'covers nearly entire image' WARNING bbox from the Block 2 audit,
    so Block 4 can visually confirm a specific flagged finding rather than
    inventing a new "suspicious" example."""
    if not audit_report_path.exists():
        return None
    with audit_report_path.open("r", encoding="utf-8") as f:
        report = json.load(f)
    for issue in report["splits"][split]["bbox_issues"]:
        if issue["severity"] == "WARNING" and "covers nearly entire image" in issue["reason"]:
            return issue
    return None


def process_split(
    split: str,
    dataset_root: Path,
    annotation_filename: str,
    output_dir: Path,
    num_samples: int,
    audit_report_path: Path,
) -> dict:
    split_data = load_canonical_split(dataset_root, split, annotation_filename)

    instance_counts = class_instance_counts(split_data)
    image_counts = class_image_counts(split_data)
    bbox_dims = bbox_dimensions(split_data)
    img_dims = image_dimensions(split_data)
    per_image_ann_count = annotations_per_image(split_data)
    class_areas = per_class_bbox_areas(split_data)

    dist_dir = output_dir / "distributions"
    plot_class_counts(instance_counts, f"{split}: instances per canonical class", dist_dir / f"{split}_instance_counts.png")
    plot_class_counts(image_counts, f"{split}: images per canonical class", dist_dir / f"{split}_image_counts.png")
    plot_bbox_size_distribution(bbox_dims, f"{split}: bbox width vs height", dist_dir / f"{split}_bbox_sizes.png")
    plot_image_dimension_distribution(img_dims, f"{split}: image width vs height", dist_dir / f"{split}_image_dims.png")

    # --- random annotated samples (deterministic, only images with >=1 annotation) ---
    sample_dir = output_dir / "samples" / split
    annotated_image_ids = sorted(per_image_ann_count.keys())
    chosen_ids = random.sample(annotated_image_ids, k=min(num_samples, len(annotated_image_ids)))
    ann_by_image: dict[int, list] = {}
    for ann in split_data.annotations:
        ann_by_image.setdefault(ann.image_id, []).append(ann)

    saved_samples = []
    for image_id in chosen_ids:
        image_record = split_data.images_by_id[image_id]
        path = save_annotated_sample(
            dataset_root, split, image_record, ann_by_image[image_id], sample_dir, tag="random"
        )
        saved_samples.append(str(path))

    # --- rare-class example ---
    rare_class = min(instance_counts, key=instance_counts.get) if instance_counts else None
    if rare_class is not None:
        rare_image_id = next(
            img_id for img_id, anns in ann_by_image.items() if any(a.canonical_class == rare_class for a in anns)
        )
        image_record = split_data.images_by_id[rare_image_id]
        path = save_annotated_sample(
            dataset_root, split, image_record, ann_by_image[rare_image_id], sample_dir, tag="rare_class"
        )
        saved_samples.append(str(path))

    # --- crowded-scene example (most annotations in one image) ---
    if per_image_ann_count:
        crowded_image_id = per_image_ann_count.most_common(1)[0][0]
        image_record = split_data.images_by_id[crowded_image_id]
        path = save_annotated_sample(
            dataset_root, split, image_record, ann_by_image[crowded_image_id], sample_dir, tag="crowded"
        )
        saved_samples.append(str(path))

    # --- suspicious annotation example, pulled from the Block 2 audit findings ---
    suspicious = find_suspicious_example(audit_report_path, split)
    if suspicious is not None:
        image_id = suspicious["image_id"]
        image_record = split_data.images_by_id.get(image_id)
        if image_record is not None:
            path = save_annotated_sample(
                dataset_root, split, image_record, ann_by_image.get(image_id, []), sample_dir, tag="suspicious"
            )
            saved_samples.append(str(path))

    total_instances = sum(instance_counts.values())
    class_summary = {}
    for cls in instance_counts:
        areas = class_areas.get(cls, [])
        class_summary[cls] = {
            "instance_count": instance_counts[cls],
            "image_count": image_counts.get(cls, 0),
            "share_of_instances_pct": round(100 * instance_counts[cls] / total_instances, 2) if total_instances else 0,
            "median_bbox_area_px2": round(statistics.median(areas), 1) if areas else None,
        }

    sorted_by_count = sorted(class_summary.items(), key=lambda kv: kv[1]["instance_count"])
    sorted_by_area = sorted(
        (kv for kv in class_summary.items() if kv[1]["median_bbox_area_px2"] is not None),
        key=lambda kv: kv[1]["median_bbox_area_px2"],
    )

    return {
        "split": split,
        "num_images": len(split_data.images),
        "num_annotations": len(split_data.annotations),
        "class_summary": class_summary,
        "rarest_classes": [name for name, _ in sorted_by_count[:3]],
        "most_common_classes": [name for name, _ in sorted_by_count[-3:]],
        "smallest_object_classes": [name for name, _ in sorted_by_area[:3]],
        "images_with_zero_annotations": len(split_data.images) - len(per_image_ann_count),
        "max_annotations_in_one_image": per_image_ann_count.most_common(1)[0][1] if per_image_ann_count else 0,
        "saved_figures": {
            "instance_counts": str(dist_dir / f"{split}_instance_counts.png"),
            "image_counts": str(dist_dir / f"{split}_image_counts.png"),
            "bbox_sizes": str(dist_dir / f"{split}_bbox_sizes.png"),
            "image_dims": str(dist_dir / f"{split}_image_dims.png"),
        },
        "saved_samples": saved_samples,
    }


def build_markdown_report(per_split_results: dict[str, dict]) -> str:
    lines = ["# Dataset EDA Summary Report", "", "Generated by `scripts/visualize_dataset.py`. Read-only against the raw dataset.", ""]
    for split, result in per_split_results.items():
        lines += [
            f"## Split: `{split}`",
            "",
            f"- Images: {result['num_images']}",
            f"- Annotations (canonical classes only): {result['num_annotations']}",
            f"- Images with zero annotations: {result['images_with_zero_annotations']}",
            f"- Most annotations in a single image (crowded scene): {result['max_annotations_in_one_image']}",
            f"- Rarest classes (fewest instances): {result['rarest_classes']}",
            f"- Most common classes: {result['most_common_classes']}",
            f"- Classes with smallest median bbox area (small-object risk): {result['smallest_object_classes']}",
            "",
            "| canonical class | instances | images | % of instances | median bbox area (px^2) |",
            "|---|---:|---:|---:|---:|",
        ]
        for cls, s in sorted(result["class_summary"].items(), key=lambda kv: -kv[1]["instance_count"]):
            lines.append(
                f"| {cls} | {s['instance_count']} | {s['image_count']} | {s['share_of_instances_pct']} | {s['median_bbox_area_px2']} |"
            )
        lines.append("")
        lines.append(f"Figures: `{result['saved_figures']}`")
        lines.append(f"Annotated samples saved: {len(result['saved_samples'])}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    setup_logging()
    args = parse_args()
    set_global_seed(args.seed)

    if not args.dataset_root.exists():
        print(f"FATAL: dataset root does not exist: {args.dataset_root}", file=sys.stderr)
        return 2

    per_split_results = {}
    for split in args.splits:
        per_split_results[split] = process_split(
            split, args.dataset_root, args.annotation_filename, args.output_dir, args.num_samples, args.audit_report
        )

    args.report_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.report_dir / "eda_summary.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(per_split_results, f, indent=2)

    markdown = build_markdown_report(per_split_results)
    md_path = args.report_dir / "eda_summary.md"
    md_path.write_text(markdown, encoding="utf-8")

    print(markdown)
    print(f"\nJSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    print(f"Figures written under: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
