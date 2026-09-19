# TELEPATI 8.0 - AgriData Intelligence Race

Deteksi penyakit tanaman padi berbasis *object detection* untuk 11 kelas
canonical, dibangun dari dataset resmi TELEPATI 8.0.

## Ringkasan

| Item | Nilai |
|---|---|
| Tugas | *Object detection*, 11 kelas canonical |
| Arsitektur | YOLOv8n, dilatih dari nol tanpa *external pretrained weights* |
| mAP@0.5 (split valid) | **0,6277** |
| mAP@0.5:0.95 (split valid) | 0,3905 |
| *Precision* / *recall* (titik *best-F1* internal Ultralytics) | 0,6406 / 0,6237 |
| *F1* lokal pada *confidence* 0,25 | 0,33 (rentang teramati 0,22 sampai 0,42) |
| Ukuran model | 6,3 MB |
| Waktu pelatihan | 7,34 jam, 50 *epoch*, Apple Silicon MPS |
| Dokumen utama | [`notebooks/final_agriData_telepati8.ipynb`](notebooks/final_agriData_telepati8.ipynb) |

Notebook final merupakan dokumen utama submission. Notebook tersebut memuat
alur lengkap dari audit dataset sampai analisis kesalahan, ditulis sebagai
laporan penelitian, bukan sekadar kumpulan sel kode.

## Tujuan

Membangun model deteksi penyakit tanaman padi yang:

1. mematuhi seluruh batasan kompetisi, terutama larangan penggunaan
   *external pretrained weights*, dataset eksternal, dan pemrosesan dataset
   menggunakan LLM atau API;
2. dapat direproduksi dan diaudit ulang oleh pihak ketiga;
3. dilaporkan secara jujur, termasuk keterbatasan yang tidak menguntungkan.

## Dataset

Dataset resmi TELEPATI 8.0 dalam format COCO, dengan pembagian *split* resmi
yang dipertahankan apa adanya. Tidak ada penggabungan maupun pengacakan ulang
antar *split*.

| Split | Citra | Anotasi canonical | Rata-rata anotasi per citra |
|---|---:|---:|---:|
| train | 10.133 | 20.163 | 1,99 |
| valid | 2.106 | 4.888 | 2,32 |
| test | 1.059 | 2.670 | 2,52 |
| **Total** | **13.298** | **27.721** | |

Dataset mentah tidak pernah diubah. Seluruh penyiapan data menulis ke
direktori terpisah menggunakan *symlink*, tanpa menyalin byte citra.

## 11 Kelas Canonical

Dataset mentah memuat 21 kategori yang kemudian dipetakan menjadi 11 kelas
canonical. Selisih tersebut berasal dari variasi penulisan label dan tiga
kategori *supercategory* yang bukan target deteksi, yaitu `Leaf-blight`,
`Rice-Leaf-Diseasee`, dan `paddy`.

| ID model | Kelas canonical | Instance (train) | AP@0.5 (valid) |
|---:|---|---:|---:|
| 0 | Bacterial leaf blight | 476 | 0,3887 |
| 1 | Bacterial panicle blight | 528 | 0,6216 |
| 2 | Blast | 4.149 | 0,4855 |
| 3 | Brown spot | 5.010 | 0,2909 |
| 4 | False smut | 845 | 0,9436 |
| 5 | Healthy | 2.373 | 0,8712 |
| 6 | Leaf roller | 818 | 0,8734 |
| 7 | Leaf scald | 1.438 | 0,3880 |
| 8 | Narrow brown | 222 | 0,9631 |
| 9 | Sheath blight | 1.762 | 0,4804 |
| 10 | Tungro | 2.540 | 0,5980 |

Pemetaan gagal secara keras bila ditemukan kategori mentah yang tidak
dikenali, sehingga perubahan dataset tidak akan lolos diam-diam. Versi tabel
pemetaan dicatat sebagai `MAPPING_VERSION`.

## Metodologi

```
Dataset mentah
  -> Audit forensik dataset
  -> Pemetaan 11 kelas canonical
  -> Pemeriksaan kebocoran antar split
  -> Penyiapan data format YOLO
  -> 21 eksperimen terkontrol
  -> Pelatihan model final
  -> Evaluasi dan analisis kesalahan
  -> Audit reproducibility
```

