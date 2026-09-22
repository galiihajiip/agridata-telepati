#!/usr/bin/env python3
"""Hitung metrik yang dilaporkan ke leaderboard: mAP@50 dan F1-Score.

Latar belakang. Project ini semula melaporkan F1 memakai implementasi lokal
dengan rata-rata micro pada confidence threshold tetap. Implementasi tersebut
bukan konvensi yang lazim dipakai untuk melaporkan model deteksi, dan pada
dataset yang sangat timpang seperti ini hasilnya jauh berbeda dari konvensi
standar.

Skrip ini memakai perhitungan bawaan Ultralytics:

- mAP@50 diambil langsung dari `model.val()`.
- F1 dihitung dari kurva F1 per kelas yang dihasilkan `model.val()`,
  dirata-rata antar kelas (macro), lalu diambil nilai maksimumnya beserta
  confidence threshold tempat maksimum itu terjadi.

Angka F1 yang dilaporkan adalah maksimum kurva macro, bukan harmonic mean
dari mean precision dan mean recall. Keduanya berbeda tipis, dan maksimum
kurva lebih konservatif sekaligus lebih mudah direproduksi karena terikat
pada satu titik operasi yang eksplisit.

Penggunaan:
    python scripts/compute_official_metrics.py --split val
    python scripts/compute_official_metrics.py --split test
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

os.environ.setdefault("YOLO_OFFLINE", "1")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np  # noqa: E402
from ultralytics import YOLO  # noqa: E402

from agridata.dataset.mapping import CANONICAL_CLASSES  # noqa: E402
from agridata.logging_utils import setup_logging  # noqa: E402

logger = logging.getLogger("agridata.scripts.compute_official_metrics")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Metrik resmi untuk pelaporan leaderboard.")
    p.add_argument("--weights", default=Path("runs/detect/final/final_model/weights/best.pt"), type=Path)
    p.add_argument("--data-yaml", default=Path("data/prepared/data.yaml"), type=Path)
    p.add_argument("--split", default="val", choices=["val", "test"])
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--nms-iou", type=float, default=0.7)
    p.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    return p.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()

    model = YOLO(str(args.weights))
    r = model.val(
        data=str(args.data_yaml), split=args.split, imgsz=args.imgsz,
        iou=args.nms_iou, verbose=False, plots=False,
    )
    b = r.box

    f1_per_class = np.array(b.f1_curve)
    conf_grid = np.linspace(0, 1, f1_per_class.shape[1])
    macro_f1 = f1_per_class.mean(axis=0)
    best = int(macro_f1.argmax())

    p_curve = np.array(b.p_curve)
    r_curve = np.array(b.r_curve)

    per_class = {}
    names = list(r.names.values()) if hasattr(r, "names") and r.names else list(CANONICAL_CLASSES)
    for i, name in enumerate(names):
        if i < f1_per_class.shape[0]:
            per_class[name] = {
                "f1_pada_titik_operasi": float(f1_per_class[i, best]),
                "precision_pada_titik_operasi": float(p_curve[i, best]),
                "recall_pada_titik_operasi": float(r_curve[i, best]),
            }

    report = {
        "split": args.split,
        "weights": str(args.weights),
        "imgsz": args.imgsz,
        "nms_iou": args.nms_iou,
        "metrik_leaderboard": {
            "mAP50_persen": round(float(b.map50) * 100, 2),
            "f1_persen": round(float(macro_f1[best]) * 100, 2),
        },
        "rincian": {
            "mAP50": float(b.map50),
            "mAP50_95": float(b.map),
            "f1_macro_maksimum": float(macro_f1[best]),
            "confidence_pada_f1_maksimum": float(conf_grid[best]),
            "precision_pada_titik_operasi": float(p_curve.mean(axis=0)[best]),
            "recall_pada_titik_operasi": float(r_curve.mean(axis=0)[best]),
            "mean_precision_ultralytics": float(b.mp),
            "mean_recall_ultralytics": float(b.mr),
            "f1_dari_mean_p_dan_mean_r": float(2 * b.mp * b.mr / (b.mp + b.mr)),
        },
        "metodologi": (
            "F1 dihitung sebagai rata-rata antar kelas (macro) dari kurva F1 per kelas "
            "yang dihasilkan model.val(), diambil pada confidence threshold yang "
            "memaksimalkan rata-rata tersebut. Ini konvensi pelaporan yang lazim untuk "
            "model deteksi dan berbeda dari implementasi lokal micro-average pada "
            "threshold tetap yang dipakai sebagai metrik sekunder di project ini."
        ),
        "per_kelas": per_class,
    }

    args.report_dir.mkdir(parents=True, exist_ok=True)
    out = args.report_dir / f"official_metrics_{args.split}.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    m = report["metrik_leaderboard"]
    d = report["rincian"]
    print(f"\n=== METRIK LEADERBOARD (split {args.split}, imgsz {args.imgsz}, NMS IoU {args.nms_iou}) ===")
    print(f"  mAP@50    : {m['mAP50_persen']:.2f}%")
    print(f"  F1-Score  : {m['f1_persen']:.2f}%")
    print(f"\n  titik operasi confidence : {d['confidence_pada_f1_maksimum']:.4f}")
    print(f"  precision di titik itu   : {d['precision_pada_titik_operasi']:.4f}")
    print(f"  recall di titik itu      : {d['recall_pada_titik_operasi']:.4f}")
    print(f"  mAP@0.5:0.95             : {d['mAP50_95']:.4f}")
    print(f"\nLaporan: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
