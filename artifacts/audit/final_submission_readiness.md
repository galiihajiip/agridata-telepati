# Audit Kesiapan Submission

Audit menyeluruh terhadap paket submission. Seluruh angka pada dokumen ini
berasal dari pemeriksaan yang dijalankan saat audit, bukan dari catatan
sebelumnya.

Tanggal audit: 23 September 2026
Tenggat submission: 26 September 2026
Repository: https://github.com/galiihajiip/agridata

## 1. Ringkasan Status

| Kategori | LULUS | TERBUKA | DI LUAR JANGKAUAN |
|---|---:|---:|---:|
| Model dan bobot | 5 | 0 | 0 |
| Metrik dan konsistensi | 6 | 0 | 0 |
| Dataset | 6 | 0 | 0 |
| Notebook | 7 | 0 | 0 |
| Dokumentasi | 6 | 0 | 0 |
| Kode dan pengujian | 4 | 0 | 0 |
| Kepatuhan regulasi | 8 | 0 | 0 |
| Repository dan Git | 4 | 0 | 0 |
| Rilis | 0 | 2 | 0 |
| Dokumen legal dan tim | 1 | 0 | 2 |
| **Total** | **47** | **2** | **2** |

Paket teknis siap. Dua item terbuka bersifat mekanis dan dua item lain berada
di luar kemampuan verifikasi otomatis.

## 2. Model Final

| Field | Nilai | Status |
|---|---|---|
| Berkas | `runs/detect/final/final_model/weights/best.pt` | LULUS |
| Arsitektur | YOLOv8n dari `yolov8n.yaml`, `pretrained=False` | LULUS |
| Ukuran | 6.253.994 byte | LULUS |
| SHA-256 | `9d74fffdd977a7bb6749bc828fe908278c5d3eaa24c3cfdbbe5a560d41f5d308` | LULUS, diverifikasi dengan `shasum -c` |
| Pemuatan proses bersih | berhasil, 11 kelas | LULUS |
| Inferensi | menghasilkan deteksi | LULUS |

## 3. Metrik yang Dilaporkan

Konfigurasi: resolusi inferensi 640, ambang NMS IoU 0,5, IoU pencocokan 0,5.

| Metrik | *Split* valid | *Split* test |
|---|---:|---:|
| mAP@50 | **64,01%** | **62,46%** |
| *F1-Score* macro | **63,83%** | **62,72%** |
| mAP@0.5:0.95 | 0,3856 | 0,3998 |

*Split* test tidak pernah dipakai untuk penyetelan apa pun. Selisih valid
terhadap test sebesar 1,55 poin pada mAP dan 1,11 poin pada *F1* konsisten
dengan generalisasi yang stabil pada kedua *split*. Satu evaluasi *held-out*
tidak cukup untuk membuktikan ketiadaan *overfitting*.

| Pemeriksaan konsistensi | Hasil | Status |
|---|---|---|
| Artefak evaluasi, notebook, README, model card | angka identik | LULUS |
| Sumber kebenaran tunggal | `evaluate.py` menghasilkan, `compute_official_metrics.py` hanya membaca | LULUS |
| Nilai metrik historis | dibedakan pada `metrics_provenance.md` | LULUS |
| Koreksi metodologi *F1* | didokumentasikan pada `metrics_methodology.md` | LULUS |
| Ambang NMS | 0,5 seragam pada kode, artefak, dan dokumen | LULUS |
| Definisi *F1* | dinyatakan sebagai implementasi lokal macro, bukan angka resmi panitia | LULUS |

## 4. Dataset

| Pemeriksaan | Hasil | Status |
|---|---|---|
| Jumlah split | train 10.133, valid 2.106, test 1.059 citra | LULUS |
| Anotasi canonical | 20.163, 4.888, 2.670 | LULUS |
| Pemetaan 11 kelas | nol kategori tidak terpetakan pada ketiga split | LULUS |
| Integritas referensi | nol berkas hilang, nol anotasi yatim, nol bbox tidak valid | LULUS |
| Kebocoran antar split | satu duplikat persis ditemukan dan dikeluarkan dari manifest latih | LULUS |
| Dataset mentah | tidak diubah, tidak ter-commit | LULUS |

