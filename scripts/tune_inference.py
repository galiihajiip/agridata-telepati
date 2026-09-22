#!/usr/bin/env python3
"""Pencarian parameter inferensi terbaik tanpa melatih ulang model (leaderboard).

Bobot model TIDAK diubah. Yang dicari hanya parameter saat inferensi:
ukuran citra, ambang NMS IoU, dan augmentasi saat uji (TTA). Parameter ini
merupakan pengaturan evaluasi, bukan bagian dari pelatihan, sehingga model
final tetap satu dan tetap dilatih tanpa bobot pra-latih eksternal.

Seluruh pencarian dijalankan pada split VALIDASI. Split test tidak pernah
dipakai untuk memilih parameter.

Penggunaan:
    python scripts/tune_inference.py
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

from agridata.logging_utils import setup_logging  # noqa: E402

logger = logging.getLogger("agridata.scripts.tune_inference")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Cari parameter inferensi terbaik pada split validasi.")
    p.add_argument("--weights", default=Path("runs/detect/final/final_model/weights/best.pt"), type=Path)
    p.add_argument("--data-yaml", default=Path("data/prepared/data.yaml"), type=Path)
    p.add_argument("--split", default="val")
    p.add_argument("--imgsz", type=int, nargs="+", default=[640, 800, 960, 1280])
    p.add_argument("--iou", type=float, nargs="+", default=[0.5, 0.6, 0.7])
    p.add_argument("--augment", action="store_true", help="ikut menguji TTA")
    p.add_argument("--report", default=Path("artifacts/reports/inference_tuning.json"), type=Path)
    return p.parse_args()


def evaluate(weights: Path, data_yaml: Path, split: str, imgsz: int, iou: float, augment: bool) -> dict:
    model = YOLO(str(weights))
    r = model.val(
        data=str(data_yaml), split=split, imgsz=imgsz, iou=iou,
        augment=augment, verbose=False, plots=False,
    )
    b = r.box
    f1_curve = np.array(b.f1_curve).mean(axis=0)
    conf_grid = np.linspace(0, 1, len(f1_curve))
    best_i = int(f1_curve.argmax())
    return {
        "imgsz": imgsz,
        "nms_iou": iou,
        "augment": augment,
        "map50": float(b.map50),
        "map50_95": float(b.map),
        "mean_precision": float(b.mp),
        "mean_recall": float(b.mr),
        "best_f1": float(f1_curve[best_i]),
        "best_f1_conf": float(conf_grid[best_i]),
    }


def main() -> int:
    setup_logging()
    args = parse_args()

    combos = [(s, i, False) for s in args.imgsz for i in args.iou]
    if args.augment:
        combos += [(s, i, True) for s in args.imgsz for i in args.iou]

    results = []
    for imgsz, iou, augment in combos:
        logger.info("Menguji imgsz=%d iou=%.2f augment=%s", imgsz, iou, augment)
        try:
            row = evaluate(args.weights, args.data_yaml, args.split, imgsz, iou, augment)
        except Exception as exc:  # noqa: BLE001
            logger.error("Gagal pada imgsz=%d iou=%.2f augment=%s: %s", imgsz, iou, augment, exc)
            continue
        results.append(row)
        logger.info(
            "  mAP50=%.4f mAP50-95=%.4f bestF1=%.4f (conf=%.3f)",
            row["map50"], row["map50_95"], row["best_f1"], row["best_f1_conf"],
        )

    if not results:
        raise SystemExit("Tidak ada hasil.")

    best_map = max(results, key=lambda r: r["map50"])
    best_f1 = max(results, key=lambda r: r["best_f1"])

    report = {
        "split_untuk_pencarian": args.split,
        "catatan": (
            "Bobot model tidak diubah. Yang dicari hanya parameter inferensi. "
            "Split test tidak pernah dipakai untuk memilih parameter."
        ),
        "baseline": next(
            (r for r in results if r["imgsz"] == 640 and r["nms_iou"] == 0.7 and not r["augment"]), None
        ),
        "terbaik_map50": best_map,
        "terbaik_f1": best_f1,
        "semua_hasil": sorted(results, key=lambda r: -r["map50"]),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n{'imgsz':>6s} {'iou':>5s} {'TTA':>4s} {'mAP50':>8s} {'mAP50-95':>9s} {'bestF1':>8s} {'conf':>6s}")
    for r in sorted(results, key=lambda r: -r["map50"]):
        print(
            f"{r['imgsz']:6d} {r['nms_iou']:5.2f} {str(r['augment'])[:4]:>4s} "
            f"{r['map50']:8.4f} {r['map50_95']:9.4f} {r['best_f1']:8.4f} {r['best_f1_conf']:6.3f}"
        )
    print(f"\nTerbaik mAP@0.5: {best_map['map50']:.4f} pada imgsz={best_map['imgsz']} iou={best_map['nms_iou']} TTA={best_map['augment']}")
    print(f"Terbaik F1     : {best_f1['best_f1']:.4f} pada imgsz={best_f1['imgsz']} iou={best_f1['nms_iou']} TTA={best_f1['augment']}")
    print(f"Laporan: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
