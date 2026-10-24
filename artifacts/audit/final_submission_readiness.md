# Audit Kesiapan Submission

Audit menyeluruh terhadap paket submission, dijalankan ulang pada 24 Oktober
2026 setelah model final diganti dari YOLOv8n ke YOLOv8s-P2. Setiap butir di
bawah berasal dari pemeriksaan yang dijalankan saat audit, bukan dari catatan
sebelumnya. Perintah pemeriksaannya disertakan agar dapat diulang.

## 1. Ringkasan Status

| Area | Status |
|---|---|
| Model final dan bobot | Siap, *checksum* tercatat dan cocok |
| Metrik yang dilaporkan | Siap, satu sumber kebenaran, identik di README, notebook, model card, dan audit |
| Kepatuhan regulasi | Lulus seluruh butir yang dapat diverifikasi otomatis |
| Notebook | Dieksekusi ulang penuh, 0 *error*, 0 sel belum dieksekusi |
| Uji unit | 69 lulus |
| Daftar periksa reproduktibilitas | 9 lulus, 1 peringatan (*working tree* belum dikomit saat audit) |
| GitHub Release bobot | **Belum dipublikasikan**, lihat bagian 9 |

## 2. Model Final

| Field | Nilai |
|---|---|
| Arsitektur | YOLOv8s-P2, dari `yolov8s-p2.yaml`, `pretrained=False` |
| Bobot | `runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt` |
| SHA-256 | `4dc86ac0e53d2849fb1b79f1a68dcb5284ae6f1e8fef27e4416fa54c6b772a9f` |
| Ukuran | 21.754.576 byte |
| Config | `configs/kaggle/yolov8s_p2_640_250ep.yaml` (salinan beranotasi: `configs/final_model_config.yaml`) |
| Pelatihan | Kaggle Notebooks, 2x NVIDIA Tesla T4, DDP dengan AMP, 250 *epoch*, 8,11 jam |
| Pemilihan | Dari empat kandidat skala penuh, hanya berdasarkan *split* valid (`artifacts/candidates/README.md`) |

Pemeriksaan checkpoint, dari proses Python yang bersih:

```bash
YOLO_OFFLINE=1 python -c "from ultralytics import YOLO; m=YOLO('runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt'); print(m.ckpt['train_args']['model'], m.ckpt['train_args']['pretrained'], list(m.names.values()))"
# yolov8s-p2.yaml False ['Bacterial leaf blight', ..., 'Tungro']  (11 kelas, urutan canonical)
```

## 3. Metrik yang Dilaporkan

| Metrik | *Split* valid | *Split* test |
|---|---:|---:|
| **mAP@50** | **70,71%** | 70,65% |
| **F1-Score macro** | **72,33%** | 71,45% |
| mAP@0.5:0.95 | 0,4611 | 0,4830 |

Angka untuk form submission adalah angka *split* valid: mAP@50 **70,71** dan
*F1-Score* **72,33**.

Jalur angka: `scripts/evaluate.py` menulis `artifacts/reports/evaluation_{split}.json`,
lalu `scripts/compute_official_metrics.py` membacanya tanpa menghitung ulang dan
menulis `official_metrics_{split}.json`. README, notebook, model card, dan
`metrics_provenance.md` mengutip angka yang sama.

Kestabilan: evaluasi *split* valid dijalankan tiga kali (satu di CPU, dua di
MPS) dan menghasilkan mAP@50, *F1* macro, jumlah deteksi, dan hitungan analisis
kesalahan yang identik sampai digit terakhir. Rincian pada
`metrics_provenance.md` bagian 7.2.

## 4. Kepatuhan Regulasi

| Aturan | Status | Bukti |
|---|---|---|
| Tanpa *external pretrained weights* | LULUS | Checkpoint final: `model=yolov8s-p2.yaml`, `pretrained=False`. `build_compliant_model` menolak berkas `.pt` sebagai arsitektur. Tidak ada `yolo*.pt` di repository maupun di cache Ultralytics |
| Pengunduhan bobot pretrained oleh pustaka | LULUS, setelah perbaikan | Pengecekan AMP Ultralytics di GPU mengunduh `yolo26n.pt` walaupun `YOLO_OFFLINE` aktif. Ditemukan pada log percobaan pertama, percobaan itu dihentikan, lalu diblokir lewat `scripts/kaggle_site/sitecustomize.py` sebelum seluruh kandidat dilatih. Bobot itu tidak pernah masuk ke model mana pun |
| Tanpa dataset eksternal | LULUS | Satu-satunya data adalah dataset resmi. `scripts/export_kaggle_dataset.py` hanya menyalin `data/prepared` |
| Tanpa pemrosesan dataset dengan LLM/API | LULUS | Tidak ada panggilan API atau pustaka LLM pada `src/` maupun `scripts/` |
| *Split* resmi dipertahankan | LULUS | valid 2.106 dan test 1.059 citra, sama dengan dataset mentah. Train 10.132 dari 10.133, satu citra dikeluarkan karena identik dengan citra test (MD5) |
| *Split* test tidak dipakai untuk penyetelan | LULUS | Pemilihan kandidat dan ensemble hanya memakai *split* valid. Test dievaluasi untuk model terpilih saja, setelah pilihan dikunci |
| 11 kelas canonical | LULUS | `names` pada checkpoint identik dengan `CANONICAL_CLASSES` versi pemetaan 1.0.0 |
| `YOLO_OFFLINE` pada skrip yang memuat Ultralytics | LULUS | Seluruh 9 skrip yang mengimpor Ultralytics menyetel `YOLO_OFFLINE` atau memuatnya lewat `agridata.training` |
| Bobot dipublikasikan lewat GitHub Release atau Git LFS | **BELUM** | Rilis disiapkan, perintah ada di `weights/README.md` |