## 5. Notebook

| Pemeriksaan | Hasil | Status |
|---|---|---|
| Jumlah sel | 127 sel, 49 sel kode | LULUS |
| Eksekusi | 0 *error*, 0 sel belum dieksekusi | LULUS |
| Figur tertanam | 18 | LULUS |
| Struktur | 22 bagian utama | LULUS |
| Bahasa | Bahasa Indonesia, istilah asing dimiringkan | LULUS |
| Suara penulis | orang pertama jamak "kami" pada 70 dari 78 sel markdown | LULUS |
| *Em dash* | 0 | LULUS |
| Keluaran cocok dengan artefak | ya | LULUS |

## 6. Dokumentasi

| Berkas | Status |
|---|---|
| `README.md` | LULUS |
| `docs/model_card_draft.md` | LULUS, memuat penggunaan yang tidak dianjurkan |
| `weights/README.md` | LULUS |
| `references/README.md` | LULUS, audit sitasi per kalimat |
| `SUBMISSION_CHECKLIST.md` | LULUS |
| `docs/originality_statement_placeholder.md` | LULUS sebagai penanda kewajiban |

Tautan internal pada seluruh berkas Markdown: **0 rusak**.

## 7. Kode dan Pengujian

| Pemeriksaan | Hasil | Status |
|---|---|---|
| Uji unit | 69 lulus | LULUS |
| *Path* absolut personal pada kode sumber | tidak ada | LULUS |
| *Secret*, *API key*, *token* | tidak ada | LULUS |
| Penanda TODO atau FIXME | tidak ada | LULUS |

## 8. Kepatuhan Regulasi

| Ketentuan | Status | Bukti |
|---|---|---|
| Tanpa *external pretrained weights* | LULUS | `build_compliant_model` menolak `pretrained=True` dan argumen menyerupai checkpoint, `YOLO_OFFLINE=1` aktif |
| Hanya dataset resmi | LULUS | Tidak ada dataset lain pada repository maupun rujukan kode |
| Tanpa pemrosesan LLM atau API | LULUS | Seluruh prapemrosesan berupa kode Python deterministik |
| Pemetaan 11 kelas canonical | LULUS | `canonical_mapping_report.md` |
| Split resmi dipertahankan | LULUS | Tidak ada penggabungan atau pengacakan ulang |
| Tanpa kebocoran data | LULUS | `dataset_audit_report.md` |
| *Seeding* deterministik | LULUS | `seed=42` pada Python, NumPy, PyTorch |
| Satu model final | LULUS | `final_model_metadata.json` |

## 9. Repository dan Git

| Pemeriksaan | Hasil | Status |
|---|---|---|
| Repository publik | ya | LULUS |
| Riwayat commit bertahap | ya | LULUS |
| Dataset mentah pada riwayat publik | 0 objek dapat dijangkau dari `origin/main` | LULUS |
| Berkas prompt internal | sudah dikeluarkan, lihat `repository_cleanup.md` | LULUS |

## 10. Item Terbuka

### 10.1 GitHub Release belum dipublikasikan

Rilis sudah disiapkan lengkap. Berkas *checksum* dan metadata terkomit, dan
perintah `gh release create` beserta daftar aset tersedia pada
`weights/README.md`.

Penghalang: `gh auth status` melaporkan token pada *keyring* tidak valid,
sehingga publikasi tidak dapat dijalankan sebelum `gh auth login` diulang.

Dampak bila tidak diselesaikan: regulasi mensyaratkan tautan unduhan langsung
untuk bobot model. Tanpa rilis, juri tidak dapat mengunduh bobot karena
berkas tersebut sengaja tidak dikomit ke Git.

### 10.2 Metadata rilis belum diperbarui

