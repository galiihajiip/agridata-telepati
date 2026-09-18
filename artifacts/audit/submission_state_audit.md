# Audit Kondisi Paket Submission (BLOCK A)

Dokumen ini merupakan audit menyeluruh terhadap kondisi paket *submission*
sebelum dilakukan perubahan apa pun pada notebook, README, maupun dokumen
lain. Tidak ada file naratif yang diubah pada block ini. Tidak ada *training*
ulang, tidak ada perubahan *hyperparameter*, dan tidak ada perubahan pada
*model weights*.

Tanggal audit: 19 September 2026
Commit saat audit dijalankan: `ddb26a3af29c0895de8c6692bf2f94b62a4acd67`

## 1. Ringkasan Temuan

| No | Temuan | Tingkat | Status |
|---:|---|---|---|
| 1 | Konflik nilai mAP@0.5 (0,5620 vs 0,6277) pada notebook | Kritis | Penyebab teridentifikasi, perlu diperbaiki pada BLOCK C |
| 2 | Perbedaan *commit* antara *training* dan *evaluation* | Sedang | Terverifikasi valid, perlu didokumentasikan |
| 3 | Nilai *F1* lokal tidak stabil antar eksekusi (4 sampel berbeda) | Sedang | Perlu penyajian sebagai rentang, bukan angka tunggal |
| 4 | Artefak evaluasi di disk tidak sinkron dengan *output* tersimpan di notebook | Sedang | Perlu eksekusi ulang terkontrol pada BLOCK H |
| 5 | Seluruh narasi notebook masih berbahasa Inggris (20 dari 20 sel *markdown*) | Kritis untuk regulasi bahasa | Perlu penulisan ulang pada BLOCK C |
| 6 | Terdapat 386 karakter *em dash* pada repository | Tinggi | Perlu pembersihan pada BLOCK G |
| 7 | Notebook belum memiliki *profiling* dataset yang memadai | Tinggi | Perlu penambahan pada BLOCK B dan BLOCK C |
| 8 | *Path* absolut personal muncul pada artefak yang dihasilkan otomatis | Rendah | Dapat diterima, perlu penjelasan |
| 9 | Tidak ditemukan *secret*, *API key*, maupun penanda TODO | Baik | Tidak ada tindakan |
| 10 | *Source code* bebas dari *path* absolut personal | Baik | Tidak ada tindakan |

## 2. ISSUE 1: Konflik Nilai mAP@0.5

### Hasil penelusuran

Pencarian dilakukan terhadap seluruh repository untuk pola `0.5620` dan
`0.6277`. Hasilnya dikelompokkan sebagai berikut.

Kemunculan `0,5620` yang **sah secara historis** (merujuk model lama secara
eksplisit):

| Lokasi | Konteks |
|---|---|
| `artifacts/archive/20epoch_run/evaluation_valid.md` | Arsip hasil model 20 *epoch* |
| `artifacts/archive/20epoch_run/evaluation_valid.json` | Arsip hasil model 20 *epoch* |
| `artifacts/archive/20epoch_run/block15_final_training_summary.json` | Arsip ringkasan *training* 20 *epoch* |
| `artifacts/archive/20epoch_run/final_model_metadata.json` | Arsip metadata model 20 *epoch* |
| `README.md` baris 174 | Disebut eksplisit sebagai "earlier 20-epoch run" |
| `configs/final_model_config.yaml` baris 10 dan 84 | Catatan revisi konfigurasi |
| `artifacts/reports/final_model_metadata.json` baris 43 | Field `revision_note` |
| `weights/README.md` baris 24 | Keterangan model yang digantikan |
| `artifacts/audit/final_submission_audit.md` | Perbandingan historis |
| `artifacts/audit/block16_clean_reproduction_test.md` baris 99 | Catatan uji yang memang dijalankan pada model 20 *epoch* |

Kemunculan `0,5620` yang **tidak sah dan menyesatkan**:

