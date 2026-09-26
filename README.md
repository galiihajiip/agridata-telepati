# TELEPATI 8.0 AgriData Intelligence Race

Deteksi penyakit tanaman padi berbasis *object detection* untuk 11 kelas
canonical, dibangun dari dataset resmi TELEPATI 8.0. Model dilatih sepenuhnya
dari nol tanpa *external pretrained weights*, sesuai ketentuan lomba.

Dokumen utama submission kami adalah
[`notebooks/final_agriData_telepati8.ipynb`](notebooks/final_agriData_telepati8.ipynb).
Notebook itu memuat alur lengkap dari audit dataset sampai analisis kesalahan,
dan kami tulis sebagai laporan penelitian, bukan sekadar kumpulan sel kode.
README ini merupakan peta jalan menuju bukti-bukti di dalamnya.

## Ringkasan

| Item | Nilai |
|---|---|
| Tugas | *Object detection*, 11 kelas canonical |
| Arsitektur | YOLOv8n, dilatih dari nol, `pretrained=False` |
| **mAP@50 (valid)** | **66,78%** |
| **F1-Score macro (valid)** | **68,26%** |
| mAP@50 (test) | 65,96% |
| F1-Score macro (test) | 66,41% |
| Resolusi inferensi | 640 |
| Ambang NMS IoU | 0,5 (bukan bawaan 0,7) |
| Ukuran model | 6,3 MB (6.260.394 byte) |
| Waktu pelatihan | 20,84 jam, 100 *epoch*, Apple Silicon MPS |
| Jumlah percobaan tercatat | 21 percobaan terkontrol |
| Uji unit | 69, seluruhnya lulus |

## Bagi juri yang ingin memverifikasi dengan cepat

Kalau Anda hanya perlu memastikan angka yang kami laporkan benar, dua perintah
berikut cukup dan tidak memerlukan pelatihan ulang:

```bash
python scripts/evaluate.py --weights runs/detect/final/model_100epoch/weights/best.pt --split valid --nms-iou 0.5
python scripts/compute_official_metrics.py --split valid
```

Perintah pertama memakan sekitar 8 sampai 10 menit pada Apple Silicon dan
menghasilkan `artifacts/reports/evaluation_valid.json`. Perintah kedua hanya
membaca berkas itu dan mencetak dua angka leaderboard, tanpa menghitung ulang
apa pun. Pemisahan ini sengaja kami buat agar hanya ada satu sumber kebenaran
untuk setiap angka.

