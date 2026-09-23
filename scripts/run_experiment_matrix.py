#!/usr/bin/env python3
"""Matriks percobaan terkontrol satu faktor pada satu waktu.

Pemakaian:
    python scripts/run_experiment_matrix.py --matrix-config configs/experiments/matrix.yaml

Skrip menjalankan matriks satu faktor pada satu waktu sesuai definisi pada berkas
konfigurasi YAML yang diberikan, yaitu satu baseline ditambah N varian, dan
setiap varian mengubah tepat satu faktor dari baseline.

Seluruh percobaan memakai dataset, split, seed, dan metode evaluasi yang sama,
serta tanpa external pretrained weights, yang ditegakkan oleh
agridata.training.train.build_compliant_model. Setiap eksekusi dicatat ke pelacak
percobaan dengan nilai hasil pengukuran yang sesungguhnya; tidak ada satu pun
angka di sini yang diperkirakan atau diandaikan belakangan.

Sebelum berjalan, skrip melaporkan kondisi disk, RAM, dan perangkat, supaya
matriks yang panjang tidak pernah dijalankan tanpa gambaran sumber daya.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.device import detect_device  # noqa: E402
from agridata.experiments.tracker import (  # noqa: E402
    ExperimentRecord,
    append_experiment,
    build_markdown_table,
    compute_manifest_hash,
    load_experiments,
)
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.reproducibility.environment import get_git_commit  # noqa: E402
from agridata.seed import set_global_seed  # noqa: E402
from agridata.training.train import run_training  # noqa: E402

import logging  # noqa: E402

logger = logging.getLogger("agridata.scripts.run_experiment_matrix")

AUGMENTATION_KEYS = {"degrees", "translate", "scale", "shear", "perspective", "flipud", "fliplr", "bgr", "mosaic", "mixup", "copy_paste", "hsv_h", "hsv_s", "hsv_v"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Block 10 controlled hyperparameter experiment matrix.")
    parser.add_argument("--matrix-config", default=Path("configs/experiments/matrix.yaml"), type=Path)
    parser.add_argument("--project", default=Path("runs/detect/matrix"), type=Path)
    parser.add_argument("--manifest", default=Path("data/prepared/manifest_train.json"), type=Path)
    parser.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    return parser.parse_args()


def report_resources(device: str) -> dict:
    disk = shutil.disk_usage(".")
    return {
        "device": device,
        "disk_free_gb": round(disk.free / (1024**3), 1),
        "disk_total_gb": round(disk.total / (1024**3), 1),
    }


def build_experiment_configs(matrix: dict) -> list[dict]:
    """Merge common + baseline + each variant's overrides into one flat config per experiment."""
    common = matrix["common"]
    baseline = matrix["baseline"]

    configs = [{**common, **baseline, "experiment_id": "E02", "axis": "baseline", "notes": "Baseline matriks percobaan, dipakai sebagai titik referensi pengujian satu faktor."}]
    for variant in matrix["variants"]:
        merged = {**common, **baseline, **variant["overrides"]}
        merged["experiment_id"] = f"E{len(configs) + 2:02d}"
        merged["axis"] = variant["axis"]
        merged["notes"] = f"Varian satu faktor: {variant['axis']} diubah dari baseline, seluruh parameter lain ditahan tetap."
        configs.append(merged)
    return configs


def run_one_experiment(config: dict, project: Path, git_commit: str | None, manifest_hash: str) -> dict:
    device = detect_device() if config["device"] == "auto" else config["device"]
    set_global_seed(config["seed"])

    extra_kwargs: dict = {
        "optimizer": config["optimizer"],
        "lr0": config["learning_rate"],
        "momentum": config["momentum"],
        "weight_decay": config["weight_decay"],
    }
    extra_kwargs.update({k: v for k, v in config.get("augmentation", {}).items() if k in AUGMENTATION_KEYS})

    logger.info("=== Experiment %s (axis: %s) ===", config["experiment_id"], config["axis"])
    logger.info(
        "imgsz=%d batch=%d epochs=%d optimizer=%s lr0=%.6g device=%s",
        config["image_size"], config["batch_size"], config["epochs"], config["optimizer"], config["learning_rate"], device,
    )

    started_at = time.monotonic()
    result = run_training(
        model_arch=config["model_arch"],
        data_yaml=Path(config["data_yaml"]),
        output_project=project,
        run_name=config["experiment_id"],
        image_size=config["image_size"],
        batch_size=config["batch_size"],
        epochs=config["epochs"],
        device=device,
        seed=config["seed"],
        workers=config["workers"],
        fraction=config["fraction"],
        plots=False,
        validate=config["validate_during_training"],
        extra_train_kwargs=extra_kwargs,
    )
    duration = time.monotonic() - started_at

    # One authoritative val() pass post-training, same native-metric
    # methodology Block 7 established (mAP@0.5 via Ultralytics' own
    # implementation), used consistently across every experiment here.
    from ultralytics import YOLO

    model = YOLO(result["best_weights"])
    val_results = model.val(data=config["data_yaml"], split="val", plots=False, verbose=False, device=device)

    record = ExperimentRecord(
        experiment_id=config["experiment_id"],
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=git_commit,
        seed=config["seed"],
        model_architecture=config["model_arch"],
        pretrained=config["pretrained"],
        dataset_manifest_hash=manifest_hash,
        image_size=config["image_size"],
        batch_size=config["batch_size"],
        epochs=config["epochs"],
        optimizer=result["resolved_hyperparameters"]["optimizer"],
        learning_rate=result["resolved_hyperparameters"]["learning_rate"],
        weight_decay=result["resolved_hyperparameters"]["weight_decay"],
        scheduler=result["resolved_hyperparameters"]["scheduler"],
        augmentation_config=result["resolved_hyperparameters"]["augmentation"],
        device=device,
        best_val_map50=float(val_results.box.map50),
        best_val_f1=None,  # local F1 (Block 7) is reserved for the final chosen config, not every screening run
        precision=float(val_results.box.mp),
        recall=float(val_results.box.mr),
        training_duration_seconds=duration,
        notes=config["notes"],
        compliance_notes="No external pretrained weights (yaml-only architecture, pretrained=False). YOLO_OFFLINE enforced.",
    )

    return {"config": config, "record": record, "mAP50_95": float(val_results.box.map)}