Setiap tahap memiliki skrip tersendiri pada `scripts/` dan menghasilkan
laporan terstruktur pada `artifacts/`, sehingga setiap klaim dapat
ditelusuri sampai ke berkas hasil eksekusi.

## Profiling Dataset

Temuan utama dari `scripts/profile_dataset.py`:

| Temuan | train | valid | test |
|---|---:|---:|---:|
| Rasio ketidakseimbangan kelas | 22,6x | 32,5x | 31,1x |
| Porsi objek kecil (kurang dari 1 persen luas citra) | 38,1% | 43,3% | 46,8% |
| Citra tanpa anotasi | 59 | 13 | 5 |

Audit *missingness* khusus deteksi objek menghasilkan nol temuan pada
seluruh pemeriksaan integritas referensi, yaitu berkas citra hilang, berkas
tanpa *record* JSON, anotasi yatim, *bounding box* kosong atau tidak valid,
dan metadata dimensi citra yang hilang.

Satu pasangan citra identik ditemukan antara *split* latih dan uji. Entri
pada sisi `train` dikeluarkan dari *manifest* data siap latih, sedangkan
dataset mentah dan *split* lain tidak diubah.

## Model

| Parameter | Nilai |
|---|---|
| Arsitektur | `yolov8n.yaml`, dibangun dari definisi arsitektur saja |
| *Pretrained* | `False`, ditegakkan pada tingkat kode |
| Ukuran citra masukan | 640 |
| *Batch size* | 16 |
| *Optimizer* | AdamW |
| *Learning rate* | 0,001 |
| *Weight decay* | 0,0005 |
| *Scheduler* | linear |
| *Epoch* | 50 |
| *Patience* | 8 |
| *Seed* | 42 |
| Perangkat | MPS (Apple Silicon), dengan *fallback* CPU |

Fungsi `build_compliant_model` menolak berjalan bila diberi `pretrained=True`
atau bila argumen arsitektur menyerupai berkas *checkpoint*. Variabel
`YOLO_OFFLINE=1` diaktifkan sebelum `ultralytics` diimpor, sehingga setiap
upaya pengunduhan gagal secara keras.

## Eksperimen

21 percobaan terkontrol tercatat pada
[`artifacts/experiments/experiment_log.json`](artifacts/experiments/experiment_log.json),
lengkap dengan *seed*, *hyperparameter*, *hash manifest* dataset, dan
*commit* Git.

Pengujian satu faktor pada satu waktu terhadap *baseline* E02:

| Faktor yang diubah | Selisih mAP@0.5 | Arah |
|---|---:|---|
| *Epoch* 5 menjadi 10 | +0,0117 | membantu |
| Ukuran citra 320 menjadi 640 | +0,0023 | membantu |
| Kekuatan augmentasi diubah | -0,0011 | menurunkan |
| *Batch* 16 menjadi 32 | -0,0013 | menurunkan |
| *Optimizer* AdamW menjadi SGD | -0,0015 | menurunkan |
| *Learning rate* 0,001 menjadi 0,0001 | -0,0016 | menurunkan |

Catatan penting: seluruh angka percobaan berada pada skala penyaringan,
yaitu sebagian data latih dengan *epoch* sedikit, sehingga **tidak
sebanding** dengan hasil model final.

Satu keputusan tidak mengikuti selisih metrik. Augmentasi tetap diaktifkan
meskipun percobaan tanpa augmentasi sedikit unggul pada skala penyaringan,
dengan alasan arah tren dan penalaran domain. Keputusan ini ditandai secara
eksplisit sebagai penilaian pada notebook Bagian 12.

## Hasil

Evaluasi pada *split* validasi, bobot
`runs/detect/final/final_model/weights/best.pt`:

| Metrik | Nilai |
|---|---:|
| mAP@0.5 | **0,6277** |
| mAP@0.5:0.95 | 0,3905 |
| *Precision* (titik *best-F1* internal Ultralytics) | 0,6406 |
| *Recall* (titik *best-F1* internal Ultralytics) | 0,6237 |
| *F1* lokal pada *confidence* 0,25 | 0,3326 |

Sensitivitas terhadap *confidence threshold*, dihitung ulang dari prediksi
tersimpan sehingga bersifat deterministik:

