"""Unit tests for the official 11-class canonical mapping (Block 3)."""

from __future__ import annotations

import pytest

from agridata.dataset.mapping import (
    CANONICAL_CLASSES,
    CANONICAL_NUM_CLASSES,
    KNOWN_SUPERCATEGORY_LABELS,
    RAW_TO_CANONICAL,
    UnknownRawCategoryError,
    build_mapping_report,
    map_raw_category,
)


def test_exactly_eleven_canonical_classes() -> None:
    assert CANONICAL_NUM_CLASSES == 11
    assert len(CANONICAL_CLASSES) == 11
    assert len(set(CANONICAL_CLASSES)) == 11  # no duplicates


@pytest.mark.parametrize("raw_name,expected_canonical", sorted(RAW_TO_CANONICAL.items()))
def test_every_official_raw_name_maps_correctly(raw_name: str, expected_canonical: str) -> None:
    result = map_raw_category(raw_category_id=999, raw_name=raw_name)
    assert result.canonical_name == expected_canonical
    assert result.is_supercategory_placeholder is False
    assert result.canonical_id is not None


@pytest.mark.parametrize("supercategory_name", sorted(KNOWN_SUPERCATEGORY_LABELS))
def test_known_supercategory_labels_are_not_canonical_targets(supercategory_name: str) -> None:
    result = map_raw_category(raw_category_id=0, raw_name=supercategory_name)
    assert result.is_supercategory_placeholder is True
    assert result.canonical_name is None
    assert result.canonical_id is None


@pytest.mark.parametrize("unknown_name", ["Totally Unknown Disease", "leaf_blast_typo", "", "RANDOM_LABEL_123"])
def test_unknown_raw_category_raises_loudly(unknown_name: str) -> None:
    with pytest.raises(UnknownRawCategoryError):
        map_raw_category(raw_category_id=1234, raw_name=unknown_name)


def test_mapping_is_deterministic() -> None:
    for raw_name in RAW_TO_CANONICAL:
        first = map_raw_category(1, raw_name)
        second = map_raw_category(1, raw_name)
        assert first == second


def test_build_mapping_report_against_actual_dataset_categories() -> None:
    """Validates against the real category list discovered by the Block 2
    forensic audit (artifacts/audit/dataset_audit_report.md), proving the
    mapping covers the actual dataset with zero unmapped categories."""
    actual_categories = [
        {"id": 0, "name": "Leaf-blight"},
        {"id": 1, "name": "Bacterial panicle Blight"},
        {"id": 2, "name": "False-Smut"},
        {"id": 3, "name": "Healthy Rice Leaf"},
        {"id": 4, "name": "Healthy Rice beads"},
        {"id": 5, "name": "Infected Blast"},
        {"id": 6, "name": "Leaf-roller"},
        {"id": 7, "name": "Rice-Leaf-Diseasee"},
        {"id": 8, "name": "Blast"},
        {"id": 9, "name": "BrownSpot"},
        {"id": 10, "name": "Healthy"},
        {"id": 11, "name": "Leaf Scald"},
        {"id": 12, "name": "Rice-Tungro"},
        {"id": 13, "name": "Sheath Blight"},
        {"id": 14, "name": "paddy"},
        {"id": 15, "name": "Bacterial leaf blight"},
        {"id": 16, "name": "Brown spot"},
        {"id": 17, "name": "Leaf blast"},
        {"id": 18, "name": "Leaf scald"},
        {"id": 19, "name": "Narrow brown"},
        {"id": 20, "name": "healthy"},
    ]
    report = build_mapping_report(actual_categories)
    assert report["total_raw_categories"] == 21
    assert report["unmapped_raw_categories"] == []
    assert report["canonical_classes_with_zero_raw_labels"] == []
    assert len(report["mapped"]) == 18
    assert len(report["supercategory_placeholders"]) == 3
