# TELEPATI 8.0 AgriData Intelligence Race
## Analisis Final, Arah Penyempurnaan Notebook, dan Prompt Claude Code

Dokumen ini menjadi panduan final untuk merapikan paket submission TELEPATI 8.0 AgriData Intelligence Race setelah model, pipeline, audit dataset, evaluasi, dan eksperimen utama telah dikerjakan.

Fokus tahap ini bukan membuat solusi baru dari nol. Fokusnya adalah mengubah project yang sudah matang secara teknis menjadi artefak *data science* yang:

- runtut;
- ilmiah;
- mudah dibaca juri;
- transparan;
- dapat diaudit;
- konsisten antara kode, notebook, README, dan artefak;
- bersih dari artefak pengembangan internal;
- tidak terasa seperti keluaran *LLM*;
- dan tetap mematuhi regulasi kompetisi.

---

# BAGIAN A. KESIMPULAN ANALISIS TEKNIS

## A1. Posisi model saat ini

Model final yang menjadi kandidat utama adalah YOLOv8n yang dilatih dari inisialisasi acak tanpa *external pretrained weights*.

Hasil yang tersedia menunjukkan:

- mAP@0.5 validasi sekitar **0,6277**
- mAP@0.5 test sekitar **0,6145**
- mAP@0.5:0.95 validasi sekitar **0,3905**
- *Precision* validasi sekitar **0,6406**
- *Recall* validasi sekitar **0,6237**

Hasil *per-class AP* menunjukkan variasi performa yang sangat besar. *Narrow brown* mencapai AP sekitar 0,9631, sedangkan *Brown spot* sekitar 0,2909.

Artinya, angka mAP agregat tidak cukup untuk menjelaskan kualitas model. Analisis harus dilanjutkan ke karakteristik dataset dan pola kesalahan model.

## A2. Apakah mAP sekitar 64% dapat disebut kompetitif?

Tidak ada dasar yang cukup untuk menyimpulkan posisi relatif terhadap tim lain karena tidak tersedia distribusi skor peserta atau *leaderboard* yang dapat digunakan sebagai pembanding.

Karena itu jangan menulis:

- "model kami terbaik";
- "model kami paling akurat";
- "model kami pasti masuk tiga besar";
- "0,64 merupakan skor yang sangat tinggi";
- "0,64 cukup untuk menang".

Formulasi ilmiah yang tepat:

> "Hasil validasi menunjukkan mAP@0.5 sebesar 0,6277. Pada *split* test yang tidak digunakan untuk penyetelan, mAP@0.5 mencapai 0,6145. Tidak tersedia informasi skor peserta lain, sehingga performa relatif terhadap tim lain tidak dapat disimpulkan."

Perbedaan validasi dan test sebesar sekitar 0,0132 merupakan temuan positif untuk stabilitas evaluasi, tetapi **tidak boleh disebut sebagai bukti definitif bahwa model bebas dari *overfitting***.

Formulasi yang lebih tepat:

> "Selisih mAP@0.5 yang relatif kecil antara validasi dan test konsisten dengan generalisasi yang cukup stabil pada dua *split* tersebut. Namun, satu evaluasi *held-out* tidak cukup untuk membuktikan bahwa tidak terdapat *overfitting*."

---

# BAGIAN B. MASALAH METODOLOGI PALING PENTING

## B1. Definisi F1 harus dikunci

Dalam riwayat project terdapat F1 lokal 0,3326 dan kemudian F1 *macro* sekitar 0,6181 sampai 0,6383 tergantung konfigurasi inferensi.

Masalahnya bukan sekadar memilih angka yang lebih tinggi.

Masalah utamanya adalah:

> Apakah definisi F1 yang kita gunakan sama dengan definisi yang digunakan evaluator kompetisi?

Materi regulasi yang tersedia menyebut F1 sebagai metrik penilaian, tetapi tidak merinci seluruh aspek averaging secara eksplisit.

Karena itu jangan menulis:

> F1 resmi = 63,83%

kecuali definisi tersebut benar-benar telah dikonfirmasi.

Gunakan istilah:

> "*F1-score* lokal (*macro*)"

atau:

> "F1 *macro* berdasarkan implementasi evaluasi lokal"

lalu jelaskan:

- *confidence threshold*;
- NMS IoU;
- definisi averaging;
- cara menghitung precision;
- cara menghitung recall;
- sumber implementasi.

Jika kemudian panitia memberikan definisi resmi, gunakan definisi panitia sebagai sumber kebenaran.

## B2. Mengapa F1 0,3326 perlu dijelaskan, bukan dihapus

Riwayat 0,3326 merupakan bagian dari sejarah metodologi project.

Nilai itu muncul dari implementasi lokal terdahulu pada *threshold* tetap dan metode agregasi tertentu. Nilai tersebut kemudian diketahui tidak konsisten dengan precision dan recall pada implementasi evaluasi yang berbeda.

Kesalahan tersebut harus dijelaskan sebagai:

> koreksi metodologi evaluasi

bukan disembunyikan.

Namun angka historis harus diberi label sebagai hasil versi lama, bukan skor final.