| Lokasi | Masalah |
|---|---|
| `notebooks/final_agriData_telepati8.ipynb` sel indeks 38 (`id=b0bbd973`), baris 2209 | Sel *markdown* menyatakan bahwa eksekusi ulang evaluasi pada *checkpoint* final menghasilkan mAP@0.5 sebesar 0,5620 "every time". Pernyataan ini tidak lagi benar untuk model final saat ini. |

### Akar masalah

Sel tersebut merupakan sel *markdown*. Ketika notebook dieksekusi ulang
menggunakan `jupyter nbconvert --execute`, hanya sel kode yang dijalankan
ulang, sedangkan teks *markdown* tetap sebagaimana adanya. Ketika model
final diperbarui dari 20 *epoch* menjadi 50 *epoch*, sel kode secara otomatis
membaca ulang artefak JSON dan menampilkan angka baru (0,6277), tetapi teks
naratif pada sel *markdown* tidak ikut diperbarui. Akibatnya notebook saat ini
menampilkan angka 0,6277 pada *output* sel kode dan 0,5620 pada narasi, di
dalam satu dokumen yang sama.

### Kronologi terverifikasi

1. Model 20 *epoch* dilatih, menghasilkan mAP@0.5 sebesar 0,5620208736891205.
   Bukti: `artifacts/archive/20epoch_run/block15_final_training_summary.json`.
2. Seluruh dokumentasi pada tahap tersebut, termasuk sel *markdown* notebook,
   ditulis berdasarkan angka itu.
3. Model dilatih ulang dari awal selama 50 *epoch* atas permintaan eksplisit
   pengguna, menghasilkan mAP@0.5 sebesar 0,6276771766514752.
   Bukti: `artifacts/reports/block15_final_training_summary.json`.
4. Notebook dieksekusi ulang. Sel kode memperbarui angka, sel *markdown* tidak.

### Nilai final yang tervalidasi

| Metrik | Nilai final | Sumber artefak |
|---|---:|---|
| mAP@0.5 | 0,6276771766514752 | `artifacts/reports/evaluation_valid.json`, `block15_final_training_summary.json` |
| mAP@0.5:0.95 | 0,39054142391436314 | sumber yang sama |
| *Precision* (titik *best F1* internal Ultralytics) | 0,6406313025367592 | sumber yang sama |
| *Recall* (titik *best F1* internal Ultralytics) | 0,6237468463233555 | sumber yang sama |

Nilai mAP@0.5 tercatat identik hingga digit terakhir pada empat eksekusi
evaluasi terpisah, sehingga dapat diperlakukan sebagai nilai final yang
stabil.

### Tindakan yang direkomendasikan

Perbaiki sel *markdown* indeks 38 pada BLOCK C. Jangan menghapus kemunculan
`0,5620` yang berada pada arsip atau pada kalimat yang secara eksplisit
menyebutnya sebagai hasil model lama, karena kemunculan tersebut merupakan
jejak audit yang sah.

## 3. ISSUE 2: Provenance Commit

### Tabel provenance

| Artefak | Commit | Hash atau ID | Fungsi |
|---|---|---|---|
| *Training* final | `28668899fb000cee3a2a8386ac65ddeba2d04d02` | durasi 26.445,997 detik, 50 *epoch* | Menghasilkan *final weights* |
| Eksekusi notebook | `892f315c619ede405e38e46e94bf6c8d861e75bf` | tercatat pada *output* sel 3 dan sel 27 | Dokumentasi *submission* |
| Evaluasi terakhir di disk | `f10a20cb9194692adfa8ba1250efee3f47d8d1d8` | `artifacts/reports/evaluation_valid.json` | Menghasilkan metrik |
| *Dataset manifest* | tidak bergantung *commit* | `cf81abe0fbdae2740ad9eb27741f7fa0ef8cfcaabb18fd150ef16ba2ae55ab44` | Identitas dataset |
| *Model weights* | dihasilkan pada `2866889` | `9d74fffdd977a7bb6749bc828fe908278c5d3eaa24c3cfdbbe5a560d41f5d308` | Model final, 6.253.994 *byte* |
| HEAD lokal saat audit | `ddb26a3af29c0895de8c6692bf2f94b62a4acd67` | 178 *commit* | Kondisi repository |