| Threshold | Precision | Recall | F1 lokal |
|---:|---:|---:|---:|
| 0,05 | 0,2339 | 0,3331 | 0,2748 |
| 0,15 | 0,4829 | 0,2719 | **0,3479** |
| 0,25 | 0,6390 | 0,2248 | 0,3326 |
| 0,50 | 0,8561 | 0,1387 | 0,2387 |
| 0,90 | 0,9744 | 0,0078 | 0,0154 |

Faktor pembatas adalah *recall*, bukan *precision*. Nilai *recall* tertinggi
pada seluruh rentang hanya 0,3331.

Komposisi kesalahan pada analisis kesalahan:

| Jenis kesalahan | Porsi |
|---|---:|
| *False negative* | 63,5% |
| *False positive* terhadap latar belakang | 34,9% |
| Salah kelas | 1,5% |

Masalah utama model adalah menemukan objek, bukan membedakan penyakit.
Median luas *bounding box* yang terlewat adalah 3.376 px2, sekitar setengah
dari median keseluruhan sebesar 7.051,6 px2.

Pada tingkat citra, 469 dari 2.093 citra validasi (22,4 persen) terdeteksi
sempurna tanpa kesalahan apa pun.

## Analisis Kelebihan dan Keterbatasan

### Kelebihan

1. Kepatuhan ditegakkan pada tingkat kode, bukan sekadar dinyatakan.
2. Pemetaan canonical gagal secara keras pada kategori tak dikenal.
3. Penyiapan data deterministik dan tidak merusak dataset mentah.
4. Keputusan konfigurasi berbasis 21 percobaan tercatat.
5. Jejak audit lengkap pada setiap tahap.
6. Keterbatasan dilaporkan apa adanya, termasuk yang merugikan penyajian.

### Keterbatasan

1. Model dilatih dari nol, konsekuensi aturan kompetisi.
2. *Backend* MPS memiliki operasi nondeterministik, sehingga reproduksi
   pelatihan bit per bit tidak diklaim.
3. *F1* lokal bervariasi pada rentang 0,22 sampai 0,42 antar pengulangan
   pada *checkpoint* yang sama. Penyebab pastinya belum ditelusuri tuntas.
4. Performa antar kelas timpang, selisih AP@0.5 antara kelas terbaik dan
   terburuk melebihi 0,67.
5. Pemilihan *hyperparameter* divalidasi pada skala penyaringan, lalu
   diterapkan pada skala penuh.
6. Kandidat duplikat berbasis *perceptual hash* belum diverifikasi visual
   satu per satu.
7. Belum ada validasi pada data di luar dataset kompetisi.
8. Seluruh pekerjaan dijalankan pada satu laptop.

## Reproducibility

Tiga tingkat reproduksi dibedakan agar klaim tidak melampaui bukti:

| Tingkat | Status |
|---|---|
| Prapemrosesan | Terverifikasi identik byte per byte |
| Konfigurasi | Terverifikasi, seluruh parameter tercatat |
| Pelatihan bit per bit | **Tidak diklaim**, karena nondeterminisme MPS |

Risiko pada tingkat ketiga dikurangi melalui *seed* tetap, konfigurasi beku,
*manifest* tetap, validasi pemuatan pada proses bersih, *checksum* model, dan
kode yang terversi.

Uji reproduksi pada lingkungan bersih (`artifacts/audit/block16_clean_reproduction_test.md`)
menemukan dan memperbaiki dua cacat nyata sebelum submission, yaitu konflik
versi `numpy` yang membuat instalasi dari nol gagal, dan kegagalan
*backend* MPS pada inferensi berukuran besar.

## Instalasi

```bash
git clone https://github.com/galiihajiip/agridata.git
cd agridata
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Membutuhkan Python 3.11.x. Seluruh dependensi dikunci pada versi eksak dan
sudah diuji melalui instalasi dari nol. CUDA tidak diasumsikan tersedia.

## Cara Menjalankan

Letakkan dataset resmi pada `Telepati 8.0 Datasets/`, atau arahkan
`--dataset-root` ke lokasi lain. Tidak ada *path* personal yang ditulis
permanen pada kode.

```bash
# 1. Menyiapkan data siap latih
python scripts/prepare_dataset.py --dataset-root "Telepati 8.0 Datasets" --output-dir data/prepared --seed 42

# 2. Profiling dataset
python scripts/profile_dataset.py --dataset-root "Telepati 8.0 Datasets"

# 3. Pelatihan final (sekitar 7,3 jam pada Apple Silicon)
python scripts/run_final_training.py --config configs/final_model_config.yaml

