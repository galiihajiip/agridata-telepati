# Pra-pemeriksaan Final Polish (BLOCK 1)

Audit kondisi repository dan notebook sebelum tahap penyempurnaan akhir.
**Tidak ada perbaikan yang dilakukan pada block ini.** Seluruh isi dokumen
merupakan hasil pemeriksaan, bukan tindakan.

Tanggal audit: 23 September 2026
Commit saat audit: 259 commit, `main` sinkron dengan `origin/main`
Tenggat submission: 26 September 2026

## 1. Ringkasan Temuan

| Tingkat | Jumlah | Ringkasan |
|---|---:|---|
| Kritis | 3 | Angka final tidak punya artefak pendukung, keluaran notebook usang, tiga sumber angka saling bertentangan |
| Tinggi | 2 | Berkas prompt internal ter-commit, eksperimen 960 belum ada keputusan |
| Sedang | 3 | *Absolute path* pada keluaran notebook, *em dash* sisa, artefak evaluasi dari kode lama |
| Rendah | 2 | Metrik historis tersebar tanpa label, komentar kode berbahasa Inggris |
| Baik | 5 | Tes lulus, tidak ada *secret*, notebook bersih dari *error*, Git sinkron, narasi sudah Bahasa Indonesia |

## 2. KRITIS 1: Angka Final Tidak Memiliki Artefak Pendukung

`README.md` menyatakan mAP@50 sebesar **64,01%** dan *F1-Score* sebesar
**63,83%** sebagai hasil utama.

Namun:

- `artifacts/reports/official_metrics_val.json` **tidak ada**.
- `artifacts/reports/official_metrics_test.json` **tidak ada**.

Kedua angka itu berasal dari sapuan parameter inferensi yang dijalankan
sekali, lalu diketik ke dalam dokumen. Tidak ada berkas yang dapat dirujuk
juri untuk memverifikasinya.

Ini melanggar prinsip *source of truth*: angka final harus dapat ditelusuri
ke artefak, bukan ke ingatan.

**Status: FAIL.**

## 3. KRITIS 2: Keluaran Notebook Usang

Notebook memuat 127 sel, 0 *error*, seluruh sel telah dieksekusi. Namun
keluaran yang tersimpan berasal dari eksekusi **sebelum** perubahan kode
metrik.

| Sel | Isi | Nomor eksekusi | Masalah |
|---:|---|---:|---|
| 87 | Metrik utama | 35 | Menampilkan angka konfigurasi lama |
| 94 | Perbandingan valid dan test | 38 | Sama |

Angka yang muncul pada keluaran tersimpan:

| Nilai | Ada di keluaran | Seharusnya |
|---|---|---|
| 0,3326 (*F1* lokal lama) | **ada** | tidak lagi menjadi angka utama |
| 0,6277 (mAP NMS 0,7) | **ada** | seharusnya 0,6401 pada NMS 0,5 |
| 0,6383 (*F1* NMS 0,5) | tidak ada | seharusnya ada |
| 0,6401 (mAP NMS 0,5) | tidak ada | seharusnya ada |

Sel 87 dan 94 sudah diubah agar memanggil `compute_official_metrics.py`,
tetapi belum pernah dieksekusi ulang karena GPU sedang dipakai pelatihan.

**Status: FAIL.**

## 4. KRITIS 3: Tiga Sumber Angka Saling Bertentangan

Saat ini terdapat tiga versi kebenaran yang berbeda di dalam satu repository:

| Sumber | mAP@50 | *F1* |
|---|---:|---:|
| `README.md` dan model card | 64,01% | 63,83% |
| Keluaran notebook tersimpan | 62,77% | 33,26% |
| `artifacts/reports/evaluation_valid.json` | 62,77% | 33,26% (lokal) |

Selisih relatif *F1* antara dokumen dan notebook mencapai sekitar **48%**.
Ambang REJECTED pada regulasi adalah selisih relatif di atas 2%.

Bila submission dikirim dalam kondisi ini dan juri menjalankan *audit run*,
kemungkinan besar hasilnya **REJECTED**.

**Status: FAIL. Ini risiko tunggal paling besar pada paket submission.**

## 5. TINGGI 1: Berkas Prompt Internal Ter-commit

Dua berkas berikut merupakan instruksi kerja internal, bukan artefak yang
dibutuhkan juri maupun pipeline:

| Berkas | Ukuran | Sifat |
|---|---:|---|
| `TELEPATI_8_AgriData_Master_Context.md` | 73.621 byte | Spesifikasi kerja internal, memuat 47 *em dash* |
| `TELEPATI_8_AgriData_Final_Polish_and_Claude_Code_Prompt.md` | 36.905 byte | Prompt tahap penyempurnaan |

Pemeriksaan kebutuhan:

