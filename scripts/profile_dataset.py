#!/usr/bin/env python3
"""Profiling dataset tingkat submission (BLOCK B).

Menghasilkan figur dan laporan JSON yang dipakai notebook final, sehingga
notebook cukup memanggil fungsi dan menampilkan hasil, bukan memuat logika
analisis.

Penggunaan:
    python scripts/profile_dataset.py --dataset-root "Telepati 8.0 Datasets"
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.analysis.dataset_profile import (  # noqa: E402
    audit_missingness,
    compute_bbox_geometry,
    load_duplicate_summary,
    scene_density_summary,
    summarize_class_imbalance,
    summarize_resolution,
)
from agridata.dataset.stats import load_canonical_split  # noqa: E402
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.visualization.distributions import (  # noqa: E402
    plot_aspect_ratio_distribution,
    plot_class_distribution_comparison,
    plot_image_dimension_distribution,
    plot_relative_area_distribution,
    plot_split_overview,
)

logger = logging.getLogger("agridata.scripts.profile_dataset")

SPLITS = ("train", "valid", "test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profiling dataset untuk dokumen submission.")
    parser.add_argument("--dataset-root", default=Path("Telepati 8.0 Datasets"), type=Path)
    parser.add_argument("--annotation-filename", default="_annotations.coco.json")
    parser.add_argument("--audit-report", default=Path("artifacts/audit/dataset_audit_report.json"), type=Path)
    parser.add_argument("--figures-dir", default=Path("artifacts/figures/final_submission"), type=Path)
    parser.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    parser.add_argument("--small-object-threshold", type=float, default=0.01)
    return parser.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()
    args.figures_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    profile: dict = {
        "dataset_root": str(args.dataset_root),
        "small_object_threshold": args.small_object_threshold,
        "splits": {},
        "figures": {},
    }
    split_counts: dict[str, dict[str, int]] = {}

    for split in SPLITS:
        logger.info("Memproses split %s", split)
        split_data = load_canonical_split(args.dataset_root, split, args.annotation_filename)

        imbalance = summarize_class_imbalance(split_data)
        geometry = compute_bbox_geometry(split_data, args.small_object_threshold)
        resolution = summarize_resolution(split_data)
        missingness = audit_missingness(args.dataset_root, split, args.annotation_filename)
        density = scene_density_summary(split_data)

        split_counts[split] = {
            "images": len(split_data.images),
            "annotations": len(split_data.annotations),
        }

        profile["splits"][split] = {
            "images": len(split_data.images),
            "annotations_canonical": len(split_data.annotations),
            "class_imbalance": imbalance.to_dict(),
            "bbox_geometry": geometry.summary(),
            "resolution": resolution.summary(),
            "missingness": missingness.to_dict(),
            "scene_density": density,
        }

        figs = {}
        figs["class_distribution"] = str(
            plot_class_distribution_comparison(
                imbalance.per_class_instances,
                imbalance.per_class_images,
                f"Distribusi kelas pada split {split}",
                args.figures_dir / f"{split}_class_distribution.png",
            )
        )
        figs["relative_area"] = str(
            plot_relative_area_distribution(
                geometry.relative_areas,
                f"Distribusi luas bounding box relatif pada split {split}",
                args.figures_dir / f"{split}_bbox_relative_area.png",
                args.small_object_threshold,
            )
        )
        figs["aspect_ratio"] = str(
            plot_aspect_ratio_distribution(
                geometry.aspect_ratios,
                f"Distribusi rasio aspek bounding box pada split {split}",
                args.figures_dir / f"{split}_bbox_aspect_ratio.png",
            )
        )
        figs["resolution"] = str(
            plot_image_dimension_distribution(
                list(zip(resolution.widths, resolution.heights)),
                f"Distribusi resolusi citra pada split {split}",
                args.figures_dir / f"{split}_image_resolution.png",
            )
        )
        profile["figures"][split] = figs

    profile["figures"]["split_overview"] = str(
        plot_split_overview(split_counts, args.figures_dir / "split_overview.png")
    )
    profile["duplicates"] = load_duplicate_summary(args.audit_report)

    report_path = args.report_dir / "dataset_profile.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)

    print(f"Laporan profiling: {report_path}")
    print(f"Figur: {args.figures_dir}")
    for split in SPLITS:
        s = profile["splits"][split]
        ci = s["class_imbalance"]
        print(
            f"  {split:5s}: {s['images']:5d} citra | {s['annotations_canonical']:6d} anotasi canonical | "
            f"rasio imbalance {ci['imbalance_ratio']:.1f}x | "
            f"objek kecil {s['bbox_geometry']['small_object_share']:.1%}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
