# Daftar Periksa Submission

Status per 24 Oktober 2026. Tenggat submission 25 Oktober 2026 pukul 23.59.

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

- [x] Satu model final: YOLOv8s-P2, 250 *epoch*, dilatih di Kaggle 2x T4
- [x] mAP@50 70,71% dan *F1-Score* macro 72,33% pada *split* valid
- [x] Dikonfirmasi pada *split* test: 70,65% dan 71,45%
- [x] Dipilih dari empat kandidat skala penuh, hanya berdasarkan *split* valid
- [x] Pengunduhan `yolo26n.pt` oleh pengecekan AMP diblokir pada seluruh kandidat
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

## Angka untuk form submission

| Isian form | Nilai | Sumber |
|---|---|---|
| mAP@50 (%) | **70,71** | `artifacts/reports/official_metrics_valid.json` |
| F1-Score (%) | **72,33** | `artifacts/reports/official_metrics_valid.json` |

Kedua angka berasal dari *split* valid, konvensi yang sama dengan seluruh
laporan sebelumnya. Angka *split* test (70,65 dan 71,45) dicantumkan di README
sebagai konfirmasi.

## Tindakan yang masih perlu dilakukan

1. **Pastikan seluruh perubahan sudah ter-*push*** oleh daemon auto-commit
   sebelum mengisi form, karena juri membaca repository publik.
2. **Publikasikan GitHub Release** berisi `best.pt` model YOLOv8s-P2, berkas
   *checksum*, dan metadata. Perintah siap pakai tersedia pada
   `weights/README.md`. Bila `gh auth status` gagal, jalankan `gh auth login`.
3. **Perbarui `weights/README.md` dan field `release`** pada
   `artifacts/reports/final_model_metadata.json` dengan tautan aset setelah
   rilis terbit.
4. **Selesaikan pernyataan orisinalitas bertanda tangan** sesuai daftar periksa
   pada `docs/originality_statement_placeholder.md`.
5. **Konfirmasi komposisi tim** terhadap data pendaftaran kompetisi.
6. **Isi form submission:** surat orisinalitas (PDF maks. 2 MB), tautan GitHub
   Release bobot, tautan notebook, tautan repository, serta dua angka di atas.