## 5. Dataset

| *Split* | Citra mentah | Citra siap latih | Anotasi canonical |
|---|---:|---:|---:|
| train | 10.133 | 10.132 | 20.163 |
| valid | 2.106 | 2.106 | 4.888 |
| test | 1.059 | 1.059 | 2.670 |

Dataset mentah tidak pernah diubah. `data/prepared` dibangun ulang identik byte
per byte oleh `scripts/prepare_dataset.py` dengan *seed* 42 (butir 1 daftar
periksa reproduktibilitas).

## 6. Notebook

- Dieksekusi ulang penuh dengan `jupyter nbconvert --execute`: 129 sel,
  0 *error*, 0 sel kode belum dieksekusi.
- Seluruh tabel dan angka pada keluaran sel dibaca dari `artifacts/`, bukan
  diketik ulang.
- Narasi markdown diperiksa terhadap keluaran sel. Pemeriksaan otomatis atas
  angka model lama (0,6401, 0,6383, 0,6246, 0,6272, 0,9717, 0,3153, 0,9809,
  0,2582, `model_100epoch`, `yolov8n.yaml`) tidak menemukan sisa.
- Bagian 13.1 baru memuat empat kandidat skala penuh, dibaca dari
  `artifacts/candidates/`.

## 7. Kode dan Pengujian

- `python -m pytest -q`: 69 lulus.
- `scripts/evaluate.py` dan `scripts/run_error_analysis.py` kini memproses
  prediksi dalam potongan 16 citra. Potongan 500 kehabisan memori MPS untuk
  model yang lebih besar dari YOLOv8n, sehingga verifikasi juri di Mac akan
  gagal tanpa perbaikan ini.
- `scripts/register_final_model.py` menulis metadata, ringkasan pelatihan,
  riwayat pelatihan, dan *checksum* dari satu folder run, dan hanya mengutip
  laporan evaluasi yang dibuat untuk bobot yang sama.

## 8. Repository

Pembersihan menjelang submission dicatat pada `repository_cleanup.md` bagian
24 Oktober. Artefak model sebelumnya diarsipkan utuh pada
`artifacts/archive/100epoch_v8n_run/`, bukan dihapus.

## 9. Item Terbuka

1. **Komit dan push** seluruh perubahan. Saat audit ini, *working tree* belum
   dikomit, sehingga butir 7 daftar periksa reproduktibilitas berstatus
   PERINGATAN dan repository publik masih menampilkan model lama.
2. **Publikasikan GitHub Release** berisi bobot final, `weights/best.pt.sha256`,
   dan `artifacts/reports/final_model_metadata.json`.
3. **Perbarui** tautan rilis pada `weights/README.md` dan *field* `release` pada
   `final_model_metadata.json`.

## 10. Di Luar Jangkauan Verifikasi Otomatis

- Pernyataan orisinalitas bertanda tangan basah (`docs/originality_statement_placeholder.md`).
- Komposisi tim terhadap data pendaftaran.
- Definisi resmi panitia untuk *F1-Score*. Regulasi tidak merinci metode
  *averaging*; angka kami adalah *F1* macro pada titik operasi terbaik dan
  dinyatakan demikian di seluruh dokumen.

## 11. Riwayat Penggantian Model Final

| Model | mAP@50 valid | *F1* macro valid | Arsip |
|---|---:|---:|---|
| YOLOv8n, 20 *epoch* | 56,20% | tidak dihitung | `artifacts/archive/20epoch_run/` |
| YOLOv8n, 50 *epoch* | 64,01% | 63,83% | `artifacts/archive/50epoch_640_run/` |
| YOLOv8n, 100 *epoch* | 66,78% | 68,26% | `artifacts/archive/100epoch_v8n_run/` |
| **YOLOv8s-P2, 250 *epoch*** | **70,71%** | **72,33%** | model final |

Setiap penggantian diputuskan di atas *split* valid, dan *split* test model
final baru dievaluasi setelah pilihan dikunci.

## 12. Kesimpulan

Paket submission siap secara teknis. Yang tersisa adalah tindakan pemilik
repository: komit dan push, publikasi GitHub Release, dan dokumen
administratif.