def build_recommendation(results: list[dict]) -> str:
    baseline = next(r for r in results if r["config"]["axis"] == "baseline")
    lines = [
        "# Matriks Percobaan Baseline: Hasil dan Rekomendasi",
        "",
        "Perlu dicatat soal skalanya. Matriks ini memakai sebagian kecil data latih dengan "
        "sedikit *epoch* sebagai tahap penyaringan yang cepat, bukan rezim pelatihan final. "
        "Nilai mAP absolutnya memang rendah, dan pada tahap ini hanya perbedaan *relatif* "
        "antar varian terhadap baseline yang bermakna.",
        "",
        "## Hasil",
        "",
        "| Percobaan | Faktor yang diubah | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall | Durasi (detik) |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        rec = r["record"]
        lines.append(
            f"| {rec.experiment_id} | {r['config']['axis']} | {rec.best_val_map50:.4f} | {r['mAP50_95']:.4f} | "
            f"{rec.precision:.4f} | {rec.recall:.4f} | {rec.training_duration_seconds:.1f} |"
        )

    lines += ["", "## Efek tiap faktor, relatif terhadap baseline", ""]
    baseline_map = baseline["record"].best_val_map50
    for r in results:
        if r["config"]["axis"] == "baseline":
            continue
        delta = r["record"].best_val_map50 - baseline_map
        direction = "naik" if delta > 0 else ("turun" if delta < 0 else "tidak berubah")
        lines.append(f"- **{r['config']['axis']}**: mAP@0.5 {direction} sebesar {delta:+.4f} terhadap baseline "
            f"(durasi {r['record'].training_duration_seconds:.0f} detik berbanding {baseline['record'].training_duration_seconds:.0f} detik pada baseline).")

    best = max(results, key=lambda r: r["record"].best_val_map50)
    lines += [
        "",
        "## Rekomendasi",
        "",
        f"mAP@0.5 tertinggi pada tahap penyaringan ini: **{best['config']['experiment_id']}** "
        f"({best['config']['axis']}, mAP@0.5={best['record'].best_val_map50:.4f}).",
        "",
        "Hasil ini TIDAK dinyatakan sebagai konfigurasi final. Tidak ada konfigurasi yang disebut "
        "terbaik sebelum diukur pada skala penuh. Temuan di sini menjadi masukan, bukan pengganti, "
        "bagi ablasi augmentasi, ablasi ketidakseimbangan kelas, dan analisis kesalahan, sebelum "
        "konfigurasi final dibekukan.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    setup_logging()
    args = parse_args()

    with args.matrix_config.open("r", encoding="utf-8") as f:
        matrix = yaml.safe_load(f)

    device = detect_device() if matrix["common"]["device"] == "auto" else matrix["common"]["device"]
    resources = report_resources(device)
    logger.info("Resource check before running matrix: %s", resources)
    print(f"Resource check: {json.dumps(resources, indent=2)}")

    configs = build_experiment_configs(matrix)
    logger.info("Planned %d experiments: %s", len(configs), [c["experiment_id"] for c in configs])

    git_commit = get_git_commit()
    manifest_hash = compute_manifest_hash(args.manifest)

    results = []
    for config in configs:
        result = run_one_experiment(config, args.project, git_commit, manifest_hash)
        append_experiment(result["record"])
        results.append(result)
        logger.info("Experiment %s done: mAP@0.5=%.4f (%.1fs)", result["record"].experiment_id, result["record"].best_val_map50, result["record"].training_duration_seconds)

    args.report_dir.mkdir(parents=True, exist_ok=True)
    recommendation = build_recommendation(results)
    (args.report_dir / "block10_matrix_recommendation.md").write_text(recommendation, encoding="utf-8")

    all_records = load_experiments()
    (Path("artifacts/experiments") / "experiment_log.md").write_text(build_markdown_table(all_records), encoding="utf-8")

    print(recommendation)
    print(f"\nExperiment log updated: artifacts/experiments/experiment_log.json")
    print(f"Recommendation report: artifacts/reports/block10_matrix_recommendation.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