Tujuannya agar juri tidak melihat dua angka F1 dan menganggap project tidak konsisten.

---

# BAGIAN C. NMS 0,5

Eksperimen pada validasi menunjukkan bahwa perubahan NMS IoU dari 0,7 menjadi 0,5 meningkatkan hasil tanpa mengubah bobot model.

Hasil lokal:

| NMS IoU | mAP@0.5 | F1 *macro* |
|---:|---:|---:|
| 0,5 | 0,6401 | 0,6383 |
| 0,6 | 0,6380 | 0,6325 |
| 0,7 | 0,6277 | 0,6181 |
| 0,8 | 0,6038 | 0,5795 |

Jangan menulis:

> "mendapat peningkatan gratis"

karena itu bukan bahasa laporan ilmiah.

Gunakan:

> "Pada data validasi, perubahan ambang NMS IoU dari 0,7 menjadi 0,5 meningkatkan mAP@0.5 dari 0,6277 menjadi 0,6401 tanpa mengubah bobot model."

Yang paling penting, konfigurasi NMS final harus benar-benar berada di pipeline yang dijalankan juri. Jangan menghitung skor dengan NMS 0,5 tetapi notebook atau script final masih menggunakan 0,7.

---

# BAGIAN D. EKSPERIMEN RESOLUSI 960

Eksperimen 960 tidak menjadi prioritas utama.

Alasannya:

1. biaya komputasinya sangat besar;
2. sinyal awal berada jauh di bawah model 640;
3. training berlangsung sekitar 14,7 jam;
4. eksperimen mengubah resolusi dan batch secara bersamaan;
5. akibatnya, efek resolusi tidak dapat diisolasi secara bersih.

Karena dua faktor berubah sekaligus:

```text
imgsz: 640 → 960
batch: 16 → 8
```

maka jika performa berubah, kita tidak boleh mengatakan perubahan tersebut disebabkan resolusi saja.

Model 640 telah memberikan hasil yang nyata dan tervalidasi. Karena itu, pada tahap finalisasi submission, model 640 harus diperlakukan sebagai *frozen candidate* kecuali ditemukan masalah validitas.

Jangan mengorbankan paket submission yang sudah matang untuk eksperimen yang membutuhkan berjam-jam dan belum menunjukkan bukti kuat akan mengungguli model final.

---

# BAGIAN E. TEMUAN DATASET YANG PALING BERHARGA

Dataset terdiri dari:

- 13.298 citra;
- 27.721 anotasi;
- 11 kelas canonical;
- 3 *split* resmi: train, valid, test;
- anotasi COCO.

Distribusi:

| Split | Citra | Anotasi |
|---|---:|---:|
| Train | 10.133 | 20.163 |
| Valid | 2.106 | 4.888 |
| Test | 1.059 | 2.670 |

Dataset memiliki ketidakseimbangan kelas yang nyata.

Kelas terbanyak:

> Brown spot = 5.010 *instance* train

Kelas tersedikit:

> Narrow brown = 222 *instance* train

Namun:

- Narrow brown AP sekitar 0,9631
- Brown spot AP sekitar 0,2909

Korelasi Pearson antara jumlah *instance* train dan AP@0.5 per kelas sekitar -0,5074.

Interpretasi:

> jumlah *instance* yang besar tidak otomatis berarti kelas tersebut mudah dideteksi.

Ini merupakan temuan penting karena mencegah narasi sederhana:

> "Semakin banyak data, semakin tinggi performa."

Data aktual justru menunjukkan bahwa hubungan performa dipengaruhi oleh karakteristik lain.

---

# BAGIAN F. RANTAI SEBAB-AKIBAT YANG HARUS MUNCUL DI NOTEBOOK

Notebook final harus memiliki rantai analisis berikut:

```text
Distribusi kelas
        ↓
Distribusi ukuran objek
        ↓
Kepadatan objek pada citra
        ↓
Kesulitan lokalisasi
        ↓
Pola false negative
        ↓
Perbedaan AP antar kelas
        ↓
Interpretasi performa akhir
```

Temuan yang mendukung rantai tersebut:

- objek <1% luas citra mencapai sekitar 38,1% pada train;
- 43,3% pada valid;
- 46,8% pada test;
- terdapat citra dengan puluhan objek;
- tiga citra terpadat memiliki sekitar 178, 126, dan 90 anotasi;
- *false negative* merupakan komponen kesalahan terbesar;
- *false negative* pada adegan padat lebih tinggi dibanding adegan jarang;
- objek yang terlewat memiliki median luas lebih kecil daripada median seluruh objek;
- Brown spot memiliki AP terendah.

Namun, narasi harus tetap berhati-hati.

Jangan menyatakan:

> "Objek kecil menyebabkan rendahnya AP."

Lebih tepat:

> "Proporsi objek berukuran kecil dan tingginya kepadatan objek merupakan karakteristik data yang konsisten dengan pola *false negative* yang lebih tinggi. Temuan ini memberikan penjelasan yang masuk akal terhadap kesulitan lokalisasi yang terlihat pada hasil per kelas."

---

