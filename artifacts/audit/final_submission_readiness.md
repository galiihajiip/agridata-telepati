# Audit Kesiapan Submission Final

Audit ini memeriksa seluruh paket submission setelah rangkaian pekerjaan
BLOCK A sampai BLOCK H selesai. Seluruh angka pada dokumen ini berasal dari
pemeriksaan yang dijalankan pada saat audit, bukan dari catatan sebelumnya.

Tanggal audit: 22 September 2026
Tenggat submission: 26 September 2026
*Commit* saat audit: `2e8521d51b16200c16e99e14524f6144797242c3`
Repository: https://github.com/galiihajiip/agridata

## 1. Ringkasan Status

| Kategori | Lulus | Terbuka | Di luar jangkauan otomatis |
|---|---:|---:|---:|
| Notebook | 7 | 0 | 0 |
| README dan dokumentasi | 6 | 0 | 0 |
| Requirements dan lingkungan | 3 | 0 | 0 |
| Kode sumber dan pengujian | 4 | 0 | 0 |
| Bobot model | 5 | 0 | 0 |
| Rilis | 0 | 2 | 0 |
| Riwayat Git | 4 | 0 | 0 |
| Kepatuhan regulasi | 8 | 0 | 0 |
| Dokumen orisinalitas dan tim | 1 | 0 | 2 |
| **Total** | **38** | **2** | **2** |

**Kesimpulan: paket teknis siap. Dua item terbuka bersifat administratif dan
berada pada kendali tim, bukan pada kode.**

## 2. Notebook

| Pemeriksaan | Hasil | Status |
|---|---|---|
| Jumlah sel | 117 sel, 45 di antaranya sel kode | LULUS |
| Eksekusi penuh | 0 *error*, 0 sel belum dieksekusi | LULUS |
| Figur tertanam | 15 figur | LULUS |
| Struktur naratif | 22 bagian utama lengkap | LULUS |
| Bahasa | Bahasa Indonesia penuh, istilah asing dimiringkan | LULUS |
| *Em dash* | 0 | LULUS |
| Ukuran berkas | 7,8 MB | LULUS |

Catatan: figur sempat tidak tertanam sama sekali akibat `matplotlib.use("Agg")`
pada modul visualisasi yang dipakai juga oleh skrip tanpa layar. Diperbaiki
pada BLOCK H dengan mengembalikan *backend* inline di dalam notebook.

## 3. README dan Dokumentasi

| Berkas | Status |
|---|---|
| `README.md` | LULUS, berbahasa Indonesia, 19 bagian, angka sesuai artefak |
| `docs/model_card_draft.md` | LULUS, status FINAL, memuat penggunaan yang tidak dianjurkan |
| `weights/README.md` | LULUS, memuat *checksum* dan perintah rilis |
| `references/README.md` | LULUS, audit sitasi per kalimat |
| `docs/originality_statement_placeholder.md` | LULUS sebagai placeholder |
| `SUBMISSION_CHECKLIST.md` | LULUS |

Tautan internal pada seluruh berkas Markdown diperiksa: **0 tautan rusak**.

## 4. Requirements dan Lingkungan

| Pemeriksaan | Hasil | Status |
|---|---|---|
| Versi terkunci | 15 entri memakai `==` | LULUS |
| Kesesuaian dengan *virtual environment* | seluruh paket inti cocok | LULUS |
| Uji instalasi dari nol | dilakukan pada BLOCK 16, menemukan dan memperbaiki konflik `numpy` | LULUS |

## 5. Kode Sumber dan Pengujian

| Pemeriksaan | Hasil | Status |
|---|---|---|
| Uji unit | 69 lulus | LULUS |
| *Path* absolut personal pada kode | tidak ditemukan | LULUS |
| *Secret*, *API key*, *token* | tidak ditemukan | LULUS |
| Penanda TODO atau FIXME | tidak ditemukan | LULUS |