Field `release` pada `artifacts/reports/final_model_metadata.json` masih
bernilai `published: false` dan perlu diperbarui bersama tautan aset pada
`weights/README.md` setelah rilis terbit.

## 11. Item di Luar Jangkauan Verifikasi Otomatis

1. **Pernyataan orisinalitas bertanda tangan.** Artefak manusia di luar
   repository. Daftar periksa tersedia pada
   `docs/originality_statement_placeholder.md`.
2. **Komposisi tim.** Ketentuan 2 sampai 3 mahasiswa aktif, satu universitas,
   satu ketua tim, dan satu dosen pembimbing tidak dapat diperiksa dari
   repository.

## 12. Eksperimen yang Sedang Berjalan

Pelatihan dengan anggaran 100 *epoch* sedang dijalankan sebagai eksperimen
terpisah. Dasarnya adalah kurva pelatihan model final yang menunjukkan model
belum konvergen pada epoch 50: mAP@0.5 masih naik, *train loss* masih turun,
dan *val loss* juga masih turun.

Eksperimen resolusi 960 dihentikan pada epoch 7. Alasannya, bila model pada
resolusi 640 saja belum konvergen dalam 50 *epoch*, model resolusi 960 yang
konvergensinya teramati sekitar dua kali lebih lambat akan jauh lebih belum
konvergen pada anggaran yang sama. Checkpoint beserta skrip pelanjutnya tetap
disimpan, lihat `artifacts/reports/experiment_960_status.md`.

Model final yang dibekukan untuk submission tetap model 640 dengan 50
*epoch*. Tidak ada eksperimen yang akan menggantikannya kecuali terbukti
unggul pada prosedur evaluasi yang sama, pada *split* validasi, dan
dikonfirmasi pada *split* test.

## 13. Keterbatasan Audit Ini

Disampaikan terbuka agar cakupan audit tidak terbaca lebih luas daripada yang
sebenarnya:

1. **Penamaan sebagian laporan masih memakai penomoran block internal**,
   misalnya `block13_error_analysis.md`, yang tidak bermakna bagi juri.
   Penggantian nama ditunda agar tidak memicu tautan rusak menjelang tenggat.
2. **Reproduksi pelatihan bit per bit tidak diverifikasi** dan tidak diklaim,
   karena nondeterminisme *backend* MPS.
3. **Metrik lokal diagnostik tidak stabil** antar pengulangan pada rentang
   0,22 sampai 0,42. Metrik ini berstatus sekunder, bukan angka yang
   dilaporkan.
4. **Definisi *F1* panitia tidak diketahui.** Angka yang dilaporkan merupakan
   *F1* macro hasil implementasi evaluasi lokal.
5. **Belum ada validasi di luar dataset kompetisi.**
6. **Satu regenerasi analisis kesalahan menghasilkan keluaran yang rusak dan
   dibatalkan.** Eksekusi yang dijalankan bersamaan dengan pelatihan 100
   *epoch* hanya menghasilkan sekitar sembilan prediksi untuk 2.106 citra,
   padahal eksekusi yang sah menghasilkan 1.381 *true positive*. Artefak yang
   sah dipulihkan dari riwayat Git dan dipakai kembali, sedangkan penyebab
   kegagalannya belum ditelusuri karena kemungkinan besar berkaitan dengan
   perebutan sumber daya MPS. Hal ini disampaikan terbuka agar tidak terbaca
   seolah setiap eksekusi ulang pasti menghasilkan angka yang sama.

## 14. Kesimpulan

Seluruh aspek teknis berada dalam kondisi siap dan dapat diaudit. Angka yang
dilaporkan konsisten pada seluruh artefak dan dokumen, berasal dari satu
sumber kebenaran, dan dapat direproduksi dengan dua perintah.

Audit ini **tidak** menyatakan submission selesai. Dua item mekanis, yaitu
publikasi rilis dan pembaruan metadata rilis, serta dua item administratif,
yaitu pernyataan orisinalitas dan konfirmasi komposisi tim, masih terbuka.