# BAGIAN G. ERROR ANALYSIS

Analisis kesalahan adalah salah satu aset terkuat project.

Komposisi kesalahan:

- *false negative* sekitar 63,5%;
- *false positive* terhadap latar sekitar 34,9%;
- salah kelas sekitar 1,5%.

Jika proporsi ini berasal dari definisi error tertentu, definisinya harus dijelaskan.

Implikasi yang dapat dibahas:

> kesalahan lebih dominan pada tahap menemukan objek daripada pada pembedaan kelas setelah objek berhasil dideteksi.

Tetapi klaim tersebut harus selalu merujuk pada definisi error yang digunakan.

Temuan lain:

- median bbox yang terlewat sekitar 3.376 px²;
- median keseluruhan sekitar 7.051,6 px²;
- rasio sekitar 0,48;
- *false negative rate* pada adegan padat sekitar 0,7981;
- *false negative rate* pada adegan jarang sekitar 0,4542;
- hanya sekitar 22,4% citra valid yang seluruh objeknya terdeteksi tanpa kesalahan.

Ini harus dibuat sebagai bukti visual dan kuantitatif.

---

# BAGIAN H. KESIMPULAN DATA SCIENCE

Kesimpulan yang ideal bukan:

> "Model mencapai 64% sehingga model bagus."

Kesimpulan harus berbentuk:

> "Model YOLOv8n yang dilatih dari inisialisasi acak berhasil mendeteksi 11 kelas canonical pada dataset resmi dengan mAP@0.5 validasi sekitar 0,63. Performa antar kelas sangat tidak merata. Kelas seperti Narrow brown dan False smut memiliki AP tinggi, sedangkan Brown spot memiliki AP jauh lebih rendah. Profiling dataset menunjukkan ketidakseimbangan kelas, proporsi objek kecil yang besar, dan kepadatan objek yang tinggi pada sebagian citra. Analisis kesalahan memperlihatkan dominasi *false negative*, terutama pada objek berukuran kecil dan adegan padat. Dengan demikian, keterbatasan performa tidak dapat dijelaskan hanya oleh jumlah data, tetapi perlu dipahami bersama geometri objek, kepadatan adegan, dan kapasitas model yang dilatih dari nol."

Ini jauh lebih kuat secara ilmiah karena menghubungkan:

DATA → MODEL → ERROR → RESULT.

---

# BAGIAN I. STRATEGI FINALISASI

Urutan prioritas:

```text
1. Kunci model 640
2. Kunci konfigurasi inferensi
3. Kunci definisi F1
4. Regenerasi artefak metric dari source of truth
5. Eksekusi ulang notebook dari awal
6. Clean environment test
7. README final
8. Submission checklist
9. GitHub Release
10. Final compliance audit
```

Jangan melakukan:

```text
training → notebook → README → training lagi → metric berubah → notebook berubah → README berubah
```

Semua artefak final harus dibangun dari satu *source of truth*.

---

# BAGIAN J. PROMPT UTAMA UNTUK CLAUDE CODE

Gunakan prompt berikut langsung pada Claude Code.