| Kriteria | Master Context | Final Polish Prompt |
|---|---|---|
| Dibutuhkan juri | Tidak | Tidak |
| Dibutuhkan pipeline | Tidak | Tidak |
| Dibutuhkan untuk audit | Sebagian, sebagai rujukan regulasi | Tidak |
| Dirujuk dokumen lain | Ya, oleh `references/README.md` dan `submission_state_audit.md` | Tidak |

Catatan: `Master_Context` dirujuk sebagai sumber regulasi pada dua dokumen.
Bila dikeluarkan dari repository, rujukan tersebut perlu disesuaikan.

Berkas ketiga yang namanya mengandung kata "draft", yaitu
`docs/model_card_draft.md`, **bukan** berkas internal. Isinya adalah model
card final berstatus FINAL. Hanya namanya yang menyesatkan.

**Status: perlu keputusan.**

## 6. TINGGI 2: Eksperimen Resolusi 960 Belum Ada Keputusan

Pelatihan pada resolusi 960 masih berjalan: **epoch 7 dari 50**, sudah
berjalan 2 jam 29 menit, estimasi total sekitar 14,7 jam.

Sinyal awal berada di bawah model 640 pada epoch yang sama:

| Epoch | 640 mAP@0.5 | 960 mAP@0.5 |
|---:|---:|---:|
| 1 | 0,0366 | 0,0195 |
| 2 | 0,1120 | 0,0426 |
| 3 | 0,1863 | 0,0986 |
| 4 | 0,2042 | 0,1158 |
| 6 | - | 0,1957 |

Eksperimen ini mengubah dua variabel sekaligus, yaitu resolusi 640 ke 960 dan
*batch* 16 ke 8. Perubahan *batch* dilakukan karena keterbatasan memori, bukan
karena alasan metodologis. Akibatnya efek resolusi tidak dapat diisolasi.

Model 640 tetap menjadi kandidat final yang dibekukan.

**Status: perlu keputusan apakah dilanjutkan atau dihentikan dan dicatat
sebagai eksperimen eksploratif.**

## 7. SEDANG 1: Absolute Path pada Keluaran Notebook

Tujuh kemunculan `/Users/macbookpro` pada notebook, seluruhnya berada pada
**keluaran sel**, bukan pada kode sumber.

| Sel | Konteks |
|---:|---|
| 5 | Cetak *root* project |
| 9 | Cetak lokasi dataset |
| 52 | Keluaran penyiapan data |
| 78 | Keluaran pelatihan |
| 85 | Keluaran evaluasi |

Kode sumber sendiri bersih: tidak ada *path* personal yang ditulis permanen.
Kemunculan ini merupakan jejak lingkungan eksekusi, bukan cacat kode.

**Status: WARN, dapat diterima bila dijelaskan, atau dihilangkan dengan
mencetak *path* relatif.**

## 8. SEDANG 2: Em Dash Tersisa

| Berkas | Jumlah | Keterangan |
|---|---:|---|
| `TELEPATI_8_AgriData_Master_Context.md` | 47 | Dokumen kerja internal |
| `artifacts/archive/20epoch_run/evaluation_valid.md` | 1 | Arsip historis |

Seluruh berkas submission lain sudah **0**. Kedua berkas di atas sebelumnya
sengaja dikecualikan. Bila `Master_Context` dikeluarkan dari repository,
masalah ini otomatis selesai untuk 47 kemunculan.

**Status: WARN.**

## 9. SEDANG 3: Artefak Evaluasi Dihasilkan Kode Lama

`artifacts/reports/evaluation_valid.json` tidak memuat *field* `nms_iou`
maupun `macro_f1`. Artinya artefak ini dihasilkan sebelum `evaluate.py`
diperbarui.

Konsekuensinya, artefak yang saat ini menjadi rujukan notebook memuat metrik
dengan konfigurasi NMS 0,7, sedangkan dokumen melaporkan hasil NMS 0,5.

**Status: FAIL, perlu regenerasi.**

## 10. RENDAH 1: Metrik Historis Tersebar Tanpa Label Konsisten

Sebaran kemunculan angka pada berkas terlacak di luar direktori arsip:

| Nilai | Jumlah berkas | Makna |
|---|---:|---|
| 0.5620 | 14 | Model 20 *epoch*, historis |
| 0.6277 | 15 | Model 50 *epoch*, NMS 0,7 |
| 0.3326 | 11 | *F1* lokal *micro*, metodologi lama |
| 0.6181 | 8 | *F1* macro, NMS 0,7 |
| 0.6383 | 5 | *F1* macro, NMS 0,5 |
| 0.6401 | 6 | mAP, NMS 0,5 |

Sebagian besar kemunculan sudah diberi konteks historis, namun belum ada satu
tabel provenance terpusat yang membedakan keenam nilai tersebut.

**Status: WARN.**

## 11. RENDAH 2: Komentar dan Docstring Berbahasa Inggris

