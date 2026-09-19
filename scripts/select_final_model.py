#!/usr/bin/env python3
"""Final model configuration selection report (Block 14).

Usage:
    python scripts/select_final_model.py

Reviews all logged experiments (artifacts/experiments/experiment_log.json)
and produces a factual selection report plus model metadata / model-card
draft. This selects and freezes a CONFIGURATION, not a trained weights
file, the actual final weights are produced by Block 15 using
configs/final_model_config.yaml. Per the master spec, no configuration is
declared "acceptable" on validation performance until the full-scale run
completes; this report says so explicitly rather than overclaiming.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.dataset.mapping import CANONICAL_CLASSES, MAPPING_VERSION  # noqa: E402
from agridata.reproducibility.environment import capture_environment_snapshot  # noqa: E402

FINAL_CONFIG_PATH = Path("configs/final_model_config.yaml")
EXPERIMENT_LOG_PATH = Path("artifacts/experiments/experiment_log.json")
REPORT_DIR = Path("artifacts/reports")
DOCS_DIR = Path("docs")


def load_experiments() -> list[dict]:
    with EXPERIMENT_LOG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_file_size_mb(path: Path) -> float | None:
    return round(path.stat().st_size / (1024 * 1024), 2) if path.exists() else None


def build_candidate_table(experiments: list[dict]) -> str:
    lines = [
        "| Experiment | imgsz | epochs | optimizer | mAP@0.5 | Precision | Recall | Duration (s) | Notes |",
        "|---|---:|---:|---|---:|---:|---:|---:|---|",
    ]
    for r in sorted(experiments, key=lambda r: -r["best_val_map50"]):
        notes = r["notes"][:70].replace("|", "\\|")
        lines.append(
            f"| {r['experiment_id']} | {r['image_size']} | {r['epochs']} | {r['optimizer']} | "
            f"{r['best_val_map50']:.4f} | {r['precision']:.4f} | {r['recall']:.4f} | "
            f"{r['training_duration_seconds']:.0f} | {notes} |"
        )
    return "\n".join(lines)


def get_git_commit() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def build_compliance_checklist(experiments: list[dict]) -> list[dict]:
    best = max(experiments, key=lambda r: r["best_val_map50"])
    return [
        {
            "item": "No external pretrained weights",
            "status": "PASS",
            "evidence": "Block 6: model always built from yolov8n.yaml (architecture only); "
            "build_compliant_model() raises if pretrained=True or given a .pt/.pth/.ckpt file. "
            "YOLO_OFFLINE enforced across all training/eval scripts. Empty pretrained-checkpoint-cache "
            "verification performed in Block 6 (before/after directory diff, zero .pt files appeared "
            "anywhere outside this project's own runs/ output).",
        },
        {
            "item": "No data leakage",
            "status": "PARTIAL, one confirmed case fixed, residual risk documented",
            "evidence": "Block 2 forensic audit found exactly one exact-duplicate image (MD5-identical) "
            "across train/test ('leaf_scald-230...'); Block 5 excludes it from the prepared train "
            "manifest. Perceptual-hash overlap candidates (Block 2) are unconfirmed and were not "
            "further investigated, flagged as a residual, documented risk, not silently ignored.",
        },
        {
            "item": "Official canonical 11 classes",
            "status": "PASS",
            "evidence": f"Block 3: canonical mapping validated against the actual dataset with zero "
            f"unmapped raw categories (mapping version {MAPPING_VERSION}). Block 5's data.yaml always "
            f"declares exactly {len(CANONICAL_CLASSES)} classes in canonical order: {list(CANONICAL_CLASSES)}.",
        },
        {
            "item": "Reproducible preprocessing",
            "status": "PASS",
            "evidence": "Block 8: rerunning scripts/prepare_dataset.py with the same seed produced a "
            "byte-for-byte identical 10,132-image manifest, verified via a live rerun-and-diff, not assumed.",
        },
        {
            "item": "Reproducible configuration",
            "status": "PASS",
            "evidence": f"Block 9 tracker records seed/git-commit/hyperparameters for every one of the "
            f"{len(experiments)} logged experiments. This report's frozen config "
            f"({FINAL_CONFIG_PATH}) is itself version-controlled.",
        },
        {
            "item": "Valid checkpoint",
            "status": "PASS for screening checkpoints, PENDING for final weights",
            "evidence": "All 21 screening experiments produced a loadable best.pt (verified by reloading "
            "fresh in evaluate.py/error-analysis runs). The actual final-submission checkpoint does not "
            "exist yet, it is produced by Block 15 and must be re-verified there.",
        },
        {
            "item": "Successful inference",
            "status": "PASS",
            "evidence": "Block 6: standalone inference test on a freshly-loaded checkpoint in a clean "
            "process. Blocks 7/13: evaluate.py and run_error_analysis.py both successfully ran inference "
            "on screening checkpoints across the full valid split (2,106 images).",
        },
        {
            "item": "Acceptable validation performance",
            "status": "PENDING, NOT YET MET, explicitly not claimed",
            "evidence": f"Best screening result so far: {best['experiment_id']} at mAP@0.5="
            f"{best['best_val_map50']:.4f}, trained on only ~10% of train data for {best['epochs']} epochs. "
            "This is a screening-scale number, not a competitive result, and is not represented as one. "
            "Full-scale training (Block 15: fraction=1.0, epochs=50, patience=15) is required before this "
            "item can be assessed honestly.",
        },
    ]


def build_report(experiments: list[dict], checklist: list[dict], git_commit: str) -> str:
    best = max(experiments, key=lambda r: r["best_val_map50"])
    lines = [
        "# Block 14. Final Model Configuration Selection",
        "",
        f"Reviewed all {len(experiments)} logged experiments (E01-E{len(experiments):02d}). This block "
        "selects and freezes a CONFIGURATION for full-scale training (Block 15), it does not itself "
        "produce the final submitted weights.",
        "",
        "## All candidate experiments (sorted by mAP@0.5)",
        "",
        build_candidate_table(experiments),
        "",
        f"## Selected configuration: see `{FINAL_CONFIG_PATH}`",
        "",
        f"Best individual screening result: **{best['experiment_id']}** (mAP@0.5={best['best_val_map50']:.4f}). "
        "The frozen final config does not simply copy this one experiment's settings verbatim, it "
        "synthesizes evidence across all 21 experiments (see the config file's inline rationale comments "
        "for each hyperparameter) plus Block 11's semantic-plausibility reasoning and Block 13's "
        "independent error-analysis evidence.",
        "",
        "## Compliance checklist (evidence-based, not asserted)",
        "",
        "| # | Item | Status | Evidence |",
        "|---:|---|---|---|",
    ]
    for i, c in enumerate(checklist, start=1):
        lines.append(f"| {i} | {c['item']} | {c['status']} | {c['evidence']} |")

    lines += [
        "",
        "## Known risks",
        "",
        "- Residual, unconfirmed perceptual-hash overlap candidates from Block 2 (train-vs-valid: 426, "
        "train-vs-test: 210, valid-vs-test: 84) were never individually visually confirmed as true "
        "duplicates or false positives from the coarse 8x8 aHash. Only the one exact-MD5 duplicate was "
        "acted on.",
        "- All 21 screening experiments used a small fraction of train data (8-10%) and few epochs "
        "(5-12); the frozen config's full-scale numbers (epochs=50, fraction=1.0) are extrapolated, "
        "not directly measured. Block 15 is the first point at which the real full-scale behavior "
        "is observed.",
        "- MPS backend has confirmed non-deterministic kernels for `scatter_reduce_mps` and "
        "`index_put_with_accumulate_mps` (Block 6/8 finding), exact bit-for-bit reproducibility of "
        "training is not guaranteed, only reproducible configuration/preprocessing.",
        "- Estimated full-scale training time (~8.2 hours on this project's hardware) is long; "
        "`patience=15` may shorten it, but Block 15 must re-verify this estimate before committing.",
        "",
        f"Git commit at selection time: `{git_commit}`",
    ]
    return "\n".join(lines) + "\n"


def build_model_metadata(git_commit: str) -> dict:
    return {
        "model_name": "agridata-telepati8-yolov8n",
        "architecture": "YOLOv8n (Ultralytics), built from architecture-only .yaml, pretrained=False",
        "task": "object_detection",
        "num_classes": len(CANONICAL_CLASSES),
        "class_names": list(CANONICAL_CLASSES),
        "mapping_version": MAPPING_VERSION,
        "input": {"image_size": 640, "channels": 3, "format": "RGB"},
        "output": "bounding boxes (xyxy) + class + confidence, per canonical class",
        "training_config_path": str(FINAL_CONFIG_PATH),
        "compliance": {
            "external_pretrained_weights": False,
            "external_dataset_used": False,
            "llm_api_dataset_processing": False,
            "yolo_offline_enforced": True,
        },
        "status": "CONFIGURATION FROZEN, weights not yet produced (pending Block 15)",
        "selected_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit_at_selection": git_commit,
        "weights_path": None,
        "weights_checksum_sha256": None,
    }


def build_model_card_draft() -> str:
    return f"""# Model Card (Draft). AgriData TELEPATI 8.0 Rice Disease Detector

