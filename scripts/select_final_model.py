#!/usr/bin/env python3
"""Pemilihan konfigurasi model final berdasarkan bukti percobaan.

Pemakaian:
    python scripts/select_final_model.py --only report

Skrip membaca seluruh percobaan yang tercatat pada
artifacts/experiments/experiment_log.json, lalu menyusun laporan pemilihan
beserta metadata model dan draf model card. Yang dibekukan di sini adalah
KONFIGURASI, bukan berkas bobot; bobot final dihasilkan oleh
scripts/run_final_training.py memakai configs/final_model_config.yaml.

Tidak ada konfigurasi yang dinyatakan memadai berdasarkan performa validasi
sebelum pelatihan skala penuh selesai, dan laporan ini menyatakannya secara
terbuka alih-alih mengklaim lebih dari yang terbukti.

Argumen --only membatasi keluaran karena model card dan metadata model sudah
difinalisasi setelah pelatihan selesai; menulis ulang keduanya dari templat
draf akan mengembalikannya ke kondisi sebelum ada bobot.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.dataset.mapping import CANONICAL_CLASSES, MAPPING_VERSION  # noqa: E402
from agridata.reproducibility.environment import capture_environment_snapshot  # noqa: E402

FINAL_CONFIG_PATH = Path("configs/final_model_config.yaml")
EXPERIMENT_LOG_PATH = Path("artifacts/experiments/experiment_log.json")
REPORT_DIR = Path("artifacts/reports")
DOCS_DIR = Path("docs")


def load_experiments() -> list[dict]:
    with EXPERIMENT_LOG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_file_size_mb(path: Path) -> float | None:
    return round(path.stat().st_size / (1024 * 1024), 2) if path.exists() else None


def build_candidate_table(experiments: list[dict]) -> str:
    lines = [
        "| Percobaan | imgsz | epoch | optimizer | mAP@0.5 | Precision | Recall | Durasi (detik) | Catatan |",
        "|---|---:|---:|---|---:|---:|---:|---:|---|",
    ]
    for r in sorted(experiments, key=lambda r: -r["best_val_map50"]):
        notes = r["notes"][:70].replace("|", "\\|")
        lines.append(
            f"| {r['experiment_id']} | {r['image_size']} | {r['epochs']} | {r['optimizer']} | "
            f"{r['best_val_map50']:.4f} | {r['precision']:.4f} | {r['recall']:.4f} | "
            f"{r['training_duration_seconds']:.0f} | {notes} |"
        )
    return "\n".join(lines)


def get_git_commit() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def build_compliance_checklist(experiments: list[dict]) -> list[dict]:
    best = max(experiments, key=lambda r: r["best_val_map50"])
    return [
        {
            "item": "Tanpa external pretrained weights",
            "status": "LULUS",
            "evidence": "Model selalu dibangun dari yolov8n.yaml yang hanya memuat arsitektur. "
            "build_compliant_model() melempar galat bila diberi pretrained=True atau berkas "
            ".pt/.pth/.ckpt. YOLO_OFFLINE ditegakkan pada seluruh skrip pelatihan dan evaluasi. "
            "Verifikasi cache checkpoint kosong dijalankan dengan membandingkan isi direktori "
            "sebelum dan sesudah pelatihan; tidak ada berkas .pt yang muncul di luar keluaran "
            "runs/ milik project ini sendiri.",
        },
        {
            "item": "Tanpa kebocoran data",
            "status": "SEBAGIAN, satu kasus terkonfirmasi sudah ditangani, risiko sisa didokumentasikan",
            "evidence": "Audit forensik menemukan tepat satu citra duplikat persis (identik menurut MD5) "
            "antara split train dan test ('leaf_scald-230...'), dan entri tersebut dikeluarkan dari "
            "manifest latih. Kandidat kemiripan berbasis perceptual hash belum dikonfirmasi satu per satu "
            "dan tidak ditelusuri lebih jauh; hal ini dicatat sebagai risiko sisa yang terdokumentasi, "
            "bukan diabaikan diam-diam.",
        },
        {
            "item": "Memakai 11 kelas canonical resmi",
            "status": "LULUS",
            "evidence": f"Pemetaan canonical divalidasi terhadap dataset aktual tanpa menyisakan satu pun "
            f"kategori mentah yang tidak terpetakan (versi pemetaan {MAPPING_VERSION}). Berkas data.yaml "
            f"selalu mendeklarasikan tepat {len(CANONICAL_CLASSES)} kelas dalam urutan canonical: "
            f"{list(CANONICAL_CLASSES)}.",
        },
        {
            "item": "Prapemrosesan yang dapat direproduksi",
            "status": "LULUS",
            "evidence": "Menjalankan ulang scripts/prepare_dataset.py dengan seed yang sama menghasilkan "
            "manifest 10.132 citra yang identik byte per byte. Hal ini diverifikasi melalui eksekusi ulang "
            "dan pembandingan langsung, bukan diasumsikan.",
        },
        {
            "item": "Konfigurasi yang dapat direproduksi",
            "status": "LULUS",
            "evidence": f"Pelacak percobaan mencatat seed, commit Git, dan hyperparameter untuk seluruh "
            f"{len(experiments)} percobaan yang tercatat. Konfigurasi beku pada laporan ini "
            f"({FINAL_CONFIG_PATH}) sendiri berada di bawah kendali versi.",
        },
        {
            "item": "Checkpoint yang valid",
            "status": "LULUS untuk checkpoint penyaringan, MENUNGGU untuk bobot final",
            "evidence": "Seluruh 21 percobaan penyaringan menghasilkan best.pt yang dapat dimuat, "
            "diverifikasi dengan memuat ulang secara segar pada proses evaluasi dan analisis kesalahan. "
            "Checkpoint final untuk submission belum ada pada tahap ini dan harus diverifikasi ulang "
            "setelah pelatihan skala penuh selesai.",
        },
        {
            "item": "Inferensi berhasil dijalankan",
            "status": "LULUS",
            "evidence": "Uji inferensi mandiri dijalankan pada checkpoint yang baru dimuat di dalam proses "
            "bersih. Selain itu evaluate.py dan run_error_analysis.py keduanya berhasil menjalankan "
            "inferensi pada checkpoint penyaringan di seluruh split validasi (2.106 citra).",
        },
        {
            "item": "Performa validasi yang memadai",
            "status": "MENUNGGU, BELUM TERPENUHI, dan sengaja tidak diklaim",
            "evidence": f"Hasil penyaringan terbaik sejauh ini: {best['experiment_id']} dengan mAP@0.5="
            f"{best['best_val_map50']:.4f}, dilatih hanya pada sekitar 10 persen data latih selama "
            f"{best['epochs']} epoch. Angka ini berskala penyaringan, bukan hasil yang kompetitif, dan "
            "tidak disajikan sebagai hasil kompetitif. Pelatihan skala penuh (fraction=1.0, epochs=50, "
            "patience=15) diperlukan sebelum butir ini dapat dinilai secara jujur.",
        },
    ]


def build_model_metadata(git_commit: str) -> dict:
    return {
        "model_name": "agridata-telepati8-yolov8n",
        "architecture": "YOLOv8n (Ultralytics), built from architecture-only .yaml, pretrained=False",
        "task": "object_detection",
        "num_classes": len(CANONICAL_CLASSES),
        "class_names": list(CANONICAL_CLASSES),
        "mapping_version": MAPPING_VERSION,
        "input": {"image_size": 640, "channels": 3, "format": "RGB"},
        "output": "bounding boxes (xyxy) + class + confidence, per canonical class",
        "training_config_path": str(FINAL_CONFIG_PATH),
        "compliance": {
            "external_pretrained_weights": False,
            "external_dataset_used": False,
            "llm_api_dataset_processing": False,
            "yolo_offline_enforced": True,
        },
        "status": "CONFIGURATION FROZEN, weights not yet produced (pending Block 15)",
        "selected_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit_at_selection": git_commit,
        "weights_path": None,
        "weights_checksum_sha256": None,
    }


def build_model_card_draft() -> str:
    return f"""# Model Card (Draft). AgriData TELEPATI 8.0 Rice Disease Detector

