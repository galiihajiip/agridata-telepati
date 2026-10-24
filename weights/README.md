# Bobot Model

**Status: rilis sudah disiapkan, menunggu publikasi.** Berkas *checksum*
(`best.pt.sha256`) dan metadata
(`../artifacts/reports/final_model_metadata.json`) ditulis oleh
`scripts/register_final_model.py` langsung dari bobot dan laporan evaluasinya.
Berkas bobot itu sendiri merupakan biner dan sengaja tidak dikomit ke Git
(lihat `.gitignore`), melainkan didistribusikan sebagai lampiran GitHub
Release. Perintah dan daftar asetnya ada di bagian "Rencana GitHub Release" di
bawah.

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

## Rencana GitHub Release

Regulasi mensyaratkan bobot model dipublikasikan melalui GitHub Release atau
Git LFS dengan tautan unduhan langsung, bukan tautan penyimpanan awan pribadi.
Ukuran berkasnya 21,8 MB, jauh di bawah batas per berkas GitHub, sehingga kami
memilih lampiran GitHub Release: lebih sederhana dan sama patuhnya dibanding
Git LFS.

Rilisnya sudah siap tetapi **belum dipublikasikan**, karena publikasi
merupakan tindakan publik yang sulit dibatalkan dan kami tunda sampai ada
konfirmasi eksplisit dari pemilik repository. Perintahnya:

```bash
gh release create v2.0.0-final-model \
  runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt \
  weights/best.pt.sha256 \
  artifacts/reports/final_model_metadata.json \
  --title "Model Final v2.0.0: Detektor Penyakit Padi YOLOv8s-P2" \
  --notes-file <berkas catatan rilis>
```

Setelah rilis terbit, bagian ini perlu diperbarui dengan tautan aset langsung,
dan *field* `release` pada `artifacts/reports/final_model_metadata.json`
disetel menjadi `published: true` beserta metode dan URL-nya.
