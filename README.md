# TELEPATI 8.0 AgriData Intelligence Race

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galiihajiip/agridata-telepati/blob/main/notebooks/final_agriData_telepati8.ipynb)

| | |
|---|---|
| Nama tim | Di Bandung Di Ganesha |
| Perguruan tinggi | Universitas Pembangunan Nasional "Veteran" Jawa Timur |
| Ketua | Galih Aji Pangestu |
| Anggota | Stevyka Frista Aninda, Putri Ayu Ajeng Nina Zuraida |
| Dosen pembimbing | Andreas Nugroho Sihananto, S.Kom., M.Kom. |
| Cabang lomba | AgriData Intelligence Race, TELEPATI 8.0 |

Deteksi penyakit tanaman padi berbasis *object detection* untuk 11 kelas
canonical, dibangun dari dataset resmi TELEPATI 8.0. Model dilatih sepenuhnya
dari nol tanpa *external pretrained weights*, sesuai ketentuan lomba.

Dokumen utama submission kami adalah
[`notebooks/final_agriData_telepati8.ipynb`](notebooks/final_agriData_telepati8.ipynb).
Notebook itu memuat alur lengkap dari audit dataset sampai analisis kesalahan,
dan kami tulis sebagai laporan penelitian, bukan sekadar kumpulan sel kode.
README ini merupakan peta jalan menuju bukti-bukti di dalamnya.

Tombol *Open in Colab* di atas membuka notebook beserta seluruh keluaran,
tabel, dan figurnya yang sudah tertanam, sehingga dapat dibaca tanpa instalasi.
Untuk menjalankan ulang sel-selnya diperlukan dataset resmi dan bobot dari
GitHub Release; langkahnya ada pada bagian [Cara Menjalankan](#cara-menjalankan).

## Ringkasan

| Item | Nilai |
|---|---|
| Tugas | *Object detection*, 11 kelas canonical |
| Arsitektur | YOLOv8s-P2, dilatih dari nol, `pretrained=False` |
| **mAP@50 (valid)** | **70,71%** |
| **F1-Score macro (valid)** | **72,33%** |
| mAP@50 (test) | 70,65% |
| F1-Score macro (test) | 71,45% |
| Resolusi inferensi | 640 |
| Ambang NMS IoU | 0,5 (bukan bawaan 0,7) |
| Ukuran model | 21,8 MB (21.754.576 byte) |
| Waktu pelatihan | 8,11 jam, 250 *epoch*, Kaggle 2x NVIDIA Tesla T4 |
| Jumlah percobaan tercatat | 21 percobaan penyaringan dan 4 kandidat skala penuh |
| Uji unit | 69, seluruhnya lulus |

## Bagi juri yang ingin memverifikasi dengan cepat

**Cara tercepat, di Google Colab:**
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galiihajiip/agridata-telepati/blob/main/notebooks/verify_colab.ipynb)

Buka [`notebooks/verify_colab.ipynb`](notebooks/verify_colab.ipynb), isi `DATASET_ZIP`
dengan zip dataset resmi, lalu Runtime > Run all. Notebook itu meng-*clone*
repository ini, mengunduh bobot dari GitHub Release dan memverifikasi
SHA-256-nya, menyiapkan dataset dengan `scripts/prepare_dataset.py`,
menjalankan dua perintah di bawah, lalu membandingkan hasilnya dengan angka
kami pada toleransi 2 persen relatif. Uji kami dari dataset mentah memberi
mAP@50 70,71% dan *F1-Score* 72,33%, selisih 0,00%, dalam sekitar 4 menit.

**Atau secara lokal**, dua perintah
berikut cukup dan tidak memerlukan pelatihan ulang:

```bash
python scripts/evaluate.py --weights runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt --split valid --nms-iou 0.5
python scripts/compute_official_metrics.py --split valid
```

