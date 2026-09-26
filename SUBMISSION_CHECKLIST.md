# Daftar Periksa Submission

Status per 26 September 2026, yaitu hari tenggat submission.

Legenda: `[x]` terverifikasi otomatis, `[ ]` masih terbuka, `[!]` di luar
kemampuan verifikasi otomatis dan harus dikonfirmasi tim.

## Dataset

- [x] Menggunakan dataset resmi kompetisi
- [x] Pemetaan 11 kelas canonical diterapkan, nol kategori tidak terpetakan
- [x] Tanpa kebocoran data, satu duplikat persis dikeluarkan dari manifest latih
- [x] Tanpa dataset eksternal
- [x] Dataset mentah tidak diubah
- [x] Pembagian split resmi dipertahankan

## Model

- [x] Satu model final, hasil pelatihan 100 *epoch*
- [x] mAP@50 66,78% dan *F1-Score* macro 68,26% pada *split* valid
- [x] Dikonfirmasi pada *split* test: 65,96% dan 66,41%
- [x] Pemilihan model dilakukan hanya di atas *split* valid, test dievaluasi sekali
- [x] *Checksum* SHA-256 bobot final tercatat dan diverifikasi
- [x] Tanpa *external pretrained weights*, ditegakkan pada tingkat kode
- [x] Bobot dapat dimuat dari proses bersih
- [x] Inferensi berjalan dan menghasilkan deteksi
- [x] `YOLO_OFFLINE=1` aktif pada seluruh skrip pelatihan dan evaluasi

## Notebook

- [x] Seluruh sel berjalan, 0 *error*, 0 sel belum dieksekusi
- [x] Narasi lengkap 22 bagian, berbahasa Indonesia
- [x] Metrik benar dan konsisten dengan artefak
- [x] Tanpa angka usang
- [x] Sitasi valid dan terverifikasi
- [x] Tanpa *em dash*
- [x] Figur tertanam pada keluaran (18 figur)
- [x] Narasi memakai sudut pandang penulis "kami" pada 70 dari 78 sel markdown

## Repository

- [x] Repository publik
- [x] Berkas kerja sementara dan perkakas pengembangan sudah dikeluarkan
- [x] Tautan internal pada seluruh berkas Markdown: 0 rusak
- [x] Tanpa *path* absolut personal, *secret*, maupun penanda TODO pada kode
- [x] Riwayat commit bertahap
- [x] README lengkap berbahasa Indonesia
- [x] `requirements.txt` terkunci pada versi eksak
- [x] Dataset mentah tidak ada pada riwayat Git publik
- [ ] Rilis bobot model dipublikasikan dengan tautan langsung

## Audit

- [x] Uji lingkungan bersih
- [x] Daftar periksa reproduktibilitas: 10 dari 10 butir lulus
- [x] Uji unit: 69 lulus
- [x] Batas kestabilan pengukuran didokumentasikan terbuka
- [x] Uji inferensi
- [x] Metrik dihasilkan ulang dan konsisten
- [x] *Checksum* bobot diverifikasi
- [x] Provenance tercatat (commit pelatihan, hash manifest, checksum)

## Dokumen

- [x] Notebook final
- [x] README
- [x] Model card
- [x] Audit kepatuhan
- [x] Audit sitasi dan daftar pustaka
- [x] Placeholder pernyataan orisinalitas
- [!] Pernyataan orisinalitas bertanda tangan basah
- [!] Komposisi tim: 2 sampai 3 mahasiswa aktif, satu universitas, satu ketua,
      satu dosen pembimbing

## Tindakan yang masih perlu dilakukan

1. **Perbarui otentikasi GitHub CLI.** `gh auth status` melaporkan token pada
   *keyring* tidak valid, sehingga publikasi rilis belum dapat dijalankan.
   Jalankan `gh auth login`.
2. **Publikasikan GitHub Release** berisi `best.pt`, berkas *checksum*, dan
   metadata. Perintah siap pakai tersedia pada `weights/README.md`.
3. **Perbarui `weights/README.md` dan field `release`** pada
   `artifacts/reports/final_model_metadata.json` dengan tautan aset setelah
   rilis terbit.
4. **Selesaikan pernyataan orisinalitas bertanda tangan** sesuai daftar periksa
   pada `docs/originality_statement_placeholder.md`.
5. **Konfirmasi komposisi tim** terhadap data pendaftaran kompetisi.
6. **Commit dan push seluruh perubahan.** Pekerjaan hari ini belum dikomit,
   sesuai permintaan pemilik repository untuk melakukannya sendiri. Perubahan
   mencakup penggantian model final ke 100 *epoch*, pembaruan seluruh artefak
   evaluasi, README, model card, dokumen audit, dan notebook yang sudah
   dieksekusi ulang.
7. **Opsional:** hapus cabang lokal `backup-origin-main` bila sudah yakin
   dengan hasil pembersihan riwayat, lalu jalankan `git gc --prune=now` untuk
   mengecilkan `.git` lokal dari 974 MB. Cabang ini tidak pernah di-*push*.
