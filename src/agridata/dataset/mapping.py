"""Canonical 11-class label mapping for the TELEPATI 8.0 AgriData pipeline.

Maps the official dataset's raw COCO category names to the official 11
canonical disease/health classes defined by the competition regulation
(master spec, Section 10). The mapping table below was cross-checked against
the actual dataset in Block 2 (see artifacts/audit/dataset_audit_report.md):
all three splits contain exactly 21 raw categories — 3 supercategory
placeholders with zero annotations (Leaf-blight, Rice-Leaf-Diseasee, paddy,
per Section 11) plus 18 real leaf/plant condition labels, all 18 of which are
covered here with zero unexpected names.

This mapping is deterministic and, by design, refuses to silently map any
raw name it does not recognize — an unrecognized label must be investigated
and explicitly added, never guessed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Bump this whenever RAW_TO_CANONICAL or KNOWN_SUPERCATEGORY_LABELS changes,
# so prepared dataset outputs can record exactly which mapping produced them.
MAPPING_VERSION = "1.0.0"

CANONICAL_CLASSES: tuple[str, ...] = (
    "Bacterial leaf blight",
    "Bacterial panicle blight",
    "Blast",
    "Brown spot",
    "False smut",
    "Healthy",
    "Leaf roller",
    "Leaf scald",
    "Narrow brown",
    "Sheath blight",
    "Tungro",
)

CANONICAL_NUM_CLASSES = len(CANONICAL_CLASSES)  # 11, per competition regulation

# Canonical id (1-indexed, matches the official numbering in the master spec) -> name.
CANONICAL_ID_TO_NAME: dict[int, str] = {i + 1: name for i, name in enumerate(CANONICAL_CLASSES)}
CANONICAL_NAME_TO_ID: dict[str, int] = {name: i for i, name in CANONICAL_ID_TO_NAME.items()}

# Raw category name -> canonical class name.
# Source: TELEPATI 8.0 master spec Section 10, verified against the actual
# dataset's raw categories in the Block 2 forensic audit.
RAW_TO_CANONICAL: dict[str, str] = {
    "Bacterial leaf blight": "Bacterial leaf blight",
    "Bacterial panicle Blight": "Bacterial panicle blight",
    "Blast": "Blast",
    "Leaf blast": "Blast",
    "Infected Blast": "Blast",
    "BrownSpot": "Brown spot",
    "Brown spot": "Brown spot",
    "False-Smut": "False smut",
    "Healthy Rice Leaf": "Healthy",
    "Healthy Rice beads": "Healthy",
    "Healthy": "Healthy",
    "healthy": "Healthy",
    "Leaf-roller": "Leaf roller",
    "Leaf Scald": "Leaf scald",
    "Leaf scald": "Leaf scald",
    "Narrow brown": "Narrow brown",
    "Sheath Blight": "Sheath blight",
    "Rice-Tungro": "Tungro",
}

# Known non-canonical supercategory labels present in the raw dataset. These
# carry zero annotations (verified in the Block 2 audit) and are explicitly
# excluded as object-detection targets per master spec Section 11.
KNOWN_SUPERCATEGORY_LABELS: frozenset[str] = frozenset({"Leaf-blight", "Rice-Leaf-Diseasee", "paddy"})


class UnknownRawCategoryError(ValueError):
    """Raised when a raw category name has no known canonical mapping and is
    not a recognized supercategory placeholder.

    This fails loudly by design: per the master spec, an unrecognized raw
    label must never be silently mapped or dropped.
    """


@dataclass(frozen=True)
class CategoryMappingResult:
    """Result of mapping one raw COCO category to its canonical class."""

    raw_category_id: int
    raw_name: str
    canonical_name: str | None  # None if this is a supercategory placeholder
    canonical_id: int | None
    is_supercategory_placeholder: bool


def map_raw_category(raw_category_id: int, raw_name: str) -> CategoryMappingResult:
    """Map a single raw COCO category to its canonical class.

    Raises:
        UnknownRawCategoryError: if `raw_name` is neither a known canonical
            raw name nor a recognized supercategory placeholder.
    """
    if raw_name in KNOWN_SUPERCATEGORY_LABELS:
        return CategoryMappingResult(raw_category_id, raw_name, None, None, True)

    canonical_name = RAW_TO_CANONICAL.get(raw_name)
    if canonical_name is None:
        raise UnknownRawCategoryError(
            f"Raw category '{raw_name}' (id={raw_category_id}) has no known canonical "
            "mapping and is not a recognized supercategory placeholder. Refusing to "
            "silently map it — verify against the official mapping and update "
            "RAW_TO_CANONICAL or KNOWN_SUPERCATEGORY_LABELS explicitly."
        )

    return CategoryMappingResult(
        raw_category_id, raw_name, canonical_name, CANONICAL_NAME_TO_ID[canonical_name], False
    )


def map_categories(categories: list[dict[str, Any]]) -> list[CategoryMappingResult]:
    """Map a list of raw COCO category dicts (each with at least 'id' and 'name')."""
    return [map_raw_category(c["id"], c["name"]) for c in categories]


def build_mapping_report(categories: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a structured, non-fatal report comparing raw categories to the official mapping.

    Unlike `map_raw_category`, this does not raise on an unknown category —
    it records it in `unmapped_raw_categories` so a full audit report can
    still be produced. Use `map_raw_category`/`map_categories` directly
    wherever strict fail-loudly behavior is required (e.g. dataset
    preparation in a later block).
    """
    results: list[CategoryMappingResult] = []
    unmapped: list[dict[str, Any]] = []

    for c in categories:
        try:
            results.append(map_raw_category(c["id"], c["name"]))
        except UnknownRawCategoryError:
            unmapped.append(c)

    covered_canonical = {r.canonical_name for r in results if r.canonical_name is not None}
    canonical_with_zero_raw_labels = [name for name in CANONICAL_CLASSES if name not in covered_canonical]

    return {
        "total_raw_categories": len(categories),
        "mapped": [
            {
                "raw_id": r.raw_category_id,
                "raw_name": r.raw_name,
                "canonical_name": r.canonical_name,
                "canonical_id": r.canonical_id,
            }
            for r in results
            if not r.is_supercategory_placeholder
        ],
        "supercategory_placeholders": [
            {"raw_id": r.raw_category_id, "raw_name": r.raw_name}
            for r in results
            if r.is_supercategory_placeholder
        ],
        "unmapped_raw_categories": unmapped,
        "canonical_classes_with_zero_raw_labels": canonical_with_zero_raw_labels,
    }
