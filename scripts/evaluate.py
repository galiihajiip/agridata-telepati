#!/usr/bin/env python3
"""Antarmuka baris perintah untuk evaluasi mAP@50 dan F1 yang dapat direproduksi.

Pemakaian:
    python scripts/evaluate.py --weights <PATH> --split valid --config configs/base.yaml

Ada dua jalur metrik. Alasan keduanya ada dan cara masing-masing dihitung
didokumentasikan lengkap pada src/agridata/metrics/detection.py.

  1. mAP@0.5 dan mAP@0.5:0.95 NATIVE melalui `model.val()` bawaan Ultralytics.
     Inilah sumber kebenaran untuk mAP, dan project ini tidak
     mengimplementasikan ulang integrasi AP.
  2. Precision, recall, dan F1 LOKAL pada `--conf-threshold`, melalui
     pencocokan greedy pada IoU >= 0,5 milik project ini sendiri. Jalur ini
     diperlukan karena precision dan recall yang dilaporkan Ultralytics memakai
     confidence threshold yang dipilih otomatis secara internal dan tidak dapat
     diatur.

Kedua tahap itu berjalan pada PROSES TERPISAH, bukan berurutan dalam satu proses.
Uji reproduksi pada lingkungan bersih menemukan bahwa menjalankan `model.val()`
lalu `model.predict(..., stream=True)` pada objek model yang sama, bahkan pada
objek yang baru dimuat ulang sekalipun, di dalam satu proses akan merusak kondisi
internal backend MPS. Kegagalannya muncul sebagai "MPSGraph does not support
tensor dims larger than INT_MAX" atau sebagai galat kehabisan memori MPS, dan
tetap terjadi meski `torch.mps.empty_cache()` dan `gc.collect()` dipanggil di
antara keduanya.

Hanya isolasi penuh pada tingkat proses, yaitu interpreter Python dan konteks GPU
yang baru untuk setiap tahap, yang terbukti andal menghindarinya. Karena itu
pemanggilan bawaan skrip ini menjalankan dirinya sendiri dua kali melalui
`--stage`, sementara antarmuka CLI yang dipakai dari luar tidak berubah.

Evaluasi pada split test hanya untuk pelaporan akhir, tidak pernah untuk
penyetelan model secara berulang. PERINGATAN dicatat setiap kali `--split test`
dipakai.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

os.environ.setdefault("YOLO_OFFLINE", "1")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.dataset.mapping import CANONICAL_CLASSES, CANONICAL_ID_TO_NAME  # noqa: E402
from agridata.device import detect_device  # noqa: E402
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.metrics.detection import (  # noqa: E402
    Detection,
    GroundTruthBox,
    match_detections_to_ground_truth,
)
from agridata.reproducibility.environment import get_git_commit  # noqa: E402
from agridata.visualization.images import draw_annotated_image  # noqa: E402
from agridata.dataset.stats import AnnotationRecord, ImageRecord  # noqa: E402

logger = logging.getLogger("agridata.scripts.evaluate")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reproducible mAP@50 / F1 evaluation (no test-set tuning).")
    parser.add_argument("--weights", required=True, type=Path)
    parser.add_argument("--split", required=True, choices=["train", "valid", "test"])
    parser.add_argument("--prepared-dir", default=Path("data/prepared"), type=Path)
    parser.add_argument("--data-yaml", default=None, type=Path, help="Defaults to <prepared-dir>/data.yaml")
    parser.add_argument("--device", default="auto", help="'auto' resolves via agridata.device.detect_device() (no CUDA assumed).")
    parser.add_argument(
        "--render-only",
        action="store_true",
        help="Membentuk ulang laporan Markdown dari evaluation_{split}.json yang sudah ada, "
        "tanpa menjalankan inferensi. Dipakai ketika hanya format laporan yang berubah, "
        "supaya angka tidak bergeser akibat nondeterminisme backend MPS.",
    )
    parser.add_argument(
        "--nms-iou", type=float, default=0.5,
        help=(
            "NMS IoU threshold passed to model.val(). Default 0.5 rather than Ultralytics' "
            "0.7: a sweep on the validation split (artifacts/reports/inference_tuning_nms.json) "
            "showed 0.5 gives +0.0124 mAP@0.5 and +0.0202 macro F1 on this dataset, which is "
            "dominated by small, densely packed objects. This is the value used for every "
            "reported metric."
        ),
    )
    parser.add_argument("--conf-threshold", type=float, default=0.25, help="Confidence threshold for the LOCAL F1 computation (configurable).")
    parser.add_argument("--collection-conf", type=float, default=0.001, help="Low threshold used once to collect raw predictions; --conf-threshold filters afterward.")
    parser.add_argument("--num-vis-samples", type=int, default=6)
    parser.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    parser.add_argument("--predictions-dir", default=Path("artifacts/predictions"), type=Path)
    parser.add_argument("--figures-dir", default=Path("artifacts/figures/predictions"), type=Path)
    parser.add_argument(
        "--stage",
        choices=["native_val", "local_f1"],
        default=None,
        help=argparse.SUPPRESS,  # internal use only: this process re-invokes itself with this flag
    )
    parser.add_argument("--stage-output", type=Path, default=None, help=argparse.SUPPRESS)
    return parser.parse_args()


def validate_class_mapping(model) -> None:
    """Gagal secara keras bila urutan kelas model tidak cocok dengan pemetaan canonical.

    Ground truth yang berasal dari manifest memakai model_class_id =
    canonical_id - 1 mengikuti urutan CANONICAL_CLASSES. Bila urutan kelas milik
    model sampai menyimpang dari itu, misalnya karena dilatih terhadap data.yaml
    yang berbeda, prediksi dan ground truth akan salah sejajar secara diam-diam.
    """
    model_names = [model.names[i] for i in range(len(model.names))]
    if model_names != list(CANONICAL_CLASSES):
        raise ValueError(
            f"Model class order {model_names} does not match the canonical class "
            f"order {list(CANONICAL_CLASSES)}, ground truth and predictions would "
            "not be comparable. Refusing to compute metrics."
        )


def load_ground_truth(manifest_path: Path) -> tuple[list[GroundTruthBox], dict[int, dict]]:
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)
    ground_truths = []
    images_by_id = {}
    for entry in manifest:
        images_by_id[entry["original_image_id"]] = entry
        for ann in entry["annotations"]:
            ground_truths.append(
                GroundTruthBox(entry["original_image_id"], ann["model_class_id"], tuple(ann["bbox_xywh"]))
            )
    return ground_truths, images_by_id


def collect_predictions(
    model, images_dir: Path, images_by_id: dict[int, dict], collection_conf: float, device: str
) -> list[Detection]:
    """Menjalankan inferensi pada confidence threshold rendah.

    Penyaringan dengan ambang yang lebih tinggi dilakukan belakangan di
    match_detections_to_ground_truth, yang merupakan fungsi murni sehingga tidak
    perlu inferensi ulang untuk setiap ambang.

    Parameter `stream=True` dipakai supaya Ultralytics menghasilkan satu Result
    pada satu waktu, alih-alih menumpuk seluruhnya di RAM dengan setiap Result
    membawa tensor citra. Pada skala dataset penuh hal ini diperlukan, dan
    Ultralytics sendiri memperingatkan agar tidak memakai bentuk non-stream
    justru karena alasan tersebut.

    Daftar path dikirim dalam potongan sebesar `CHUNK_SIZE`, bukan sebagai satu
    daftar berisi lebih dari 2.000 path. Uji reproduksi pada lingkungan bersih
    menemukan bahwa mengirim daftar path split valid secara utuh, yaitu 2.106
    citra, ke satu pemanggilan `predict(..., stream=True)` akan gagal dengan
    "MPSGraph does not support tensor dims larger than INT_MAX" pada kombinasi
    numpy, torch, dan MPS yang dipakai project ini.

    Kegagalan itu tereproduksi tanpa kaitan sama sekali dengan pemanggilan
    `val()` sebelumnya, murni akibat ukuran daftar path-nya. Pengujian
    mengonfirmasi bahwa sampai 1.000 path dalam satu pemanggilan masih berhasil,
    sedangkan 2.106 path gagal. Akar masalahnya belum terisolasi sepenuhnya, dan
    kemungkinan merupakan interaksi numpy 2.4.x dengan torch MPS khusus untuk
    daftar path eksplisit yang sangat panjang. Pemecahan menjadi potongan
    merupakan solusi sementara yang sudah terverifikasi dan kokoh.
    """
    CHUNK_SIZE = 500
    ordered_ids = list(images_by_id.keys())
    image_paths = [str(images_dir / images_by_id[iid]["file_name"]) for iid in ordered_ids]

    detections: list[Detection] = []
    for chunk_start in range(0, len(image_paths), CHUNK_SIZE):
        chunk_ids = ordered_ids[chunk_start : chunk_start + CHUNK_SIZE]
        chunk_paths = image_paths[chunk_start : chunk_start + CHUNK_SIZE]
        results_stream = model.predict(chunk_paths, conf=collection_conf, verbose=False, stream=True, device=device)
        for image_id, result in zip(chunk_ids, results_stream, strict=True):
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append(
                    Detection(
                        image_id=image_id,
                        class_id=int(box.cls.item()),
                        confidence=float(box.conf.item()),
                        bbox_xywh=(x1, y1, x2 - x1, y2 - y1),
                    )
                )
    return detections


def save_prediction_samples(
    images_dir: Path,
    images_by_id: dict[int, dict],
    detections: list[Detection],
    conf_threshold: float,
    num_samples: int,
    output_dir: Path,
) -> list[str]:
    """Save a small number of images with PREDICTED boxes drawn, for visual sanity-checking."""
    det_by_image: dict[int, list[Detection]] = {}
    for d in detections:
        if d.confidence >= conf_threshold:
            det_by_image.setdefault(d.image_id, []).append(d)

    image_ids_with_predictions = sorted(det_by_image.keys())[:num_samples]
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for image_id in image_ids_with_predictions:
        entry = images_by_id[image_id]
        image_record = ImageRecord(image_id, entry["file_name"], entry["width"], entry["height"])
        pred_annotations = [
            AnnotationRecord(
                annotation_id=-1,
                image_id=image_id,
                canonical_class=CANONICAL_ID_TO_NAME[d.class_id + 1],
                bbox=d.bbox_xywh,
            )
            for d in det_by_image[image_id]
        ]
        annotated = draw_annotated_image(images_dir / entry["file_name"], image_record, pred_annotations)
        out_path = output_dir / f"pred_id{image_id}_{entry['file_name']}"
        annotated.save(out_path)
        saved.append(str(out_path))
    return saved


def run_native_val_stage(args: argparse.Namespace) -> None:
    """Runs in its OWN process: load model, run model.val(), write results to --stage-output."""
    from ultralytics import YOLO

    data_yaml = args.data_yaml or (args.prepared_dir / "data.yaml")
    device = detect_device() if args.device == "auto" else args.device

    model = YOLO(str(args.weights))
    validate_class_mapping(model)

    ultralytics_split = {"train": "train", "valid": "val", "test": "test"}[args.split]
    val_results = model.val(
        data=str(data_yaml), split=ultralytics_split, iou=args.nms_iou,
        plots=False, verbose=False, device=device,
    )

    # F1 macro: kurva F1 per kelas dirata-ratakan antar kelas, lalu diambil pada
    # satu confidence threshold yang memaksimalkan rata-rata tersebut. Inilah
    # F1-Score yang dilaporkan. F1 rata-rata micro yang dihitung pada tahap lain
    # berstatus diagnostik sekunder, bukan angka yang dilaporkan. Lihat
    # artifacts/audit/metrics_methodology.md.
    import numpy as np

    f1_per_class = np.array(val_results.box.f1_curve)
    conf_grid = np.linspace(0, 1, f1_per_class.shape[1])
    macro_f1_curve = f1_per_class.mean(axis=0)
    best = int(macro_f1_curve.argmax())

    native_metrics = {
        "mAP50": float(val_results.box.map50),
        "mAP50_95": float(val_results.box.map),
        "precision_at_internal_best_f1_point": float(val_results.box.mp),
        "recall_at_internal_best_f1_point": float(val_results.box.mr),
        "nms_iou": float(args.nms_iou),
        "macro_f1": float(macro_f1_curve[best]),
        "macro_f1_confidence": float(conf_grid[best]),
        "precision_at_macro_f1_point": float(np.array(val_results.box.p_curve).mean(axis=0)[best]),
        "recall_at_macro_f1_point": float(np.array(val_results.box.r_curve).mean(axis=0)[best]),
    }
    per_class_map50 = {}
    for idx, class_id in enumerate(val_results.box.ap_class_index):
        canonical_name = CANONICAL_ID_TO_NAME[int(class_id) + 1]
        per_class_map50[canonical_name] = float(val_results.box.ap50[idx])

    with args.stage_output.open("w", encoding="utf-8") as f:
        json.dump({"native_metrics": native_metrics, "per_class_map50": per_class_map50}, f)


def run_local_f1_stage(args: argparse.Namespace) -> None:
    """Runs in its OWN process: load model, collect predictions, match, save
    artifacts+figures, write results to --stage-output."""
    from ultralytics import YOLO

    device = detect_device() if args.device == "auto" else args.device
    manifest_path = args.prepared_dir / f"manifest_{args.split}.json"
    images_dir = args.prepared_dir / args.split / "images"

    model = YOLO(str(args.weights))
    validate_class_mapping(model)

    ground_truths, images_by_id = load_ground_truth(manifest_path)
    detections = collect_predictions(model, images_dir, images_by_id, args.collection_conf, device)

    local_result = match_detections_to_ground_truth(detections, ground_truths, args.conf_threshold)
    local_overall = local_result["overall"]
    local_per_class = {
        CANONICAL_ID_TO_NAME[cid + 1]: asdict(prf1) for cid, prf1 in local_result["per_class"].items()
    }

    args.predictions_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = args.predictions_dir / f"predictions_{args.split}.json"
    with predictions_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(d) for d in detections], f, indent=2)

    saved_samples = save_prediction_samples(
        images_dir, images_by_id, detections, args.conf_threshold, args.num_vis_samples, args.figures_dir
    )

    with args.stage_output.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "overall": asdict(local_overall),
                "per_class": local_per_class,
                "num_detections_collected": len(detections),
                "num_ground_truth_boxes": len(ground_truths),
                "predictions_artifact": str(predictions_path),
                "sample_prediction_figures": saved_samples,
            },
            f,
        )


def run_stage_in_subprocess(stage: str, args: argparse.Namespace) -> dict:
    """Menjalankan proses baru `python scripts/evaluate.py --stage <stage> ...` lalu
    membaca kembali hasil JSON-nya. Alasan tahap ini dijalankan sebagai proses
    terpisah, bukan sebagai pemanggilan fungsi, dijelaskan pada docstring
    modul."""
    with tempfile.TemporaryDirectory() as tmpdir:
        stage_output = Path(tmpdir) / f"{stage}.json"
        cmd = [
            sys.executable, __file__,
            "--weights", str(args.weights),
            "--split", args.split,
            "--prepared-dir", str(args.prepared_dir),
            "--device", args.device,
            "--conf-threshold", str(args.conf_threshold),
            "--collection-conf", str(args.collection_conf),
            "--num-vis-samples", str(args.num_vis_samples),
            "--predictions-dir", str(args.predictions_dir),
            "--figures-dir", str(args.figures_dir),
            "--stage", stage,
            "--stage-output", str(stage_output),
        ]
        if args.data_yaml:
            cmd += ["--data-yaml", str(args.data_yaml)]

        logger.info("Running stage '%s' in a fresh subprocess (isolates MPS state)...", stage)
        result = subprocess.run(cmd)
        if result.returncode != 0:
            raise RuntimeError(f"Stage '{stage}' subprocess failed with exit code {result.returncode}")

        with stage_output.open("r", encoding="utf-8") as f:
            return json.load(f)


def build_markdown(summary: dict, conf_threshold: float) -> str:
    """Menyusun laporan Markdown dari ringkasan evaluasi.

    Dipisahkan dari alur inferensi agar laporan dapat dibentuk ulang dari berkas
    JSON yang sudah tersimpan, tanpa menjalankan inferensi lagi. Dengan begitu
    perubahan format laporan tidak berisiko menggeser angka, karena backend MPS
    tidak menjamin hasil inferensi yang identik antar pengulangan.
    """
    native_metrics = summary["native_metrics"]
    per_class_map50 = native_metrics["per_class_AP50"]
    local_overall = summary["local_f1_metrics"]["overall"]
    local_per_class = summary["local_f1_metrics"]["per_class"]
    split = summary["split"]

    # Path bobot ditampilkan relatif terhadap akar repository agar laporan tidak
    # memuat path absolut milik mesin tertentu.
    weights = Path(summary["weights"])
    root = Path(__file__).resolve().parent.parent
    try:
        weights = weights.resolve().relative_to(root)
    except ValueError:
        pass

    lines = [
        f"# Laporan Evaluasi, split: `{split}`",
        "",
        f"Bobot: `{weights}`  |  Commit Git: `{summary['git_commit']}`",
        "",
        "## Metrik native Ultralytics, sumber kebenaran untuk mAP",
        "",
        f"- mAP@0.5: {native_metrics['mAP50']:.4f}",
        f"- mAP@0.5:0.95: {native_metrics['mAP50_95']:.4f}",
        f"- Ambang NMS IoU: {native_metrics['nms_iou']}",
        f"- F1 macro pada titik operasi terbaik: {native_metrics['macro_f1']:.4f} "
        f"(confidence {native_metrics['macro_f1_confidence']:.4f})",
        f"- Precision dan recall pada titik operasi tersebut: "
        f"{native_metrics.get('precision_at_macro_f1_point', 0):.4f} / "
        f"{native_metrics.get('recall_at_macro_f1_point', 0):.4f}",
        "",
        "| Kelas canonical | AP@0.5 |",
        "|---|---:|",
    ]
    for cls, ap in per_class_map50.items():
        lines.append(f"| {cls} | {ap:.4f} |")
    lines += [
        "",
        f"## Metrik lokal diagnostik, rata-rata micro pada confidence {conf_threshold}",
        "",
        f"- Precision keseluruhan: {local_overall['precision']:.4f}",
        f"- Recall keseluruhan: {local_overall['recall']:.4f}",
        f"- F1 keseluruhan: {local_overall['f1']:.4f}",
        f"- TP={local_overall['true_positives']} FP={local_overall['false_positives']} "
        f"FN={local_overall['false_negatives']}",
        "",
        "| Kelas canonical | precision | recall | F1 | TP | FP | FN |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for cls, prf1 in local_per_class.items():
        lines.append(
            f"| {cls} | {prf1['precision']:.4f} | {prf1['recall']:.4f} | {prf1['f1']:.4f} | "
            f"{prf1['true_positives']} | {prf1['false_positives']} | {prf1['false_negatives']} |"
        )
    if split == "test":
        lines += [
            "",
            "**PERINGATAN: ini evaluasi pada split test. Ground truth test tidak boleh dipakai "
            "untuk penyetelan model secara berulang.**",
        ]
    return "\n".join(lines) + "\n"


def main() -> int:
    setup_logging()
    args = parse_args()

    if args.render_only:
        json_path = args.report_dir / f"evaluation_{args.split}.json"
        if not json_path.exists():
            raise SystemExit(f"Tidak menemukan {json_path}. Jalankan evaluasi penuh terlebih dahulu.")
        with json_path.open("r", encoding="utf-8") as f:
            summary = json.load(f)
        md_path = args.report_dir / f"evaluation_{args.split}.md"
        md_path.write_text(build_markdown(summary, args.conf_threshold), encoding="utf-8")
        print(f"Laporan dibentuk ulang dari {json_path} tanpa inferensi: {md_path}")
        return 0

    if args.device == "auto":
        args.device = detect_device()

    # Pemanggilan internal: jalankan tepat satu tahap lalu keluar.
    if args.stage == "native_val":
        run_native_val_stage(args)
        return 0
    if args.stage == "local_f1":
        run_local_f1_stage(args)
        return 0

    # Top-level invocation: orchestrate both stages as separate processes.
    if args.split == "test":
        logger.warning(
            "Evaluating on the TEST split. Per the master spec, test ground truth must "
            "NEVER be used to tune the model. This run should only happen for final, "
            "frozen-model reporting (Block 15+), not iterative experimentation."
        )

    logger.info("Device: %s", args.device)
    data_yaml = args.data_yaml or (args.prepared_dir / "data.yaml")

    native = run_stage_in_subprocess("native_val", args)
    local = run_stage_in_subprocess("local_f1", args)

    native_metrics = native["native_metrics"]
    per_class_map50 = native["per_class_map50"]
    local_overall = local["overall"]
    local_per_class = local["per_class"]

    summary = {
        "block": 7,
        "git_commit": get_git_commit(),
        "weights": str(args.weights),
        "split": args.split,
        "data_yaml": str(data_yaml),
        "iou_threshold": 0.5,
        "native_metrics": {
            "description": "Computed via ultralytics model.val(), source of truth for mAP. "
            "IoU thresholds: torch.linspace(0.5, 0.95, 10); mAP50 uses index 0 (IoU=0.50). "
            "Run in its own subprocess, see module docstring for why.",
            **native_metrics,
            "per_class_AP50": per_class_map50,
        },
        "local_f1_metrics": {
            "description": "LOCAL implementation detail (not the official scoring formula): "
            "greedy IoU>=0.5 matching at a caller-specified confidence threshold. See "
            "src/agridata/metrics/detection.py for full methodology. Run in its own subprocess.",
            "confidence_threshold": args.conf_threshold,
            "overall": local_overall,
            "per_class": local_per_class,
        },
        "num_detections_collected": local["num_detections_collected"],
        "num_ground_truth_boxes": local["num_ground_truth_boxes"],
        "predictions_artifact": local["predictions_artifact"],
        "sample_prediction_figures": local["sample_prediction_figures"],
        "test_set_tuning_warning_issued": args.split == "test",
    }

    args.report_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.report_dir / f"evaluation_{args.split}.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    markdown = build_markdown(summary, args.conf_threshold)

    md_path = args.report_dir / f"evaluation_{args.split}.md"
    md_path.write_text(markdown, encoding="utf-8")

    print(markdown)
    print(f"\nJSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    print(f"Prediction artifacts: {local['predictions_artifact']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