## 6. Bobot Model

| Field | Nilai | Status |
|---|---|---|
| Berkas | `runs/detect/final/final_model/weights/best.pt` | LULUS |
| Ukuran | 6.253.994 byte | LULUS |
| SHA-256 | `9d74fffdd977a7bb6749bc828fe908278c5d3eaa24c3cfdbbe5a560d41f5d308` | LULUS, diverifikasi ulang dengan `shasum -c` |
| Pemuatan proses bersih | berhasil, 11 kelas | LULUS |
| Inferensi | berhasil menghasilkan deteksi | LULUS |

## 7. Konsistensi Metrik

Nilai mAP@0.5 diperiksa pada tiga artefak independen:

| Sumber | mAP@0.5 |
|---|---|
| `final_model_metadata.json` | 0,6276771766514752 |
| `evaluation_valid.json` | 0,6276771766514752 |
| `block15_final_training_summary.json` | 0,6276771766514752 |

**Identik hingga digit terakhir.** Seluruh penyebutan nilai lama 0,5620 pada
dokumentasi diperiksa satu per satu dan seluruhnya berada pada konteks
historis yang menyebut model 20 *epoch* secara eksplisit.

## 8. Riwayat Git

| Pemeriksaan | Hasil | Status |
|---|---|---|
| Jumlah *commit* | 224 | LULUS |
| Sinkronisasi dengan remote | `main` sama dengan `origin/main` | LULUS |
| Dataset mentah pada riwayat publik | **0 objek** dapat dijangkau dari `origin/main` | LULUS |
| Ukuran berkas terlacak | 48 MB | LULUS |

Komposisi awalan pesan *commit*: `feat` 73, `docs` 58, `refactor` 39,
`chore` 36, `fix` 11, `test` 7.

Catatan penting: paparan dataset mentah sebesar 590 MB yang sebelumnya ada
pada riwayat publik **sudah teratasi**. Penulisan ulang riwayat dengan
`git filter-repo` telah di-*force-push* oleh pemilik repository. Cabang lokal
`backup-origin-main` masih menyimpan riwayat lama sebagai cadangan dan tidak
pernah di-*push*, sehingga `.git` lokal berukuran 974 MB. Cabang tersebut
aman dihapus bila sudah tidak diperlukan.

## 9. Kepatuhan Regulasi

| Ketentuan | Status | Bukti |
|---|---|---|
| Tanpa *external pretrained weights* | LULUS | `build_compliant_model` menolak `pretrained=True` dan argumen menyerupai *checkpoint*; `YOLO_OFFLINE=1` aktif |
| Hanya dataset resmi | LULUS | Tidak ada direktori atau rujukan dataset lain |
| Tanpa pemrosesan LLM atau API | LULUS | Seluruh prapemrosesan berupa kode Python deterministik |
| Pemetaan 11 kelas canonical | LULUS | Nol kategori tidak terpetakan pada ketiga *split* |
| Split resmi dipertahankan | LULUS | Tidak ada penggabungan atau pengacakan ulang |
| Tanpa kebocoran data | LULUS | Satu duplikat persis dikeluarkan dari *manifest* latih |
| *Seeding* deterministik | LULUS | `seed=42` pada Python, NumPy, dan PyTorch |
| Satu model final | LULUS | `final_model_metadata.json` |

## 10. Item yang Masih Terbuka

### 10.1 GitHub Release belum dipublikasikan

Rilis sudah disiapkan lengkap: berkas *checksum* terkomit, metadata terisi,
dan perintah `gh release create` beserta daftar aset tersedia pada
`weights/README.md`.

Penghalang saat ini: `gh auth status` melaporkan token pada *keyring* tidak
valid, sehingga publikasi tidak dapat dijalankan sebelum `gh auth login`
diulang.

