#!/usr/bin/env python3
"""Menyusun metrik yang dilaporkan dari artefak evaluasi.

Skrip ini **tidak menghitung ulang** apa pun. Seluruh angka dibaca dari
`artifacts/reports/evaluation_{split}.json` yang dihasilkan
`scripts/evaluate.py`. Tujuannya memastikan hanya ada satu sumber kebenaran
untuk metrik, sehingga tidak mungkin terjadi dua angka berbeda untuk hal yang
sama.

Definisi metrik yang dilaporkan:

- **mAP@50** diambil dari `model.val()` bawaan Ultralytics.
- **F1-Score** merupakan rata-rata antar kelas (*macro*) dari kurva F1 per
  kelas, diambil pada satu *confidence threshold* yang memaksimalkan rata-rata
  tersebut.
- Keduanya dihitung pada ambang NMS IoU yang tercatat di artefak evaluasi.

Peringatan penting: regulasi kompetisi menyebut F1 sebagai metrik penilaian
tetapi tidak merinci metode *averaging* maupun *threshold* yang dipakai
evaluator. Angka F1 pada skrip ini karenanya merupakan hasil implementasi
evaluasi lokal, bukan angka resmi panitia. Bila panitia kemudian menerbitkan
definisi resmi, definisi tersebut yang harus dipakai.

Penggunaan:
    python scripts/compute_official_metrics.py --split valid
    python scripts/compute_official_metrics.py --split test
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.logging_utils import setup_logging  # noqa: E402

logger = logging.getLogger("agridata.scripts.compute_official_metrics")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Susun metrik pelaporan dari artefak evaluasi.")
    p.add_argument("--split", default="valid", choices=["valid", "test"])
    p.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    return p.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()

    source = args.report_dir / f"evaluation_{args.split}.json"
    if not source.exists():
        raise SystemExit(
            f"Artefak evaluasi tidak ditemukan: {source}\n"
            f"Jalankan terlebih dahulu:\n"
            f"  python scripts/evaluate.py --weights <PATH> --split {args.split}"
        )

    with source.open("r", encoding="utf-8") as f:
        evaluation = json.load(f)

    native = evaluation["native_metrics"]

    wajib = ["macro_f1", "macro_f1_confidence", "nms_iou"]
    hilang = [k for k in wajib if k not in native]
    if hilang:
        raise SystemExit(
            f"Artefak {source} tidak memuat field {hilang}.\n"
            "Artefak ini dihasilkan versi evaluate.py yang lama. "
            "Jalankan ulang scripts/evaluate.py untuk meregenerasinya."
        )

    local_overall = evaluation["local_f1_metrics"]["overall"]

    report = {
        "split": evaluation["split"],
        "weights": evaluation["weights"],
        "git_commit": evaluation["git_commit"],
        "sumber_angka": str(source),
        "dihitung_ulang": False,
        "konfigurasi_inferensi": {
            "nms_iou": native["nms_iou"],
            "iou_pencocokan": evaluation["iou_threshold"],
        },
        "metrik_dilaporkan": {
            "mAP50_persen": round(native["mAP50"] * 100, 2),
            "f1_persen": round(native["macro_f1"] * 100, 2),
        },
        "rincian": {
            "mAP50": native["mAP50"],
            "mAP50_95": native["mAP50_95"],
            "f1_macro": native["macro_f1"],
            "confidence_titik_operasi": native["macro_f1_confidence"],
            "precision_titik_operasi": native.get("precision_at_macro_f1_point"),
            "recall_titik_operasi": native.get("recall_at_macro_f1_point"),
        },
        "metrik_diagnostik_sekunder": {
            "keterangan": (
                "Implementasi lokal dengan rata-rata micro pada confidence threshold tetap. "
                "Bukan angka yang dilaporkan. Sistematis lebih rendah pada dataset timpang "
                "dan tidak sebanding langsung dengan F1 macro di atas."
            ),
            "f1_lokal_micro": local_overall["f1"],
            "confidence_threshold": evaluation["local_f1_metrics"]["confidence_threshold"],
        },
        "caveat_definisi": (
            "Regulasi tidak merinci metode averaging maupun threshold untuk F1. "
            "Angka F1 di sini merupakan hasil implementasi evaluasi lokal dengan "
            "rata-rata macro, bukan angka resmi panitia."
        ),
        "per_kelas_AP50": native["per_class_AP50"],
    }

    out = args.report_dir / f"official_metrics_{args.split}.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    m = report["metrik_dilaporkan"]
    d = report["rincian"]
    print(f"\n=== METRIK DILAPORKAN, split {evaluation['split']} ===")
    print(f"  mAP@50    : {m['mAP50_persen']:.2f}%")
    print(f"  F1-Score  : {m['f1_persen']:.2f}%  (macro, implementasi lokal)")
    print(f"\n  ambang NMS IoU           : {native['nms_iou']}")
    print(f"  confidence titik operasi : {d['confidence_titik_operasi']:.4f}")
    if d["precision_titik_operasi"] is not None:
        print(f"  precision titik operasi  : {d['precision_titik_operasi']:.4f}")
        print(f"  recall titik operasi     : {d['recall_titik_operasi']:.4f}")
    print(f"  mAP@0.5:0.95             : {d['mAP50_95']:.4f}")
    print(f"\n  metrik diagnostik (micro): {report['metrik_diagnostik_sekunder']['f1_lokal_micro']:.4f}")
    print(f"\n  sumber : {source}")
    print(f"  keluaran: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
