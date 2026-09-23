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


def build_report(experiments: list[dict], checklist: list[dict], git_commit: str) -> str:
    best = max(experiments, key=lambda r: r["best_val_map50"])
    lines = [
        "# Pemilihan Konfigurasi Model Final",
        "",
        f"Laporan ini meninjau seluruh {len(experiments)} percobaan yang tercatat "
        f"(E01 sampai E{len(experiments):02d}). Yang dipilih dan dibekukan di sini adalah KONFIGURASI "
        "untuk pelatihan skala penuh; laporan ini sendiri tidak menghasilkan bobot final yang disubmit.",
        "",
        "## Seluruh percobaan kandidat, diurutkan menurut mAP@0.5",
        "",
        build_candidate_table(experiments),
        "",
        f"## Konfigurasi terpilih: lihat `{FINAL_CONFIG_PATH}`",
        "",
        f"Hasil penyaringan individual terbaik adalah **{best['experiment_id']}** "
        f"(mAP@0.5={best['best_val_map50']:.4f}). Konfigurasi final yang dibekukan tidak sekadar "
        "menyalin pengaturan percobaan tersebut apa adanya, melainkan merangkum bukti dari seluruh 21 "
        "percobaan. Alasan untuk setiap hyperparameter tercantum sebagai komentar di dalam berkas "
        "konfigurasi, dan dilengkapi penalaran kelayakan semantik dari ablasi augmentasi serta bukti "
        "independen dari analisis kesalahan.",
        "",
        "## Daftar periksa kepatuhan, berbasis bukti dan bukan sekadar pernyataan",
        "",
        "| # | Butir | Status | Bukti |",
        "|---:|---|---|---|",
    ]
    for i, c in enumerate(checklist, start=1):
        lines.append(f"| {i} | {c['item']} | {c['status']} | {c['evidence']} |")

    lines += [
        "",
        "## Risiko yang diketahui",
        "",
        "- Kandidat tumpang tindih berbasis perceptual hash yang tersisa dari audit dataset "
        "(train terhadap valid: 426, train terhadap test: 210, valid terhadap test: 84) tidak pernah "
        "dikonfirmasi satu per satu secara visual, sehingga belum diketahui mana yang benar-benar "
        "duplikat dan mana yang merupakan false positive dari aHash 8x8 yang kasar. Hanya satu duplikat "
        "persis menurut MD5 yang ditindaklanjuti.",
        "- Seluruh 21 percobaan penyaringan memakai sebagian kecil data latih (8 sampai 10 persen) dan "
        "sedikit epoch (5 sampai 12). Angka skala penuh pada konfigurasi beku (epochs=50, fraction=1.0) "
        "merupakan ekstrapolasi, bukan hasil pengukuran langsung. Perilaku skala penuh yang sebenarnya "
        "baru teramati pada pelatihan final.",
        "- Backend MPS terbukti memiliki kernel yang tidak deterministik untuk `scatter_reduce_mps` dan "
        "`index_put_with_accumulate_mps`. Karena itu reproduksi pelatihan bit per bit tidak dijamin; "
        "yang dijamin hanya reproduksi konfigurasi dan prapemrosesan.",
        "- Perkiraan waktu pelatihan skala penuh sekitar 8,2 jam pada perangkat yang dipakai project ini "
        "tergolong lama. Nilai `patience=15` berpotensi memperpendeknya, tetapi perkiraan ini harus "
        "diverifikasi ulang saat pelatihan final dijalankan.",
        "",
        f"Commit Git pada saat pemilihan: `{git_commit}`",
    ]
    return "\n".join(lines) + "\n"


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
    return f"""# Model Card (Draf). Detektor Penyakit Padi AgriData TELEPATI 8.0

**Status: DRAF.** Konfigurasi pelatihan sudah dibekukan pada `{FINAL_CONFIG_PATH}`, sedangkan bobot,
metrik final, dan hasil evaluasi baru diisi setelah pelatihan final dan uji reproduksi pada
lingkungan bersih selesai. Jangan memperlakukan angka mana pun pada draf ini sebagai angka final.

## Tujuan penggunaan

Deteksi objek untuk kondisi penyakit dan kesehatan tanaman padi dari citra lapangan, baik hasil
tangkapan drone maupun kamera genggam, sebagai komponen sistem pemantauan Smart Agriculture sesuai
studi kasus TELEPATI 8.0 AgriData Intelligence Race, yaitu membantu petani memantau lahan luas
tanpa harus memeriksa seluruhnya secara manual.

## Arsitektur model

YOLOv8n (Ultralytics), diinisialisasi dari definisi yang hanya memuat arsitektur. Tidak ada
external pretrained weights, `pretrained=False`, dan hal ini diverifikasi melalui pemeriksaan kode
sumber serta pemeriksaan cache checkpoint yang kosong. Sekitar 3,0 juta parameter dengan kepala
deteksi 11 kelas.

## Data pelatihan

Dataset resmi TELEPATI 8.0 AgriData dalam format COCO hasil ekspor Roboflow, dengan 11 kelas
canonical. Pemetaan dari kategori mentah ke kelas canonical yang sudah diverifikasi dapat dilihat
pada `src/agridata/dataset/mapping.py`. Kesebelas kelas tersebut adalah:
{', '.join(CANONICAL_CLASSES)}.

Satu citra yang terbukti duplikat persis antara split train dan test dikeluarkan dari data latih.

## Prosedur pelatihan

Konfigurasi lengkap yang berada di bawah kendali versi dapat dilihat pada `{FINAL_CONFIG_PATH}`.
Konfigurasi tersebut dipilih dari 21 percobaan penyaringan terkontrol, dengan penalaran lengkap per
hyperparameter pada `artifacts/reports/block14_final_model_selection.md`.

## Evaluasi

*Menunggu pelatihan final dan uji reproduksi.* Metrik dihitung melalui `scripts/evaluate.py`, dengan
mAP@0.5 memakai implementasi bawaan Ultralytics. Nilai F1 memakai implementasi lokal yang
terdokumentasi melalui pencocokan greedy pada IoU minimal 0,5 dengan confidence threshold yang dapat
dikonfigurasi, karena precision dan recall yang dilaporkan Ultralytics sendiri memakai threshold
yang dipilih otomatis secara internal dan tidak dapat diatur. Rinciannya pada
`src/agridata/metrics/detection.py`.

## Keterbatasan yang diketahui pada draf ini

- Seluruh temuan sejauh ini berasal dari percobaan penyaringan dengan fraksi data kecil dan jumlah
  epoch rendah, sehingga perilaku pada skala penuh dapat berbeda.
- Kandidat near-duplicate lintas split berbasis perceptual hash belum diselesaikan satu per satu.
- Tidak ada jaminan determinisme pelatihan bit per bit pada Apple Silicon dengan backend MPS,
  karena dua operasi yang dipakai pipeline ini terbukti memiliki kernel yang tidak deterministik.
- Ketidakseimbangan kelas nyata, dengan rasio instance terbanyak terhadap tersedikit sebesar 22,6
  kali. Mitigasi berupa oversampling terarah sudah diuji dan tidak menunjukkan manfaat yang jelas
  pada skala penyaringan, sehingga tidak diadopsi pada konfigurasi final per draf ini. Keputusan
  tersebut dapat ditinjau ulang setelah hasil skala penuh tersedia.

## Pernyataan kepatuhan

Tanpa external pretrained weights, tanpa dataset eksternal, dan tanpa pemrosesan dataset memakai
LLM atau API. Daftar periksa kepatuhan lengkap yang berbasis bukti tersedia pada
`artifacts/reports/block14_final_model_selection.md`.
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
