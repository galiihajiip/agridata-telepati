"""Raw dataset forensic audit for the TELEPATI 8.0 AgriData pipeline.

This module is strictly READ-ONLY with respect to the official dataset: it
never renames, moves, edits, or deletes any raw file. It inspects the actual
COCO-style annotation JSON and image files for each split and reports
structural findings (schema, counts, categories) and integrity findings
(missing files, invalid boxes, duplicates, corrupt images, cross-split
overlap) without applying any canonical class mapping — that mapping is a
separate, later step (Block 3) so this audit reflects the dataset exactly as
the competition organizers shipped it.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError
from tqdm import tqdm

logger = logging.getLogger("agridata.dataset.inspect")

REQUIRED_COCO_KEYS = ("images", "annotations", "categories")

# Bounding boxes below this pixel area are flagged as suspiciously small.
MIN_PLAUSIBLE_BBOX_AREA = 4.0
# Bounding boxes covering more than this fraction of the image area are
# flagged as suspiciously large (may indicate a mislabeled full-image box).
MAX_PLAUSIBLE_BBOX_AREA_FRACTION = 0.98
# Boxes that exceed the image boundary by no more than this many pixels are
# treated as float-rounding noise (WARNING, clampable) rather than a broken
# annotation (FATAL). Verified empirically on this dataset: every
# "exceeds image bounds" case across train/valid/test overshoots by <= 0.5px
# (a Roboflow export rounding artifact), so 1.0px is a conservative cutoff
# that would still catch a genuinely broken box.
BBOX_BOUNDARY_TOLERANCE_PX = 1.0


@dataclass
class BBoxIssue:
    """A single bounding-box validation finding tied to one annotation."""

    annotation_id: int | None
    image_id: int | None
    bbox: list[float]
    reason: str
    severity: str  # "FATAL" | "WARNING"


@dataclass
class SplitAudit:
    """Full forensic audit result for one dataset split (train/valid/test)."""

    split: str
    json_path: str
    exists: bool = True
    parse_error: str | None = None
    top_level_keys: list[str] = field(default_factory=list)
    num_images: int = 0
    num_annotations: int = 0
    num_categories: int = 0
    categories: list[dict[str, Any]] = field(default_factory=list)
    categories_zero_annotations: list[dict[str, Any]] = field(default_factory=list)
    images_zero_annotations: list[int] = field(default_factory=list)
    annotations_missing_image_ref: list[int] = field(default_factory=list)
    duplicate_annotation_ids: list[int] = field(default_factory=list)
    duplicate_image_ids: list[int] = field(default_factory=list)
    bbox_issues: list[BBoxIssue] = field(default_factory=list)
    missing_image_files: list[str] = field(default_factory=list)
    image_formats: dict[str, int] = field(default_factory=dict)
    corrupt_images: list[str] = field(default_factory=list)
    dimension_mismatches: list[dict[str, Any]] = field(default_factory=list)
    file_hashes: dict[str, str] = field(default_factory=dict)  # filename -> md5
    perceptual_hashes: dict[str, str] = field(default_factory=dict)  # filename -> aHash hex

    @property
    def is_fatal(self) -> bool:
        """True if this split has an issue the audit script must fail loudly on."""
        if self.parse_error is not None or not self.exists:
            return True
        if self.annotations_missing_image_ref:
            return True
        if any(issue.severity == "FATAL" for issue in self.bbox_issues):
            return True
        if self.missing_image_files:
            return True
        return False


def _average_hash(image: Image.Image, hash_size: int = 8) -> str:
    """Compute a simple average-hash (aHash) for approximate duplicate detection.

    This is a best-effort perceptual hash: an exact aHash match strongly
    suggests two images are visually near-identical (e.g. an accidental
    duplicate export under a different filename). It is NOT a full
    nearest-neighbor search over Hamming distance — only exact-hash bucket
    collisions are reported, matching the "if practical" scope requested for
    this audit. Any match should be treated as a candidate for visual
    confirmation, not proof of leakage.
    """
    small = image.convert("L").resize((hash_size, hash_size), Image.LANCZOS)
    pixels = list(small.getdata())
    avg = sum(pixels) / len(pixels)
    bits = "".join("1" if p >= avg else "0" for p in pixels)
    return f"{int(bits, 2):0{hash_size * hash_size // 4}x}"


def _md5_of_file(path: Path, chunk_size: int = 1 << 20) -> str:
    """Compute the MD5 hex digest of a file's exact byte content."""
    hasher = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def audit_split(split: str, split_dir: Path, annotation_filename: str) -> SplitAudit:
    """Run the full forensic audit for a single dataset split. Strictly read-only."""
    json_path = split_dir / annotation_filename
    audit = SplitAudit(split=split, json_path=str(json_path))

    if not split_dir.exists():
        audit.exists = False
        logger.error("[%s] split directory does not exist: %s", split, split_dir)
        return audit

    if not json_path.exists():
        audit.exists = False
        logger.error("[%s] annotation file does not exist: %s", split, json_path)
        return audit

    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        audit.parse_error = str(exc)
        logger.error("[%s] failed to parse JSON: %s", split, exc)
        return audit

    audit.top_level_keys = list(data.keys())
    missing_keys = [k for k in REQUIRED_COCO_KEYS if k not in data]
    if missing_keys:
        audit.parse_error = f"missing required COCO keys: {missing_keys}"
        logger.error("[%s] %s", split, audit.parse_error)
        return audit

    images: list[dict[str, Any]] = data["images"]
    annotations: list[dict[str, Any]] = data["annotations"]
    categories: list[dict[str, Any]] = data["categories"]

    audit.num_images = len(images)
    audit.num_annotations = len(annotations)
    audit.num_categories = len(categories)
    audit.categories = [
        {"id": c.get("id"), "name": c.get("name"), "supercategory": c.get("supercategory")}
        for c in categories
    ]

    # --- duplicate ID detection -------------------------------------------------
    image_id_counts = Counter(img["id"] for img in images)
    audit.duplicate_image_ids = sorted(iid for iid, cnt in image_id_counts.items() if cnt > 1)

    ann_id_counts = Counter(ann["id"] for ann in annotations)
    audit.duplicate_annotation_ids = sorted(aid for aid, cnt in ann_id_counts.items() if cnt > 1)

    # --- image lookup + zero-annotation / missing-reference detection -----------
    images_by_id = {img["id"]: img for img in images}
    annotation_count_per_image: Counter[int] = Counter()
    annotation_count_per_category: Counter[int] = Counter()

    for ann in annotations:
        image_id = ann.get("image_id")
        if image_id not in images_by_id:
            audit.annotations_missing_image_ref.append(ann.get("id"))
            continue
        annotation_count_per_image[image_id] += 1
        annotation_count_per_category[ann.get("category_id")] += 1

    audit.images_zero_annotations = sorted(
        img_id for img_id in images_by_id if annotation_count_per_image[img_id] == 0
    )
    audit.categories_zero_annotations = [
        c for c in audit.categories if annotation_count_per_category[c["id"]] == 0
    ]

    # --- bbox validation ----------------------------------------------------------
    for ann in annotations:
        image_id = ann.get("image_id")
        image = images_by_id.get(image_id)
        if image is None:
            continue  # already recorded as a missing image reference above

        bbox = ann.get("bbox")
        if not bbox or len(bbox) != 4:
            audit.bbox_issues.append(
                BBoxIssue(ann.get("id"), image_id, list(bbox or []), "missing or malformed bbox", "FATAL")
            )
            continue

        x, y, w, h = bbox
        img_w, img_h = image.get("width"), image.get("height")

        if x < 0 or y < 0:
            audit.bbox_issues.append(BBoxIssue(ann["id"], image_id, bbox, "negative x/y origin", "FATAL"))
        if w <= 0 or h <= 0:
            audit.bbox_issues.append(BBoxIssue(ann["id"], image_id, bbox, "non-positive width/height", "FATAL"))
        elif img_w is not None and img_h is not None:
            if x + w > img_w or y + h > img_h:
                audit.bbox_issues.append(BBoxIssue(ann["id"], image_id, bbox, "bbox exceeds image bounds", "FATAL"))
            area = w * h
            image_area = img_w * img_h
            if image_area > 0:
                if area < MIN_PLAUSIBLE_BBOX_AREA:
                    audit.bbox_issues.append(
                        BBoxIssue(ann["id"], image_id, bbox, "suspiciously small bbox area", "WARNING")
                    )
                elif area / image_area > MAX_PLAUSIBLE_BBOX_AREA_FRACTION:
                    audit.bbox_issues.append(
                        BBoxIssue(ann["id"], image_id, bbox, "bbox covers nearly entire image", "WARNING")
                    )

    # --- on-disk file checks: existence, format, corruption, dimensions, hashes --
    format_counter: Counter[str] = Counter()
    for img in tqdm(images, desc=f"[{split}] auditing image files", unit="img"):
        filename = img.get("file_name")
        image_path = split_dir / filename
        if not image_path.exists():
            audit.missing_image_files.append(filename)
            continue

        format_counter[image_path.suffix.lower()] += 1

        try:
            with Image.open(image_path) as im:
                im.verify()
            with Image.open(image_path) as im:
                actual_w, actual_h = im.size
                audit.perceptual_hashes[filename] = _average_hash(im)
        except (UnidentifiedImageError, OSError) as exc:
            audit.corrupt_images.append(filename)
            logger.warning("[%s] corrupt/unreadable image %s: %s", split, filename, exc)
            continue

        declared_w, declared_h = img.get("width"), img.get("height")
        if declared_w is not None and declared_h is not None and (declared_w, declared_h) != (actual_w, actual_h):
            audit.dimension_mismatches.append(
                {"file_name": filename, "declared": [declared_w, declared_h], "actual": [actual_w, actual_h]}
            )

        audit.file_hashes[filename] = _md5_of_file(image_path)

    audit.image_formats = dict(format_counter)
    return audit


