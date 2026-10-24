# Laporan Pembersihan Repository

Catatan tindakan pembersihan repository menjelang submission. Setiap berkas
kandidat dibaca isinya terlebih dahulu, bukan dinilai dari namanya saja.

Tanggal: 23 September 2026

## 1. Kriteria Keputusan

Setiap kandidat dinilai dengan empat pertanyaan:

1. Apakah dibutuhkan juri untuk memahami atau menilai submission?
2. Apakah dibutuhkan pipeline agar dapat dijalankan?
3. Apakah dibutuhkan sebagai bukti audit?
4. Apakah isinya murni instruksi kerja internal?

Berkas dikeluarkan hanya bila jawaban pertanyaan 1 sampai 3 seluruhnya tidak,
dan jawaban pertanyaan 4 ya.

## 2. Berkas yang Dihapus

| Berkas | Ukuran | Alasan |
|---|---:|---|
| Dokumen spesifikasi kerja internal | 3.736 baris | Bukan artefak submission, tidak dipakai pipeline. Juga sumber 47 karakter *em dash* pada repository. |
| Dokumen instruksi tahap penyempurnaan | 1.365 baris | Instruksi kerja internal. Tidak memuat bukti teknis apa pun. |
| `artifacts/audit/final_polish_precheck.md` | 282 baris | Audit kerja sementara. Seluruh temuannya sudah ditindaklanjuti dan terangkum pada dokumen audit yang berlaku. |
| `artifacts/audit/submission_state_audit.md` | 325 baris | Audit kondisi awal. Isinya sudah digantikan audit kesiapan yang lebih mutakhir. |
| `artifacts/audit/block21_final_freeze.md` | 215 baris | Catatan proses pembekuan yang memakai penomoran block internal. Isinya tumpang tindih dengan audit kesiapan. |
| `artifacts/audit/final_submission_audit.md` | 122 baris | Audit kepatuhan yang isinya sudah tercakup pada bagian kepatuhan di audit kesiapan. Memakai penomoran block internal. |
| `notebooks/.gitkeep` | 0 baris | Penanda direktori kosong yang tidak lagi diperlukan karena direktori sudah berisi notebook. |

Total: 6.045 baris dokumen internal dikeluarkan dari repository.

## 3. Rujukan yang Diperbaiki Setelah Penghapusan

Penghapusan berkas berpotensi meninggalkan tautan rusak. Seluruh rujukan
diperiksa dan diperbaiki:

| Berkas | Perbaikan |
|---|---|
| `references/README.md` | Rujukan ke dokumen spesifikasi internal dihapus, diganti keterangan bahwa dokumen kompetisi tidak disertakan |
| `README.md` | Rujukan audit kepatuhan diarahkan ke `final_submission_readiness.md` |
| `docs/model_card_draft.md` | Sama |
| `docs/originality_statement_placeholder.md` | Sama |
| `notebooks/final_agriData_telepati8.ipynb` | Rujukan audit lama diarahkan ke `metrics_provenance.md` |

## 4. Berkas yang Dipertahankan Beserta Alasannya

### Dokumen utama submission

| Berkas | Alasan |
|---|---|
| `README.md` | Dokumen masuk utama bagi juri |
| `notebooks/final_agriData_telepati8.ipynb` | Dokumen utama submission |
| `SUBMISSION_CHECKLIST.md` | Daftar periksa kesiapan |
| `docs/model_card_draft.md` | Model card, memuat batasan penggunaan |
| `docs/originality_statement_placeholder.md` | Penanda kewajiban dokumen legal |
| `references/README.md` | Audit sitasi per kalimat |
| `weights/README.md` | Informasi rilis dan checksum bobot |

### Bukti audit teknis

| Berkas | Alasan |
|---|---|
| `artifacts/audit/dataset_audit_report.md` | Bukti audit forensik dataset, memuat temuan duplikat lintas split |
| `artifacts/audit/canonical_mapping_report.md` | Bukti validasi pemetaan 11 kelas |
| `artifacts/audit/reproducibility_checklist.md` | Bukti pemeriksaan reproduktibilitas |
| `artifacts/audit/block16_clean_reproduction_test.md` | Bukti uji lingkungan bersih yang menemukan dua cacat nyata |
| `artifacts/audit/metrics_methodology.md` | Penjelasan koreksi metodologi F1, penting untuk kredibilitas angka |
| `artifacts/audit/metrics_provenance.md` | Pembeda seluruh nilai metrik historis dan final |
| `artifacts/audit/final_submission_readiness.md` | Audit kesiapan yang berlaku |

### Bukti eksperimen

Seluruh isi `artifacts/reports/` dan `artifacts/experiments/` dipertahankan
karena merupakan bukti hasil eksekusi, bukan catatan proses internal.
Termasuk laporan ablasi augmentasi, ablasi ketidakseimbangan kelas, matriks
percobaan, pemilihan konfigurasi final, dan analisis kesalahan.