### Verifikasi validitas

Perbedaan *commit* antara *training* dan evaluasi tidak dengan sendirinya
menandakan kesalahan. Pemeriksaan berikut dilakukan:

```
git diff --stat 28668899 892f315 -- scripts/evaluate.py src/agridata/metrics/ src/agridata/training/
```

Hasil: kosong. Artinya tidak ada perubahan pada kode evaluasi, kode metrik,
maupun kode *training* di antara kedua *commit* tersebut. Perbedaan *commit*
hanya disebabkan oleh *commit* dokumentasi yang terjadi setelah *training*
selesai.

*Checksum* SHA-256 *model weights* juga identik pada seluruh catatan, yaitu
`9d74fffdd977a7bb6749bc828fe908278c5d3eaa24c3cfdbbe5a560d41f5d308`,
sehingga metrik yang dilaporkan memang berasal dari *weights* yang sama
dengan yang dihasilkan proses *training*.

Kesimpulan: provenance valid. Tidak ada alasan untuk menghentikan finalisasi
berdasarkan temuan ini. Namun tabel provenance di atas perlu ditampilkan
secara eksplisit di notebook agar dapat diaudit tanpa penelusuran manual.

## 4. ISSUE 3: Definisi dan Stabilitas F1

### Status definisi

Regulasi yang tersedia pada `TELEPATI_8_AgriData_Master_Context.md`
bagian 13 hanya menyebut dua metrik penilaian, yaitu mAP@50 dan *F1-Score*,
tanpa menjelaskan *confidence threshold* yang digunakan panitia maupun
mekanisme *matching* yang dipakai. Master specification juga secara eksplisit
melarang mengarang formula penilaian di luar materi resmi.

Oleh karena itu, nilai *F1* pada project ini harus selalu ditulis sebagai
*F1-score* lokal dengan menyebut *confidence threshold* yang digunakan, dan
tidak boleh disebut sebagai skor resmi lomba.

### Stabilitas nilai

Empat eksekusi evaluasi terpisah terhadap *checkpoint* yang identik
menghasilkan nilai *F1* lokal sebagai berikut:

| Eksekusi | *F1* pada *threshold* 0,25 | *Precision* | *Recall* | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 0,2211 | 0,6818 | 0,1320 | 645 | 301 | 4243 |
| 2 | 0,4224 | 0,6757 | 0,3073 | 1502 | 721 | 3386 |
| 3 | 0,3326 | 0,6390 | 0,2248 | 1099 | 621 | 3789 |
| 4 | 0,3718 | tidak dicatat terpisah | tidak dicatat terpisah | tidak dicatat terpisah | tidak dicatat terpisah | tidak dicatat terpisah |

Rentang teramati: 0,2211 sampai 0,4224.

Pada seluruh eksekusi tersebut, mAP@0.5 tercatat identik pada
0,6276771766514752. Jumlah *ground truth* juga konsisten, yaitu 4.888 kotak,
sehingga perbedaan bukan berasal dari perbedaan data yang dievaluasi.

Pola ini konsisten dengan sifat nondeterministik *backend* MPS pada Apple
Silicon yang sudah terdokumentasi pada project ini, yang tampak memengaruhi
tahap *inference* dan bukan hanya tahap *training*. Penjelasan tersebut belum
dibuktikan melalui eksperimen terkontrol, sehingga harus disajikan sebagai
indikasi, bukan sebagai sebab yang terbukti.

### Tindakan yang direkomendasikan

1. Pada seluruh dokumen, sajikan *F1* lokal sebagai rentang teramati disertai
   *threshold*, bukan sebagai satu angka tunggal.
2. Tambahkan analisis sensitivitas *threshold* pada BLOCK E menggunakan data
   validasi, tanpa memilih *threshold* berdasarkan *test set*.
3. Nyatakan secara eksplisit bahwa implementasi *F1* bersifat lokal.

## 5. ISSUE 4: Ketidaksinkronan Artefak Evaluasi

