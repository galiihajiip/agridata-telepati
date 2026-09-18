"""Unit tests untuk profiling dataset (BLOCK B).

Menguji logika murni dengan data sintetis kecil, sehingga tidak bergantung
pada dataset resmi dan tetap berjalan dalam milidetik.
"""

from __future__ import annotations

import json

from agridata.analysis.dataset_profile import (
    audit_missingness,
    compute_bbox_geometry,
    scene_density_summary,
    summarize_class_imbalance,
    summarize_resolution,
)
from agridata.dataset.stats import AnnotationRecord, ImageRecord, SplitData


def _split(images, annotations) -> SplitData:
    return SplitData(
        split="dummy",
        images=images,
        annotations=annotations,
        images_by_id={img.image_id: img for img in images},
    )


def test_imbalance_ratio_uses_largest_over_smallest_present_class() -> None:
    images = [ImageRecord(1, "a.jpg", 100, 100)]
    annotations = [
        AnnotationRecord(1, 1, "Blast", (0, 0, 10, 10)),
        AnnotationRecord(2, 1, "Blast", (0, 0, 10, 10)),
        AnnotationRecord(3, 1, "Blast", (0, 0, 10, 10)),
        AnnotationRecord(4, 1, "Tungro", (0, 0, 10, 10)),
    ]
    summary = summarize_class_imbalance(_split(images, annotations))

    assert summary.most_frequent_class == "Blast"
    assert summary.least_frequent_class == "Tungro"
    assert summary.imbalance_ratio == 3.0
    assert summary.per_class_instances["Blast"] == 3
    assert "Healthy" in summary.classes_with_zero_instances


def test_instance_shares_sum_to_one() -> None:
    images = [ImageRecord(1, "a.jpg", 100, 100)]
    annotations = [
        AnnotationRecord(1, 1, "Blast", (0, 0, 10, 10)),
        AnnotationRecord(2, 1, "Healthy", (0, 0, 10, 10)),
    ]
    summary = summarize_class_imbalance(_split(images, annotations))
    assert abs(sum(summary.per_class_instance_share.values()) - 1.0) < 1e-9


def test_class_image_count_differs_from_instance_count() -> None:
    """Dua instance pada satu citra harus dihitung sebagai satu citra."""
    images = [ImageRecord(1, "a.jpg", 100, 100)]
    annotations = [
        AnnotationRecord(1, 1, "Blast", (0, 0, 10, 10)),
        AnnotationRecord(2, 1, "Blast", (20, 20, 10, 10)),
    ]
    summary = summarize_class_imbalance(_split(images, annotations))
    assert summary.per_class_instances["Blast"] == 2
    assert summary.per_class_images["Blast"] == 1


def test_relative_area_is_computed_against_its_own_image() -> None:
    images = [ImageRecord(1, "a.jpg", 100, 100), ImageRecord(2, "b.jpg", 200, 200)]
    annotations = [
        AnnotationRecord(1, 1, "Blast", (0, 0, 10, 10)),
        AnnotationRecord(2, 2, "Blast", (0, 0, 10, 10)),
    ]
    geometry = compute_bbox_geometry(_split(images, annotations))

    assert geometry.areas == [100.0, 100.0]
    assert geometry.relative_areas == [0.01, 0.0025]


def test_small_object_share_respects_threshold() -> None:
    images = [ImageRecord(1, "a.jpg", 100, 100)]
    annotations = [
        AnnotationRecord(1, 1, "Blast", (0, 0, 5, 5)),
        AnnotationRecord(2, 1, "Blast", (0, 0, 50, 50)),
    ]
    geometry = compute_bbox_geometry(_split(images, annotations), small_object_threshold=0.01)
    assert geometry.small_object_share == 0.5


def test_degenerate_boxes_are_excluded_from_geometry() -> None:
    images = [ImageRecord(1, "a.jpg", 100, 100)]
    annotations = [
        AnnotationRecord(1, 1, "Blast", (0, 0, 10, 10)),
        AnnotationRecord(2, 1, "Blast", (0, 0, 0, 10)),
        AnnotationRecord(3, 1, "Blast", (0, 0, 10, -5)),
    ]
    geometry = compute_bbox_geometry(_split(images, annotations))
    assert geometry.count == 1