Direktori `artifacts/archive/` dipertahankan sebagai arsip historis model 20
*epoch*, model 640 sebelum penyesuaian ambang NMS, dan checkpoint eksperimen
resolusi 960 yang dijeda.

## 5. Pembersihan Bahasa pada Kode Sumber

Seluruh *docstring* modul dan komentar pada paket `src/agridata/` diterjemahkan
ke Bahasa Indonesia, mencakup 16 berkas:

| Modul | Cakupan |
|---|---|
| `training/train.py` | Docstring modul, penjelasan kepatuhan, catatan resolusi path, catatan optimizer |
| `dataset/inspect.py` | Docstring modul, ambang pemeriksaan bbox, penjelasan perceptual hash |
| `dataset/mapping.py` | Docstring modul, sumber tabel pemetaan, penjelasan supercategory |
| `dataset/stats.py` | Docstring modul dan seluruh fungsi |
| `analysis/dataset_profile.py` | Docstring modul, penjelasan ambang objek kecil, definisi missingness |
| `analysis/error_analysis.py` | Docstring fungsi |
| `metrics/detection.py` | Docstring modul dan penjelasan metode pencocokan |
| `visualization/images.py` | Docstring modul dan fungsi, catatan pemilihan warna |
| `visualization/distributions.py` | Docstring seluruh fungsi, label sumbu grafik |
| `experiments/tracker.py` | Docstring modul dan fungsi |
| `reproducibility/environment.py` | Docstring seluruh fungsi |
| `config.py`, `device.py`, `seed.py`, `logging_utils.py` | Docstring modul dan fungsi |
| `dataset/__init__.py`, `reproducibility/__init__.py` | Docstring paket |

Pada `scripts/`, judul *docstring* modul untuk 17 skrip diterjemahkan, dan
penomoran block internal dihapus dari judul tersebut.

Prioritas khusus diberikan pada teks yang muncul di artefak yang dibaca juri.
Fungsi `_caveat_text` pada `scripts/run_error_analysis.py` menghasilkan
kalimat yang tercetak langsung ke `artifacts/reports/block13_error_analysis.md`,
sehingga seluruh kalimat keluarannya diterjemahkan.

## 6. Penyelesaian Pembersihan Bahasa

Seluruh butir yang sebelumnya terbuka pada dokumen ini sudah ditutup.

*Docstring* modul dan fungsi pada `scripts/`, `src/`, dan `tests/` kini
sepenuhnya Bahasa Indonesia, termasuk paragraf penjelas yang sebelumnya
hanya judulnya saja yang diterjemahkan. Pemeriksaan otomatis atas seluruh
*docstring* menggunakan `ast` tidak lagi menemukan sisa teks Inggris.
Komentar sebaris juga sudah diterjemahkan.

Seluruh laporan pada `artifacts/reports/` dan `artifacts/audit/` berbahasa
Indonesia. Cara penerjemahannya dibedakan menurut sifat laporannya:

| Laporan | Cara |
|---|---|
| `evaluation_valid.md`, `evaluation_test.md` | Dibentuk ulang dari JSON tersimpan melalui `evaluate.py --render-only`, tanpa inferensi ulang |
| `block14_final_model_selection.md`, `experiment_log.md` | Diregenerasi dari log percobaan memakai templat yang sudah diterjemahkan |
| `block10_matrix_recommendation.md`, `block11_augmentation_ablation.md` | Dibentuk ulang dari log percobaan; seluruh angka diverifikasi identik |
| `block12_class_imbalance_ablation.md`, `block13_error_analysis.md` | Label diterjemahkan di tempat karena nilai AP per kelas berpresisi penuh tidak tersimpan; seluruh angka dipertahankan persis |
| `dataset_audit_report.md`, `canonical_mapping_report.md`, `eda_summary.md`, `class_imbalance_diagnostics.md`, `reproducibility_checklist.md` | Dijalankan ulang terhadap dataset asli; angkanya diverifikasi identik |
| `block16_clean_reproduction_test.md` | Ditulis ulang, karena merupakan dokumen yang disusun manual |

Catatan pada `artifacts/experiments/experiment_log.json` ikut diterjemahkan.
Hanya field `notes` dan `compliance_notes` yang berubah, sementara seluruh
field metrik dan *hyperparameter* diverifikasi identik sebelum penulisan.

Repository juga bebas dari karakter *em dash* dan dari *path* absolut
personal pada artefak yang dibaca juri.

## 7. Yang Belum Selesai

**Penamaan berkas laporan masih memakai penomoran block internal**,
misalnya `block13_error_analysis.md`. Penomoran ini tidak bermakna bagi
juri. Mengganti nama memerlukan pembaruan rujukan pada notebook dan README,
sehingga ditunda agar tidak memicu tautan rusak menjelang tenggat.

## 8. Pembersihan Akhir Menjelang Submission

Dijalankan pada 26 September 2026, bersamaan dengan penggantian model final ke
model 100 *epoch*.