```text
Kita masuk ke fase FINAL SUBMISSION POLISH untuk project TELEPATI 8.0 AgriData Intelligence Race.

Baca terlebih dahulu:
1. TELEPATI_8_AgriData_Master_Context_for_Claude.md
2. notebook final saat ini
3. audit report
4. evaluation artifacts
5. experiment artifacts
6. README
7. source code
8. configuration
9. Git history

Jangan langsung mengedit.

Tujuan fase ini:
mengubah repository dan notebook yang sudah bekerja menjadi paket submission yang bersih, ilmiah, mudah dibaca juri, dapat diaudit, dan konsisten.

============================================================
PRIORITAS
============================================================

Prioritas:

1. kepatuhan kompetisi
2. kebenaran data
3. reproduktibilitas
4. integritas validasi
5. konsistensi metric
6. kualitas analisis
7. kualitas penulisan
8. kebersihan repository

JANGAN mengejar peningkatan performa model pada fase ini.

JANGAN melakukan full retraining kecuali menemukan masalah validitas yang benar-benar memaksa retraining.

Model 640 adalah kandidat final yang dibekukan.

============================================================
PERAN
============================================================

Bertindak sebagai:

Senior Data Scientist
+
Senior Computer Vision Research Engineer
+
ML Engineer
+
Research Methodology Reviewer
+
Competition Submission Auditor
+
Technical Editor

Gunakan pola pikir seorang profesional berpengalaman puluhan tahun:

- jangan terpaku pada solusi sebelum memahami data;
- jangan mengambil kesimpulan dari satu angka;
- cari akar masalah;
- bedakan observasi, inferensi, dan klaim kausal;
- selalu cari bukti;
- jangan mengarang;
- akui keterbatasan.

============================================================
ATURAN BAHASA
============================================================

Seluruh artefak submission harus menggunakan Bahasa Indonesia.

Istilah asing dalam narasi harus ditulis dengan *italic*.

Contoh:

*computer vision*
*object detection*
*bounding box*
*baseline*
*inference*
*data leakage*
*false positive*
*false negative*
*recall*
*precision*

Nama kelas canonical tidak diterjemahkan.

Jangan menggunakan karakter Unicode em dash:

U+2014 / -

Target:
0 occurrence pada submission artifacts.

Master specification internal boleh dikecualikan dari scan akhir jika memang merupakan dokumen kerja internal.

============================================================
BERSIHKAN REPOSITORY
============================================================

Repository yang dikumpulkan adalah repository submission.

Karena itu lakukan audit seluruh file yang tracked.

Identifikasi file yang hanya berguna sebagai prompt internal, catatan percakapan, atau artefak pengembangan.

Contoh kandidat yang perlu diperiksa:

- master prompt untuk Claude
- prompt block
- catatan instruksi AI
- file "conversation"
- file "prompt"
- draft internal
- laporan yang jelas-jelas hanya berisi instruksi ke agent
- scratch notebook
- temporary experiment notes yang tidak dibutuhkan juri

JANGAN menghapus file hanya berdasarkan namanya.

Untuk setiap kandidat:
1. baca isinya;
2. tentukan apakah dibutuhkan juri;
3. tentukan apakah dibutuhkan oleh pipeline;
4. tentukan apakah dibutuhkan untuk audit;
5. jika hanya prompt/internal instruction, keluarkan dari repository submission.

Jangan menghapus:
- source code yang diperlukan;
- notebook final;
- README;
- model metadata;
- evaluation artifact yang menjadi source of truth;
- audit evidence yang memang relevan;
- requirements;
- konfigurasi final;
- legal/originality files;
- file yang diperlukan agar notebook berjalan.

Buat laporan:
`artifacts/audit/repository_cleanup.md`

Isi:
- file dipertahankan
- file dipindahkan/diarsipkan
- file dihapus
- alasan
- apakah file diperlukan juri atau hanya internal

============================================================
ATURAN "BERSIH DARI UNSUR AI"
============================================================

Bersihkan artefak submission dari meta-language seperti:

- "As an AI"
- "Claude"
- "ChatGPT"
- "generated by AI"
- "prompt"
- "assistant"
- "instruction to model"
- "LLM"
- "I was asked to"
- "we instructed the model"
- "generated automatically by Claude"

JANGAN memalsukan provenance.

Jika regulasi memerlukan pengungkapan tertentu, jangan menghapusnya.

Tujuan bagian ini adalah menghilangkan artefak percakapan dan meta-prompt yang tidak relevan bagi juri, bukan menyembunyikan fakta yang diwajibkan oleh panitia.

============================================================
BERSIHKAN KOMENTAR DAN DOCSTRING
============================================================

Audit seluruh Python source.

Hapus komentar yang:
- conversational;
- terlalu panjang;
- menjelaskan hal yang jelas;
- berupa catatan pribadi;
- berupa prompt;
- mengandung gaya percakapan AI;
- berisi "TODO" yang sudah tidak relevan;
- menyebut agent/LLM secara tidak perlu.

Pertahankan komentar yang benar-benar membantu memahami:
- alasan teknis;
- constraint kompetisi;
- keputusan reproducibility;
- workaround platform;
- bentuk data;
- alasan parameter.

Docstring harus terdengar seperti dokumentasi software profesional.

Contoh buruk:
"Let's make sure this works..."

Contoh baik:
"Validates that all annotations reference an existing image and that bounding boxes remain within image boundaries."

Namun gunakan Bahasa Indonesia:

"Memvalidasi bahwa seluruh anotasi merujuk pada citra yang tersedia dan bahwa seluruh *bounding box* berada di dalam batas citra."

============================================================
NOTEBOOK FINAL
============================================================

Bangun notebook sebagai dokumen penelitian.

Notebook harus dibaca dari atas ke bawah seperti cerita.

Urutan:

# TELEPATI 8.0: AgriData Intelligence Race

## 1. Latar Belakang dan Tujuan
## 2. Rumusan Masalah
## 3. Gambaran Solusi
## 4. Lingkungan Eksekusi dan Reproduktibilitas
## 5. Dataset dan Sumber Data
## 6. Eksplorasi dan Profiling Dataset
### 6.1 Struktur Dataset
### 6.2 Distribusi Split
### 6.3 Distribusi Kelas
### 6.4 Ketidakseimbangan Kelas
### 6.5 Analisis Bounding Box
### 6.6 Resolusi Citra
### 6.7 Missingness dan Validitas
### 6.8 Duplicate dan Risiko Leakage
### 6.9 Visualisasi Dataset
### 6.10 Implikasi Data terhadap Pemodelan
## 7. Canonical Class Mapping
## 8. Persiapan dan Preprocessing Data
## 9. Strategi Eksperimen
## 10. Baseline
## 11. Eksperimen Terkontrol
## 12. Pemilihan Konfigurasi Final
## 13. Pelatihan Model Final
## 14. Evaluasi Model
## 15. Analisis Per Kelas
## 16. Analisis Kesalahan
## 17. Hubungan Karakteristik Data dengan Performa
## 18. Kelebihan dan Keterbatasan
## 19. Reproduktibilitas dan Audit
## 20. Kesimpulan
## 21. Daftar Pustaka
## 22. Lampiran Teknis

============================================================
ALUR CERITA
============================================================

Setiap bagian harus menjawab:

"Apa yang baru saja kita temukan, dan mengapa pembaca perlu peduli?"

Gunakan bridging.

Contoh:

Setelah menunjukkan ketidakseimbangan kelas:
"Namun, frekuensi kelas saja belum menjelaskan kesulitan deteksi. Dua kelas dengan jumlah data berbeda dapat memiliki karakteristik objek yang sangat berbeda. Karena itu, pemeriksaan berikutnya beralih dari 'berapa banyak objek' ke 'seperti apa ukuran objek yang harus ditemukan model'."

Setelah bbox:
"Temuan ini penting karena model tidak hanya harus mengenali kelas, tetapi juga menemukan lokasi objek. Jika objek berukuran sangat kecil, sedikit kesalahan pada lokasi dapat menyebabkan perubahan IoU yang lebih besar. Karena itu, distribusi geometri objek perlu dibaca bersama hasil *error analysis*."

Setelah error analysis:
"Temuan tersebut membawa kita kembali ke pertanyaan awal: apakah nilai mAP agregat yang diperoleh terutama dibatasi oleh kemampuan klasifikasi atau kemampuan menemukan objek? Bagian berikut menjawab pertanyaan tersebut."

============================================================
DATA STORY
============================================================

Notebook harus menjawab:

- dataset seperti apa?
- apa yang paling menonjol?
- apa masalah datanya?
- apa dampaknya?
- apa yang dilakukan?
- apakah tindakan tersebut membantu?
- apa yang masih menjadi masalah?

Jangan membuat EDA sebagai kumpulan grafik.

Setiap grafik harus punya fungsi.

============================================================
VISUALISASI WAJIB
============================================================

Tambahkan atau pastikan tersedia:

1. jumlah citra per split;
2. jumlah anotasi per split;
3. jumlah instance per kelas;
4. jumlah gambar per kelas;
5. rasio ketidakseimbangan;
6. distribusi area bbox;
7. distribusi relative bbox area;
8. distribusi bbox width/height;
9. distribusi resolusi gambar;
10. audit missingness;
11. duplicate/leakage summary;
12. contoh citra satu objek;
13. contoh citra multi-object;
14. contoh objek kecil;
15. contoh adegan padat;
16. contoh prediction benar;
17. contoh false positive;
18. contoh false negative;
19. AP per kelas;
20. hasil eksperimen;
21. training curves;
22. sensitivity NMS atau threshold jika dipakai.

Jangan memenuhi notebook dengan grafik tanpa interpretasi.

============================================================
SOURCE OF TRUTH UNTUK ANGKA
============================================================

Jangan mengetik angka final secara manual jika dapat diambil dari JSON atau artifact.

Gunakan source of truth.

Ideal:

evaluation_valid.json
evaluation_test.json
per_class_metrics.json
training results
experiment registry

Notebook membaca artefak tersebut.

Dengan demikian jika metric berubah, notebook otomatis mengikuti source of truth.

============================================================
KONFLIK METRIC
============================================================

Cari seluruh repository:

0.5620
0.6277
0.3326
0.6181
0.6383
0.6401
63.83
64.01

Buat satu tabel provenance.

Bedakan:

- model lama 20 epoch;
- model final 50 epoch;
- metric lama;
- metric baru;
- konfigurasi NMS;
- definisi F1.

Tidak boleh ada dua nilai yang tampak seperti dua "final score".

Riwayat 20 epoch boleh dipertahankan sebagai bagian eksperimen historis.

Tetapi beri label:

"Hasil historis"

dan jangan meletakkannya sejajar dengan hasil final tanpa konteks.

============================================================
F1
============================================================

Jangan menyebut F1 lokal sebagai F1 resmi panitia tanpa dasar.

Nyatakan secara lengkap:

- jenis averaging;
- threshold;
- NMS;
- sumber perhitungan;
- apakah itu metric resmi atau diagnostik lokal.

Jika definisi panitia tidak ditemukan:
buat caveat yang eksplisit.

Jangan mengubah definisi metric hanya karena menghasilkan angka yang lebih tinggi.

============================================================
NMS
============================================================

Jika NMS 0,5 digunakan pada score final:
pastikan seluruh pipeline final menggunakan 0,5.

Verifikasi:
- notebook;
- evaluate.py;
- compute_official_metrics.py;
- README;
- metadata;
- metric artifacts.

Jangan ada dokumen yang masih mengatakan 0,7 sebagai konfigurasi final.

============================================================
MODEL 960
============================================================

Perlakukan eksperimen 960 sebagai eksperimen eksploratif/historis.

Jangan menjadikannya final candidate kecuali ada bukti aktual yang mengungguli model 640 dengan prosedur evaluasi yang valid.

Jika training 960 masih berjalan:
jangan mengubah model final 640.

Jika eksperimen 960 perlu dihentikan demi submission:
catat secara transparan sebagai eksperimen yang tidak dilanjutkan karena biaya komputasi dan sinyal awal.

Jangan menghapus sejarah eksperimen.

============================================================
ANALISIS DATA KE PERFORMA
============================================================

Buat bagian khusus:

# Hubungan Karakteristik Dataset dengan Performa

Minimal analisis:

1. instance per kelas vs AP kelas;
2. bbox size vs missed object;
3. scene density vs false negative rate;
4. kelas dominan vs AP;
5. small-object proportion vs error pattern.

Untuk setiap hubungan:

- tampilkan data;
- jelaskan metode;
- jelaskan keterbatasan;
- hindari klaim kausal jika hanya korelasi.

Jika hanya 11 kelas:
jelaskan bahwa n=11 kecil.

============================================================
ERROR ANALYSIS
============================================================

Buat contoh visual terstruktur:

### Contoh keberhasilan

- ground truth;
- prediction;
- confidence;
- interpretasi.

### Contoh kegagalan

- ground truth;
- prediction;
- confidence;
- jenis error;
- kemungkinan faktor terkait.

Pastikan sample berasal dari data aktual.

============================================================
KETERBATASAN
============================================================

Jangan menyembunyikan:

- training dari nol;
- MPS nondeterminism;
- keterbatasan resource;
- small object;
- class imbalance;
- duplicate candidate;
- tidak adanya external validation;
- F1 definition caveat;
- eksperimen skala penyaringan;
- eksperimen 960 yang belum selesai jika masih relevan.

Keterbatasan harus ditulis sebagai batas penelitian.

============================================================
REFERENSI ILMIAH
============================================================

Jika notebook menggunakan klaim dari jurnal:
gunakan *in-text citation* APA 7.

Setiap citation wajib:
- benar;
- diverifikasi;
- relevan;
- benar-benar mendukung klaim.

Jangan menambah citation hanya untuk dekorasi.

Jika citation berasal dari dokumentasi framework:
gunakan dokumentasi resmi.

Tambahkan:

## Daftar Pustaka

Gunakan format APA 7.

Gunakan tautan yang dapat diklik.

============================================================
LINK INTERNAL REPOSITORY
============================================================

Jika notebook/README merujuk ke file project lain, gunakan relative Markdown links.

Contoh:

[Audit dataset](../artifacts/audit/dataset_audit.md)

[Konfigurasi final](../configs/final_model_config.yaml)

[Evaluasi validasi](../artifacts/evaluation/evaluation_valid.json)

[Ringkasan eksperimen](../artifacts/reports/experiment_summary.md)

[Source preprocessing](../src/agridata/dataset/convert.py)

Jangan menggunakan:
- absolute local path;
- path `/Users/...`;
- link ke file lokal yang hanya bekerja di laptop.

Pastikan semua link internal benar dan dapat dibuka dari repository GitHub.

Untuk GitHub Release, gunakan link release final yang benar-benar diterbitkan.

============================================================
README
============================================================

README harus terlihat seperti repository penelitian/kompetisi yang selesai.

Bukan catatan development.

Susunan:

# TELEPATI 8.0 - AgriData Intelligence Race

## Ringkasan

## Latar Belakang

## Pertanyaan Penelitian

## Dataset

## Canonical Class Mapping

## Profiling Dataset

## Metodologi

## Preprocessing

## Model

## Eksperimen

## Hasil

## Error Analysis

## Keterbatasan

## Reproduktibilitas

## Instalasi

## Cara Menjalankan

## Inferensi

## Model Weights

## Struktur Repository

## Kepatuhan terhadap Regulasi

## Referensi

README harus singkat dibanding notebook, tetapi seluruh informasi penting dapat ditelusuri ke notebook atau artefak.

============================================================
REPOSITORY CLEANUP
============================================================

Target repository:

- tidak ada prompt;
- tidak ada catatan percakapan;
- tidak ada file scratch;
- tidak ada output notebook lama yang membingungkan;
- tidak ada metric lama yang diberi nama seperti final jika bukan final;
- tidak ada dataset mentah yang ter-commit jika regulasi tidak mengharuskannya;
- tidak ada secret;
- tidak ada absolute path;
- tidak ada em dash pada submission artifact;
- tidak ada komentar AI yang tidak perlu.

Namun:
jangan menghapus bukti eksperimen yang relevan.

Gunakan:
archive/
atau
artifacts/archive/

untuk artifact historis yang memang perlu dipertahankan tetapi tidak perlu ditonjolkan sebagai final.

============================================================
NOTEBOOK CLEANUP
============================================================

Audit semua 127 sel notebook.

Target:

- tidak ada stale output;
- tidak ada output dari run lama yang bertentangan;
- tidak ada English narrative;
- tidak ada em dash;
- tidak ada absolute local path;
- tidak ada debug print yang tidak perlu;
- tidak ada prompt;
- tidak ada percakapan;
- tidak ada temporary experiments yang seolah final;
- tidak ada duplicate chart;
- tidak ada plot tanpa interpretasi.

Notebook harus dapat:
Kernel restart → Run All

Untuk mode default:
load final weights dan evaluasi.

Untuk reproduksi penuh:
training branch tetap tersedia tetapi tidak harus dijalankan pada mode default.

============================================================
KOMENTAR / DOCSTRING
============================================================

Semua komentar source harus:
- Bahasa Indonesia;
- singkat;
- profesional;
- teknis;
- tidak repetitif;
- tidak terasa seperti komentar AI.

Jangan mengubah source logic hanya demi gaya.

============================================================
AUDIT FINAL
============================================================

Buat script atau checklist final untuk memeriksa:

1. em dash count = 0 pada submission artifacts
2. no prompt files
3. no secret
4. no absolute path
5. final metric consistency
6. final checkpoint consistency
7. model checksum
8. dataset manifest hash
9. canonical 11 classes
10. NMS configuration consistency
11. F1 definition consistency
12. notebook Run All
13. README links
14. internal links
15. Git status
16. Git history
17. model release existence

============================================================
GIT
============================================================

Setiap perubahan harus dibuat sebagai commit kecil dan bermakna.

Gunakan semantic commit:

cleanup(repository): remove internal prompt and development artifacts

docs(notebook): polish final notebook narrative and analysis

feat(eda): finalize dataset profiling visuals and interpretation

docs(results): align metrics and error analysis with final evaluation

docs(readme): finalize competition submission documentation

test(submission): verify final artifacts and reproducibility

Jangan membuat commit seperti:
- update
- final
- fix stuff
- changes
- tes
- coba

============================================================
JANGAN MENGGUNAKAN EM DASH
============================================================

Cari:

grep -RIl $'\u2014' .

Target pada submission artifacts:
0.

============================================================
FINAL FREEZE
============================================================

Sebelum menyatakan project selesai:

- jangan ubah model weights;
- jangan training ulang;
- jangan ubah dataset;
- jangan mengubah score secara manual;
- jangan menghapus evidence penting;
- jangan mengarang reference;
- jangan mengarang causal explanation.

Semua angka final harus berasal dari source of truth.

============================================================
FINAL REPORT
============================================================

Buat:

artifacts/audit/final_submission_readiness.md

Isi:

## Kondisi Paket
## Final Model
## Final Metrics
## Dataset
## Reproduktibilitas
## Repository
## Notebook
## README
## Weights
## References
## Compliance
## Remaining Risks

Jika ada item belum diverifikasi:
gunakan status:

PASS
WARN
FAIL
NOT VERIFIED

Jangan menulis PASS tanpa bukti.

============================================================
STOP RULE
============================================================

Kerjakan per blok.

Jangan otomatis mengerjakan seluruh block sekaligus.

Setelah setiap block:

- test;
- audit;
- git status;
- commit;
- report;
- stop.

Jika menemukan masalah yang memerlukan keputusan saya:
STOP.

Jangan mengambil keputusan diam-diam.

============================================================
MULAI
============================================================

Mulai dari:

BLOCK 1:
REPOSITORY CLEANUP AUDIT + NOTEBOOK FORENSIC REVIEW

Tugas:
1. audit repository;
2. audit notebook;
3. identifikasi file prompt/internal;
4. identifikasi stale metric;
5. identifikasi stale output;
6. identifikasi English prose;
7. identifikasi em dash;
8. identifikasi absolute path;
9. identifikasi inconsistency metric;
10. identifikasi artifact yang harus dipertahankan.

JANGAN memperbaiki dulu.

Hanya audit.

Buat:
artifacts/audit/final_polish_precheck.md

Setelah selesai:
STOP.


---

# BAGIAN K. CHECKLIST KUALITAS AKHIR

## Kualitas ilmiah

- [ ] Ada pertanyaan penelitian yang jelas.
- [ ] Dataset dianalisis sebelum model dibahas.
- [ ] Ada hubungan antara karakteristik dataset dan hasil.
- [ ] Klaim kausal tidak dibuat dari korelasi saja.
- [ ] Keterbatasan diakui.
- [ ] Angka dapat ditelusuri.
- [ ] Hasil per kelas dianalisis.
- [ ] *Error analysis* tersedia.
- [ ] Kesimpulan menjawab pertanyaan yang diajukan.

## Kualitas data

- [ ] Jumlah train/valid/test benar.
- [ ] Canonical mapping benar.
- [ ] Missingness dilaporkan.
- [ ] Invalid annotation dilaporkan.
- [ ] Duplicate dilaporkan.
- [ ] Leakage diperiksa.
- [ ] Distribusi kelas divisualisasikan.
- [ ] Distribusi bbox divisualisasikan.
- [ ] Resolusi citra dianalisis.

## Kualitas model

- [ ] Model final jelas.
- [ ] Bobot final jelas.
- [ ] Tidak ada external pretrained weights.
- [ ] Konfigurasi final konsisten.
- [ ] NMS konsisten.
- [ ] F1 definition konsisten.
- [ ] Metric source of truth tunggal.
- [ ] Per-class AP tersedia.
- [ ] Training curve tersedia.
- [ ] Error analysis tersedia.

## Kualitas notebook

- [ ] Bahasa Indonesia.
- [ ] Istilah asing ditulis *italic*.
- [ ] Tidak ada em dash.
- [ ] Tidak ada prompt.
- [ ] Tidak ada komentar percakapan.
- [ ] Tidak ada stale output.
- [ ] Tidak ada absolute path.
- [ ] Run All berhasil.
- [ ] Narasi mengalir.
- [ ] Bridging antar bagian jelas.
- [ ] Setiap grafik dijelaskan.

## Kualitas repository

- [ ] Tidak ada prompt internal.
- [ ] Tidak ada scratch file.
- [ ] Tidak ada secret.
- [ ] Tidak ada dataset mentah yang tidak seharusnya masuk Git.
- [ ] README bersih.
- [ ] requirements konsisten.
- [ ] commit history wajar.
- [ ] model weights tersedia melalui mekanisme submission.
- [ ] internal links aktif.
- [ ] GitHub Release dapat diakses.

---

# BAGIAN L. GAYA NARASI YANG DIINGINKAN

Notebook harus terasa seperti seorang *data scientist* sedang mengajak juri mengikuti proses berpikir.

Bukan:

> "Berikut grafik distribusi kelas."

Lalu grafik.

Lebih baik:

> "Sebelum memilih konfigurasi model, kami terlebih dahulu memeriksa apakah data memberikan kesempatan belajar yang relatif seimbang bagi setiap kelas. Pemeriksaan ini penting karena mAP agregat dapat terlihat cukup tinggi meskipun beberapa kelas tertentu hampir tidak terdeteksi. Hasil distribusi *instance* berikut menunjukkan bahwa kondisi tersebut memang perlu diperhatikan."

Lalu grafik.

Setelah grafik:

> "Brown spot mendominasi jumlah *instance*, sedangkan Narrow brown memiliki jumlah observasi yang jauh lebih sedikit. Namun, perbedaan jumlah ini nantinya tidak berbanding lurus dengan performa, sehingga tahap berikutnya perlu memeriksa ukuran dan kepadatan objek."

Kemudian pindah ke bbox.

Ini yang membuat notebook memiliki *story*.

---

# BAGIAN M. BRIDGING ANTAR BAGIAN

Gunakan bridging seperti:

### Dari masalah ke data

> "Masalah yang ingin diselesaikan menentukan informasi apa yang harus tersedia pada data. Karena tugasnya adalah *object detection*, label kelas saja tidak cukup; lokasi setiap objek menjadi bagian penting dari informasi yang harus dipelajari model."

### Dari data ke preprocessing

> "Setelah struktur dan kualitas data dipastikan, langkah berikutnya bukan langsung memilih model, melainkan memastikan bahwa representasi data yang masuk ke model tidak kehilangan informasi yang dibutuhkan untuk deteksi."

### Dari preprocessing ke model

> "Dengan data yang telah tervalidasi dan dipetakan ke 11 kelas canonical, persoalan berikutnya adalah menentukan model yang dapat dilatih dari nol sekaligus masih sesuai dengan keterbatasan komputasi yang tersedia."

### Dari model ke eksperimen

> "Model awal memberikan titik acuan, tetapi satu konfigurasi tidak cukup untuk menyimpulkan bahwa pilihan hiperparameter telah tepat. Karena itu perubahan dilakukan secara terkontrol agar dampak masing-masing faktor dapat dibaca."

### Dari eksperimen ke hasil

> "Setelah konfigurasi final dipilih, evaluasi tidak berhenti pada satu angka agregat. Kami perlu melihat apakah performa tersebut berlaku relatif merata pada seluruh kelas dan pada kondisi visual yang berbeda."

### Dari hasil ke error analysis

> "Perbedaan AP antar kelas menunjukkan bahwa masih terdapat pola kegagalan yang perlu dijelaskan. Karena itu, analisis berikutnya beralih dari 'berapa tinggi skor' menjadi 'di mana model masih gagal dan apa karakteristik citranya'."

### Dari error ke kesimpulan

> "Temuan tersebut memungkinkan kita kembali ke karakteristik awal dataset dan melihat hubungan antara kondisi data, strategi pemodelan, dan pola kesalahan yang akhirnya membentuk performa agregat."

---

# BAGIAN N. PRINSIP TERAKHIR

Notebook yang sempurna bukan notebook yang menyatakan bahwa semua keputusan benar.

Notebook yang baik adalah notebook yang menunjukkan:

- keputusan apa yang dibuat;
- bukti apa yang mendasarinya;
- keputusan mana yang berhasil;
- keputusan mana yang tidak berhasil;
- apa yang diketahui;
- apa yang belum diketahui;
- dan mengapa angka akhir memiliki bentuk seperti yang terlihat.

Target utama:

```text
DATA
  ↓
UNDERSTANDING
  ↓
QUALITY
  ↓
PREPROCESSING
  ↓
MODELING
  ↓
EXPERIMENT
  ↓
EVALUATION
  ↓
ERROR ANALYSIS
  ↓
ROOT-CAUSE INTERPRETATION
  ↓
LIMITATION
  ↓
CONCLUSION
```

Semua bagian harus saling menyambung.

Tidak boleh ada bagian yang terasa seperti tempelan.

# END