`artifacts/reports/evaluation_valid.json` pada disk tercatat dimodifikasi
pada 19 September 2026 pukul 00.39.25 dan memuat *F1* sebesar 0,3718 dengan
`git_commit` bernilai `f10a20cb9194692adfa8ba1250efee3f47d8d1d8`.

Sementara itu, *output* yang tersimpan di dalam notebook menampilkan *F1*
sebesar 0,3326, karena notebook terakhir dieksekusi pada 18 September 2026
pukul 22.32.08.

Penyebab yang teridentifikasi: terdapat proses `ipykernel_launcher` yang
masih aktif (PID 75676, dimulai pukul 00.32) yang berjalan dari *virtual
environment* project. Hal ini menunjukkan notebook dijalankan kembali secara
independen setelah eksekusi terakhir yang tercatat, sehingga
`scripts/evaluate.py` menulis ulang artefak evaluasi tanpa memperbarui
*output* yang tersimpan pada berkas notebook.

Nilai mAP@0.5 tidak terpengaruh karena identik pada kedua eksekusi.

Tindakan yang direkomendasikan: lakukan satu eksekusi notebook terkontrol
pada BLOCK H setelah seluruh perubahan naratif selesai, lalu simpan
notebook, sehingga *output* tersimpan dan artefak di disk berasal dari
eksekusi yang sama.

## 6. Audit Bahasa

| Pemeriksaan | Hasil | Status |
|---|---:|---|
| Sel *markdown* pada notebook | 20 sel | - |
| Sel *markdown* yang masih berbahasa Inggris | 20 dari 20 | Perlu penulisan ulang penuh |
| Sel kode pada notebook | 19 sel | - |
| README | berbahasa Inggris penuh | Perlu penulisan ulang penuh |
| Laporan pada `artifacts/` | sebagian besar berbahasa Inggris | Perlu peninjauan |

Seluruh narasi notebook dan README saat ini berbahasa Inggris. Berdasarkan
aturan bahasa yang ditetapkan, seluruhnya harus ditulis ulang dalam Bahasa
Indonesia dengan istilah asing ditulis miring.

## 7. Audit Em Dash

Total karakter *em dash* (U+2014) pada repository: **386**.

Sepuluh berkas dengan jumlah terbanyak:

| Jumlah | Berkas |
|---:|---|
| 47 | `TELEPATI_8_AgriData_Master_Context.md` |
| 25 | `notebooks/final_agriData_telepati8.ipynb` |
| 23 | `README.md` |
| 20 | `scripts/select_final_model.py` |
| 20 | `artifacts/audit/block21_final_freeze.md` |
| 17 | `artifacts/reports/block14_final_model_selection.md` |
| 16 | `artifacts/audit/block16_clean_reproduction_test.md` |
| 15 | `artifacts/audit/final_submission_audit.md` |
| 13 | `scripts/check_reproducibility.py` |
| 13 | `configs/experiments/augmentation_ablation.yaml` |

Total berkas yang terdampak: 49.

Catatan: 47 dari 386 kemunculan berada pada
`TELEPATI_8_AgriData_Master_Context.md`, yaitu dokumen
*specification* yang disediakan pengguna, bukan dokumen yang dihasilkan
project. Perlu keputusan eksplisit pada BLOCK G mengenai apakah dokumen
tersebut ikut dibersihkan atau dikecualikan sebagai dokumen sumber.

## 8. Audit Path, Secret, dan Penanda Pekerjaan

| Pemeriksaan | Hasil | Status |
|---|---|---|
| *Path* absolut personal pada `src/`, `scripts/`, `configs/` | Tidak ditemukan | Baik |
| *Path* absolut personal pada artefak hasil eksekusi | Ditemukan pada 10 berkas | Dapat diterima |
| *Secret*, *API key*, *password*, *token* | Tidak ditemukan | Baik |
| Penanda TODO, FIXME, XXX | Tidak ditemukan | Baik |