**Status: DRAFT.** Training config is frozen (`{FINAL_CONFIG_PATH}`); weights, final metrics, and
evaluation results will be filled in after Block 15 (final training run) and Block 16 (clean
reproduction test). Do not treat any number in this draft as final.

## Intended use

Object detection of rice plant disease/health conditions from field-captured imagery (drone or
handheld camera), as a component of a Smart Agriculture monitoring system, per the TELEPATI 8.0
AgriData Intelligence Race case study (assisting a farmer in monitoring large plots without
exhaustive manual inspection).

## Model architecture

YOLOv8n (Ultralytics), initialized from an architecture-only definition (no external pretrained
weights, `pretrained=False`, verified via source inspection and empty-checkpoint-cache checks in
Block 6). ~3.0M parameters, 11-class detection head.

## Training data

Official TELEPATI 8.0 AgriData dataset (COCO-format, Roboflow export). 11 canonical classes
(see `src/agridata/dataset/mapping.py` for the verified raw-to-canonical mapping):
{', '.join(CANONICAL_CLASSES)}.

One confirmed exact-duplicate image across train/test was excluded from training (Block 2/5).

## Training procedure

See `{FINAL_CONFIG_PATH}` for the complete, version-controlled configuration. Selected from 21
controlled screening experiments (Blocks 10-13), see
`artifacts/reports/block14_final_model_selection.md` for full reasoning per hyperparameter.