Seluruh *docstring* dan komentar pada `src/` dan `scripts/` masih berbahasa
Inggris. Narasi notebook, README, model card, dan dokumen referensi sudah
berbahasa Indonesia.

Laporan audit historis per block juga masih berbahasa Inggris, yaitu
`final_submission_audit.md`, `block21_final_freeze.md`,
`block16_clean_reproduction_test.md`, `reproducibility_checklist.md`, dan
laporan block 10 sampai 14.

**Status: WARN.**

## 12. Hasil Pemeriksaan yang Baik

| Pemeriksaan | Hasil |
|---|---|
| Uji unit | 69 lulus |
| *Secret*, *API key*, *token* | tidak ditemukan |
| *Error* pada notebook | 0 |
| Sel notebook belum dieksekusi | 0 |
| Figur tertanam | 18 |
| *Em dash* pada notebook | 0 |
| Narasi notebook berbahasa Indonesia | 77 dari 78 sel *markdown* |
| *Absolute path* pada kode sumber | tidak ada |
| Git | bersih dan sinkron dengan remote |
| Dataset mentah pada riwayat publik | 0 objek |

Catatan: satu sel *markdown* terdeteksi tanpa penanda Bahasa Indonesia oleh
pemeriksaan otomatis, yaitu sel 63. Pemeriksaan manual menunjukkan sel
tersebut sebenarnya sudah berbahasa Indonesia. Ini positif palsu dari
heuristik, bukan temuan.

## 13. Artefak yang Harus Dipertahankan

Berikut berkas yang **tidak boleh** dihapus pada tahap pembersihan:

| Kategori | Berkas |
|---|---|
| Notebook final | `notebooks/final_agriData_telepati8.ipynb` |
| Dokumentasi utama | `README.md`, `docs/model_card_draft.md`, `references/README.md`, `SUBMISSION_CHECKLIST.md` |
| Kode sumber | seluruh isi `src/agridata/` dan `scripts/` |
| Konfigurasi | `configs/final_model_config.yaml`, `requirements.txt`, `pytest.ini`, `data_config.yaml` |
| Metadata model | `artifacts/reports/final_model_metadata.json`, `weights/best.pt.sha256`, `weights/README.md` |
| Bukti evaluasi | `evaluation_valid.json`, `evaluation_test.json`, `block13_error_analysis.json`, `threshold_sensitivity_valid.json`, `dataset_profile.json` |
| Bukti eksperimen | `artifacts/experiments/experiment_log.json` |
| Riwayat pelatihan | `artifacts/reports/final_training_history.csv` |
| Bukti audit | seluruh isi `artifacts/audit/` |
| Arsip historis | `artifacts/archive/` beserta isinya |
| Legal | `docs/originality_statement_placeholder.md` |
| Uji | seluruh isi `tests/` |

## 14. Urutan Perbaikan yang Disarankan

Berdasarkan tingkat risiko, bukan berdasarkan kemudahan:

1. **Kunci konfigurasi inferensi**, pastikan NMS 0,5 dipakai seragam pada
   seluruh jalur kode, dokumen, dan artefak.
2. **Regenerasi artefak metrik** dari *source of truth*, menghasilkan
   `official_metrics_val.json` dan `official_metrics_test.json`, serta
   memperbarui `evaluation_valid.json` dan `evaluation_test.json` dengan
   kode yang sudah diperbarui.
3. **Eksekusi ulang notebook** sehingga keluaran tersimpan cocok dengan
   artefak dan dokumen.
4. **Selaraskan README, model card, dan audit** dengan angka hasil regenerasi.
5. **Buat tabel provenance terpusat** yang membedakan keenam nilai metrik.
6. **Putuskan nasib eksperimen 960** dan catat keputusannya.
7. **Putuskan nasib dua berkas prompt internal** dan sesuaikan rujukannya.
8. Pembersihan bahasa pada komentar kode dan laporan audit historis.
9. Publikasi GitHub Release.
10. Audit kepatuhan final.

Langkah 1 sampai 4 bersifat saling bergantung dan harus dikerjakan berurutan
dalam satu rangkaian, karena hasil langkah sebelumnya menjadi masukan langkah
berikutnya.

## 15. Hambatan yang Perlu Diputuskan Terlebih Dahulu

Langkah 2 dan 3 membutuhkan GPU, sedangkan GPU saat ini dipakai pelatihan
resolusi 960 yang masih menyisakan sekitar 12 jam.

Menjalankan evaluasi bersamaan dengan pelatihan berisiko: project ini sudah
mendokumentasikan bahwa menjalankan dua proses MPS secara bersamaan
berpotensi menghasilkan variasi metrik yang tidak diinginkan.

Karena itu diperlukan keputusan mengenai eksperimen 960 sebelum perbaikan
kritis dapat dijalankan.
