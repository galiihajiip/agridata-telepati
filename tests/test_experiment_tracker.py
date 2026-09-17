"""Unit tests for the lightweight experiment tracker (Block 9)."""

from __future__ import annotations

import pytest

from agridata.experiments.tracker import (
    ExperimentRecord,
    append_experiment,
    build_markdown_table,
    compute_manifest_hash,
    load_experiments,
)


def _make_record(experiment_id: str = "E01") -> ExperimentRecord:
    return ExperimentRecord(
        experiment_id=experiment_id,
        timestamp_utc="2026-01-01T00:00:00+00:00",
        git_commit="abc123",
        seed=42,
        model_architecture="yolov8n.yaml",
        pretrained=False,
        dataset_manifest_hash="deadbeef",
        image_size=320,
        batch_size=8,
        epochs=2,
        optimizer="AdamW",
        learning_rate=0.000667,
        weight_decay=0.0005,
        scheduler="linear",
        augmentation_config={"fliplr": 0.5},
        device="mps",
        best_val_map50=0.0,
        best_val_f1=0.0,
        precision=0.0,
        recall=0.0,
        training_duration_seconds=104.7,
        notes="baseline smoke test",
        compliance_notes="no external pretrained weights",
    )


def test_append_and_load_roundtrip(tmp_path) -> None:
    log_path = tmp_path / "log.json"
    append_experiment(_make_record("E01"), log_path)

    records = load_experiments(log_path)
    assert len(records) == 1
    assert records[0]["experiment_id"] == "E01"
    assert records[0]["seed"] == 42


def test_append_multiple_experiments(tmp_path) -> None:
    log_path = tmp_path / "log.json"
    append_experiment(_make_record("E01"), log_path)
    append_experiment(_make_record("E02"), log_path)

    records = load_experiments(log_path)
    assert {r["experiment_id"] for r in records} == {"E01", "E02"}


def test_duplicate_experiment_id_rejected(tmp_path) -> None:
    log_path = tmp_path / "log.json"
    append_experiment(_make_record("E01"), log_path)

    with pytest.raises(ValueError, match="already exists"):
        append_experiment(_make_record("E01"), log_path)


def test_load_experiments_missing_file_returns_empty_list(tmp_path) -> None:
    assert load_experiments(tmp_path / "does_not_exist.json") == []


def test_manifest_hash_is_deterministic_and_content_sensitive(tmp_path) -> None:
    manifest_a = tmp_path / "manifest_a.json"
    manifest_a.write_text('[{"id": 1}]', encoding="utf-8")
    manifest_b = tmp_path / "manifest_b.json"
    manifest_b.write_text('[{"id": 1}]', encoding="utf-8")
    manifest_c = tmp_path / "manifest_c.json"
    manifest_c.write_text('[{"id": 2}]', encoding="utf-8")

    assert compute_manifest_hash(manifest_a) == compute_manifest_hash(manifest_b)
    assert compute_manifest_hash(manifest_a) != compute_manifest_hash(manifest_c)


def test_markdown_table_sorted_by_experiment_id() -> None:
    records = [_make_record("E02").__dict__, _make_record("E01").__dict__]
    table = build_markdown_table(records)
    assert table.index("E01") < table.index("E02")


def test_markdown_table_handles_missing_metrics_gracefully() -> None:
    record = _make_record("E01").__dict__
    record["best_val_map50"] = None
    table = build_markdown_table([record])
    assert "N/A" in table
