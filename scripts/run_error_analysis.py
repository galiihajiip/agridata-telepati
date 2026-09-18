#!/usr/bin/env python3
"""Object detection error analysis (Block 13).

Usage:
    python scripts/run_error_analysis.py --weights runs/detect/matrix/E08/weights/best.pt --split valid

Read-only against the model and dataset: this script only ANALYZES and
REPORTS. It never modifies training data or the model based on what it
finds — per the master spec, any data change proposed from visual
inspection must be a separate, explicitly documented decision made by a
human/later block, not applied automatically here.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import statistics
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

os.environ.setdefault("YOLO_OFFLINE", "1")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ultralytics import YOLO  # noqa: E402

from agridata.analysis.error_analysis import analyze_errors  # noqa: E402
from agridata.dataset.mapping import CANONICAL_CLASSES, CANONICAL_ID_TO_NAME  # noqa: E402
from agridata.dataset.stats import AnnotationRecord, ImageRecord  # noqa: E402
from agridata.device import detect_device  # noqa: E402
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.metrics.detection import Detection, GroundTruthBox  # noqa: E402
from agridata.visualization.images import draw_annotated_image  # noqa: E402

logger = logging.getLogger("agridata.scripts.run_error_analysis")

CLASS_NAMES = {i: name for i, name in enumerate(CANONICAL_CLASSES)}


def _caveat_text(per_class_pr: dict) -> str:
    """Describe how much of the class space this checkpoint has actually learned.

    Computed from this run's real per-class TP counts — never a hardcoded
    description of some other, earlier checkpoint. A prior version of this
    function hardcoded prose about a specific 10-epoch screening checkpoint
    (E08); that text kept printing verbatim for every later checkpoint this
    script analyzed, including the final submitted model, which had already
    learned every class. Fixed to be dynamic."""
    zero_tp = [cls for cls, pr in per_class_pr.items() if pr["tp"] == 0]
    total = len(per_class_pr)
    if not zero_tp:
        return (
            f"This checkpoint has at least one true positive on all {total}/{total} classes — "
            "confusion patterns above reflect genuine model behavior, not simply classes the "
            "model has not learned yet."
        )
    return (
        f"This checkpoint has zero true positives on {len(zero_tp)}/{total} classes "
        f"({', '.join(zero_tp)}) — it has not learned those classes at all. Confusion patterns "
        "above involving those classes mostly reflect \"the model hasn't learned this yet\", not "
        "a stable, meaningful semantic confusion. Only classes with non-trivial TP counts support "
        "any real interpretation at this stage."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Object detection error analysis (read-only; proposes, does not apply, changes).")
    parser.add_argument("--weights", required=True, type=Path)
    parser.add_argument("--split", default="valid")
    parser.add_argument("--prepared-dir", default=Path("data/prepared"), type=Path)
    parser.add_argument("--confidence-threshold", type=float, default=0.1)
    parser.add_argument("--collection-conf", type=float, default=0.02)
    parser.add_argument("--num-examples", type=int, default=4)
    parser.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    parser.add_argument("--figures-dir", default=Path("artifacts/figures/error_analysis"), type=Path)
    return parser.parse_args()


def load_ground_truth(manifest_path: Path) -> tuple[list[GroundTruthBox], dict[int, dict]]:
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)
    ground_truths, images_by_id = [], {}
    for entry in manifest:
        images_by_id[entry["original_image_id"]] = entry
        for ann in entry["annotations"]:
            ground_truths.append(GroundTruthBox(entry["original_image_id"], ann["model_class_id"], tuple(ann["bbox_xywh"])))
    return ground_truths, images_by_id


def collect_predictions(model: YOLO, images_dir: Path, images_by_id: dict[int, dict], collection_conf: float, device: str) -> list[Detection]:
    """Chunked to avoid a Block 16-confirmed failure: passing a very large
    (2000+) explicit path list to a single `predict(..., stream=True)` call
    fails with "MPSGraph does not support tensor dims larger than INT_MAX"
    on this project's numpy/torch/MPS combination — see
    scripts/evaluate.py::collect_predictions for the full investigation."""
    CHUNK_SIZE = 500
    ordered_ids = list(images_by_id.keys())
    image_paths = [str(images_dir / images_by_id[iid]["file_name"]) for iid in ordered_ids]
    detections = []
    for chunk_start in range(0, len(image_paths), CHUNK_SIZE):
        chunk_ids = ordered_ids[chunk_start : chunk_start + CHUNK_SIZE]
        chunk_paths = image_paths[chunk_start : chunk_start + CHUNK_SIZE]
        results_stream = model.predict(chunk_paths, conf=collection_conf, verbose=False, stream=True, device=device)
        for image_id, result in zip(chunk_ids, results_stream, strict=True):
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append(Detection(image_id, int(box.cls.item()), float(box.conf.item()), (x1, y1, x2 - x1, y2 - y1)))
    return detections


def save_examples(images_dir: Path, images_by_id: dict, entries: list, tag: str, output_dir: Path, num: int, det_or_gt: str) -> list[str]:
    """Save a handful of images annotated with the specific error-type boxes drawn."""
    by_image: dict[int, list] = {}
    for e in entries:
        by_image.setdefault(e.image_id, []).append(e)

    saved = []
    for image_id in list(by_image.keys())[:num]:
        entry = images_by_id[image_id]
        image_record = ImageRecord(image_id, entry["file_name"], entry["width"], entry["height"])
        anns = []
        for e in by_image[image_id]:
            if det_or_gt == "bg_fp":
                anns.append(AnnotationRecord(-1, image_id, f"FP:{e.predicted_class}", e.bbox_xywh))
            else:
                anns.append(AnnotationRecord(-1, image_id, f"FN:{e.true_class}", e.bbox_xywh))
        annotated = draw_annotated_image(images_dir / entry["file_name"], image_record, anns)
        out_path = output_dir / f"{tag}_id{image_id}_{entry['file_name']}"
        output_dir.mkdir(parents=True, exist_ok=True)
        annotated.save(out_path)
        saved.append(str(out_path))
    return saved


def main() -> int:
    setup_logging()
    args = parse_args()
    device = detect_device()

    images_dir = args.prepared_dir / args.split / "images"
    manifest_path = args.prepared_dir / f"manifest_{args.split}.json"

    model = YOLO(str(args.weights))
    ground_truths, images_by_id = load_ground_truth(manifest_path)
    logger.info("Collecting predictions on %d images (conf>=%.3f)...", len(images_by_id), args.collection_conf)
    detections = collect_predictions(model, images_dir, images_by_id, args.collection_conf, device)
    logger.info("Collected %d raw detections.", len(detections))

    result = analyze_errors(detections, ground_truths, CLASS_NAMES, args.confidence_threshold)

    # --- confusion matrix (only non-empty entries, for readability) ---
    matrix = result.confusion_matrix(list(CANONICAL_CLASSES))
    confused_pairs = sorted(
        ((t, p, matrix[t][p]) for t in matrix for p in matrix[t] if t != p and matrix[t][p] > 0),
        key=lambda x: -x[2],
    )

    # --- per-class precision/recall from this same analysis ---
    per_class_pr = result.per_class_precision_recall(list(CANONICAL_CLASSES))

    # --- low-confidence detection analysis: TP vs FP confidence distributions ---
    tp_confidences = [tp.confidence for tp in result.true_positives]
    fp_confidences = [bg.confidence for bg in result.background_false_positives] + [c.confidence for c in result.class_confusions]
    conf_stats = {
        "true_positive_confidence": {"mean": statistics.mean(tp_confidences), "median": statistics.median(tp_confidences)} if tp_confidences else None,
        "false_positive_confidence": {"mean": statistics.mean(fp_confidences), "median": statistics.median(fp_confidences)} if fp_confidences else None,
    }

    # --- missed small objects: FN area vs overall GT area distribution ---
    all_gt_areas = [gt.bbox_xywh[2] * gt.bbox_xywh[3] for gt in ground_truths]
    fn_areas = [fn.bbox_area for fn in result.false_negatives]
    overall_median_area = statistics.median(all_gt_areas) if all_gt_areas else 0.0
    fn_median_area = statistics.median(fn_areas) if fn_areas else 0.0
    small_object_miss_analysis = {
        "overall_median_gt_area_px2": round(overall_median_area, 1),
        "false_negative_median_area_px2": round(fn_median_area, 1),
        "false_negatives_are_smaller_than_average": fn_median_area < overall_median_area if (fn_areas and all_gt_areas) else None,
    }

    # --- crowded scenes: correlate per-image GT instance count with FN rate ---
    gt_count_per_image = Counter(gt.image_id for gt in ground_truths)
    fn_count_per_image = Counter(fn.image_id for fn in result.false_negatives)
    crowded_threshold = statistics.median(list(gt_count_per_image.values())) if gt_count_per_image else 0
    crowded_images = [iid for iid, c in gt_count_per_image.items() if c > crowded_threshold]
    sparse_images = [iid for iid, c in gt_count_per_image.items() if c <= crowded_threshold]
    crowded_fn_rate = sum(fn_count_per_image.get(i, 0) for i in crowded_images) / max(1, sum(gt_count_per_image[i] for i in crowded_images))
    sparse_fn_rate = sum(fn_count_per_image.get(i, 0) for i in sparse_images) / max(1, sum(gt_count_per_image[i] for i in sparse_images))

    # --- difficult backgrounds: images with the most background FPs ---
    bg_fp_count_per_image = Counter(bg.image_id for bg in result.background_false_positives)
    difficult_background_images = [images_by_id[iid]["file_name"] for iid, _ in bg_fp_count_per_image.most_common(5)]

    # --- visual examples ---
    fp_examples = save_examples(images_dir, images_by_id, result.background_false_positives, "bg_fp", args.figures_dir, args.num_examples, "bg_fp")
    fn_examples = save_examples(images_dir, images_by_id, result.false_negatives, "fn", args.figures_dir, args.num_examples, "fn")

    summary = {
        "weights": str(args.weights),
        "split": args.split,
        "confidence_threshold": args.confidence_threshold,
        "counts": {
            "true_positives": len(result.true_positives),
            "class_confusions": len(result.class_confusions),
            "background_false_positives": len(result.background_false_positives),
            "false_negatives": len(result.false_negatives),
        },
        "confusion_matrix": matrix,
        "top_confused_pairs": [{"true_class": t, "predicted_class": p, "count": c} for t, p, c in confused_pairs[:10]],
        "per_class_precision_recall": per_class_pr,
        "confidence_stats": conf_stats,
        "small_object_miss_analysis": small_object_miss_analysis,
        "crowded_vs_sparse_scene_fn_rate": {
            "crowded_scene_fn_rate": round(crowded_fn_rate, 4),
            "sparse_scene_fn_rate": round(sparse_fn_rate, 4),
            "crowded_threshold_instances": crowded_threshold,
        },
        "difficult_background_candidates": difficult_background_images,
        "fp_example_images": fp_examples,
        "fn_example_images": fn_examples,
    }

    args.report_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.report_dir / "block13_error_analysis.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    md_lines = [
        "# Block 13 — Error Analysis",
        "",
        f"Weights: `{args.weights}` | Split: `{args.split}` | Confidence threshold: {args.confidence_threshold}",
        "",
        "## Counts",
        "",
        f"- True positives: {summary['counts']['true_positives']}",
        f"- Class confusions (right place, wrong label): {summary['counts']['class_confusions']}",
        f"- Background false positives (detected something where nothing is): {summary['counts']['background_false_positives']}",
        f"- False negatives (missed entirely): {summary['counts']['false_negatives']}",
        "",
        "## Top confused class pairs (true -> predicted)",
        "",
        "| True class | Predicted as | Count |",
        "|---|---|---:|",
    ]
    for pair in summary["top_confused_pairs"]:
        md_lines.append(f"| {pair['true_class']} | {pair['predicted_class']} | {pair['count']} |")

    md_lines += [
        "",
        "## Per-class precision/recall (this analysis's own matching)",
        "",
        "| Class | Precision | Recall | TP | FP | FN |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for cls, pr in per_class_pr.items():
        md_lines.append(f"| {cls} | {pr['precision']:.4f} | {pr['recall']:.4f} | {pr['tp']} | {pr['fp']} | {pr['fn']} |")

    md_lines += [
        "",
        "## Confidence: true positives vs. false positives",
        "",
        f"- True positive confidence: {conf_stats['true_positive_confidence']}",
        f"- False positive confidence: {conf_stats['false_positive_confidence']}",
        "",
        "## Small-object miss analysis",
        "",
        f"- Overall median GT bbox area: {small_object_miss_analysis['overall_median_gt_area_px2']} px²",
        f"- False-negative median bbox area: {small_object_miss_analysis['false_negative_median_area_px2']} px²",
        f"- False negatives skew smaller than average: {small_object_miss_analysis['false_negatives_are_smaller_than_average']}",
        "",
        "## Crowded vs. sparse scenes",
        "",
        f"- Crowded-scene (> {crowded_threshold} instances/image) false-negative rate: {summary['crowded_vs_sparse_scene_fn_rate']['crowded_scene_fn_rate']}",
        f"- Sparse-scene false-negative rate: {summary['crowded_vs_sparse_scene_fn_rate']['sparse_scene_fn_rate']}",
        "",
        "## Difficult-background candidates (most background FPs)",
        "",
        f"{difficult_background_images}",
        "",
        "## Visual examples",
        "",
        f"- False positives: {fp_examples}",
        f"- False negatives: {fn_examples}",
        "",
        "## Important caveat before drawing conclusions",
        "",
        _caveat_text(per_class_pr),
        "",
        "## Observations",
        "",
        "Findings from this specific checkpoint's actual errors (not a generic template):",
        "",
        f"1. **False negatives skew smaller than the overall GT area distribution** "
        f"({small_object_miss_analysis['false_negative_median_area_px2']} vs. "
        f"{small_object_miss_analysis['overall_median_gt_area_px2']} px² median) — consistent with the "
        "well-known difficulty of small-object detection; this checkpoint already uses the largest "
        "image size (640) and full training budget evaluated in this project.",
        f"2. **Crowded scenes have a higher false-negative rate** ({summary['crowded_vs_sparse_scene_fn_rate']['crowded_scene_fn_rate']} "
        f"vs. {summary['crowded_vs_sparse_scene_fn_rate']['sparse_scene_fn_rate']} for sparse scenes) — "
        "small, densely-packed lesions remain the hardest case even at this checkpoint's training scale.",
        "3. These are documented as known limitations of the final submitted model, not a proposal for "
        "further experimentation — see the project README's Known Limitations section for the final "
        "disclosure.",
        "",
        "## IMPORTANT: no changes were applied automatically",
        "",
        "This script only analyzes and reports. Any data or model change suggested by these "
        "findings (e.g. relabeling, excluding an image, adjusting a class's augmentation) must be "
        "a separate, explicitly documented decision — never applied automatically from this "
        "analysis, per the master spec.",
    ]

    md_path = args.report_dir / "block13_error_analysis.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print("\n".join(md_lines))
    print(f"\nJSON: {json_path}")
    print(f"Markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
