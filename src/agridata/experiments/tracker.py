"""Lightweight, offline experiment tracker (Block 9).

Deliberately avoids MLflow/W&B: this project's audit constraints prioritize
zero external dependencies, no internet requirement, no privacy exposure,
and minimal moving parts for a judge to reproduce, a single JSON file that
any script (or a human) can read is enough for this project's scale. Each
experiment is one record with a fixed schema; see `ExperimentRecord`.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_LOG_PATH = Path("artifacts/experiments/experiment_log.json")


@dataclass
class ExperimentRecord:
    """One row of the experiment tracker, fields per the master spec's Block 9 schema."""

    experiment_id: str
    timestamp_utc: str
    git_commit: str | None
    seed: int
    model_architecture: str
    pretrained: bool
    dataset_manifest_hash: str
    image_size: int
    batch_size: int
    epochs: int
    optimizer: str
    learning_rate: float
    weight_decay: float
    scheduler: str
    augmentation_config: dict[str, Any] = field(default_factory=dict)
    device: str = "cpu"
    best_val_map50: float | None = None
    best_val_f1: float | None = None
    precision: float | None = None
    recall: float | None = None
    training_duration_seconds: float | None = None
    notes: str = ""
    compliance_notes: str = ""


def compute_manifest_hash(manifest_path: Path) -> str:
    """SHA-256 of a prepared-dataset manifest file, a concrete, verifiable
    "dataset version" fingerprint tying an experiment to the exact data it
    was trained/evaluated on."""
    with manifest_path.open("rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_experiments(log_path: Path = DEFAULT_LOG_PATH) -> list[dict[str, Any]]:
    if not log_path.exists():
        return []
    with log_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def append_experiment(record: ExperimentRecord, log_path: Path = DEFAULT_LOG_PATH) -> None:
    """Append one experiment record to the log (read-modify-write on a single
    JSON array, sufficient at this project's scale; a real database is
    unnecessary complexity for a handful of tracked experiments)."""
    records = load_experiments(log_path)
    existing_ids = {r["experiment_id"] for r in records}
    if record.experiment_id in existing_ids:
        raise ValueError(f"experiment_id '{record.experiment_id}' already exists in {log_path}, use a unique ID.")

    records.append(asdict(record))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def build_markdown_table(records: list[dict[str, Any]]) -> str:
    """Render the experiment log as a Markdown table, sorted by experiment_id."""
    lines = [
        "# Experiment Log",
        "",
        "| Experiment | Model | Image Size | Batch | Optimizer | LR | Weight Decay | Scheduler | Epochs | Device | Best mAP@50 | Best F1 | Precision | Recall | Duration (s) | Notes |",
        "|---|---|---:|---:|---|---:|---:|---|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in sorted(records, key=lambda r: r["experiment_id"]):
        lines.append(
            f"| {r['experiment_id']} | {r['model_architecture']} | {r['image_size']} | {r['batch_size']} | "
            f"{r['optimizer']} | {r['learning_rate']:.6g} | {r['weight_decay']:.6g} | {r['scheduler']} | "
            f"{r['epochs']} | {r['device']} | "
            f"{_fmt(r['best_val_map50'])} | {_fmt(r['best_val_f1'])} | {_fmt(r['precision'])} | {_fmt(r['recall'])} | "
            f"{_fmt(r['training_duration_seconds'], 1)} | {r['notes']} |"
        )
    return "\n".join(lines) + "\n"


def _fmt(value: float | None, ndigits: int = 4) -> str:
    return "N/A" if value is None else f"{value:.{ndigits}f}"
