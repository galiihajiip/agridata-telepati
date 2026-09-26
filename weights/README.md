# Bobot Model

**Status: rilis sudah disiapkan, menunggu publikasi.** Berkas *checksum*
(`best.pt.sha256`) dan metadata
(`../artifacts/reports/final_model_metadata.json`) sudah final. Berkas bobot
itu sendiri merupakan biner dan sengaja tidak dikomit ke Git (lihat
`.gitignore`), melainkan didistribusikan sebagai lampiran GitHub Release.
Perintah dan daftar asetnya ada di bagian "Rencana GitHub Release" di bawah.

## Model final

| Field | Nilai |
|---|---|
| Berkas | `runs/detect/final/model_100epoch/weights/best.pt` |
| Format | *Checkpoint* PyTorch (`.pt`) |
| Ukuran | 6.260.394 byte (6,3 MB) |
| SHA-256 | `c631a363ab580ca614c52b51eaaf798e31c44a3ba92f2aa05efcfe27f5a86965` |
| Arsitektur | YOLOv8n (Ultralytics), dibangun dari `yolov8n.yaml`, `pretrained=False` |
| Konfigurasi pelatihan | [`configs/final_model_config.yaml`](../configs/final_model_config.yaml), 100 *epoch* |
| Ringkasan pelatihan | [`artifacts/reports/block15_final_training_summary.json`](../artifacts/reports/block15_final_training_summary.json) |
| *Commit* Git saat pelatihan | `38754ce334149e7eeb633edb8d9d81820bad3b13` |
| *Hash* manifest dataset | `cf81abe0fbdae274...` |
| mAP@0.5 | 0,6678 (valid) dan 0,6596 (test) |
| *F1-Score* macro | 0,6826 (valid) dan 0,6641 (test) |

Nama direktori `model_100epoch` kami pertahankan apa adanya karena mencerminkan
anggaran *epoch* yang menghasilkannya, dan kami menilai itu lebih jujur
daripada menamainya ulang menjadi sesuatu yang generik.

## Model yang digantikan

Dua model sebelumnya kami arsipkan utuh dan tidak kami hapus, supaya jejak
keputusannya tetap dapat diperiksa:

| Model | mAP@0.5 valid | *F1* macro valid | Arsip |
|---|---:|---:|---|
| 20 *epoch* | 0,5620 | tidak dihitung | [`artifacts/archive/20epoch_run/`](../artifacts/archive/20epoch_run/) |
| 50 *epoch* | 0,6401 | 0,6383 | [`artifacts/archive/50epoch_640_run/`](../artifacts/archive/50epoch_640_run/) |

Alasan penggantian terakhir kami catat pada
[`artifacts/audit/metrics_provenance.md`](../artifacts/audit/metrics_provenance.md):
kurva pelatihan model 50 *epoch* menunjukkan model belum konvergen, dan
perpanjangan anggaran ke 100 *epoch* terbukti menaikkan mAP@0.5 sebesar 0,0277
pada *split* valid sekaligus 0,0350 pada *split* test.

## Verifikasi

Pemuatan dan inferensi dari proses yang benar-benar bersih sudah diverifikasi.
Lihat *field* `clean_process_load_validation` pada
[`artifacts/reports/block15_final_training_summary.json`](../artifacts/reports/block15_final_training_summary.json)
serta uji reproduksi lingkungan bersih pada
[`artifacts/audit/block16_clean_reproduction_test.md`](../artifacts/audit/block16_clean_reproduction_test.md).

Untuk memverifikasi *checksum* salinan Anda sendiri:

```bash
shasum -a 256 runs/detect/final/model_100epoch/weights/best.pt
# atau, dari berkas checksum yang disertakan:
shasum -a 256 -c weights/best.pt.sha256
```

Hasilnya harus sama persis dengan nilai SHA-256 pada tabel di atas.

## Rencana GitHub Release

Regulasi mensyaratkan bobot model dipublikasikan melalui GitHub Release atau
Git LFS dengan tautan unduhan langsung, bukan tautan penyimpanan awan pribadi.
Karena ukuran berkasnya hanya 6,3 MB, jauh di bawah batas per berkas GitHub,
kami memilih lampiran GitHub Release: lebih sederhana dan sama patuhnya
dibanding Git LFS.

Rilisnya sudah siap tetapi **belum dipublikasikan**, karena publikasi
merupakan tindakan publik yang sulit dibatalkan dan kami tunda sampai ada
konfirmasi eksplisit dari pemilik repository. Perintahnya:

```bash
gh release create v1.0.0-final-model \
  runs/detect/final/model_100epoch/weights/best.pt \
  weights/best.pt.sha256 \
  artifacts/reports/final_model_metadata.json \
  --title "Model Final v1.0.0: Detektor Penyakit Padi YOLOv8n" \
  --notes-file <berkas catatan rilis>
```

Setelah rilis terbit, bagian ini perlu diperbarui dengan tautan aset langsung,
dan *field* `release` pada `artifacts/reports/final_model_metadata.json`
disetel menjadi `published: true` beserta metode dan URL-nya.
