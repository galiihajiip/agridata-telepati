#!/usr/bin/env python3
"""CLI to log a completed training run into the experiment tracker (Block 9).

Usage:
    python scripts/track_experiment.py \\
        --experiment-id E01 \\
        --training-summary artifacts/reports/block6_baseline_smoke_summary.json \\
        --evaluation-summary artifacts/reports/evaluation_valid.json \\
        --manifest data/prepared/manifest_train.json \\
        --notes "baseline smoke test" \\
        --compliance-notes "no external pretrained weights; YOLO_OFFLINE enforced"

Reads the training and (optional) evaluation summaries already produced by
scripts/train.py / scripts/evaluate.py rather than re-deriving anything,
this script's only job is to assemble and append one ExperimentRecord.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.experiments.tracker import (  # noqa: E402
    DEFAULT_LOG_PATH,
    ExperimentRecord,
    append_experiment,
    build_markdown_table,
    compute_manifest_hash,
    load_experiments,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Log a completed training run into the experiment tracker.")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--training-summary", required=True, type=Path)
    parser.add_argument("--evaluation-summary", type=Path, default=None, help="Optional: scripts/evaluate.py JSON output, for validation metrics.")
    parser.add_argument("--manifest", required=True, type=Path, help="Prepared-dataset manifest to fingerprint (dataset version).")
    parser.add_argument("--notes", default="")
    parser.add_argument("--compliance-notes", default="")
    parser.add_argument("--log-path", default=DEFAULT_LOG_PATH, type=Path)
    parser.add_argument("--report-path", default=Path("artifacts/experiments/experiment_log.md"), type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    with args.training_summary.open("r", encoding="utf-8") as f:
        training = json.load(f)

    best_val_map50 = best_val_f1 = precision = recall = None
    if args.evaluation_summary and args.evaluation_summary.exists():
        with args.evaluation_summary.open("r", encoding="utf-8") as f:
            evaluation = json.load(f)
        best_val_map50 = evaluation["native_metrics"]["mAP50"]
        local_overall = evaluation["local_f1_metrics"]["overall"]
        best_val_f1 = local_overall["f1"]
        precision = local_overall["precision"]
        recall = local_overall["recall"]

    hyperparams = training.get("resolved_hyperparameters", {})
    record = ExperimentRecord(
        experiment_id=args.experiment_id,
        timestamp_utc=training["finished_at_utc"],
        git_commit=training.get("git_commit"),
        seed=training["seed"],
        model_architecture=training["model_arch"],
        pretrained=training["pretrained"],
        dataset_manifest_hash=compute_manifest_hash(args.manifest),
        image_size=training["image_size"],
        batch_size=training["batch_size"],
        epochs=training["epochs"],
        optimizer=hyperparams.get("optimizer", "unknown"),
        learning_rate=hyperparams.get("learning_rate", 0.0),
        weight_decay=hyperparams.get("weight_decay", 0.0),
        scheduler=hyperparams.get("scheduler", "unknown"),
        augmentation_config=hyperparams.get("augmentation", {}),
        device=training["device"],
        best_val_map50=best_val_map50,
        best_val_f1=best_val_f1,
        precision=precision,
        recall=recall,
        training_duration_seconds=training.get("duration_seconds"),
        notes=args.notes,
        compliance_notes=args.compliance_notes,
    )

    append_experiment(record, args.log_path)
    records = load_experiments(args.log_path)

    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(build_markdown_table(records), encoding="utf-8")

    print(f"Logged experiment '{args.experiment_id}' to {args.log_path}")
    print(build_markdown_table(records))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
