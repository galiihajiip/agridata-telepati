"""Submission-grade dataset profiling (BLOCK B).

Pure analysis helpers that turn a split's raw COCO JSON and its canonical
view into structured summaries: class balance, bounding box geometry, image
resolution, and an object-detection-specific missingness audit. Every
function returns plain data so the notebook can render it without embedding
analysis logic.

Nothing here writes to the raw dataset.
"""

from __future__ import annotations

import json
import statistics
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

from agridata.dataset.mapping import CANONICAL_CLASSES
from agridata.dataset.stats import (
    SplitData,
    annotations_per_image,
    class_image_counts,
    class_instance_counts,
)

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass(frozen=True)
class ClassImbalance:
    per_class_instances: dict[str, int]
    per_class_images: dict[str, int]
    per_class_instance_share: dict[str, float]
    most_frequent_class: str
    least_frequent_class: str
    max_instances: int
    min_instances: int
    imbalance_ratio: float
    classes_with_zero_instances: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class BboxGeometry:
    count: int
    widths: list[float]
    heights: list[float]
    areas: list[float]
    relative_areas: list[float]
    aspect_ratios: list[float]
    median_area: float
    median_relative_area: float
    median_aspect_ratio: float
    small_object_share: float

    def summary(self) -> dict:
        return {
            "count": self.count,
            "median_area_px2": round(self.median_area, 2),
            "median_relative_area": round(self.median_relative_area, 6),
            "median_aspect_ratio": round(self.median_aspect_ratio, 4),
            "small_object_share": round(self.small_object_share, 4),
        }


@dataclass(frozen=True)
class ResolutionSummary:
    count: int
    widths: list[int]
    heights: list[int]
    distinct_resolutions: int
    most_common_resolution: tuple[int, int]
    most_common_share: float

    def summary(self) -> dict:
        return {
            "count": self.count,
            "distinct_resolutions": self.distinct_resolutions,
            "most_common_resolution": list(self.most_common_resolution),
            "most_common_share": round(self.most_common_share, 4),
        }


@dataclass
class MissingnessCheck:
    name: str
    count: int
    total: int
    detail: str = ""

    @property
    def percentage(self) -> float:
        return (self.count / self.total * 100.0) if self.total else 0.0

    def to_dict(self) -> dict:
        return {
            "check": self.name,
            "count": self.count,
            "total": self.total,
            "percentage": round(self.percentage, 4),
            "status": "OK" if self.count == 0 else "PERLU DITINJAU",
            "detail": self.detail,
        }


@dataclass
class MissingnessReport:
    split: str
    checks: list[MissingnessCheck] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"split": self.split, "checks": [c.to_dict() for c in self.checks]}

    @property
    def all_clear(self) -> bool:
        return all(c.count == 0 for c in self.checks)


def summarize_class_imbalance(split_data: SplitData) -> ClassImbalance:
    instances = class_instance_counts(split_data)
    images = class_image_counts(split_data)

    per_class_instances = {cls: int(instances.get(cls, 0)) for cls in CANONICAL_CLASSES}
    per_class_images = {cls: int(images.get(cls, 0)) for cls in CANONICAL_CLASSES}

    total = sum(per_class_instances.values())
    shares = {
        cls: (count / total if total else 0.0) for cls, count in per_class_instances.items()
    }

    present = {cls: c for cls, c in per_class_instances.items() if c > 0}
    if present:
        most = max(present, key=lambda c: present[c])
        least = min(present, key=lambda c: present[c])
        max_n, min_n = present[most], present[least]
        ratio = max_n / min_n if min_n else float("inf")
    else:
        most = least = ""
        max_n = min_n = 0
        ratio = 0.0

    return ClassImbalance(
        per_class_instances=per_class_instances,
        per_class_images=per_class_images,
        per_class_instance_share=shares,
        most_frequent_class=most,
        least_frequent_class=least,
        max_instances=max_n,
        min_instances=min_n,
        imbalance_ratio=ratio,
        classes_with_zero_instances=[c for c, n in per_class_instances.items() if n == 0],
    )


def compute_bbox_geometry(split_data: SplitData, small_object_threshold: float = 0.01) -> BboxGeometry:
    """Bounding box geometry, including area relative to its own image.

    `small_object_threshold` is a fraction of image area: 0.01 means boxes
    covering under one percent of the image are counted as small objects.
    """
    widths: list[float] = []
    heights: list[float] = []
    areas: list[float] = []
    relative_areas: list[float] = []
    aspect_ratios: list[float] = []

    for ann in split_data.annotations:
        _, _, w, h = ann.bbox
        if w <= 0 or h <= 0:
            continue
        image = split_data.images_by_id.get(ann.image_id)
        widths.append(float(w))
        heights.append(float(h))
        areas.append(float(w * h))
        aspect_ratios.append(float(w / h))
        if image and image.width > 0 and image.height > 0:
            relative_areas.append(float(w * h) / float(image.width * image.height))

    small_share = (
        sum(1 for r in relative_areas if r < small_object_threshold) / len(relative_areas)
        if relative_areas
        else 0.0
    )

    return BboxGeometry(
        count=len(areas),
        widths=widths,
        heights=heights,
        areas=areas,
        relative_areas=relative_areas,
        aspect_ratios=aspect_ratios,
        median_area=statistics.median(areas) if areas else 0.0,
        median_relative_area=statistics.median(relative_areas) if relative_areas else 0.0,
        median_aspect_ratio=statistics.median(aspect_ratios) if aspect_ratios else 0.0,
        small_object_share=small_share,
    )


