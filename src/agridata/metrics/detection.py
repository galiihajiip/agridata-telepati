"""Metrik evaluasi deteksi objek.

Project ini memakai dua jalur metrik yang saling melengkapi dan diberi label
secara jelas.

1. Metrik NATIVE, yaitu mAP@0.5 dan mAP@0.5:0.95, dihitung dengan memanggil
   `model.val()` bawaan Ultralytics dan tidak diimplementasikan ulang di sini.
   Hal ini diverifikasi dengan membaca `ultralytics/utils/metrics.py::ap_per_class`
   dan `ultralytics/models/yolo/detect/val.py`. AP dihitung sebagai integrasi
   kurva precision-recall terinterpolasi 101 titik per kelas, dievaluasi pada
   `iouv = torch.linspace(0.5, 0.95, 10)`, dengan indeks 0 tepat berada pada
   IoU=0,50, yaitu yang dimaksud regulasi kompetisi sebagai mAP@50. Implementasi
   Ultralytics diperlakukan sebagai sumber kebenaran untuk mAP, alih-alih
   menurunkan ulang integrasi AP dari nol.

2. Metrik LOKAL berupa precision, recall, dan F1 pada confidence threshold yang
   ditentukan pemanggil, diimplementasikan di sini melalui algoritma pencocokan
   greedy standar pada IoU >= 0,5. Prediksi diurutkan menurut confidence
   menurun, lalu setiap prediksi dipasangkan dengan kotak ground truth berkelas
   sama pada citra yang sama yang IoU-nya tertinggi dan belum berpasangan,
   sepanjang IoU >= 0,5. Prediksi yang tidak berpasangan terhitung false
   positive, sedangkan ground truth yang tidak berpasangan terhitung false
   negative.

   Jalur kedua ini diperlukan karena precision dan recall yang dilaporkan
   Ultralytics sendiri mengacu pada confidence threshold yang DIPILIH OTOMATIS
   SECARA INTERNAL, yaitu ambang yang memaksimalkan rata-rata F1 antar kelas
   (`ap_per_class`: `i = smooth(f1_curve.mean(0), 0.1).argmax()`), dan ambang itu
   tidak dapat diatur pemanggil.

   Perhitungan lokal ini secara eksplisit dinyatakan sebagai detail
   implementasi. Penilaian resmi kompetisi tetap menjadi sumber kebenaran, dan
   perhitungan di sini merupakan pendekatan metrik F1 yang terdokumentasi dan
   dapat direproduksi pada titik operasi yang dapat dikendalikan.
"""

from __future__ import annotations

from dataclasses import dataclass

# Sesuai regulasi kompetisi: mAP@50 dan F1 merupakan
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
    """Pencocokan greedy berbasis IoU pada confidence threshold tetap.

    Prediksi di bawah `confidence_threshold` dibuang lebih dulu. Sisanya
    dikelompokkan menurut pasangan (image_id, class_id) bersama ground truth
    pada kelompok yang sama, lalu dicocokkan secara greedy menurut confidence
    menurun. Setiap prediksi mengambil ground truth belum berpasangan dengan IoU
    tertinggi di kelompoknya sepanjang IoU >= `iou_threshold`, dan bila tidak
    ada, prediksi itu terhitung false positive. Ground truth yang tidak pernah
    berpasangan terhitung false negative.

    Fungsi mengembalikan dict berisi "overall", yaitu rata-rata micro seluruh
    kelas, dan "per_class" yang berkunci class_id, keduanya bertipe
    `PRF1Result`, beserta ambang yang dipakai demi keterlacakan audit.
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