Penjelasan lengkap cara menyiapkan lingkungan dan data ada pada bagian
[Instalasi](#instalasi) dan [Cara Menjalankan](#cara-menjalankan).

## Tujuan

Kami menetapkan tiga tujuan, dan urutannya mencerminkan prioritas kami:

1. mematuhi seluruh batasan kompetisi, terutama larangan *external pretrained
   weights*, dataset eksternal, dan pemrosesan dataset memakai LLM atau API;
2. menghasilkan pekerjaan yang dapat direproduksi dan diaudit ulang pihak
   ketiga, karena skor yang tidak dapat diverifikasi tidak ada nilainya;
3. melaporkan hasil secara jujur, termasuk keterbatasan yang tidak
   menguntungkan posisi kami sendiri.

## Dataset

Kami hanya memakai dataset resmi TELEPATI 8.0 dalam format COCO, dan
mempertahankan pembagian *split* resmi apa adanya. Tidak ada penggabungan
maupun pengacakan ulang antar *split*, karena tindakan itu akan merusak dasar
perbandingan dengan peserta lain sekaligus membuka peluang kebocoran data uji
ke data latih.

| Split | Citra | Anotasi canonical | Rata-rata anotasi per citra |
|---|---:|---:|---:|
| train | 10.133 | 20.163 | 1,99 |
| valid | 2.106 | 4.888 | 2,32 |
| test | 1.059 | 2.670 | 2,52 |
| **Total** | **13.298** | **27.721** | |

Dataset mentah tidak pernah kami ubah. Seluruh penyiapan data menulis ke
direktori terpisah dan merujuk citra lewat *symlink*, sehingga tidak ada byte
citra yang diduplikasi dan dataset asli tetap utuh untuk diperiksa.

## 11 Kelas Canonical

Dataset mentah memuat 21 kategori, sedangkan target deteksi resmi berjumlah 11
kelas. Selisih itu berasal dari variasi penulisan label, variasi kapitalisasi
dan tanda hubung, serta tiga kategori *supercategory* yang bukan target
deteksi, yaitu `Leaf-blight`, `Rice-Leaf-Diseasee`, dan `paddy`. Ketiganya
kami kecualikan setelah terbukti tidak memuat satu pun anotasi pada seluruh
*split*.

| ID model | Kelas canonical | Instance (train) | AP@0.5 valid | AP@0.5 test |
|---:|---|---:|---:|---:|
| 0 | Bacterial leaf blight | 476 | 0,4679 | 0,3673 |
| 1 | Bacterial panicle blight | 528 | 0,6530 | 0,7671 |
| 2 | Blast | 4.149 | 0,5358 | 0,5066 |
| 3 | Brown spot | 5.010 | 0,3303 | 0,2811 |
| 4 | False smut | 852 | 0,9528 | 0,9471 |
| 5 | Healthy | 2.374 | 0,8717 | 0,9357 |
| 6 | Leaf roller | 812 | 0,9134 | 0,8966 |
| 7 | Leaf scald | 1.438 | 0,4490 | 0,4180 |
| 8 | Narrow brown | 222 | 0,9755 | 0,9729 |
| 9 | Sheath blight | 1.762 | 0,5502 | 0,5094 |
| 10 | Tungro | 2.540 | 0,6460 | 0,6533 |

Pemetaannya kami buat eksplisit dan sengaja gagal secara keras bila menemukan
kategori mentah yang tidak dikenali, supaya perubahan dataset di masa depan
tidak lolos diam-diam. Buktinya pada
[`artifacts/audit/canonical_mapping_report.md`](artifacts/audit/canonical_mapping_report.md).

Satu hal langsung terlihat dari tabel di atas: jumlah data bukan penentu
tunggal performa. Narrow brown hanya punya 222 *instance* tetapi memperoleh AP
tertinggi, sedangkan Brown spot punya 5.010 *instance* tetapi terendah. Kami
periksa hubungan itu secara khusus pada Bagian 17 notebook.

## Metodologi

Urutan kerja kami:

```
Dataset resmi (tidak diubah)
  -> Audit forensik dataset
  -> Pemetaan 21 kategori menjadi 11 kelas canonical
  -> Profiling dan eksplorasi
  -> Penyiapan data format YOLO (symlink, manifest)
  -> 21 percobaan terkontrol satu faktor pada satu waktu
  -> Pembekuan konfigurasi final
  -> Pelatihan skala penuh
  -> Evaluasi, analisis kesalahan, audit
```

Kami tidak menetapkan *hyperparameter* berdasarkan nilai bawaan maupun
intuisi. Setiap keputusan konfigurasi bersandar pada percobaan yang tercatat
lengkap dengan *seed*, *hyperparameter*, arsitektur, *hash* manifest dataset,
dan *commit* Git saat percobaan dijalankan. Seluruhnya ada pada
[`artifacts/experiments/experiment_log.md`](artifacts/experiments/experiment_log.md).

## Profiling Dataset

Lima karakteristik yang kami bawa ke tahap pemodelan:

| Temuan | Nilai |
|---|---|
| Ketimpangan kelas (train) | rasio 22,6 kali antara kelas terbanyak dan tersedikit |
| Ketimpangan kelas (valid dan test) | lebih dari 30 kali |
| Dominasi objek kecil | 38,1 persen pada train, 46,8 persen pada test |
| Integritas anotasi | bersih pada seluruh pemeriksaan |
| Duplikat lintas *split* | satu ditemukan, dikeluarkan dari manifest latih |

Adegan terpadat memuat 178 anotasi dalam satu citra, seluruhnya kelas Brown
spot. Temuan itu menjelaskan secara visual mengapa Brown spot sekaligus
menjadi kelas dengan *instance* terbanyak dan AP terendah: gejalanya berupa
puluhan bercak kecil yang berdesakan pada satu helai daun.

Laporan lengkap:
[`artifacts/audit/dataset_audit_report.md`](artifacts/audit/dataset_audit_report.md),
[`artifacts/reports/eda_summary.md`](artifacts/reports/eda_summary.md),
[`artifacts/reports/class_imbalance_diagnostics.md`](artifacts/reports/class_imbalance_diagnostics.md).

## Model

| Aspek | Nilai |
|---|---|
| Arsitektur | YOLOv8n (Ultralytics), dari definisi `yolov8n.yaml` |
| Inisialisasi | acak, `pretrained=False` |
| Parameter | sekitar 3,0 juta |
| Kepala deteksi | 11 kelas |
| Resolusi masukan | 640 x 640 |
| Ukuran *checkpoint* | 6,3 MB |

Larangan *external pretrained weights* tidak hanya kami nyatakan di dokumen,
tetapi kami tegakkan di dalam kode. Fungsi `build_compliant_model` menolak
berjalan bila diberi `pretrained=True` atau bila argumen arsitekturnya
menyerupai berkas *checkpoint*, dan `YOLO_OFFLINE=1` dipaksa aktif sebelum
Ultralytics diimpor sehingga setiap upaya pengunduhan bobot gagal secara
keras. Dengan begitu pelanggaran aturan akan berhenti sebagai galat, bukan
lolos diam-diam.

## Eksperimen

Kami menjalankan 21 percobaan terkontrol pada skala penyaringan, yaitu
sebagian data latih dengan jumlah *epoch* kecil, karena anggaran komputasi kami
terbatas pada satu laptop. Nilai mAP absolut pada tahap ini sangat rendah dan
**tidak sebanding** dengan hasil skala penuh; angkanya hanya kami pakai untuk
membandingkan faktor satu terhadap yang lain.

Dari enam pertanyaan yang kami ajukan, dua faktor terbukti membantu:

| Faktor | Hasil |
|---|---|
| Durasi pelatihan | pengaruh terbesar, mAP naik sekitar tujuh kali lipat dari 5 ke 10 *epoch* |
| Ukuran citra 640 dibanding 320 | membantu, konsisten dengan dominasi objek kecil |
| Batch lebih besar | menurunkan hasil |
| *Learning rate* lebih kecil | menurunkan hasil |
| *Optimizer* SGD | menurunkan hasil |
| *Oversampling* kelas minoritas | menurunkan hasil, tidak diadopsi |

Satu keputusan kami ambil bukan berdasarkan selisih metrik: augmentasi tetap
diaktifkan meskipun percobaan tanpa augmentasi sedikit unggul pada anggaran
pendek. Alasannya kami nyatakan terbuka sebagai penilaian, yaitu bahwa
selisihnya menyempit seiring bertambahnya anggaran dan bahwa model ini
ditujukan untuk kondisi lapangan yang bervariasi. Penalaran lengkapnya ada
pada komentar di dalam
[`configs/final_model_config.yaml`](configs/final_model_config.yaml) dan pada
Bagian 12 notebook.

## Hasil

Bobot yang dievaluasi: `runs/detect/final/model_100epoch/weights/best.pt`.

**Konvensi pengukuran**, kami nyatakan eksplisit agar juri dapat mereproduksi
angka yang sama persis:

- mAP@50 diambil langsung dari `model.val()` bawaan Ultralytics. Kami tidak
  mengimplementasikan ulang integrasi AP.
- *F1-Score* kami hitung sebagai rata-rata antar kelas (*macro*) dari kurva
  *F1* per kelas, diambil pada satu *confidence threshold* yang memaksimalkan
  rata-rata tersebut.
- Ambang NMS IoU **0,5**, bukan bawaan 0,7, berdasarkan pencarian pada *split*
  valid yang terdokumentasi di
  [`artifacts/reports/inference_tuning_nms.json`](artifacts/reports/inference_tuning_nms.json).

| Metrik | Valid | Test | Selisih |
|---|---:|---:|---:|
| **mAP@50** | **66,78%** | **65,96%** | -0,82 poin |
| **F1-Score macro** | **68,26%** | **66,41%** | -1,85 poin |
| mAP@0.5:0.95 | 0,4141 | 0,4330 | +0,0189 |
| *Precision* pada titik operasi | 0,7188 | 0,6983 | -0,0205 |
| *Recall* pada titik operasi | 0,6722 | 0,6634 | -0,0089 |
| *Confidence* titik operasi | 0,2503 | 0,2382 | |

*Split* test tidak pernah kami pakai untuk penyetelan apa pun, termasuk untuk
memilih model final. Pemilihan model kami lakukan sepenuhnya di atas *split*
valid, lalu *split* test kami evaluasi sekali setelah model dikunci. Selisih
valid terhadap test yang hanya 0,82 poin pada mAP menunjukkan performa model
tidak bergantung pada satu *split* tertentu.

Urutan kelas juga konsisten pada kedua *split*: Narrow brown tertinggi dan
Brown spot terendah. Konsistensi peringkat itu menguatkan bahwa perbedaan
performa antar kelas merupakan sifat yang stabil, bukan kebetulan satu *split*.

Reproduksi: `python scripts/compute_official_metrics.py --split valid`

### Riwayat perubahan model final

Kami mencatatnya terbuka karena memengaruhi cara membaca dokumen lama:

| Model | mAP@50 valid | *F1* macro valid | Status |
|---|---:|---:|---|
| 20 *epoch* | 56,20% | tidak dihitung | diarsipkan |
| 50 *epoch* | 64,01% | 63,83% | diarsipkan |
| **100 *epoch*** | **66,78%** | **68,26%** | **final** |

Perpanjangan terakhir kami dasarkan pada kurva pelatihan model 50 *epoch* yang
menunjukkan model belum konvergen: mAP masih naik, *train loss* masih turun,
dan *val loss* juga masih turun. Model 100 *epoch* kemudian menang di kedua
*split* sekaligus, naik 2,77 poin pada valid dan 3,50 poin pada test, sehingga
kami tidak menganggapnya kebetulan satu *split*.

Seluruh nilai metrik historis dibedakan pada
[`artifacts/audit/metrics_provenance.md`](artifacts/audit/metrics_provenance.md).

### Sensitivitas terhadap *confidence threshold*

Tabel berikut memakai **metrik lokal diagnostik** dengan rata-rata *micro*,
bukan *F1* macro yang kami laporkan di atas. Keduanya mengukur hal yang
berbeda dan tidak boleh dibandingkan langsung. Nilainya kami hitung ulang dari
prediksi yang sudah tersimpan, tanpa inferensi ulang, sehingga deterministik.

| Threshold | Precision | Recall | F1 lokal |
|---:|---:|---:|---:|
| 0,05 | 0,2273 | 0,2365 | 0,2318 |
| 0,10 | 0,3828 | 0,2064 | **0,2682** |
| 0,25 | 0,6473 | 0,1479 | 0,2408 |
| 0,50 | 0,8571 | 0,0945 | 0,1703 |
| 0,90 | 1,0000 | 0,0076 | 0,0150 |

Faktor pembatasnya adalah *recall*, bukan *precision*. Nilai *recall*
tertinggi pada seluruh rentang hanya 0,2365, yang berarti sebagian besar objek
*ground truth* tidak terpasangkan bahkan ketika ambangnya diturunkan.

Perlu kami jelaskan satu hal yang tampak berlawanan. Dibanding model 50
*epoch*, *F1* macro kami naik (63,83% menjadi 68,26%) sementara *F1* lokal
*micro* justru turun (0,3479 menjadi 0,2682). Keduanya tidak bertentangan,
karena rata-rata *micro* pada ambang tetap didominasi kelas mayoritas Brown
spot yang tetap lemah, sedangkan rata-rata *macro* pada titik operasi optimal
mengangkat kelas minoritas yang justru sangat kuat. Kami melaporkan keduanya
apa adanya alih-alih menampilkan hanya yang menguntungkan.

## Analisis Kelebihan dan Keterbatasan

### Kelebihan

1. **Kepatuhan ditegakkan pada tingkat kode**, bukan sekadar dinyatakan.
   `build_compliant_model` menolak berjalan bila dilanggar, dan
   `YOLO_OFFLINE=1` membuat setiap upaya pengunduhan gagal keras.
2. **Pemetaan canonical gagal secara keras** bila ada kategori tak dikenali,
   sehingga perubahan dataset tidak lolos diam-diam.
3. **Prapemrosesan deterministik dan tidak merusak.** Dataset mentah tidak
   pernah diubah, dan manifest dapat dihasilkan ulang identik byte per byte.
4. **Keputusan berbasis eksperimen tercatat**, 21 percobaan lengkap dengan
   *seed*, *hyperparameter*, dan *commit*.
5. **Satu sumber kebenaran per angka.** `evaluate.py` menghasilkan,
   `compute_official_metrics.py` hanya membaca, sehingga tidak mungkin ada dua
   angka berbeda untuk metrik yang sama.
6. **Keterbatasan dilaporkan apa adanya**, termasuk yang merugikan penyajian
   kami sendiri.

### Keterbatasan

1. **Model dilatih dari nol**, sehingga tidak mewarisi representasi visual
   umum. Ini konsekuensi aturan lomba, bukan pilihan desain.
2. **Reproduksi pelatihan bit per bit tidak kami klaim.** Operasi
   `scatter_reduce_mps` dan `index_put_with_accumulate_mps` tidak memiliki
   implementasi deterministik pada *backend* MPS.
3. **Evaluasi dapat bergeser antar pengulangan.** Pada perangkat ini kami
   pernah mengamati mAP@0.5 yang sama-sama sah bernilai 0,6678 dan 0,6759
   untuk *checkpoint* yang sama, yaitu selisih relatif sekitar 1,2 persen.
   Angka yang kami laporkan adalah 0,6678, hasil yang muncul berulang pada
   eksekusi bersih.
4. **Performa antar kelas tidak merata.** Selisih AP@0.5 antara Narrow brown
   dan Brown spot melebihi 0,64.
5. **Ekstrapolasi dari skala penyaringan.** Pemilihan *hyperparameter*
   divalidasi pada sebagian data dan sedikit *epoch*.
6. **Kandidat duplikat berbasis *perceptual hash* belum diverifikasi visual**
   satu per satu.
7. **Belum ada validasi di luar dataset kompetisi**, sehingga kemampuan
   generalisasi ke kondisi lapangan lain belum diketahui.
8. **Anggaran komputasi terbatas satu laptop**, yang membatasi ukuran model
   dan jumlah percobaan.

## Reproducibility

Kami membedakan tiga tingkat agar klaim kami tidak melampaui bukti:

| Tingkat | Status |
|---|---|
| Prapemrosesan | Terverifikasi identik byte per byte |
| Konfigurasi | Terverifikasi, seluruh parameter tercatat |
| Pelatihan bit per bit | **Tidak diklaim**, karena nondeterminisme MPS |

Risiko pada tingkat ketiga kami kurangi lewat *seed* tetap, konfigurasi beku,
manifest tetap, validasi pemuatan pada proses bersih, *checksum* model, dan
kode yang terversi. Daftar periksa lengkap 10 butir, seluruhnya lulus, ada
pada
[`artifacts/audit/reproducibility_checklist.md`](artifacts/audit/reproducibility_checklist.md).

Uji reproduksi pada lingkungan bersih
([`artifacts/audit/block16_clean_reproduction_test.md`](artifacts/audit/block16_clean_reproduction_test.md))
menemukan dan memperbaiki dua cacat nyata sebelum submission: konflik versi
`numpy` yang membuat instalasi dari nol gagal, dan kegagalan *backend* MPS
pada inferensi berdaftar *path* panjang. Keduanya akan membuat audit juri
gagal, dan justru itu alasan pengujian tersebut kami lakukan.

## Kebutuhan Sistem

| Kebutuhan | Keterangan |
|---|---|
| Python | 3.11.x (diuji pada 3.11) |
| RAM | minimal 8 GB untuk evaluasi, 16 GB disarankan untuk pelatihan |
| Ruang disk | sekitar 3 GB untuk dataset siap latih dan keluaran |
| GPU | **tidak wajib.** CUDA, Apple Silicon MPS, dan CPU semuanya didukung |

Perangkat dideteksi otomatis oleh `agridata.device.detect_device()` dengan
urutan CUDA, lalu MPS, lalu CPU. Ketersediaan CUDA tidak pernah kami
asumsikan, karena kami tidak tahu perangkat apa yang dipakai juri. Jalur CPU
selalu berfungsi, hanya lebih lambat.

## Instalasi

```bash
git clone https://github.com/galiihajiip/agridata.git
cd agridata
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Seluruh dependensi dikunci pada versi eksak dan sudah diuji melalui instalasi
dari nol pada *virtual environment* yang benar-benar baru. Bila pemasangan
gagal dengan `ResolutionImpossible`, periksa versi Python Anda: `ultralytics`
mengecualikan sebagian versi `numpy` pada macOS, dan patokan pada
`requirements.txt` sudah disesuaikan untuk itu.

Verifikasi pemasangan:

```bash
python -m pytest -q          # harus: 69 passed
```

## Cara Menjalankan

Letakkan dataset resmi pada direktori `Telepati 8.0 Datasets/` di akar
repository, atau arahkan `--dataset-root` ke lokasi lain. Tidak ada satu pun
*path* personal yang ditulis permanen pada kode, sehingga pipeline ini dapat
dijalankan dari direktori mana saja.

Struktur dataset yang diharapkan:

```
Telepati 8.0 Datasets/
  train/  _annotations.coco.json  + berkas citra
  valid/  _annotations.coco.json  + berkas citra
  test/   _annotations.coco.json  + berkas citra
```

### Langkah wajib sebelum apa pun

```bash
python scripts/prepare_dataset.py \
  --dataset-root "Telepati 8.0 Datasets" \
  --output-dir data/prepared --seed 42
```

Perintah ini membangun data siap latih format YOLO memakai *symlink*, tanpa
menyalin byte citra dan tanpa mengubah dataset mentah. Hasilnya harus identik
byte per byte setiap kali dijalankan dengan *seed* yang sama. Sekitar 1 menit.

### Verifikasi angka yang kami laporkan

```bash
# Evaluasi pada split valid, sekitar 8-10 menit
python scripts/evaluate.py \
  --weights runs/detect/final/model_100epoch/weights/best.pt \
  --split valid --nms-iou 0.5

# Cetak dua angka leaderboard, hanya membaca hasil di atas
python scripts/compute_official_metrics.py --split valid
```

Untuk *split* test, ganti `--split valid` menjadi `--split test`. Skrip akan
mencetak peringatan bahwa data uji tidak boleh dipakai untuk penyetelan
berulang.

### Audit dan analisis tambahan

```bash
# Audit forensik dataset, hanya membaca
python scripts/audit_dataset.py --dataset-root "Telepati 8.0 Datasets"

# Validasi pemetaan 11 kelas canonical
python scripts/validate_canonical_mapping.py --dataset-root "Telepati 8.0 Datasets"

# Profiling dan figur eksplorasi
python scripts/profile_dataset.py --dataset-root "Telepati 8.0 Datasets"
python scripts/visualize_dataset.py --dataset-root "Telepati 8.0 Datasets"

# Daftar periksa reproduktibilitas 10 butir
python scripts/check_reproducibility.py --dataset-root "Telepati 8.0 Datasets"

# Analisis kesalahan, sekitar 10 menit
python scripts/run_error_analysis.py \
  --weights runs/detect/final/model_100epoch/weights/best.pt --split valid

# Sensitivitas threshold, dari prediksi tersimpan, beberapa detik
python scripts/threshold_sensitivity.py --split valid
```

### Melatih ulang dari nol

```bash
python scripts/run_final_training.py --config configs/final_model_config.yaml
```

Memakan sekitar **20,84 jam** pada Apple Silicon dengan MPS untuk 100 *epoch*.
Sebelum mulai, skrip mencetak seluruh pengungkapan yang diwajibkan, yaitu
*commit* Git, versi pustaka, *seed*, *hash* manifest dataset, pemetaan kelas,
arsitektur, status `pretrained`, seluruh *hyperparameter*, dan perangkat.
Setelah selesai, bobotnya diverifikasi dapat dimuat dan menjalankan inferensi
dari proses Python yang benar-benar bersih.

Karena *backend* MPS tidak deterministik, angka hasil pelatihan ulang tidak
akan identik bit per bit dengan milik kami. Yang kami jamin identik adalah
konfigurasi dan prapemrosesannya.

### Menjalankan notebook

```bash
jupyter notebook notebooks/final_agriData_telepati8.ipynb
```

Secara bawaan notebook berjalan pada mode evaluasi (`SKIP_TRAINING = True`),
sehingga selesai dalam hitungan menit dengan memuat bobot yang sudah ada.
Setel `SKIP_TRAINING = False` untuk mereproduksi pelatihan penuh. Kode
pelatihan pada mode itu bukan tiruan, melainkan fungsi yang sama persis dengan
yang menghasilkan bobot final kami.

## Inferensi

```python
import os
os.environ["YOLO_OFFLINE"] = "1"
from ultralytics import YOLO

model = YOLO("runs/detect/final/model_100epoch/weights/best.pt")
results = model.predict("path/ke/citra.jpg", conf=0.25, iou=0.5, imgsz=640)

for box in results[0].boxes:
    print(int(box.cls.item()), float(box.conf.item()), box.xywh.tolist())
```

Urutan kelas mengikuti tabel [11 Kelas Canonical](#11-kelas-canonical), yaitu
`model_class_id = canonical_id - 1`. Parameter `iou=0.5` dan `imgsz=640` perlu
disertakan agar hasilnya sama dengan angka yang kami laporkan.

## Bobot Model

| Field | Nilai |
|---|---|
| Berkas | `runs/detect/final/model_100epoch/weights/best.pt` |
| Ukuran | 6.260.394 byte |
| SHA-256 | `c631a363ab580ca614c52b51eaaf798e31c44a3ba92f2aa05efcfe27f5a86965` |
| *Commit* saat pelatihan | `38754ce334149e7eeb633edb8d9d81820bad3b13` |

Berkas bobot tidak kami komit ke Git karena merupakan biner. Lihat
[`weights/README.md`](weights/README.md) untuk informasi rilis dan cara
memverifikasi *checksum*.

## Struktur Repository

```
agridata/
  configs/          konfigurasi percobaan dan konfigurasi final beku
  src/agridata/     paket inti: dataset, training, metrics, analysis, visualization
  scripts/          titik masuk CLI untuk setiap tahap pipeline
  notebooks/        notebook submission
  artifacts/
    audit/          audit dataset, pemetaan, reproduktibilitas, kesiapan submission
    reports/        laporan per tahap, evaluasi, profiling, analisis kesalahan
    figures/        figur untuk notebook dan dokumentasi
    experiments/    log 21 percobaan terkontrol
    predictions/    prediksi tersimpan, dipakai analisis deterministik
    archive/        hasil model 20 dan 50 epoch yang digantikan
  references/       audit sitasi dan daftar pustaka
  tests/            69 uji unit
  weights/          informasi rilis model dan checksum
  docs/             model card dan penanda pernyataan orisinalitas
```

## Kepatuhan terhadap Regulasi

| Ketentuan | Status | Bukti |
|---|---|---|
| Tanpa *external pretrained weights* | Patuh | `build_compliant_model` menolak `pretrained=True` dan argumen menyerupai *checkpoint*, `YOLO_OFFLINE=1` aktif |
| Hanya dataset resmi | Patuh | Tidak ada dataset lain pada repository maupun rujukan kode |
| Tanpa pemrosesan LLM atau API | Patuh | Seluruh prapemrosesan berupa kode Python deterministik |
| Pemetaan 11 kelas canonical | Patuh | [`canonical_mapping_report.md`](artifacts/audit/canonical_mapping_report.md), nol kategori tak terpetakan |
| *Split* resmi dipertahankan | Patuh | Tidak ada penggabungan atau pengacakan ulang |
| Tanpa kebocoran data | Patuh | Satu duplikat persis ditemukan dan dikeluarkan dari manifest latih |
| Data uji tidak dipakai menyetel | Patuh | Pemilihan model dilakukan di atas *split* valid, test dievaluasi sekali |
| *Seeding* deterministik | Patuh | `seed=42` pada Python, NumPy, dan PyTorch |
| Satu model final | Patuh | [`final_model_metadata.json`](artifacts/reports/final_model_metadata.json) |

Audit kesiapan lengkap pada
[`artifacts/audit/final_submission_readiness.md`](artifacts/audit/final_submission_readiness.md).

## Referensi

Daftar pustaka lengkap beserta audit sitasi per kalimat ada pada
[`references/README.md`](references/README.md) dan pada Bagian 21 notebook.
Kami hanya menambahkan sitasi untuk pernyataan yang benar-benar bersumber dari
literatur atau dokumentasi resmi; pernyataan yang berasal dari hasil eksekusi
kami sendiri tidak kami beri sitasi karena sumbernya adalah artefak pada
repository ini.

## Kontributor

- **Galih Aji Pangestu** ([@galiihajiip](https://github.com/galiihajiip))
