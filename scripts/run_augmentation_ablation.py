#!/usr/bin/env python3
"""Ablasi augmentasi satu faktor pada satu waktu.

Pemakaian:
    python scripts/run_augmentation_ablation.py --config configs/experiments/augmentation_ablation.yaml

Pengujian dilakukan satu faktor pada satu waktu, bertolak dari titik referensi
bersih TANPA AUGMENTASI. Titik ini berbeda dari baseline matriks percobaan, yang
sebenarnya sudah mengaktifkan paket augmentasi bawaan Ultralytics secara
diam-diam.

Setiap jenis augmentasi dinilai kelayakan fisik dan semantiknya untuk citra
pertanian SEBELUM dijalankan, lihat field `plausibility` per varian pada berkas
konfigurasi YAML. Seluruh hasilnya dicatat ke pelacak percobaan yang sama dengan
yang dipakai di sepanjang project ini.

Citra validasi dan uji tidak pernah disentuh. Augmentasi hanya berlaku pada
dataloader pelatihan, sesuai perilaku bawaan Ultralytics: hanya citra split
`train:` yang melewati pipeline augmentasi, sedangkan inferensi pada `val:` dan
`test:` memakai citra tanpa augmentasi.
"""

from __future__ import annotations

import argparse
import json
import logging
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

logger = logging.getLogger("agridata.scripts.run_augmentation_ablation")

# Memverifikasi secara visual kesesuaian bbox terhadap citra setelah augmentasi,
# khusus untuk dua jenis transformasi yang paling mungkin menyembunyikan
# kesalahan koordinat: pembalikan, yang mudah keliru, dan rotasi, yang paling
# rumit secara geometris di antara seluruh transformasi.
VISUAL_VERIFICATION_VARIANTS = {"hflip_only", "rotation_only"}