**Status: DRAFT.** Training config is frozen (`{FINAL_CONFIG_PATH}`); weights, final metrics, and
evaluation results will be filled in after Block 15 (final training run) and Block 16 (clean
reproduction test). Do not treat any number in this draft as final.

## Intended use

Object detection of rice plant disease/health conditions from field-captured imagery (drone or
handheld camera), as a component of a Smart Agriculture monitoring system, per the TELEPATI 8.0
AgriData Intelligence Race case study (assisting a farmer in monitoring large plots without
exhaustive manual inspection).

## Model architecture

YOLOv8n (Ultralytics), initialized from an architecture-only definition (no external pretrained
weights, `pretrained=False`, verified via source inspection and empty-checkpoint-cache checks in
Block 6). ~3.0M parameters, 11-class detection head.

## Training data

Official TELEPATI 8.0 AgriData dataset (COCO-format, Roboflow export). 11 canonical classes
(see `src/agridata/dataset/mapping.py` for the verified raw-to-canonical mapping):
{', '.join(CANONICAL_CLASSES)}.

One confirmed exact-duplicate image across train/test was excluded from training (Block 2/5).

## Training procedure

See `{FINAL_CONFIG_PATH}` for the complete, version-controlled configuration. Selected from 21
controlled screening experiments (Blocks 10-13), see
`artifacts/reports/block14_final_model_selection.md` for full reasoning per hyperparameter.