def summarize_resolution(split_data: SplitData) -> ResolutionSummary:
    widths = [img.width for img in split_data.images]
    heights = [img.height for img in split_data.images]
    pairs = Counter((img.width, img.height) for img in split_data.images)

    if pairs:
        most_common, count = pairs.most_common(1)[0]
        share = count / len(split_data.images)
    else:
        most_common, share = (0, 0), 0.0

    return ResolutionSummary(
        count=len(split_data.images),
        widths=widths,
        heights=heights,
        distinct_resolutions=len(pairs),
        most_common_resolution=most_common,
        most_common_share=share,
    )


def audit_missingness(dataset_root: Path, split: str, annotation_filename: str) -> MissingnessReport:
    """Object-detection-specific completeness checks on the raw COCO JSON.

    Missingness for a detection dataset is not a null cell in a table: it is
    a broken reference between the JSON and the image files, or a bounding
    box that cannot describe a region. Each check is reported even when its
    count is zero, because a zero is itself an audit result.
    """
    split_dir = dataset_root / split
    with (split_dir / annotation_filename).open("r", encoding="utf-8") as f:
        data = json.load(f)

    images = data.get("images", [])
    annotations = data.get("annotations", [])
    categories = data.get("categories", [])

    image_ids = {img.get("id") for img in images}
    category_ids = {cat.get("id") for cat in categories}
    referenced_files = {img.get("file_name") for img in images}
    files_on_disk = {p.name for p in split_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES}

    annotated_image_ids = {ann.get("image_id") for ann in annotations}

    missing_files = [img["file_name"] for img in images if img.get("file_name") not in files_on_disk]
    orphan_files = sorted(files_on_disk - referenced_files)
    images_no_ann = [img["id"] for img in images if img.get("id") not in annotated_image_ids]
    ann_no_image = [a.get("id") for a in annotations if a.get("image_id") not in image_ids]
    ann_unknown_cat = [a.get("id") for a in annotations if a.get("category_id") not in category_ids]

    bbox_missing = []
    bbox_invalid = []
    for ann in annotations:
        bbox = ann.get("bbox")
        if not bbox or len(bbox) != 4 or any(v is None for v in bbox):
            bbox_missing.append(ann.get("id"))
            continue
        if bbox[2] <= 0 or bbox[3] <= 0:
            bbox_invalid.append(ann.get("id"))

    dims_missing = [
        img.get("id")
        for img in images
        if not img.get("width") or not img.get("height") or img["width"] <= 0 or img["height"] <= 0
    ]

    used_category_ids = {a.get("category_id") for a in annotations}
    empty_categories = [c.get("name") for c in categories if c.get("id") not in used_category_ids]

    n_img, n_ann, n_cat = len(images), len(annotations), len(categories)

    report = MissingnessReport(split=split)
    report.checks = [
        MissingnessCheck("Berkas citra hilang (dirujuk JSON, tidak ada di disk)", len(missing_files), n_img),
        MissingnessCheck("Berkas citra di disk tanpa record JSON", len(orphan_files), len(files_on_disk)),
        MissingnessCheck("Citra tanpa anotasi", len(images_no_ann), n_img),
        MissingnessCheck("Anotasi merujuk image_id yang tidak ada", len(ann_no_image), n_ann),
        MissingnessCheck("Anotasi merujuk category_id yang tidak ada", len(ann_unknown_cat), n_ann),
        MissingnessCheck("Bounding box kosong atau tidak lengkap", len(bbox_missing), n_ann),
        MissingnessCheck("Bounding box dengan lebar atau tinggi tidak valid", len(bbox_invalid), n_ann),
        MissingnessCheck("Metadata dimensi citra tidak tersedia", len(dims_missing), n_img),
        MissingnessCheck(
            "Kategori tanpa anotasi",
            len(empty_categories),
            n_cat,
            detail=", ".join(str(c) for c in empty_categories) if empty_categories else "",
        ),
    ]
    return report


def scene_density_summary(split_data: SplitData, crowded_threshold: int = 3) -> dict:
    per_image = annotations_per_image(split_data)
    counts = list(per_image.values())
    crowded = sum(1 for c in counts if c > crowded_threshold)
    return {
        "crowded_threshold": crowded_threshold,
        "images_with_annotations": len(counts),
        "median_annotations_per_image": statistics.median(counts) if counts else 0,
        "max_annotations_in_one_image": max(counts) if counts else 0,
        "crowded_images": crowded,
        "crowded_share": round(crowded / len(counts), 4) if counts else 0.0,
    }


def load_duplicate_summary(audit_report_path: Path) -> dict:
    """Read the Block 2 forensic audit's cross-split duplicate findings."""
    if not audit_report_path.exists():
        return {"available": False, "reason": f"{audit_report_path} tidak ditemukan"}

    with audit_report_path.open("r", encoding="utf-8") as f:
        audit = json.load(f)

    overlap = audit.get("cross_split_overlap", {}).get("content_hash_overlap", {})
    return {
        "available": True,
        "pairs": {pair: len(matches) for pair, matches in overlap.items()},
        "matches": overlap,
        "total_exact_duplicates": sum(len(m) for m in overlap.values()),
    }
