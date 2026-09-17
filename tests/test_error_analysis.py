"""Unit tests for the class-agnostic error analysis matcher (Block 13)."""

from __future__ import annotations

from agridata.analysis.error_analysis import analyze_errors
from agridata.metrics.detection import Detection, GroundTruthBox

CLASS_NAMES = {0: "Blast", 1: "Healthy"}


def test_correct_class_and_location_is_true_positive() -> None:
    gt = [GroundTruthBox(1, 0, (0.0, 0.0, 10.0, 10.0))]
    det = [Detection(1, 0, 0.9, (0.0, 0.0, 10.0, 10.0))]

    result = analyze_errors(det, gt, CLASS_NAMES, confidence_threshold=0.5)
    assert len(result.true_positives) == 1
    assert len(result.class_confusions) == 0
    assert len(result.background_false_positives) == 0
    assert len(result.false_negatives) == 0


def test_right_location_wrong_class_is_class_confusion() -> None:
    gt = [GroundTruthBox(1, 0, (0.0, 0.0, 10.0, 10.0))]  # true class: Blast
    det = [Detection(1, 1, 0.9, (0.0, 0.0, 10.0, 10.0))]  # predicted: Healthy

    result = analyze_errors(det, gt, CLASS_NAMES, confidence_threshold=0.5)
    assert len(result.true_positives) == 0
    assert len(result.class_confusions) == 1
    confusion = result.class_confusions[0]
    assert confusion.true_class == "Blast"
    assert confusion.predicted_class == "Healthy"


def test_prediction_with_no_nearby_ground_truth_is_background_fp() -> None:
    gt = [GroundTruthBox(1, 0, (0.0, 0.0, 10.0, 10.0))]
    det = [Detection(1, 0, 0.9, (100.0, 100.0, 10.0, 10.0))]  # nowhere near the GT

    result = analyze_errors(det, gt, CLASS_NAMES, confidence_threshold=0.5)
    assert len(result.background_false_positives) == 1
    assert len(result.false_negatives) == 1  # the real GT was never matched either


def test_unmatched_ground_truth_is_false_negative() -> None:
    gt = [GroundTruthBox(1, 0, (0.0, 0.0, 10.0, 10.0))]
    det: list[Detection] = []

    result = analyze_errors(det, gt, CLASS_NAMES, confidence_threshold=0.5)
    assert len(result.false_negatives) == 1
    assert result.false_negatives[0].true_class == "Blast"
    assert result.false_negatives[0].bbox_area == 100.0


def test_confusion_matrix_diagonal_is_true_positives() -> None:
    gt = [GroundTruthBox(1, 0, (0.0, 0.0, 10.0, 10.0)), GroundTruthBox(1, 1, (50.0, 50.0, 10.0, 10.0))]
    det = [
        Detection(1, 0, 0.9, (0.0, 0.0, 10.0, 10.0)),  # correct
        Detection(1, 0, 0.9, (50.0, 50.0, 10.0, 10.0)),  # true=Healthy, predicted=Blast
    ]

    result = analyze_errors(det, gt, CLASS_NAMES, confidence_threshold=0.5)
    matrix = result.confusion_matrix(list(CLASS_NAMES.values()))
    assert matrix["Blast"]["Blast"] == 1
    assert matrix["Healthy"]["Blast"] == 1
    assert matrix["Healthy"]["Healthy"] == 0


def test_per_class_precision_recall_counts_confusions_correctly() -> None:
    # Blast GT correctly found; Healthy GT found but mislabeled as Blast.
    gt = [GroundTruthBox(1, 0, (0.0, 0.0, 10.0, 10.0)), GroundTruthBox(1, 1, (50.0, 50.0, 10.0, 10.0))]
    det = [
        Detection(1, 0, 0.9, (0.0, 0.0, 10.0, 10.0)),
        Detection(1, 0, 0.9, (50.0, 50.0, 10.0, 10.0)),
    ]

    result = analyze_errors(det, gt, CLASS_NAMES, confidence_threshold=0.5)
    pr = result.per_class_precision_recall(list(CLASS_NAMES.values()))
    # Blast: 2 predictions labeled Blast, 1 correct -> precision 0.5; 1 true Blast GT, found -> recall 1.0
    assert pr["Blast"]["tp"] == 1
    assert pr["Blast"]["fp"] == 1
    assert pr["Blast"]["recall"] == 1.0
    # Healthy: 0 predictions labeled Healthy -> precision undefined (0.0 by convention); 1 true Healthy GT, missed (mislabeled) -> recall 0.0
    assert pr["Healthy"]["tp"] == 0
    assert pr["Healthy"]["fn"] == 1
    assert pr["Healthy"]["recall"] == 0.0


def test_confidence_threshold_filters_low_confidence_predictions() -> None:
    gt = [GroundTruthBox(1, 0, (0.0, 0.0, 10.0, 10.0))]
    det = [Detection(1, 0, 0.1, (0.0, 0.0, 10.0, 10.0))]  # below threshold

    result = analyze_errors(det, gt, CLASS_NAMES, confidence_threshold=0.5)
    assert len(result.true_positives) == 0
    assert len(result.false_negatives) == 1  # GT unmatched since the low-conf det was dropped