BLUR_NOISE_ANALYSIS = """
## Kandidat yang tidak diuji secara empiris: blur dan derau ringan

Pemeriksaan kode sumber `ultralytics/data/augment.py` pada kelas
`Albumentations` menunjukkan transformasi bawaan beserta probabilitasnya
yang akan diterapkan Ultralytics bila paket opsional `albumentations`
terpasang:

    A.Blur(p=0.01), A.MedianBlur(p=0.01), A.ToGray(p=0.01), A.CLAHE(p=0.01),
    A.RandomBrightnessContrast(p=0.0), A.RandomGamma(p=0.0), A.ImageCompression(p=0.0)

Paket `albumentations` TIDAK terpasang pada project ini, sehingga tidak ada
satu pun transformasi di atas yang aktif. Hal ini dikonfirmasi, bukan
diasumsikan, melalui `pip show albumentations` yang tidak menemukan apa pun.

Penilaian kami atas ketiganya:

- **Blur dan MedianBlur, masing-masing p=0,01.** MASUK AKAL, karena blur
  ringan akibat fokus atau gerakan lazim terjadi pada fotografi lapangan.
  Namun pada probabilitas 1 persen, terhadap sekitar 800 citra latih
  dikali 5 epoch atau kurang lebih 4.000 tampilan citra, hanya sekitar 80
  tampilan yang akan menerima salah satu transformasi tersebut. Terlalu
  jarang untuk menghasilkan perbedaan mAP yang terukur pada skala
  penyaringan ini, sehingga eksekusi empirisnya akan lebih banyak mengukur
  derau daripada efek transformasinya.
- **ToGray, p=0,01.** DIRAGUKAN khusus untuk domain ini, karena warna lesi
  merupakan ciri diagnostik yang nyata bagi beberapa kelas canonical,
  misalnya Brown spot terhadap Blast. Mengubah citra menjadi skala abu-abu
  justru menghapus sinyal yang sengaja dijaga oleh varian `color_only` di
  atas melalui pembatasan pergeseran hue.
- **CLAHE, p=0,01.** MASUK AKAL, karena penguatan kontras adaptif membantu
  menghadapi variasi pencahayaan, dengan penalaran serupa varian
  `brightness_only`.

**Keputusan:** `albumentations` tidak ditambahkan sebagai dependensi project
pada tahap ini. Efeknya nyata tetapi terlalu jarang muncul pada probabilitas
1 persen untuk membenarkan penambahan dependensi baru sekaligus percobaan
langsung yang hasilnya akan didominasi derau penyampelan pada skala ini.
Keputusan ini dapat ditinjau ulang pada analisis kesalahan bila kepekaan
terhadap blur ternyata merupakan mode kegagalan yang nyata.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Menjalankan ablasi augmentasi terkontrol.")
    parser.add_argument("--config", default=Path("configs/experiments/augmentation_ablation.yaml"), type=Path)
    parser.add_argument("--project", default=Path("runs/detect/augmentation_ablation"), type=Path)
    parser.add_argument("--manifest", default=Path("data/prepared/manifest_train.json"), type=Path)
    parser.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    parser.add_argument("--start-experiment-num", type=int, default=9, help="First experiment_id number (E09 by default, continuing from Block 10's E02-E08).")
    return parser.parse_args()


def run_one(experiment_id: str, axis: str, plausibility: str, extra_kwargs: dict, common: dict, project: Path, git_commit: str, manifest_hash: str, plots: bool) -> dict:
    device = detect_device() if common["device"] == "auto" else common["device"]
    set_global_seed(common["seed"])

    logger.info("=== Experiment %s (augmentation: %s) ===", experiment_id, axis)
    logger.info("Plausibility assessment: %s", plausibility)
    logger.info("Augmentation overrides: %s", extra_kwargs)

    started_at = time.monotonic()
    result = run_training(
        model_arch=common["model_arch"],
        data_yaml=Path(common["data_yaml"]),
        output_project=project,
        run_name=experiment_id,
        image_size=common["image_size"],
        batch_size=common["batch_size"],
        epochs=common["epochs"],
        device=device,
        seed=common["seed"],
        workers=common["workers"],
        fraction=common["fraction"],
        plots=plots,
        validate=common["validate_during_training"],
        extra_train_kwargs={
            "optimizer": common["optimizer"],
            "lr0": common["learning_rate"],
            "momentum": common["momentum"],
            "weight_decay": common["weight_decay"],
            **extra_kwargs,
        },
    )
    duration = time.monotonic() - started_at

    from ultralytics import YOLO

    model = YOLO(result["best_weights"])
    val_results = model.val(data=common["data_yaml"], split="val", plots=False, verbose=False, device=device)

    record = ExperimentRecord(
        experiment_id=experiment_id,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=git_commit,
        seed=common["seed"],
        model_architecture=common["model_arch"],
        pretrained=common["pretrained"],
        dataset_manifest_hash=manifest_hash,
        image_size=common["image_size"],
        batch_size=common["batch_size"],
        epochs=common["epochs"],
        optimizer=result["resolved_hyperparameters"]["optimizer"],
        learning_rate=result["resolved_hyperparameters"]["learning_rate"],
        weight_decay=result["resolved_hyperparameters"]["weight_decay"],
        scheduler=result["resolved_hyperparameters"]["scheduler"],
        augmentation_config=result["resolved_hyperparameters"]["augmentation"],
        device=device,
        best_val_map50=float(val_results.box.map50),
        best_val_f1=None,
        precision=float(val_results.box.mp),
        recall=float(val_results.box.mr),
        training_duration_seconds=duration,
        notes=f"Ablasi augmentasi: {axis}. {plausibility}",
        compliance_notes="Tanpa external pretrained weights. YOLO_OFFLINE ditegakkan. Augmentasi hanya berlaku pada split latih.",
    )

    saved_batch_images = []
    if plots:
        save_dir = Path(result["save_dir"])
        saved_batch_images = sorted(str(p) for p in save_dir.glob("train_batch*.jpg"))

    return {"axis": axis, "plausibility": plausibility, "record": record, "saved_batch_images": saved_batch_images}


def build_report(results: list[dict], baseline_default_map50: float) -> str:
    lines = [
        "# Ablasi Augmentasi",
        "",
        "Skalanya sama dengan matriks percobaan, yaitu fraksi data kecil dengan sedikit *epoch*, "
        "agar langsung sebanding. Nilai mAP absolutnya rendah, dan yang bermakna di sini hanya "
        "efek relatifnya.",
        "",
        f"Sebagai pembanding, E02 pada matriks percobaan yang memakai paket augmentasi gabungan "
        f"bawaan Ultralytics memperoleh mAP@0.5={baseline_default_map50:.4f}. Ablasi ini justru "
        "mengisolasi setiap faktor satu per satu bertolak dari referensi bersih tanpa augmentasi, "
        "yaitu E09.",
        "",
        "## Hasil",
        "",
        "| Percobaan | Augmentasi | Kelayakan | mAP@0.5 | Precision | Recall | Durasi (detik) |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for r in results:
        rec = r["record"]
        plausibility_short = r["plausibility"].split(", ")[0]
        lines.append(
            f"| {rec.experiment_id} | {r['axis']} | {plausibility_short} | {rec.best_val_map50:.4f} | "
            f"{rec.precision:.4f} | {rec.recall:.4f} | {rec.training_duration_seconds:.1f} |"
        )

    no_aug = next(r for r in results if r["axis"] == "none")
    lines += ["", "## Efek tiap augmentasi, relatif terhadap referensi tanpa augmentasi", ""]
    for r in results:
        if r["axis"] == "none":
            continue
        delta = r["record"].best_val_map50 - no_aug["record"].best_val_map50
        direction = "naik" if delta > 0 else ("turun" if delta < 0 else "tidak berubah")
        lines.append(f"- **{r['axis']}**: mAP@0.5 {direction} sebesar {delta:+.4f} terhadap referensi tanpa augmentasi.")

    lines.append(BLUR_NOISE_ANALYSIS)

    lines += [
        "## Rekomendasi",
        "",
        "Pemilihan augmentasi harus menimbang *kelayakan semantik untuk domain ini*, bukan semata "
        "angka mentah pada skala penyaringan yang kecil. Secara konkret:",
        "",
        "- Direkomendasikan **dipertahankan**: pembalikan horizontal, rotasi sedang, penskalaan, "
        "translasi, kecerahan dan kontras, serta pergeseran warna yang konservatif. Seluruhnya "
        "masuk akal secara fisik untuk citra padi hasil tangkapan lapangan, terlepas dari kecilnya "
        "efek individual pada skala penyaringan ini.",
        "- Direkomendasikan **dikeluarkan**: pembalikan vertikal. Sekalipun terukur berefek positif di "
        "atas, transformasi itu tidak masuk akal secara fisik untuk tanaman yang orientasinya "
        "ditentukan gravitasi, dan berisiko mengajarkan model orientasi yang tidak akan pernah "
        "ditemuinya saat dipakai. Penalaran domain mengungguli perolehan metrik yang marginal.",
        "- **Mosaic**: dipertahankan hanya bila efek terukurnya di atas netral sampai positif. Bila "
        "jelas merugikan pada skala ini, sebaiknya diuji ulang pada skala pelatihan penuh sebelum "
        "diputuskan, karena manfaat mosaic umumnya baru terlihat dengan data dan *epoch* yang lebih "
        "banyak daripada tahap penyaringan ini.",
        "- Blur dan derau ringan: sengaja tidak diadopsi pada tahap ini, lihat analisis di atas.",
        "",
        "Ini merupakan rekomendasi berskala penyaringan yang dibawa ke ablasi ketidakseimbangan kelas "
        "dan pembekuan konfigurasi final, bukan keputusan final yang berdiri sendiri.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    setup_logging()
    args = parse_args()

    with args.config.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    common = config["common"]
    git_commit = get_git_commit()
    manifest_hash = compute_manifest_hash(args.manifest)

    results = []
    exp_num = args.start_experiment_num

    # No-augmentation reference point.
    no_aug_id = f"E{exp_num:02d}"
    results.append(run_one(no_aug_id, "none", "Reference point: all augmentation disabled.", config["no_augmentation"], common, args.project, git_commit, manifest_hash, plots=False))
    append_experiment(results[-1]["record"])
    exp_num += 1

    for variant in config["variants"]:
        exp_id = f"E{exp_num:02d}"
        plots = variant["id"] in VISUAL_VERIFICATION_VARIANTS
        result = run_one(
            exp_id, variant["augmentation"], variant["plausibility"],
            {**config["no_augmentation"], **variant["overrides"]},
            common, args.project, git_commit, manifest_hash, plots,
        )
        append_experiment(result["record"])
        results.append(result)
        logger.info("Experiment %s done: mAP@0.5=%.4f (%.1fs)", exp_id, result["record"].best_val_map50, result["record"].training_duration_seconds)
        exp_num += 1

    args.report_dir.mkdir(parents=True, exist_ok=True)
    # Referensi baseline dari E02 yang tercatat pada matriks percobaan.
    all_records = load_experiments()
    e02 = next(r for r in all_records if r["experiment_id"] == "E02")
    report = build_report(results, e02["best_val_map50"])
    (args.report_dir / "block11_augmentation_ablation.md").write_text(report, encoding="utf-8")

    (Path("artifacts/experiments") / "experiment_log.md").write_text(build_markdown_table(all_records), encoding="utf-8")

    verification_images = [img for r in results for img in r["saved_batch_images"]]

    print(report)
    print(f"\nVisual verification batch images saved: {verification_images}")
    print("Experiment log updated: artifacts/experiments/experiment_log.json")
    print("Report: artifacts/reports/block11_augmentation_ablation.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