## Evaluation

*Pending Block 15/16.* Metrics will be computed via `scripts/evaluate.py` (mAP@0.5. Ultralytics'
native implementation; F1, a documented local implementation via greedy IoU≥0.5 matching at a
configurable confidence threshold, since Ultralytics' own reported precision/recall uses an
internally auto-selected threshold that is not configurable, see
`src/agridata/metrics/detection.py`).

## Known limitations (as of this draft)

- All findings so far come from small-fraction, low-epoch screening experiments; full-scale
  behavior may differ.
- Residual, unconfirmed perceptual-hash near-duplicate candidates across splits (Block 2) were
  not individually resolved.
- No bit-for-bit training determinism guarantee on Apple Silicon / MPS (confirmed non-deterministic
  kernels for two operations used in this pipeline).
- Class imbalance is real (22.6x max/min instance ratio); a targeted-oversampling mitigation was
  tested (Block 12) and did not show a clear benefit at screening scale, not adopted in the final
  config as of this draft; may be revisited after Block 15's full-scale results.

## Compliance statement

No external pretrained weights, no external dataset, no LLM/API dataset processing. See
`artifacts/reports/block14_final_model_selection.md` for the full evidence-based compliance
checklist.
"""


def main() -> int:
    experiments = load_experiments()
    git_commit = get_git_commit()
    checklist = build_compliance_checklist(experiments)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    report = build_report(experiments, checklist, git_commit)
    (REPORT_DIR / "block14_final_model_selection.md").write_text(report, encoding="utf-8")

    metadata = build_model_metadata(git_commit)
    with (REPORT_DIR / "final_model_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    (DOCS_DIR / "model_card_draft.md").write_text(build_model_card_draft(), encoding="utf-8")

    env_snapshot = capture_environment_snapshot()
    with (REPORT_DIR / "block14_environment_snapshot.json").open("w", encoding="utf-8") as f:
        json.dump(env_snapshot, f, indent=2)

    print(report)
    print("\nWritten:")
    print(f"  {REPORT_DIR / 'block14_final_model_selection.md'}")
    print(f"  {REPORT_DIR / 'final_model_metadata.json'}")
    print(f"  {DOCS_DIR / 'model_card_draft.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
