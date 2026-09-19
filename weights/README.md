# Bobot Model

**Status: rilis disiapkan, menunggu konfirmasi publikasi.** Berkas *checksum*
(`best.pt.sha256`) dan metadata
(`../artifacts/reports/final_model_metadata.json`) sudah final dan terkomit.
Berkas bobot itu sendiri merupakan biner berukuran besar dan sengaja tidak
dikomit ke Git (lihat `.gitignore`), melainkan didistribusikan sebagai
lampiran GitHub Release. Lihat bagian "Rencana GitHub Release" di bawah untuk
perintah dan daftar aset yang sudah disiapkan.

## Model final saat ini

| Field | Nilai |
|---|---|
| Berkas | `runs/detect/final/final_model/weights/best.pt` |
| Format | *Checkpoint* PyTorch (`.pt`) |
| Ukuran | 6.253.994 byte (6,3 MB) |
| SHA-256 | `9d74fffdd977a7bb6749bc828fe908278c5d3eaa24c3cfdbbe5a560d41f5d308` |
| Arsitektur | YOLOv8n (Ultralytics), dibangun dari `yolov8n.yaml`, `pretrained=False` |
| Konfigurasi pelatihan | [`configs/final_model_config.yaml`](../configs/final_model_config.yaml), 50 *epoch* |
| Ringkasan pelatihan | [`artifacts/reports/block15_final_training_summary.json`](../artifacts/reports/block15_final_training_summary.json) |
| *Commit* Git saat pelatihan | `28668899fb000cee3a2a8386ac65ddeba2d04d02` |
| Hasil | mAP@0.5 = 0,6277 dan mAP@0.5:0.95 = 0,3905 |

Model 20 *epoch* sebelumnya (mAP@0.5 = 0,5620) digantikan atas permintaan
pengguna untuk memperpanjang pelatihan. Seluruh hasilnya tetap diarsipkan
pada [`artifacts/archive/20epoch_run/`](../artifacts/archive/20epoch_run/)
dan tidak dihapus.

Berkas ini tidak dikomit ke Git karena pola `*.pt` dan `runs/` dikecualikan
pada `.gitignore`, konsisten dengan arahan untuk tidak menyimpan biner besar
secara langsung di dalam repository. Saat ini berkas tersedia secara lokal
pada *path* di atas, hasil menjalankan `scripts/run_final_training.py` dengan
konfigurasi beku.

## Verifikasi

Pemuatan dan inferensi dari proses yang benar-benar bersih sudah diverifikasi.
Lihat *field* `clean_process_load_validation` pada
[`artifacts/reports/block15_final_training_summary.json`](../artifacts/reports/block15_final_training_summary.json)
serta uji reproduksi lingkungan bersih pada
[`artifacts/audit/block16_clean_reproduction_test.md`](../artifacts/audit/block16_clean_reproduction_test.md).

Untuk memverifikasi *checksum* salinan Anda sendiri:

```bash
shasum -a 256 runs/detect/final/final_model/weights/best.pt
```

Hasilnya harus sama persis dengan nilai SHA-256 pada tabel di atas.

## Rencana GitHub Release

Regulasi mensyaratkan bobot model dipublikasikan melalui GitHub Release atau
Git LFS dengan tautan langsung, bukan tautan penyimpanan awan pribadi.
Mengingat ukuran berkas hanya 6,3 MB, jauh di bawah batas per berkas GitHub,
lampiran GitHub Release dipilih karena lebih sederhana dan sama patuhnya
dibanding Git LFS.

Rilis sudah disiapkan tetapi **belum dipublikasikan**, karena publikasi
merupakan tindakan publik yang sulit dibatalkan dan ditunda sampai ada
konfirmasi eksplisit. Perintah yang sudah disiapkan:

```bash
gh release create v1.0.0-final-model \
  runs/detect/final/final_model/weights/best.pt \
  weights/best.pt.sha256 \
  artifacts/reports/final_model_metadata.json \
  --title "Final Model v1.0.0: YOLOv8n Rice Disease Detector" \
  --notes-file <berkas catatan rilis>
```

Setelah dipublikasikan, bagian ini akan diperbarui dengan tautan aset
langsung, dan *field* `release` pada
`artifacts/reports/final_model_metadata.json` akan disetel menjadi
`published: true` beserta metode dan URL-nya.
