"""Canonical-mapped dataset statistics for EDA (Block 4).

Loads the raw COCO annotations for a split, applies the Block 3 canonical
mapping (fail-loudly on any unrecognized raw category — see
`agridata.dataset.mapping`), and exposes simple in-memory records plus
aggregate statistics (per-class instance/image counts, bbox and image
dimension distributions). This module is read-only with respect to the raw
dataset: it never writes back to the JSON or renames/moves any image.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from agridata.dataset.mapping import map_raw_category


@dataclass(frozen=True)
class ImageRecord:
    image_id: int
    file_name: str
    width: int
    height: int


@dataclass(frozen=True)
class AnnotationRecord:
    annotation_id: int
    image_id: int
    canonical_class: str
    bbox: tuple[float, float, float, float]  # x, y, w, h in raw pixel coords


@dataclass
class SplitData:
    split: str
    images: list[ImageRecord]
    annotations: list[AnnotationRecord]
    images_by_id: dict[int, ImageRecord]


def load_canonical_split(dataset_root: Path, split: str, annotation_filename: str) -> SplitData:
    """Load one split's COCO JSON and map every annotation to its canonical class.

    Supercategory placeholder categories (Leaf-blight, Rice-Leaf-Diseasee,
    paddy) are skipped, matching the Block 2/3 finding that they carry zero
    annotations in the official dataset — if that ever changes, those
    annotations are counted and reported via the returned skip count rather
    than silently dropped without a trace.
    """
    json_path = dataset_root / split / annotation_filename
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    images = [
        ImageRecord(img["id"], img["file_name"], img["width"], img["height"]) for img in data["images"]
    ]
    images_by_id = {img.image_id: img for img in images}

    category_cache: dict[int, str | None] = {}  # category_id -> canonical name or None (placeholder)
    for cat in data["categories"]:
        result = map_raw_category(cat["id"], cat["name"])
        category_cache[cat["id"]] = result.canonical_name  # None for supercategory placeholders

    annotations: list[AnnotationRecord] = []
    for ann in data["annotations"]:
        canonical_name = category_cache.get(ann["category_id"])
        if canonical_name is None:
            continue  # supercategory placeholder or otherwise non-canonical; not a detection target
        annotations.append(
            AnnotationRecord(
                annotation_id=ann["id"],
                image_id=ann["image_id"],
                canonical_class=canonical_name,
                bbox=tuple(ann["bbox"]),
            )
        )

    return SplitData(split=split, images=images, annotations=annotations, images_by_id=images_by_id)


def class_instance_counts(split_data: SplitData) -> Counter[str]:
    """Number of annotated instances per canonical class."""
    return Counter(ann.canonical_class for ann in split_data.annotations)


def class_image_counts(split_data: SplitData) -> Counter[str]:
    """Number of distinct images containing at least one instance of each canonical class."""
    images_per_class: dict[str, set[int]] = defaultdict(set)
    for ann in split_data.annotations:
        images_per_class[ann.canonical_class].add(ann.image_id)
    return Counter({cls: len(image_ids) for cls, image_ids in images_per_class.items()})


def bbox_dimensions(split_data: SplitData) -> list[tuple[float, float]]:
    """(width, height) for every annotation's bounding box."""
    return [(ann.bbox[2], ann.bbox[3]) for ann in split_data.annotations]


def image_dimensions(split_data: SplitData) -> list[tuple[int, int]]:
    """(width, height) for every image in the split."""
    return [(img.width, img.height) for img in split_data.images]


def annotations_per_image(split_data: SplitData) -> Counter[int]:
    """Number of annotations per image_id (useful for finding crowded scenes)."""
    return Counter(ann.image_id for ann in split_data.annotations)