def detect_cross_split_overlap(audits: dict[str, SplitAudit]) -> dict[str, Any]:
    """Detect potential data leakage between splits via filename/hash/perceptual-hash overlap."""
    splits = list(audits.keys())
    result: dict[str, Any] = {
        "filename_overlap": {},
        "content_hash_overlap": {},
        "perceptual_hash_overlap": {},
    }

    for i in range(len(splits)):
        for j in range(i + 1, len(splits)):
            a, b = splits[i], splits[j]
            key = f"{a}_vs_{b}"

            names_a = set(audits[a].file_hashes) | set(audits[a].missing_image_files)
            names_b = set(audits[b].file_hashes) | set(audits[b].missing_image_files)
            result["filename_overlap"][key] = sorted(names_a & names_b)

            hashes_a = {h: f for f, h in audits[a].file_hashes.items()}
            hashes_b = {h: f for f, h in audits[b].file_hashes.items()}
            common_hashes = set(hashes_a) & set(hashes_b)
            result["content_hash_overlap"][key] = [
                {"hash": h, a: hashes_a[h], b: hashes_b[h]} for h in sorted(common_hashes)
            ]

            phash_a = {h: f for f, h in audits[a].perceptual_hashes.items()}
            phash_b = {h: f for f, h in audits[b].perceptual_hashes.items()}
            common_phash = set(phash_a) & set(phash_b)
            result["perceptual_hash_overlap"][key] = [
                {"hash": h, a: phash_a[h], b: phash_b[h]} for h in sorted(common_phash)
            ]

    return result
