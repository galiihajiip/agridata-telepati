"""Class-agnostic object detection error analysis (Block 13).

Standard object-detection error taxonomy (similar in spirit to tools like
TIDE, simplified): matching is done in two stages so that "the model looked
in the wrong place" (localization error) can be separated from "the model
found the object but named it wrong" (class confusion) — a plain
class-restricted matcher (as used for mAP/F1 in Block 7) cannot make this
distinction, since it never considers a prediction against a
different-class ground truth at all.

Per image:
  1. Predictions (above a confidence threshold) are matched to ANY unmatched
     ground-truth box in the same image by IoU >= 0.5, regardless of class,
     greedily in descending-confidence order.
  2. If a match is found:
     - predicted class == true class -> true positive
     - predicted class != true class -> class confusion (localized right,
       classified wrong)
  3. If no ground-truth box reaches IoU >= 0.5 -> background false positive
     (the model detected something where nothing relevant exists).
  4. Any ground-truth box never matched by any prediction -> false negative
     (missed entirely).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agridata.metrics.detection import Detection, GroundTruthBox, compute_iou

IOU_THRESHOLD = 0.5


@dataclass(frozen=True)
class ClassConfusion:
    image_id: int
    true_class: str
    predicted_class: str
    confidence: float
    iou: float


@dataclass(frozen=True)
class BackgroundFalsePositive:
    image_id: int
    predicted_class: str
    confidence: float
    bbox_xywh: tuple[float, float, float, float]


@dataclass(frozen=True)
class FalseNegative:
    image_id: int
    true_class: str
    bbox_xywh: tuple[float, float, float, float]
    bbox_area: float


@dataclass(frozen=True)
class TruePositive:
    image_id: int
    canonical_class: str
    confidence: float
    iou: float


@dataclass
class ErrorAnalysisResult:
    true_positives: list[TruePositive] = field(default_factory=list)
    class_confusions: list[ClassConfusion] = field(default_factory=list)
    background_false_positives: list[BackgroundFalsePositive] = field(default_factory=list)
    false_negatives: list[FalseNegative] = field(default_factory=list)

    def confusion_matrix(self, class_names: list[str]) -> dict[str, dict[str, int]]:
        """Rows = true class, columns = predicted class. Diagonal = true positives."""
        matrix = {t: {p: 0 for p in class_names} for t in class_names}
        for tp in self.true_positives:
            matrix[tp.canonical_class][tp.canonical_class] += 1
        for c in self.class_confusions:
            matrix[c.true_class][c.predicted_class] += 1
        return matrix

    def per_class_precision_recall(self, class_names: list[str]) -> dict[str, dict[str, float]]:
        """Precision/recall per class from this analysis's own matching (same
        underlying data used for the error categorization, avoiding any
        inconsistency between the two views)."""
        tp_count = {c: 0 for c in class_names}
        for tp in self.true_positives:
            tp_count[tp.canonical_class] += 1

        fp_count = {c: 0 for c in class_names}
        for c in self.class_confusions:
            fp_count[c.predicted_class] += 1  # wrong prediction counts as FP for the predicted class
        for bg in self.background_false_positives:
            fp_count[bg.predicted_class] += 1

        fn_count = {c: 0 for c in class_names}
        for c in self.class_confusions:
            fn_count[c.true_class] += 1  # the true object was still missed under its own class
        for fn in self.false_negatives:
            fn_count[fn.true_class] += 1

        result = {}
        for c in class_names:
            tp, fp, fn = tp_count[c], fp_count[c], fn_count[c]
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            result[c] = {"precision": precision, "recall": recall, "tp": tp, "fp": fp, "fn": fn}
        return result


def analyze_errors(
    detections: list[Detection],
    ground_truths: list[GroundTruthBox],
    class_names: dict[int, str],
    confidence_threshold: float,
    iou_threshold: float = IOU_THRESHOLD,
) -> ErrorAnalysisResult:
    """Run the class-agnostic error analysis described in this module's docstring."""
    filtered = [d for d in detections if d.confidence >= confidence_threshold]

    dets_by_image: dict[int, list[Detection]] = {}
    for d in filtered:
        dets_by_image.setdefault(d.image_id, []).append(d)

    gts_by_image: dict[int, list[GroundTruthBox]] = {}
    for gt in ground_truths:
        gts_by_image.setdefault(gt.image_id, []).append(gt)

    result = ErrorAnalysisResult()

    for image_id in set(dets_by_image) | set(gts_by_image):
        gts = gts_by_image.get(image_id, [])
        matched_gt = [False] * len(gts)

        dets = sorted(dets_by_image.get(image_id, []), key=lambda d: -d.confidence)
        for det in dets:
            best_iou, best_idx = 0.0, -1
            for idx, gt in enumerate(gts):
                if matched_gt[idx]:
                    continue
                iou = compute_iou(det.bbox_xywh, gt.bbox_xywh)
                if iou > best_iou:
                    best_iou, best_idx = iou, idx

            pred_class_name = class_names[det.class_id]
            if best_idx >= 0 and best_iou >= iou_threshold:
                matched_gt[best_idx] = True
                true_class_name = class_names[gts[best_idx].class_id]
                if pred_class_name == true_class_name:
                    result.true_positives.append(TruePositive(image_id, pred_class_name, det.confidence, best_iou))
                else:
                    result.class_confusions.append(
                        ClassConfusion(image_id, true_class_name, pred_class_name, det.confidence, best_iou)
                    )
            else:
                result.background_false_positives.append(
                    BackgroundFalsePositive(image_id, pred_class_name, det.confidence, det.bbox_xywh)
                )

        for idx, gt in enumerate(gts):
            if not matched_gt[idx]:
                area = gt.bbox_xywh[2] * gt.bbox_xywh[3]
                result.false_negatives.append(FalseNegative(image_id, class_names[gt.class_id], gt.bbox_xywh, area))

    return result