Bobotnya diunduh dari GitHub Release
[`v1.0.0-final-model`](https://github.com/galiihajiip/agridata-telepati/releases/tag/v1.0.0-final-model) dan diletakkan pada path di atas; perintah
unduhan dan verifikasi *checksum* ada pada [`weights/README.md`](weights/README.md).
Perintah pertama memakan sekitar 4 menit pada Apple Silicon dan
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

Urutan kerja kami dari awal sampai angka akhir:

```
Dataset resmi (tidak diubah)
  -> Audit forensik dataset
  -> Pemetaan 21 kategori menjadi 11 kelas canonical
  -> Profiling dan eksplorasi
  -> Penyiapan data format YOLO (symlink, manifest)
  -> 21 percobaan penyaringan, satu faktor pada satu waktu (laptop, MPS)
  -> Model YOLOv8n 20, 50, lalu 100 epoch (laptop, MPS)
  -> Empat kandidat skala penuh dari nol (Kaggle 2x T4 dan Colab A100)
  -> Pemilihan model final di atas split valid
  -> Evaluasi split test satu kali, analisis kesalahan, audit
```

Kami tidak menetapkan *hyperparameter* berdasarkan nilai bawaan maupun
intuisi. Setiap keputusan konfigurasi bersandar pada percobaan yang tercatat
lengkap dengan *seed*, *hyperparameter*, arsitektur, *hash* manifest dataset,
dan *commit* Git saat percobaan dijalankan. Seluruhnya ada pada
[`artifacts/experiments/experiment_log.md`](artifacts/experiments/experiment_log.md).

### Perjalanan menuju model final

Kami mencatat urutan ini lengkap, termasuk langkah yang tidak berhasil, karena
setiap angka di repository ini berasal dari salah satu tahapnya.

| Tahap | Yang dilakukan | Hasil (mAP@50 / *F1* macro, *split* valid) | Bukti |
|---|---|---|---|
| 1. Penyaringan | 21 percobaan YOLOv8n pada 5 sampai 10 persen data dan 2 sampai 12 *epoch*, untuk memilih ukuran citra, *optimizer*, augmentasi, dan penanganan ketimpangan kelas | angka sangat kecil, hanya untuk membandingkan faktor | `artifacts/experiments/` |
| 2. YOLOv8n 20 *epoch* | Pelatihan penuh pertama di Apple Silicon | 56,20% / tidak dihitung | `artifacts/archive/20epoch_run/` |
| 3. YOLOv8n 50 *epoch* | Kurva 20 *epoch* belum konvergen. Di tahap ini pula konvensi *F1* dikoreksi dari *micro* ke *macro* dan ambang NMS diturunkan ke 0,5 | 64,01% / 63,83% | `artifacts/archive/50epoch_640_run/` |
| 4. YOLOv8n 100 *epoch* | Kurva 50 *epoch* masih naik. Pelatihan memakan 20,84 jam dan kurvanya tetap belum konvergen | 66,78% / 68,26% | `artifacts/archive/100epoch_v8n_run/` |
| 5. Kandidat skala penuh | Pelatihan dipindah ke GPU. Empat kandidat dilatih dari nol: A (YOLOv8s 640), B (YOLOv8s-P2 640), C (YOLOv8s 1024), D (YOLOv8m 640) | A 70,57% / 71,37%; B 70,71% / 72,33%; C terputus di *epoch* 49; D 71,39% / 71,38% | `artifacts/candidates/` |
| 6. Ensemble | A+B dan B+D diuji dengan aturan keputusan yang ditetapkan sebelum melihat hasil: dipakai hanya bila jumlah kedua metrik naik minimal 2 poin | A+B 71,15% / 71,64%; B+D 71,77% / 71,55%; tidak dipakai | `artifacts/candidates/ensembles.json` |
| 7. Pemilihan | B dipilih: jumlah kedua metrik lomba tertinggi, bobot 2,4 kali lebih kecil dari D | **70,71% / 72,33%** | `artifacts/reports/evaluation_valid.json` |
| 8. *Split* test | Dievaluasi satu kali untuk B setelah pilihan dikunci | 70,65% / 71,45% | `artifacts/reports/evaluation_test.json` |

Dua kejadian di tahap 5 perlu kami sebut karena menyangkut kepatuhan dan
kejujuran angka. Pertama, percobaan pertama di Kaggle memperlihatkan bahwa
Ultralytics mengunduh bobot pretrained `yolo26n.pt` untuk pengecekan AMP;
percobaan itu kami hentikan dan seluruh kandidat dilatih setelah celah itu
ditutup (bagian [Model](#model)). Kedua, sebelum memakai angka ensemble kami
memvalidasi metode pengukurannya dengan menjalankan A sendirian; hasilnya
harus sama persis dengan `evaluate.py` (0,7057), dan baru setelah cocok angka
ensemble kami pakai.

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
| Arsitektur | YOLOv8s-P2 (Ultralytics), dari definisi `yolov8s-p2.yaml` |
| Inisialisasi | acak, `pretrained=False` |
| Parameter | sekitar 10,6 juta |
| Kepala deteksi | 11 kelas, empat skala keluaran (stride 4, 8, 16, 32) |
| Resolusi masukan | 640 x 640 |
| Ukuran *checkpoint* | 21,8 MB |

Varian P2 menambahkan kepala deteksi beresolusi 160 x 160 (stride 4) di atas
tiga kepala bawaan YOLOv8. Kami memilihnya karena median *bounding box* Brown
spot hanya sekitar 0,2 persen luas citra. Pada split valid keunggulannya atas
YOLOv8s biasa ternyata tipis, dan kami menjelaskannya pada bagian
[Hasil](#hasil).

Larangan *external pretrained weights* tidak hanya kami nyatakan di dokumen,
tetapi kami tegakkan di dalam kode. Fungsi `build_compliant_model` menolak
berjalan bila diberi `pretrained=True` atau bila argumen arsitekturnya
menyerupai berkas *checkpoint*, dan `YOLO_OFFLINE=1` dipaksa aktif sebelum
Ultralytics diimpor. Dengan begitu pelanggaran aturan akan berhenti sebagai
galat, bukan lolos diam-diam.

Pelatihan di GPU membuka satu celah yang tidak muncul di Apple Silicon:
pengecekan AMP bawaan Ultralytics mengunduh bobot pretrained `yolo26n.pt` untuk
membandingkan keluaran FP32 dan FP16, dan `YOLO_OFFLINE` tidak mencegahnya.
Bobot itu tidak pernah masuk ke model kami, tetapi tetap merupakan berkas
pretrained eksternal. Kami menemukannya pada log percobaan pertama di Kaggle,
menghentikan percobaan itu, dan menutup celahnya lewat
[`scripts/kaggle_site/sitecustomize.py`](scripts/kaggle_site/sitecustomize.py),
yang mengganti pengecekan tersebut pada setiap proses pelatihan termasuk proses
DDP. Seluruh kandidat yang kami laporkan dilatih setelah perbaikan ini, dan
log masing-masing memuat baris `AMP check dilewati tanpa mengunduh bobot
pretrained`.

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
[`configs/archive_100epoch_v8n_config.yaml`](configs/archive_100epoch_v8n_config.yaml)
dan pada Bagian 12 notebook. Keputusan itu kami bawa ke empat kandidat skala
penuh, yang memakai augmentasi bawaan Ultralytics dengan `flipud=0`.

Percobaan penyaringan juga memenangkan AdamW atas SGD, tetapi hanya pada 5
*epoch* dengan sekitar 10 persen data. Untuk kandidat skala penuh kami memakai
SGD dengan *learning rate* 0,01, resep bawaan Ultralytics untuk pelatihan dari
nol dengan jadwal panjang, dan kami mencatat ini sebagai keputusan yang tidak
diuji ulang pada skala penuh.

## Hasil

Bobot yang dievaluasi: `runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt`.

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
| **mAP@50** | **70,71%** | **70,65%** | -0,06 poin |
| **F1-Score macro** | **72,33%** | **71,45%** | -0,88 poin |
| mAP@0.5:0.95 | 0,4611 | 0,4830 | +0,0219 |
| *Precision* pada titik operasi | 0,7353 | 0,7626 | +0,0273 |
| *Recall* pada titik operasi | 0,7206 | 0,6904 | -0,0302 |
| *Confidence* titik operasi | 0,2142 | 0,2623 | |

*Split* test tidak pernah kami pakai untuk penyetelan apa pun, termasuk untuk
memilih model final. Pemilihan model kami lakukan sepenuhnya di atas *split*
valid, lalu *split* test kami evaluasi sekali setelah model dikunci. Selisih
mAP@50 valid terhadap test hanya 0,06 poin, sehingga performa model tidak
bergantung pada satu *split* tertentu.

Evaluasi *split* valid yang sama di CPU dan di Apple Silicon MPS menghasilkan
mAP@50 0,7071 dan *F1* macro 0,7233 yang identik pada kedua perangkat.

Reproduksi: `python scripts/compute_official_metrics.py --split valid`

### AP@50 per kelas

| Kelas | Valid | Test |
|---|---:|---:|
| Narrow brown | 0,9864 | 0,9950 |
| False smut | 0,9623 | 0,9612 |
| Leaf roller | 0,9226 | 0,9312 |
| Healthy | 0,8722 | 0,9595 |
| Bacterial panicle blight | 0,7723 | 0,8790 |
| Tungro | 0,6690 | 0,6996 |
| Sheath blight | 0,6650 | 0,6282 |
| Blast | 0,5709 | 0,5427 |
| Leaf scald | 0,5028 | 0,4898 |
| Bacterial leaf blight | 0,4787 | 0,3666 |
| Brown spot | 0,3755 | 0,3188 |

Urutan kelas konsisten pada kedua *split*: Narrow brown tertinggi dan Brown spot
terendah. Brown spot tetap menjadi penghambat terbesar walaupun kapasitas model
dan kepala deteksi objek kecil sudah ditambah, dan kami membahas dugaan
penyebabnya pada [Keterbatasan](#keterbatasan).

### Riwayat perubahan model final

Kami mencatatnya terbuka karena memengaruhi cara membaca dokumen lama:

| Model | mAP@50 valid | *F1* macro valid | Status |
|---|---:|---:|---|
| YOLOv8n, 20 *epoch* | 56,20% | tidak dihitung | diarsipkan |
| YOLOv8n, 50 *epoch* | 64,01% | 63,83% | diarsipkan |
| YOLOv8n, 100 *epoch* | 66,78% | 68,26% | diarsipkan |
| **YOLOv8s-P2, 250 *epoch*** | **70,71%** | **72,33%** | **final** |

Model YOLOv8n 100 *epoch* belum konvergen, dan satu kali pelatihannya saja
memakan 20,84 jam di Apple Silicon. Kami lalu melatih empat kandidat
berkapasitas lebih besar dari nol di GPU Kaggle dan Colab:

| Kandidat | Arsitektur | mAP@50 valid | *F1* macro valid | mAP@50-95 valid |
|---|---|---:|---:|---:|
| A | YOLOv8s, 640 | 70,57% | 71,37% | 46,40% |
| **B** | **YOLOv8s-P2, 640** | **70,71%** | **72,33%** | **46,11%** |
| C | YOLOv8s, 1024 | terputus di *epoch* 49, tidak dievaluasi | | |
| D | YOLOv8m, 640 | 71,39% | 71,38% | 48,32% |

B dan D masing-masing unggul pada satu metrik lomba dengan selisih di bawah
satu poin. Kami memilih B karena jumlah kedua metrik lombanya paling tinggi
dan bobotnya 2,4 kali lebih kecil. Ensemble B dengan D menaikkan mAP@50 menjadi
71,77% tetapi menurunkan *F1*, sehingga tidak kami pakai. Rinciannya, termasuk
aturan keputusan yang kami tetapkan sebelum melihat hasil, ada pada
[`artifacts/candidates/README.md`](artifacts/candidates/README.md).

Seluruh nilai metrik historis dibedakan pada
[`artifacts/audit/metrics_provenance.md`](artifacts/audit/metrics_provenance.md).

### Sensitivitas terhadap *confidence threshold*

Tabel berikut memakai **metrik lokal diagnostik** dengan rata-rata *micro*,
bukan *F1* macro yang kami laporkan di atas. Keduanya mengukur hal yang
berbeda dan tidak boleh dibandingkan langsung. Nilainya kami hitung ulang dari
prediksi yang sudah tersimpan, tanpa inferensi ulang, sehingga deterministik.

| Threshold | Precision | Recall | F1 lokal |
|---:|---:|---:|---:|
| 0,05 | 0,3217 | 0,6749 | 0,4357 |
| 0,10 | 0,4532 | 0,6205 | 0,5238 |
| 0,25 | 0,6735 | 0,5237 | **0,5893** |
| 0,50 | 0,8303 | 0,3893 | 0,5301 |
| 0,90 | 0,9676 | 0,0428 | 0,0819 |

Dibanding model YOLOv8n, *recall* maksimum naik dari 0,2365 menjadi 0,6749 dan
*F1* lokal tertinggi naik dari 0,2682 menjadi 0,5893. *F1* lokal *micro* tetap
lebih rendah daripada *F1* macro, karena rata-rata *micro* didominasi kelas
mayoritas Brown spot yang paling lemah, sedangkan rata-rata *macro* memberi
bobot sama pada kelas minoritas yang justru kuat.

### Analisis kesalahan

Kami mengelompokkan setiap kesalahan menjadi empat kategori pada *confidence
threshold* 0,1, memakai pencocokan yang tidak memandang kelas supaya kasus
"model salah tempat" dapat dipisahkan dari kasus "model salah nama":

| Jenis | YOLOv8n 100 *epoch* | Model final |
|---|---:|---:|
| *True positive* | 1.545 | **3.026** |
| *False negative*, objek terlewat | 3.276 | **1.755** |
| *False positive* terhadap latar belakang | 2.547 | 3.560 |
| Salah kelas | 67 | 107 |

Model final menemukan hampir dua kali lebih banyak objek dan melewatkan 46
persen lebih sedikit. Salah kelas tetap sekitar 2 persen dari seluruh
kesalahan, dan pasangan yang paling sering tertukar tetap masuk akal secara
domain, yaitu Brown spot dengan Blast (22 dan 14 kejadian), keduanya
menimbulkan lesi kecokelatan. Pada ambang serendah 0,1, *false positive*
terhadap latar kini menjadi jenis kesalahan terbanyak, yang wajar karena ambang
itu jauh di bawah titik operasi 0,21.

Dua pola pendukung, keduanya dari kesalahan aktual dan bukan dugaan:

- Objek yang masih terlewat sangat kecil. Median luas *bounding box* yang gagal
  terdeteksi 719,2 px², kira-kira 27 x 27 piksel, yaitu 0,10 kali median
  keseluruhan sebesar 7.051,6 px². Pada model YOLOv8n medianya 3.343,2 px².
- Adegan padat tetap tersulit: rasio *false negative* 0,486 berbanding 0,039
  pada adegan jarang.

Laporan lengkap pada
[`artifacts/reports/block13_error_analysis.md`](artifacts/reports/block13_error_analysis.md).

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
2. **Reproduksi pelatihan bit per bit tidak kami klaim.** Model final dilatih
   dengan DDP di dua GPU dengan AMP, dan sebagian operasi CUDA maupun MPS tidak
   memiliki implementasi deterministik.
3. **Evaluasi dapat bergeser antar pengulangan.** Pada model sebelumnya kami
   pernah mengamati mAP@0.5 yang sama-sama sah bernilai 0,6678 dan 0,6759
   untuk *checkpoint* yang sama di MPS. Untuk model final, evaluasi di CPU dan
   di MPS menghasilkan mAP@0.5 yang sama persis, 0,7071, tetapi kami tetap
   mencatat risiko ini.
4. **Performa antar kelas tidak merata.** Selisih AP@0.5 antara Narrow brown
   dan Brown spot masih melebihi 0,6. Brown spot hampir tidak membaik walaupun
   kapasitas model dinaikkan dan kepala P2 ditambahkan.
   Dugaan kami, yang belum kami buktikan, adalah konsistensi anotasinya:
   pada *split* valid median kotaknya hanya sekitar 0,2 persen luas citra,
   satu citra dapat memuat sampai 104 kotak, dan kelas ini berasal dari dua
   label mentah (`Brown spot` dan `BrownSpot`) yang tampaknya bersumber dari
   himpunan data berbeda.
5. **Ekstrapolasi dari skala penyaringan.** Pemilihan *hyperparameter*
   divalidasi pada sebagian data dan sedikit *epoch*.
6. **Kandidat duplikat berbasis *perceptual hash* belum diverifikasi visual**
   satu per satu.
7. **Belum ada validasi di luar dataset kompetisi**, sehingga kemampuan
   generalisasi ke kondisi lapangan lain belum diketahui.
8. **Anggaran komputasi terbatas.** Percobaan penyaringan berjalan di satu
   laptop, dan empat kandidat skala penuh memakai kuota GPU gratis Kaggle dan
   Colab, sehingga tiap kandidat hanya dilatih sekali dengan satu *seed*.

## Reproducibility

Kami membedakan tiga tingkat agar klaim kami tidak melampaui bukti:

| Tingkat | Status |
|---|---|
| Prapemrosesan | Terverifikasi identik byte per byte |
| Konfigurasi | Terverifikasi, seluruh parameter tercatat |
| Pelatihan bit per bit | **Tidak diklaim**, karena nondeterminisme GPU (CUDA dan MPS) |

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
git clone https://github.com/galiihajiip/agridata-telepati.git
cd agridata-telepati
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
# Evaluasi pada split valid, sekitar 4 menit di Apple Silicon
python scripts/evaluate.py \
  --weights runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt \
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
  --weights runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt --split valid

# Sensitivitas threshold, dari prediksi tersimpan, beberapa detik
python scripts/threshold_sensitivity.py --split valid
```

### Melatih ulang dari nol

Model final kami latih di Kaggle Notebooks (2x NVIDIA Tesla T4), karena
pelatihan model yang lebih besar dari YOLOv8n tidak realistis di laptop.
Langkah lengkapnya, termasuk cara menyalin dataset ke Kaggle sebagai dataset
privat, ada pada [`docs/kaggle_training.md`](docs/kaggle_training.md). Intinya:

```bash
# Di Mac: salin data siap latih (tanpa symlink) untuk diunggah ke Kaggle
python scripts/export_kaggle_dataset.py --out ~/agridata_kaggle_dataset

# Di notebook Kaggle, GPU T4 x2: sekitar 8,1 jam
python scripts/kaggle_train.py --config configs/kaggle/yolov8s_p2_640_250ep.yaml \
  --data-root /kaggle/input/<dataset-anda>
```

`kaggle_train.py` menghentikan pelatihan sendiri sebelum batas sesi 12 jam
Kaggle dan menyimpan `last.pt` yang dapat dilanjutkan dengan `--resume-from`.

Pelatihan ulang lokal tetap tersedia:

```bash
python scripts/run_final_training.py --config configs/final_model_config.yaml
```

Pada Apple Silicon, jalur ini jauh lebih lambat; YOLOv8n saja memakan 20,84 jam
untuk 100 *epoch*. Sebelum mulai, skrip mencetak seluruh pengungkapan yang diwajibkan, yaitu
*commit* Git, versi pustaka, *seed*, *hash* manifest dataset, pemetaan kelas,
arsitektur, status `pretrained`, seluruh *hyperparameter*, dan perangkat.
Setelah selesai, bobotnya diverifikasi dapat dimuat dan menjalankan inferensi
dari proses Python yang benar-benar bersih.

Karena pelatihan di GPU tidak deterministik, angka hasil pelatihan ulang tidak
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

model = YOLO("runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt")
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
| Berkas | `runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt` |
| Ukuran | 21.754.576 byte |
| SHA-256 | `4dc86ac0e53d2849fb1b79f1a68dcb5284ae6f1e8fef27e4416fa54c6b772a9f` |
| Perangkat pelatihan | Kaggle, 2x NVIDIA Tesla T4, 250 *epoch*, 8,11 jam |

Berkas bobot tidak kami komit ke Git karena merupakan biner. Lihat
[`weights/README.md`](weights/README.md) untuk informasi rilis dan cara
memverifikasi *checksum*.

## Struktur Repository

```
agridata/
  configs/          konfigurasi percobaan, konfigurasi final beku, dan configs/kaggle/ untuk kandidat
  src/agridata/     paket inti: dataset, training, metrics, analysis, visualization
  scripts/          titik masuk CLI untuk setiap tahap pipeline
  notebooks/        notebook submission
  artifacts/
    audit/          audit dataset, pemetaan, reproduktibilitas, kesiapan submission
    reports/        laporan per tahap, evaluasi, profiling, analisis kesalahan
    figures/        figur untuk notebook dan dokumentasi
    experiments/    log 21 percobaan terkontrol
    predictions/    prediksi tersimpan, dipakai analisis deterministik
    candidates/     empat kandidat skala penuh, ensemble, dan alasan pemilihan
    archive/        hasil model YOLOv8n 20, 50, dan 100 epoch yang digantikan
  references/       audit sitasi dan daftar pustaka
  tests/            69 uji unit
  weights/          informasi rilis model dan checksum
  docs/             model card, panduan pelatihan Kaggle/Colab, penanda pernyataan orisinalitas
```

## Kepatuhan terhadap Regulasi

| Ketentuan | Status | Bukti |
|---|---|---|
| Tanpa *external pretrained weights* | Patuh | `build_compliant_model` menolak `pretrained=True` dan argumen menyerupai *checkpoint*, `YOLO_OFFLINE=1` aktif, checkpoint final tercatat `model=yolov8s-p2.yaml` dan `pretrained=False` |
| Tanpa unduhan bobot pretrained oleh pustaka | Patuh | Unduhan `yolo26n.pt` oleh pengecekan AMP Ultralytics diblokir lewat `scripts/kaggle_site/sitecustomize.py` pada seluruh kandidat |
| Hanya dataset resmi | Patuh | Tidak ada dataset lain pada repository maupun rujukan kode |
| Tanpa pemrosesan LLM atau API | Patuh | Seluruh prapemrosesan berupa kode Python deterministik |
| Pemetaan 11 kelas canonical | Patuh | [`canonical_mapping_report.md`](artifacts/audit/canonical_mapping_report.md), nol kategori tak terpetakan |
| *Split* resmi dipertahankan | Patuh | Tidak ada penggabungan atau pengacakan ulang |
| Tanpa kebocoran data | Patuh | Satu duplikat persis ditemukan dan dikeluarkan dari manifest latih |
| Data uji tidak dipakai menyetel | Patuh | Pemilihan kandidat dan ensemble di atas *split* valid, test dievaluasi sekali untuk model terpilih |
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

Tim **Di Bandung Di Ganesha**, Universitas Pembangunan Nasional "Veteran" Jawa Timur.

- **Galih Aji Pangestu** (ketua, [@galiihajiip](https://github.com/galiihajiip))
- **Stevyka Frista Aninda**
- **Putri Ayu Ajeng Nina Zuraida**

Dosen pembimbing: **Andreas Nugroho Sihananto, S.Kom., M.Kom.**
