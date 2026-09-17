#!/usr/bin/env python3
"""CLI for reproducible mAP@50 and F1 evaluation (Block 7).

Usage:
    python scripts/evaluate.py --weights <PATH> --split valid --config configs/base.yaml

Two metric pathways (see src/agridata/metrics/detection.py for full
documentation of why both exist and exactly how each is computed):

  1. NATIVE mAP@0.5 / mAP@0.5:0.95 — via Ultralytics' `model.val()`. This is
     the source of truth for mAP; this project does not reimplement AP
     integration.
  2. LOCAL precision/recall/F1 at `--conf-threshold` — via our own greedy
     IoU>=0.5 matching, because Ultralytics' own reported precision/recall
     uses an internally auto-selected confidence threshold that is not
     configurable.

Test-set evaluation is for final reporting only, never for iterative model
tuning — a WARNING is logged whenever `--split test` is used.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

os.environ.setdefault("YOLO_OFFLINE", "1")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ultralytics import YOLO  # noqa: E402

from agridata.dataset.mapping import CANONICAL_CLASSES, CANONICAL_ID_TO_NAME  # noqa: E402
from agridata.device import detect_device  # noqa: E402
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.metrics.detection import (  # noqa: E402
    Detection,
    GroundTruthBox,
    match_detections_to_ground_truth,
)
from agridata.visualization.images import draw_annotated_image  # noqa: E402
from agridata.dataset.stats import AnnotationRecord, ImageRecord  # noqa: E402

logger = logging.getLogger("agridata.scripts.evaluate")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reproducible mAP@50 / F1 evaluation (no test-set tuning).")
    parser.add_argument("--weights", required=True, type=Path)
    parser.add_argument("--split", required=True, choices=["train", "valid", "test"])
    parser.add_argument("--prepared-dir", default=Path("data/prepared"), type=Path)
    parser.add_argument("--data-yaml", default=None, type=Path, help="Defaults to <prepared-dir>/data.yaml")
    parser.add_argument("--conf-threshold", type=float, default=0.25, help="Confidence threshold for the LOCAL F1 computation (configurable).")
    parser.add_argument("--collection-conf", type=float, default=0.001, help="Low threshold used once to collect raw predictions; --conf-threshold filters afterward.")
    parser.add_argument("--num-vis-samples", type=int, default=6)
    parser.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    parser.add_argument("--predictions-dir", default=Path("artifacts/predictions"), type=Path)
    parser.add_argument("--figures-dir", default=Path("artifacts/figures/predictions"), type=Path)
    return parser.parse_args()


def get_git_commit() -> str | None:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def validate_class_mapping(model: YOLO) -> None:
    """Fail loudly if the model's class order doesn't match the canonical mapping.

    Ground truth (from the Block 5 manifest) uses model_class_id =
    canonical_id - 1 in CANONICAL_CLASSES order. If the model's own class
    order ever diverged from that (e.g. trained against a different
    data.yaml), predictions and ground truth would silently misalign.
    """
    model_names = [model.names[i] for i in range(len(model.names))]
    if model_names != list(CANONICAL_CLASSES):
        raise ValueError(
            f"Model class order {model_names} does not match the canonical class "
            f"order {list(CANONICAL_CLASSES)} — ground truth and predictions would "
            "not be comparable. Refusing to compute metrics."
        )


def load_ground_truth(manifest_path: Path) -> tuple[list[GroundTruthBox], dict[int, dict]]:
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)
    ground_truths = []
    images_by_id = {}
    for entry in manifest:
        images_by_id[entry["original_image_id"]] = entry
        for ann in entry["annotations"]:
            ground_truths.append(
                GroundTruthBox(entry["original_image_id"], ann["model_class_id"], tuple(ann["bbox_xywh"]))
            )
    return ground_truths, images_by_id


def collect_predictions(model: YOLO, images_dir: Path, images_by_id: dict[int, dict], collection_conf: float) -> list[Detection]:
    """Run inference once at a low confidence threshold; filtering by a higher
    threshold happens later in match_detections_to_ground_truth (pure function,
    no re-inference needed per threshold).

    Uses `stream=True` so Ultralytics yields one Result at a time instead of
    accumulating all of them (each holding image tensors) in RAM — necessary
    at full-dataset scale (Ultralytics itself warns against the non-streamed
    form for exactly this reason).
    """
    ordered_ids = list(images_by_id.keys())
    image_paths = [str(images_dir / images_by_id[iid]["file_name"]) for iid in ordered_ids]

    detections: list[Detection] = []
    results_stream = model.predict(image_paths, conf=collection_conf, verbose=False, stream=True)
    for image_id, result in zip(ordered_ids, results_stream, strict=True):
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append(
                Detection(
                    image_id=image_id,
                    class_id=int(box.cls.item()),
                    confidence=float(box.conf.item()),
                    bbox_xywh=(x1, y1, x2 - x1, y2 - y1),
                )
            )
    return detections


def save_prediction_samples(
    images_dir: Path,
    images_by_id: dict[int, dict],
    detections: list[Detection],
    conf_threshold: float,
    num_samples: int,
    output_dir: Path,
) -> list[str]:
    """Save a small number of images with PREDICTED boxes drawn, for visual sanity-checking."""
    det_by_image: dict[int, list[Detection]] = {}
    for d in detections:
        if d.confidence >= conf_threshold:
            det_by_image.setdefault(d.image_id, []).append(d)

    image_ids_with_predictions = sorted(det_by_image.keys())[:num_samples]
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for image_id in image_ids_with_predictions:
        entry = images_by_id[image_id]
        image_record = ImageRecord(image_id, entry["file_name"], entry["width"], entry["height"])
        pred_annotations = [
            AnnotationRecord(
                annotation_id=-1,
                image_id=image_id,
                canonical_class=CANONICAL_ID_TO_NAME[d.class_id + 1],
                bbox=d.bbox_xywh,
            )
            for d in det_by_image[image_id]
        ]
        annotated = draw_annotated_image(images_dir / entry["file_name"], image_record, pred_annotations)
        out_path = output_dir / f"pred_id{image_id}_{entry['file_name']}"
        annotated.save(out_path)
        saved.append(str(out_path))
    return saved


def main() -> int:
    setup_logging()
    args = parse_args()

    if args.split == "test":
        logger.warning(
            "Evaluating on the TEST split. Per the master spec, test ground truth must "
            "NEVER be used to tune the model — this run should only happen for final, "
            "frozen-model reporting (Block 15+), not iterative experimentation."
        )

    data_yaml = args.data_yaml or (args.prepared_dir / "data.yaml")
    manifest_path = args.prepared_dir / f"manifest_{args.split}.json"
    images_dir = args.prepared_dir / args.split / "images"

    logger.info("Loading model from %s", args.weights)
    model = YOLO(str(args.weights))
    validate_class_mapping(model)
    logger.info("Class mapping validated: model class order matches canonical mapping exactly.")

    # --- 1. NATIVE metrics (mAP@0.5, mAP@0.5:0.95) via Ultralytics val() ---
    # Ultralytics' `split` argument is a literal lookup key into data.yaml
    # (which uses the YOLO convention "val", not this project's "valid"
    # directory/manifest naming) — translate explicitly rather than assume.
    ultralytics_split = {"train": "train", "valid": "val", "test": "test"}[args.split]
    logger.info("Running native Ultralytics validation for mAP@0.5 / mAP@0.5:0.95 ...")
    val_results = model.val(data=str(data_yaml), split=ultralytics_split, plots=False, verbose=False)
    native_metrics = {
        "mAP50": float(val_results.box.map50),
        "mAP50_95": float(val_results.box.map),
        "precision_at_internal_best_f1_point": float(val_results.box.mp),
        "recall_at_internal_best_f1_point": float(val_results.box.mr),
    }
    per_class_map50 = {}
    for idx, class_id in enumerate(val_results.box.ap_class_index):
        canonical_name = CANONICAL_ID_TO_NAME[int(class_id) + 1]
        per_class_map50[canonical_name] = float(val_results.box.ap50[idx])

    # --- 2. LOCAL precision/recall/F1 at a configurable confidence threshold ---
    logger.info("Collecting raw predictions for local F1 computation (conf>=%.4f) ...", args.collection_conf)
    ground_truths, images_by_id = load_ground_truth(manifest_path)
    detections = collect_predictions(model, images_dir, images_by_id, args.collection_conf)
    logger.info("Collected %d raw detections across %d images.", len(detections), len(images_by_id))

    local_result = match_detections_to_ground_truth(detections, ground_truths, args.conf_threshold)
    local_overall = local_result["overall"]
    local_per_class = {
        CANONICAL_ID_TO_NAME[cid + 1]: asdict(prf1) for cid, prf1 in local_result["per_class"].items()
    }

    # --- Save prediction artifacts ---
    args.predictions_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = args.predictions_dir / f"predictions_{args.split}.json"
    with predictions_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(d) for d in detections], f, indent=2)

    # --- Visualization: a few predicted-box samples ---
    saved_samples = save_prediction_samples(
        images_dir, images_by_id, detections, args.conf_threshold, args.num_vis_samples, args.figures_dir
    )

    summary = {
        "block": 7,
        "git_commit": get_git_commit(),
        "weights": str(args.weights),
        "split": args.split,
        "data_yaml": str(data_yaml),
        "iou_threshold": 0.5,
        "native_metrics": {
            "description": "Computed via ultralytics model.val() — source of truth for mAP. "
            "IoU thresholds: torch.linspace(0.5, 0.95, 10); mAP50 uses index 0 (IoU=0.50).",
            **native_metrics,
            "per_class_AP50": per_class_map50,
        },
        "local_f1_metrics": {
            "description": "LOCAL implementation detail (not the official scoring formula): "
            "greedy IoU>=0.5 matching at a caller-specified confidence threshold. See "
            "src/agridata/metrics/detection.py for full methodology.",
            "confidence_threshold": args.conf_threshold,
            "overall": asdict(local_overall),
            "per_class": local_per_class,
        },
        "num_detections_collected": len(detections),
        "num_ground_truth_boxes": len(ground_truths),
        "predictions_artifact": str(predictions_path),
        "sample_prediction_figures": saved_samples,
        "test_set_tuning_warning_issued": args.split == "test",
    }

    args.report_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.report_dir / f"evaluation_{args.split}.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    md_lines = [
        f"# Evaluation Report — split: `{args.split}`",
        "",
        f"Weights: `{args.weights}`  |  Git commit: `{summary['git_commit']}`",
        "",
        "## Native metrics (Ultralytics, source of truth for mAP)",
        "",
        f"- mAP@0.5: {native_metrics['mAP50']:.4f}",
        f"- mAP@0.5:0.95: {native_metrics['mAP50_95']:.4f}",
        f"- Precision/Recall at Ultralytics' internal best-F1 point: "
        f"{native_metrics['precision_at_internal_best_f1_point']:.4f} / {native_metrics['recall_at_internal_best_f1_point']:.4f}",
        "",
        "| canonical class | AP@0.5 |",
        "|---|---:|",
    ]
    for cls, ap in per_class_map50.items():
        md_lines.append(f"| {cls} | {ap:.4f} |")
    md_lines += [
        "",
        f"## Local F1 metrics (implementation detail, confidence threshold = {args.conf_threshold})",
        "",
        f"- Overall precision: {local_overall.precision:.4f}",
        f"- Overall recall: {local_overall.recall:.4f}",
        f"- Overall F1: {local_overall.f1:.4f}",
        f"- TP={local_overall.true_positives} FP={local_overall.false_positives} FN={local_overall.false_negatives}",
        "",
        "| canonical class | precision | recall | F1 | TP | FP | FN |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for cls, prf1 in local_per_class.items():
        md_lines.append(
            f"| {cls} | {prf1['precision']:.4f} | {prf1['recall']:.4f} | {prf1['f1']:.4f} | "
            f"{prf1['true_positives']} | {prf1['false_positives']} | {prf1['false_negatives']} |"
        )
    if args.split == "test":
        md_lines += ["", "**WARNING: this is a test-split evaluation. Test ground truth must never be used for iterative model tuning.**"]

    md_path = args.report_dir / f"evaluation_{args.split}.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print("\n".join(md_lines))
    print(f"\nJSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    print(f"Prediction artifacts: {predictions_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