# 4. Evaluasi
python scripts/evaluate.py --weights runs/detect/final/final_model/weights/best.pt --split valid --conf-threshold 0.25

# 5. Analisis kesalahan
python scripts/run_error_analysis.py --weights runs/detect/final/final_model/weights/best.pt --split valid

# 6. Sensitivitas threshold
python scripts/threshold_sensitivity.py --split valid
```

Notebook dapat dijalankan langsung:

```bash
jupyter notebook notebooks/final_agriData_telepati8.ipynb
```

Secara *default* notebook berjalan pada mode evaluasi (`SKIP_TRAINING = True`),
sehingga selesai dalam hitungan menit. Setel `SKIP_TRAINING = False` untuk
mereproduksi pelatihan penuh.

## Inferensi

```python
from ultralytics import YOLO

model = YOLO("runs/detect/final/final_model/weights/best.pt")
results = model.predict("path/ke/citra.jpg", conf=0.25)

for box in results[0].boxes:
    print(int(box.cls.item()), float(box.conf.item()), box.xywh.tolist())
```

## Model Weights

| Field | Nilai |
|---|---|
| Berkas | `runs/detect/final/final_model/weights/best.pt` |
| Ukuran | 6.253.994 byte |
| SHA-256 | `9d74fffdd977a7bb6749bc828fe908278c5d3eaa24c3cfdbbe5a560d41f5d308` |
| *Commit* saat pelatihan | `28668899fb000cee3a2a8386ac65ddeba2d04d02` |

Berkas bobot tidak dikomit ke Git karena merupakan biner berukuran besar.
Lihat [`weights/README.md`](weights/README.md) untuk informasi rilis.

Model 20 *epoch* sebelumnya (mAP@0.5 = 0,5620) diarsipkan pada
[`artifacts/archive/20epoch_run/`](artifacts/archive/20epoch_run/) dan tidak
dihapus.

## Struktur Repository

```
agridata/
  configs/          konfigurasi eksperimen dan konfigurasi final beku
  src/agridata/     paket inti: dataset, training, metrics, analysis, visualization
  scripts/          titik masuk CLI untuk setiap tahap pipeline
  notebooks/        notebook submission
  artifacts/
    audit/          audit dataset, mapping, reproducibility, submission
    reports/        laporan per tahap, evaluasi, profiling, analisis kesalahan
    figures/        figur untuk notebook dan dokumentasi
    experiments/    log 21 percobaan terkontrol
    archive/        hasil model 20 epoch yang digantikan
  references/       audit sitasi dan daftar pustaka
  tests/            69 uji unit
  weights/          informasi rilis model dan checksum
  docs/             model card dan placeholder pernyataan orisinalitas
```

## Kepatuhan terhadap Regulasi

| Ketentuan | Status | Bukti |
|---|---|---|
| Tanpa *external pretrained weights* | Patuh | `build_compliant_model` menolak `pretrained=True`, `YOLO_OFFLINE=1` aktif |
| Hanya dataset resmi | Patuh | Tidak ada direktori dataset lain, tidak ada rujukan data eksternal |
| Tanpa pemrosesan LLM atau API | Patuh | Seluruh prapemrosesan berupa kode Python deterministik |
| Pemetaan 11 kelas canonical | Patuh | `artifacts/audit/canonical_mapping_report.md`, nol kategori tak terpetakan |
| Split resmi dipertahankan | Patuh | Tidak ada penggabungan atau pengacakan ulang |
| Tanpa kebocoran data | Patuh | Satu duplikat persis ditemukan dan dikeluarkan dari manifest latih |
| *Seeding* deterministik | Patuh | `seed=42` pada Python, NumPy, dan PyTorch |
| Satu model final | Patuh | `artifacts/reports/final_model_metadata.json` |

Audit lengkap tersedia pada
[`artifacts/audit/final_submission_audit.md`](artifacts/audit/final_submission_audit.md).

## Referensi

Daftar pustaka lengkap beserta audit sitasi per kalimat tersedia pada
[`references/README.md`](references/README.md) dan pada Bagian 21 notebook.
Seluruh metadata diverifikasi terhadap halaman penerbit atau dokumentasi
resmi.

## Kontributor

- **Galih Aji Pangestu** ([@galiihajiip](https://github.com/galiihajiip))