def test_resolution_summary_reports_dominant_size() -> None:
    images = [
        ImageRecord(1, "a.jpg", 640, 640),
        ImageRecord(2, "b.jpg", 640, 640),
        ImageRecord(3, "c.jpg", 800, 600),
    ]
    summary = summarize_resolution(_split(images, []))
    assert summary.distinct_resolutions == 2
    assert summary.most_common_resolution == (640, 640)
    assert abs(summary.most_common_share - 2 / 3) < 1e-9


def test_scene_density_counts_crowded_images() -> None:
    images = [ImageRecord(1, "a.jpg", 100, 100), ImageRecord(2, "b.jpg", 100, 100)]
    annotations = [AnnotationRecord(i, 1, "Blast", (0, 0, 10, 10)) for i in range(1, 6)]
    annotations.append(AnnotationRecord(6, 2, "Blast", (0, 0, 10, 10)))

    density = scene_density_summary(_split(images, annotations), crowded_threshold=3)
    assert density["crowded_images"] == 1
    assert density["max_annotations_in_one_image"] == 5


def test_missingness_audit_detects_broken_references(tmp_path) -> None:
    split_dir = tmp_path / "train"
    split_dir.mkdir()
    (split_dir / "present.jpg").write_bytes(b"x")
    (split_dir / "orphan.jpg").write_bytes(b"x")

    coco = {
        "images": [
            {"id": 1, "file_name": "present.jpg", "width": 100, "height": 100},
            {"id": 2, "file_name": "absent.jpg", "width": 100, "height": 100},
            {"id": 3, "file_name": "present.jpg", "width": 0, "height": 100},
        ],
        "annotations": [
            {"id": 1, "image_id": 1, "category_id": 1, "bbox": [0, 0, 10, 10]},
            {"id": 2, "image_id": 99, "category_id": 1, "bbox": [0, 0, 10, 10]},
            {"id": 3, "image_id": 1, "category_id": 77, "bbox": [0, 0, 10, 10]},
            {"id": 4, "image_id": 1, "category_id": 1, "bbox": [0, 0, 0, 10]},
            {"id": 5, "image_id": 1, "category_id": 1, "bbox": None},
        ],
        "categories": [{"id": 1, "name": "Blast"}, {"id": 2, "name": "Unused"}],
    }
    (split_dir / "_annotations.coco.json").write_text(json.dumps(coco), encoding="utf-8")

    report = audit_missingness(tmp_path, "train", "_annotations.coco.json")
    by_name = {c.name: c.count for c in report.checks}

    assert by_name["Berkas citra hilang (dirujuk JSON, tidak ada di disk)"] == 1
    assert by_name["Berkas citra di disk tanpa record JSON"] == 1
    assert by_name["Citra tanpa anotasi"] == 2
    assert by_name["Anotasi merujuk image_id yang tidak ada"] == 1
    assert by_name["Anotasi merujuk category_id yang tidak ada"] == 1
    assert by_name["Bounding box kosong atau tidak lengkap"] == 1
    assert by_name["Bounding box dengan lebar atau tinggi tidak valid"] == 1
    assert by_name["Metadata dimensi citra tidak tersedia"] == 1
    assert by_name["Kategori tanpa anotasi"] == 1
    assert report.all_clear is False


def test_missingness_audit_reports_clean_dataset(tmp_path) -> None:
    split_dir = tmp_path / "valid"
    split_dir.mkdir()
    (split_dir / "a.jpg").write_bytes(b"x")

    coco = {
        "images": [{"id": 1, "file_name": "a.jpg", "width": 100, "height": 100}],
        "annotations": [{"id": 1, "image_id": 1, "category_id": 1, "bbox": [0, 0, 10, 10]}],
        "categories": [{"id": 1, "name": "Blast"}],
    }
    (split_dir / "_annotations.coco.json").write_text(json.dumps(coco), encoding="utf-8")

    report = audit_missingness(tmp_path, "valid", "_annotations.coco.json")
    assert report.all_clear is True
    assert all(c.percentage == 0.0 for c in report.checks)
