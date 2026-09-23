"""Analisis kesalahan deteksi objek yang tidak memandang kelas saat mencocokkan.

Taksonomi kesalahan yang dipakai merupakan taksonomi standar deteksi objek,
serupa semangatnya dengan perkakas seperti TIDE namun disederhanakan.
Pencocokan dilakukan dua tahap supaya kasus model mencari di tempat yang salah,
yaitu kesalahan lokalisasi, dapat dipisahkan dari kasus model menemukan objeknya
tetapi salah menamai, yaitu salah kelas. Pencocok biasa yang membatasi diri pada
kelas yang sama, seperti yang dipakai untuk mAP dan F1, tidak dapat membedakan
keduanya, karena sama sekali tidak pernah membandingkan prediksi dengan ground
truth berkelas lain.

Untuk setiap citra:
  1. Prediksi di atas ambang confidence dicocokkan dengan kotak ground truth
     mana pun yang belum berpasangan pada citra yang sama, berdasarkan IoU >=
     0,5, tanpa memandang kelas, secara greedy menurut confidence menurun.
  2. Bila pasangan ditemukan:
     - kelas prediksi sama dengan kelas sebenarnya -> true positive
     - kelas prediksi berbeda -> salah kelas, yaitu lokasinya benar tetapi
       penamaannya keliru
  3. Bila tidak ada kotak ground truth yang mencapai IoU >= 0,5 -> false
     positive terhadap latar, yaitu model mendeteksi sesuatu di tempat yang
     sebenarnya tidak ada objek relevan.
  4. Setiap kotak ground truth yang tidak pernah dipasangkan prediksi mana pun
     -> false negative, yaitu terlewat sepenuhnya.
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
        """Baris adalah kelas sebenarnya, kolom adalah kelas prediksi, dan diagonalnya merupakan true positive."""
        matrix = {t: {p: 0 for p in class_names} for t in class_names}
        for tp in self.true_positives:
            matrix[tp.canonical_class][tp.canonical_class] += 1
        for c in self.class_confusions:
            matrix[c.true_class][c.predicted_class] += 1
        return matrix

    def per_class_precision_recall(self, class_names: list[str]) -> dict[str, dict[str, float]]:
        """Precision dan recall per kelas dari pencocokan analisis ini sendiri.

    Keduanya dihitung dari data yang sama persis dengan yang dipakai untuk
    mengategorikan kesalahan, sehingga tidak muncul ketidaksesuaian antara kedua
    sudut pandang tersebut."""
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
    """Menjalankan analisis kesalahan tanpa memandang kelas, sesuai penjelasan modul ini."""
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