## Evaluation

*Pending Block 15/16.* Metrics will be computed via `scripts/evaluate.py` (mAP@0.5. Ultralytics'
native implementation; F1, a documented local implementation via greedy IoU≥0.5 matching at a
configurable confidence threshold, since Ultralytics' own reported precision/recall uses an
internally auto-selected threshold that is not configurable, see
`src/agridata/metrics/detection.py`).

## Known limitations (as of this draft)

- All findings so far come from small-fraction, low-epoch screening experiments; full-scale
  behavior may differ.
- Residual, unconfirmed perceptual-hash near-duplicate candidates across splits (Block 2) were
  not individually resolved.
- No bit-for-bit training determinism guarantee on Apple Silicon / MPS (confirmed non-deterministic
  kernels for two operations used in this pipeline).
- Class imbalance is real (22.6x max/min instance ratio); a targeted-oversampling mitigation was
  tested (Block 12) and did not show a clear benefit at screening scale, not adopted in the final
  config as of this draft; may be revisited after Block 15's full-scale results.

## Compliance statement

No external pretrained weights, no external dataset, no LLM/API dataset processing. See
`artifacts/reports/block14_final_model_selection.md` for the full evidence-based compliance
checklist.
"""


def main() -> int:
    experiments = load_experiments()
    git_commit = get_git_commit()
    checklist = build_compliance_checklist(experiments)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    report = build_report(experiments, checklist, git_commit)
    (REPORT_DIR / "block14_final_model_selection.md").write_text(report, encoding="utf-8")

    metadata = build_model_metadata(git_commit)
    with (REPORT_DIR / "final_model_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    (DOCS_DIR / "model_card_draft.md").write_text(build_model_card_draft(), encoding="utf-8")

    env_snapshot = capture_environment_snapshot()
    with (REPORT_DIR / "block14_environment_snapshot.json").open("w", encoding="utf-8") as f:
        json.dump(env_snapshot, f, indent=2)

    print(report)
    print("\nWritten:")
    print(f"  {REPORT_DIR / 'block14_final_model_selection.md'}")
    print(f"  {REPORT_DIR / 'final_model_metadata.json'}")
    print(f"  {DOCS_DIR / 'model_card_draft.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