| Berkas atau direktori | Tindakan | Alasan |
|---|---|---|
| `scripts/auto_commit_daemon.py`, `scripts/auto_commit.sh` | dihapus | Perkakas pengembangan milik pemilik repository. Tidak dibutuhkan juri maupun pipeline submission. |
| `scripts/train_finetune_800.py`, `configs/experiment_800_finetune.yaml` | dihapus | Eksperimen *fine-tuning* resolusi 800 yang tidak pernah dijalankan dan tidak menghasilkan artefak apa pun. |
| `configs/experiment_100epoch_config.yaml` | dihapus | Duplikat isi `configs/final_model_config.yaml`, yang sekarang menjadi konfigurasi kanonik model final. |
| `artifacts/staging/`, `artifacts/experiments_100epoch/` | dihapus | Direktori kerja sementara saat evaluasi model baru. Hasilnya sudah dipindahkan ke `artifacts/reports/`. |
| `scripts/__pycache__/` | dihapus | Artefak bytecode, bukan berkas sumber. |
| `configs/final_model_config.yaml` | ditulis ulang | Kini berisi konfigurasi 100 *epoch* yang sesungguhnya menghasilkan bobot final, seluruhnya berbahasa Indonesia. Versi 50 *epoch* dipindahkan ke `configs/archive_50epoch_config.yaml`. |

Artefak model 50 *epoch* yang digantikan kami arsipkan, tidak dihapus, pada
`artifacts/archive/50epoch_640_run/` termasuk subdirektori `nms05/` yang memuat
evaluasi final versi tersebut. Eksekusi ulang analisis kesalahan yang
menghasilkan angka berbeda kami simpan pada
`artifacts/archive/error_analysis_reruns/` agar selisihnya dapat diperiksa.

Pemeriksaan penutup setelah pembersihan:

| Pemeriksaan | Hasil |
|---|---|
| Tautan internal rusak pada seluruh berkas Markdown | 0 |
| Karakter *em dash* pada berkas terlacak | 0 |
| *Path* absolut personal pada kode sumber dan konfigurasi | tidak ada |
| *Secret*, *API key*, atau *token* | tidak ada |
| Penanda TODO atau FIXME | tidak ada |
| Rujukan ke berkas yang sudah dihapus | tidak ada |
| Uji unit | 69 lulus |
| *Docstring* berbahasa Inggris | tidak ada |

---

## Pembersihan 24 Oktober 2026

Dilakukan setelah model final diganti ke YOLOv8s-P2. Setiap berkas diperiksa
apakah masih dirujuk README, notebook, kode, tes, atau dokumen audit sebelum
dihapus.

| Berkas | Tindakan | Alasan |
|---|---|---|
| `data_config.yaml` | Dihapus | Config awal berisi 9 kelas dengan nama mentah, bukan 11 kelas canonical. Tidak dirujuk apa pun dan menyesatkan pembaca |
| `scripts/resume_training_960.py`, `configs/final_model_config_960.yaml`, `artifacts/reports/experiment_960_status.md`, `artifacts/archive/960_paused/` | Dihapus | Eksperimen YOLOv8n resolusi 960 yang dijeda pada *epoch* 7 dan tidak pernah dilanjutkan. Pertanyaan resolusi tinggi kemudian diuji ulang oleh kandidat C |
| `artifacts/archive/*.log` | Dihapus | Log mentah pelatihan, tidak dirujuk, dan sudah digantikan ringkasan JSON |
| `kaggle_results/` | Dipindah keluar repository | Folder kerja unduhan Kaggle dan Colab. Bukti yang dilaporkan disalin ke `artifacts/candidates/`, dan folder ini kini masuk `.gitignore` |
| `artifacts/figures/error_analysis/`, `artifacts/figures/predictions/` | Dikosongkan lalu dibuat ulang | Berisi campuran contoh dari model lama dan model final karena nama berkas mengikuti ID citra. Dibuat ulang hanya dari model final; metrik hasil evaluasi ulang identik dengan sebelumnya |
| `artifacts/reports/evaluation_*`, `official_metrics_*`, `final_model_metadata.json`, `block13_*`, `block15_*`, `threshold_sensitivity_valid.json` milik YOLOv8n | Dipindah ke `artifacts/archive/100epoch_v8n_run/` | Riwayat model final sebelumnya, tetap dirujuk README dan audit |
| `configs/final_model_config.yaml` milik YOLOv8n | Disalin ke `configs/archive_100epoch_v8n_config.yaml` | Memuat penalaran pemilihan hyperparameter yang dikutip notebook Bagian 12 |

Yang sengaja dipertahankan: skrip 21 percobaan penyaringan beserta
`artifacts/experiments/`, karena menghasilkan bukti yang dikutip notebook
Bagian 9 sampai 12; arsip 20, 50, dan 100 *epoch*, karena dirujuk tabel
riwayat model.