Dampak bila tidak diselesaikan: regulasi mensyaratkan tautan unduhan langsung
untuk bobot model. Tanpa rilis, juri tidak dapat mengunduh bobot, karena
berkas tersebut memang sengaja tidak dikomit ke Git.

### 10.2 Metadata rilis belum diperbarui

Setelah rilis terbit, `field` `release` pada
`artifacts/reports/final_model_metadata.json` masih bernilai
`published: false` dan perlu diperbarui bersama tautan aset pada
`weights/README.md`.

## 11. Item di Luar Jangkauan Verifikasi Otomatis

### 11.1 Pernyataan orisinalitas bertanda tangan

Dokumen bertanda tangan basah merupakan artefak manusia di luar repository.
Daftar periksa tersedia pada `docs/originality_statement_placeholder.md`.
Aspek orisinalitas yang dapat diverifikasi secara teknis, yaitu tanpa dataset
eksternal, tanpa bobot pra-latih eksternal, dan tanpa pemrosesan LLM, sudah
terverifikasi pada bagian 9.

### 11.2 Komposisi tim

Ketentuan 2 sampai 3 mahasiswa aktif, satu universitas, satu ketua tim, dan
satu dosen pembimbing tidak dapat diperiksa dari repository. Perlu
dikonfirmasi langsung terhadap data pendaftaran.

## 12. Keterbatasan Audit Ini

Disampaikan terbuka agar tidak ada kesan cakupan audit lebih luas daripada
yang sebenarnya:

1. **Laporan audit historis per block masih berbahasa Inggris**, yaitu
   `final_submission_audit.md`, `block21_final_freeze.md`,
   `block16_clean_reproduction_test.md`, `reproducibility_checklist.md`, serta
   laporan block 10 sampai 14. Dokumen submission utama, yaitu notebook,
   README, model card, referensi, dan informasi bobot, seluruhnya sudah
   berbahasa Indonesia. Komentar dan *docstring* pada kode juga masih
   berbahasa Inggris.
2. **Dua berkas dikecualikan dari pembersihan *em dash*:** dokumen
   spesifikasi milik pengguna dan satu berkas arsip historis. Mengubah
   keduanya akan mengubah rekaman yang sengaja dibekukan.
3. **Reproduksi pelatihan bit per bit tidak diverifikasi** dan memang tidak
   diklaim, karena nondeterminisme *backend* MPS.
4. **Nilai *F1* lokal tidak stabil** antar pengulangan pada rentang 0,22
   sampai 0,42. Penyebab pastinya belum ditelusuri tuntas. Sapuan *threshold*
   yang dihitung ulang dari prediksi tersimpan bersifat deterministik dan
   dapat dipakai sebagai acuan yang lebih stabil.
5. **Audit ini tidak menguji model pada data di luar dataset kompetisi**,
   sehingga kemampuan generalisasi ke kondisi lapangan lain belum diketahui.

## 13. Kesimpulan

Seluruh aspek teknis submission berada dalam kondisi siap dan dapat diaudit:
notebook berjalan bersih dengan figur lengkap, metrik konsisten pada tiga
artefak independen, bobot model terverifikasi *checksum*-nya, kepatuhan
regulasi ditegakkan pada tingkat kode, dan riwayat Git publik sudah bersih
dari dataset mentah.

Dua item terbuka, yaitu publikasi rilis dan pembaruan metadata rilis,
bersifat mekanis dan dapat diselesaikan dalam hitungan menit setelah
otentikasi GitHub CLI diperbarui.

Dua item lain, yaitu pernyataan orisinalitas bertanda tangan dan konfirmasi
komposisi tim, berada di luar kemampuan verifikasi otomatis dan merupakan
tanggung jawab tim.

Audit ini **tidak** menyatakan submission selesai. Audit ini menyatakan bahwa
bagian yang berada dalam kendali repository sudah selesai dan terverifikasi,
sedangkan empat item sisanya tercatat terbuka secara eksplisit.