Berkas artefak yang memuat *path* absolut seluruhnya merupakan berkas yang
dihasilkan otomatis dan memang mencatat lokasi eksekusi sebagai bagian dari
provenance, yaitu `block15_final_training_summary.json`,
`evaluation_valid.json`, `evaluation_valid.md`, `reproducibility_checklist.json`,
`reproducibility_checklist.md`, `block6_baseline_smoke_summary.json`,
`block14_environment_snapshot.json`, dua berkas pada direktori arsip, serta
*output* pada notebook. Hal ini tidak melanggar prinsip *path* yang dapat
dikonfigurasi, karena seluruh kode sumber menerima lokasi dataset dan
direktori keluaran sebagai argumen.

## 9. Kesenjangan Notebook terhadap Struktur Target

Notebook saat ini memiliki 22 bagian dengan fondasi teknis yang lengkap,
tetapi belum memenuhi struktur dokumen ilmiah yang ditargetkan. Kesenjangan
utama:

| Bagian target | Status saat ini |
|---|---|
| Latar belakang dan rumusan masalah | Belum ada |
| *Profiling* dataset (distribusi kelas, ukuran *bounding box*, resolusi) | Belum ada, hanya ringkasan jumlah |
| Analisis *missingness* untuk data deteksi objek | Belum ada sebagai tabel |
| Tabel *canonical mapping* beserta alasan | Belum ada di notebook |
| Narasi alur *preprocessing* | Belum ada |
| Ringkasan 21 eksperimen terkontrol | Belum ada di notebook |
| Kurva *training* dari `results.csv` | Belum ada |
| Analisis per kelas beserta interpretasi | Tabel ada, interpretasi belum ada |
| Hubungan distribusi data dengan performa | Belum ada |
| *Error analysis* dengan contoh visual | Belum ada di notebook |
| Contoh prediksi benar dan salah secara terstruktur | Sebagian |
| Kelebihan dan keterbatasan pendekatan | Sebagian, hanya pada catatan reproducibility |
| Kesimpulan | Belum ada |
| Daftar pustaka | Belum ada |

## 10. Inventaris Artefak yang Tersedia untuk Block Berikutnya

| Artefak | Lokasi | Kegunaan |
|---|---|---|
| Log 21 eksperimen | `artifacts/experiments/experiment_log.json` | BLOCK D |
| Kurva *training* 50 *epoch* | `runs/detect/final/final_model/results.csv`, 51 baris | BLOCK D |
| Laporan evaluasi | `artifacts/reports/evaluation_valid.json` | BLOCK E |
| *Error analysis* | `artifacts/reports/block13_error_analysis.json` | BLOCK E |
| Figur *error analysis* | `artifacts/figures/error_analysis/`, 17 berkas | BLOCK E |
| Figur prediksi | `artifacts/figures/predictions/`, 18 berkas | BLOCK E |
| Figur distribusi | `artifacts/figures/distributions/` | BLOCK B |
| Audit dataset | `artifacts/audit/dataset_audit_report.json` | BLOCK B |
| Diagnostik ketidakseimbangan kelas | `artifacts/reports/class_imbalance_diagnostics.json` | BLOCK B |
| Laporan *canonical mapping* | `artifacts/audit/canonical_mapping_report.json` | BLOCK C |

## 11. Yang Tidak Diubah pada Block Ini

Sesuai instruksi, block ini bersifat audit saja. Tidak ada perubahan pada:

- notebook;
- README;
- kode sumber;
- konfigurasi;
- dataset;
- *model weights*;
- artefak hasil eksperimen maupun evaluasi.

Satu-satunya berkas yang dibuat adalah dokumen audit ini.

## 12. Risiko yang Masih Terbuka

1. Repository publik belum memuat pekerjaan terbaru karena *push* masih
   tertahan akibat penulisan ulang riwayat Git. Tindakan berada pada
   pengguna.
2. *GitHub Release* untuk *model weights* belum dipublikasikan.
3. Pernyataan orisinalitas bertanda tangan belum tersedia.
4. Komposisi tim belum dapat diverifikasi dari repository.
5. Tenggat operasional adalah 20 September 2026 pukul 23.59 WIB, sehingga
   waktu yang tersisa untuk BLOCK B sampai BLOCK I sangat terbatas.
