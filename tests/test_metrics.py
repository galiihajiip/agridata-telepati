"""Unit tests for the detection evaluation metrics (Block 7)."""

from __future__ import annotations

import math

from agridata.metrics.detection import (
    Detection,
    GroundTruthBox,
    compute_iou,
    match_detections_to_ground_truth,
)


def test_iou_identical_boxes_is_one() -> None:
    box = (10.0, 10.0, 20.0, 20.0)
    assert math.isclose(compute_iou(box, box), 1.0)


def test_iou_non_overlapping_boxes_is_zero() -> None:
    a = (0.0, 0.0, 10.0, 10.0)
    b = (100.0, 100.0, 10.0, 10.0)
    assert compute_iou(a, b) == 0.0


def test_iou_known_partial_overlap() -> None:
    # a: [0,0]-[10,10] (area 100); b: [5,5]-[15,15] (area 100)
    # intersection: [5,5]-[10,10] = 5x5 = 25; union = 100+100-25 = 175
    a = (0.0, 0.0, 10.0, 10.0)
    b = (5.0, 5.0, 10.0, 10.0)
    assert math.isclose(compute_iou(a, b), 25 / 175, rel_tol=1e-9)


def test_perfect_match_all_true_positive() -> None:
    gt = [GroundTruthBox(image_id=1, class_id=0, bbox_xywh=(0.0, 0.0, 10.0, 10.0))]
    det = [Detection(image_id=1, class_id=0, confidence=0.9, bbox_xywh=(0.0, 0.0, 10.0, 10.0))]

    result = match_detections_to_ground_truth(det, gt, confidence_threshold=0.5)
    overall = result["overall"]
    assert overall.true_positives == 1
    assert overall.false_positives == 0
    assert overall.false_negatives == 0
    assert overall.precision == 1.0
    assert overall.recall == 1.0
    assert overall.f1 == 1.0


def test_missed_detection_is_false_negative() -> None:
    gt = [GroundTruthBox(image_id=1, class_id=0, bbox_xywh=(0.0, 0.0, 10.0, 10.0))]
    det: list[Detection] = []

    result = match_detections_to_ground_truth(det, gt, confidence_threshold=0.5)
    overall = result["overall"]
    assert overall.true_positives == 0
    assert overall.false_negatives == 1
    assert overall.precision == 0.0
    assert overall.recall == 0.0


def test_low_iou_detection_counts_as_false_positive_and_false_negative() -> None:
    # Detection barely overlaps the GT (IoU well under 0.5) -> not a match.
    gt = [GroundTruthBox(image_id=1, class_id=0, bbox_xywh=(0.0, 0.0, 10.0, 10.0))]
    det = [Detection(image_id=1, class_id=0, confidence=0.9, bbox_xywh=(9.0, 9.0, 10.0, 10.0))]

    result = match_detections_to_ground_truth(det, gt, confidence_threshold=0.5)
    overall = result["overall"]
    assert overall.true_positives == 0
    assert overall.false_positives == 1
    assert overall.false_negatives == 1


def test_confidence_threshold_filters_low_confidence_detections() -> None:
    gt = [GroundTruthBox(image_id=1, class_id=0, bbox_xywh=(0.0, 0.0, 10.0, 10.0))]
    det = [Detection(image_id=1, class_id=0, confidence=0.1, bbox_xywh=(0.0, 0.0, 10.0, 10.0))]

    result = match_detections_to_ground_truth(det, gt, confidence_threshold=0.5)
    overall = result["overall"]
    # Below threshold -> detection is dropped entirely -> the GT box is unmatched (FN).
    assert overall.true_positives == 0
    assert overall.false_negatives == 1
    assert overall.false_positives == 0


def test_greedy_matching_prefers_highest_confidence_prediction() -> None:
    gt = [GroundTruthBox(image_id=1, class_id=0, bbox_xywh=(0.0, 0.0, 10.0, 10.0))]
    det = [
        Detection(image_id=1, class_id=0, confidence=0.4, bbox_xywh=(0.0, 0.0, 10.0, 10.0)),
        Detection(image_id=1, class_id=0, confidence=0.9, bbox_xywh=(0.0, 0.0, 10.0, 10.0)),
    ]

    result = match_detections_to_ground_truth(det, gt, confidence_threshold=0.3)
    overall = result["overall"]
    # Only one GT to match: the higher-confidence det (0.9) takes it (TP),
    # the other duplicate detection has nothing left to match (FP).
    assert overall.true_positives == 1
    assert overall.false_positives == 1
    assert overall.false_negatives == 0


def test_per_class_breakdown_is_independent() -> None:
    gt = [
        GroundTruthBox(image_id=1, class_id=0, bbox_xywh=(0.0, 0.0, 10.0, 10.0)),
        GroundTruthBox(image_id=1, class_id=1, bbox_xywh=(50.0, 50.0, 10.0, 10.0)),
    ]
    det = [
        Detection(image_id=1, class_id=0, confidence=0.9, bbox_xywh=(0.0, 0.0, 10.0, 10.0)),
        # class 1 has no matching detection -> FN for class 1 only
    ]

    result = match_detections_to_ground_truth(det, gt, confidence_threshold=0.5)
    per_class = result["per_class"]
    assert per_class[0].true_positives == 1
    assert per_class[0].false_negatives == 0
    assert per_class[1].true_positives == 0
    assert per_class[1].false_negatives == 1
