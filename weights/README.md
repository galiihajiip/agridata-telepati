# Bobot Model

**Status: dipublikasikan** pada GitHub Release
[`v1.0.0-final-model`](https://github.com/galiihajiip/agridata-telepati/releases/tag/v1.0.0-final-model).

Unduhan langsung: <https://github.com/galiihajiip/agridata-telepati/releases/download/v1.0.0-final-model/best.pt>

```bash
mkdir -p runs/detect/final/yolov8s_p2_640_250ep/weights
curl -L -o runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt \
  https://github.com/galiihajiip/agridata-telepati/releases/download/v1.0.0-final-model/best.pt
shasum -a 256 -c weights/best.pt.sha256
```

Berkas bobot merupakan biner dan sengaja tidak dikomit ke Git (lihat
`.gitignore`). *Checksum* (`best.pt.sha256`) dan metadata
(`../artifacts/reports/final_model_metadata.json`) ditulis oleh
`scripts/register_final_model.py` langsung dari bobot dan laporan evaluasinya,
dan salinan identiknya ikut dilampirkan pada Release.

## Model final

| Field | Nilai |
|---|---|
| Berkas | `runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt` |
| Format | *Checkpoint* PyTorch (`.pt`) |
| Ukuran | 21.754.576 byte (21,8 MB) |
| SHA-256 | `4dc86ac0e53d2849fb1b79f1a68dcb5284ae6f1e8fef27e4416fa54c6b772a9f` |
| Arsitektur | YOLOv8s-P2 (Ultralytics), dibangun dari `yolov8s-p2.yaml`, `pretrained=False` |
| Konfigurasi pelatihan | [`configs/kaggle/yolov8s_p2_640_250ep.yaml`](../configs/kaggle/yolov8s_p2_640_250ep.yaml), 250 *epoch* |
| Perangkat pelatihan | Kaggle Notebooks, 2x NVIDIA Tesla T4 (DDP), 8,11 jam |
| Ringkasan pelatihan | [`artifacts/reports/block15_final_training_summary.json`](../artifacts/reports/block15_final_training_summary.json) |
| *Hash* manifest dataset | `cf81abe0fbdae274...` |
| mAP@0.5 (valid) | 0,7071 |
| *F1-Score* macro (valid) | 0,7233 |

Angka *split* test sengaja belum dicantumkan: *split* test dievaluasi satu kali
setelah pilihan model dibekukan, bukan selama pemilihan.

Nama direktori `yolov8s_p2_640_250ep` kami ambil dari nama berkas
konfigurasinya, sehingga arsitektur, resolusi, dan anggaran *epoch* terbaca
langsung dari path.

## Model yang digantikan

Seluruh model sebelumnya kami arsipkan utuh dan tidak kami hapus, supaya jejak
keputusannya tetap dapat diperiksa:

| Model | mAP@0.5 valid | *F1* macro valid | Arsip |
|---|---:|---:|---|
| YOLOv8n, 20 *epoch* | 0,5620 | tidak dihitung | [`artifacts/archive/20epoch_run/`](../artifacts/archive/20epoch_run/) |
| YOLOv8n, 50 *epoch* | 0,6401 | 0,6383 | [`artifacts/archive/50epoch_640_run/`](../artifacts/archive/50epoch_640_run/) |
| YOLOv8n, 100 *epoch* | 0,6678 | 0,6826 | [`artifacts/archive/100epoch_v8n_run/`](../artifacts/archive/100epoch_v8n_run/) |

Alasan penggantian terakhir: kurva model YOLOv8n 100 *epoch* belum konvergen,
dan satu kali pelatihan saja memakan 20,84 jam di Apple Silicon. Kami lalu
melatih empat kandidat berkapasitas lebih besar dari nol di GPU Kaggle dan
Colab, lalu memilih di antaranya hanya berdasarkan *split* valid. Prosesnya
tercatat pada [`docs/kaggle_training.md`](../docs/kaggle_training.md).

## Verifikasi

Pemuatan dan inferensi dari proses Python yang benar-benar bersih sudah
diverifikasi. Lihat *field* `clean_process_load_validation` pada
[`artifacts/reports/block15_final_training_summary.json`](../artifacts/reports/block15_final_training_summary.json).

Untuk memverifikasi *checksum* salinan Anda sendiri:

```bash
shasum -a 256 runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt
# atau, dari berkas checksum yang disertakan:
shasum -a 256 -c weights/best.pt.sha256
```

Hasilnya harus sama persis dengan nilai SHA-256 pada tabel di atas.

## GitHub Release

Regulasi mensyaratkan bobot model dipublikasikan melalui GitHub Release atau
Git LFS dengan tautan unduhan langsung. Ukuran berkasnya 21,8 MB, jauh di bawah
batas per berkas GitHub, sehingga kami memilih lampiran GitHub Release.

| Aset pada Release | Isi |
|---|---|
| `best.pt` | Bobot final, 21.754.576 byte |
| `best.pt.sha256` | *Checksum* SHA-256 |
| `final_model_metadata.json` | Metadata model, identik dengan berkas di repository |

Setelah publikasi, `best.pt` kami unduh ulang dari Release dan kami bandingkan
dengan bobot yang kami evaluasi: identik byte per byte, dengan SHA-256
`4dc86ac0e53d2849fb1b79f1a68dcb5284ae6f1e8fef27e4416fa54c6b772a9f`.

*Field* `release` pada `final_model_metadata.json` sengaja tidak kami ubah
setelah publikasi, agar salinan di repository tetap identik dengan salinan yang
dilampirkan pada Release. Tautan resmi Release adalah yang tercantum pada
dokumen ini.
