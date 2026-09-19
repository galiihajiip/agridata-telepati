"""Detection evaluation metrics for the TELEPATI 8.0 AgriData pipeline (Block 7).

Two complementary, clearly labeled metric pathways are used:

1. NATIVE metrics (mAP@0.5, mAP@0.5:0.95), computed by calling Ultralytics'
   `model.val()`, not reimplemented here. Verified by reading
   `ultralytics/utils/metrics.py::ap_per_class` and
   `ultralytics/models/yolo/detect/val.py`: AP is the standard 101-point
   interpolated precision-recall-curve integration per class, evaluated at
   `iouv = torch.linspace(0.5, 0.95, 10)`, index 0 is exactly IoU=0.50,
   which is what "mAP@50" refers to in the competition regulation. This
   project treats Ultralytics' implementation as the source of truth for
   mAP rather than re-deriving AP integration from scratch.

2. LOCAL precision/recall/F1 at a caller-specified confidence threshold,
   implemented here via a standard greedy IoU>=0.5 matching algorithm
   (predictions sorted by descending confidence; each is matched to the
   highest-IoU unmatched ground-truth box of the same class in the same
   image if IoU >= 0.5; unmatched predictions are false positives,
   unmatched ground truths are false negatives). This exists because
   Ultralytics' own reported precision/recall corresponds to an
   INTERNALLY AUTO-SELECTED confidence threshold, the one maximizing mean
   F1 across classes (`ap_per_class`: `i = smooth(f1_curve.mean(0),
   0.1).argmax()`), which is not configurable by the caller. Per the
   master spec, this local computation is explicitly labeled as an
   implementation detail: the official competition scoring is the source
   of truth, and this is a documented, reproducible approximation of the
   F1 metric at a controllable operating point.
"""

from __future__ import annotations

from dataclasses import dataclass

# Per competition regulation (master spec Section 13): mAP@50 and F1 are
# both evaluated at IoU threshold 0.50.
IOU_MATCH_THRESHOLD = 0.5

BBoxXYWH = tuple[float, float, float, float]


@dataclass(frozen=True)
class Detection:
    image_id: int
    class_id: int
    confidence: float
    bbox_xywh: BBoxXYWH  # absolute pixel coordinates


@dataclass(frozen=True)
class GroundTruthBox:
    image_id: int
    class_id: int
    bbox_xywh: BBoxXYWH  # absolute pixel coordinates


@dataclass(frozen=True)
class PRF1Result:
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float


def compute_iou(box_a: BBoxXYWH, box_b: BBoxXYWH) -> float:
    """Intersection-over-Union between two [x, y, w, h] boxes (absolute pixel coords)."""
    ax1, ay1, aw, ah = box_a
    ax2, ay2 = ax1 + aw, ay1 + ah
    bx1, by1, bw, bh = box_b
    bx2, by2 = bx1 + bw, by1 + bh

    inter_w = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    inter_h = max(0.0, min(ay2, by2) - max(ay1, by1))
    inter_area = inter_w * inter_h

    area_a = max(0.0, aw) * max(0.0, ah)
    area_b = max(0.0, bw) * max(0.0, bh)
    union = area_a + area_b - inter_area
    return inter_area / union if union > 0 else 0.0


def _prf1_from_counts(tp: int, fp: int, fn: int) -> PRF1Result:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return PRF1Result(tp, fp, fn, precision, recall, f1)


def match_detections_to_ground_truth(
    detections: list[Detection],
    ground_truths: list[GroundTruthBox],
    confidence_threshold: float,
    iou_threshold: float = IOU_MATCH_THRESHOLD,
) -> dict:
    """Greedy IoU-based matching at a fixed confidence threshold.

    Predictions below `confidence_threshold` are dropped first. Remaining
    predictions are grouped by (image_id, class_id) alongside ground truths
    in the same group, then matched greedily in descending-confidence order:
    each prediction takes the highest-IoU unmatched ground truth in its
    group if that IoU >= `iou_threshold`, else it counts as a false
    positive. Ground truths never matched count as false negatives.

    Returns a dict with "overall" (micro-averaged across all classes) and
    "per_class" (keyed by class_id) `PRF1Result` values, plus the thresholds
    used (for audit traceability).
    """
    filtered = [d for d in detections if d.confidence >= confidence_threshold]

    gt_by_key: dict[tuple[int, int], list[GroundTruthBox]] = {}
    for gt in ground_truths:
        gt_by_key.setdefault((gt.image_id, gt.class_id), []).append(gt)

    det_by_key: dict[tuple[int, int], list[Detection]] = {}
    for d in filtered:
        det_by_key.setdefault((d.image_id, d.class_id), []).append(d)

    overall_tp = overall_fp = overall_fn = 0
    per_class_counts: dict[int, dict[str, int]] = {}

    for key in set(gt_by_key) | set(det_by_key):
        _, class_id = key
        counts = per_class_counts.setdefault(class_id, {"tp": 0, "fp": 0, "fn": 0})

        gts = gt_by_key.get(key, [])
        matched_gt = [False] * len(gts)

        dets = sorted(det_by_key.get(key, []), key=lambda d: -d.confidence)
        for det in dets:
            best_iou, best_idx = 0.0, -1
            for idx, gt in enumerate(gts):
                if matched_gt[idx]:
                    continue
                iou = compute_iou(det.bbox_xywh, gt.bbox_xywh)
                if iou > best_iou:
                    best_iou, best_idx = iou, idx

            if best_idx >= 0 and best_iou >= iou_threshold:
                matched_gt[best_idx] = True
                overall_tp += 1
                counts["tp"] += 1
            else:
                overall_fp += 1
                counts["fp"] += 1

        unmatched = matched_gt.count(False)
        overall_fn += unmatched
        counts["fn"] += unmatched

    return {
        "overall": _prf1_from_counts(overall_tp, overall_fp, overall_fn),
        "per_class": {cid: _prf1_from_counts(c["tp"], c["fp"], c["fn"]) for cid, c in per_class_counts.items()},
        "confidence_threshold": confidence_threshold,
        "iou_threshold": iou_threshold,
    }
