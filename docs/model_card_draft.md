# Model Card: Detektor Penyakit Padi AgriData TELEPATI 8.0

**Status: FINAL.** Konfigurasi pelatihan dibekukan pada
`configs/final_model_config.yaml`, dan seluruh metrik pada dokumen ini
berasal dari hasil evaluasi aktual terhadap bobot final, bukan angka
sementara.

## Tim

| | |
|---|---|
| Nama tim | Di Bandung Di Ganesha |
| Perguruan tinggi | Universitas Pembangunan Nasional "Veteran" Jawa Timur |
| Ketua | Galih Aji Pangestu |
| Anggota | Stevyka Frista Aninda, Putri Ayu Ajeng Nina Zuraida |
| Dosen pembimbing | Andreas Nugroho Sihananto, S.Kom., M.Kom. |
| Cabang lomba | AgriData Intelligence Race, TELEPATI 8.0 |

## Identitas model

| Field | Nilai |
|---|---|
| Nama | `agridata-telepati8-yolov8s-p2` |
| Tugas | *Object detection* |
| Jumlah kelas | 11 kelas canonical |
| Arsitektur | YOLOv8s-P2 (Ultralytics), sekitar 10,6 juta parameter |
| Masukan | Citra RGB, ukuran 640 x 640 |
| Keluaran | *Bounding box* format xyxy, kelas, dan *confidence score* |
| Ukuran berkas | 21.754.576 byte |
| SHA-256 | `4dc86ac0e53d2849fb1b79f1a68dcb5284ae6f1e8fef27e4416fa54c6b772a9f` |
| Versi pemetaan kelas | 1.0.0 |

## Penggunaan yang dituju

Deteksi kondisi penyakit dan kesehatan tanaman padi dari citra lapangan,
baik dari kamera genggam maupun drone, sebagai komponen sistem pemantauan
pertanian cerdas. Konteks penggunaannya mengikuti studi kasus TELEPATI 8.0
AgriData Intelligence Race, yaitu membantu petani memantau lahan luas tanpa
harus memeriksa setiap tanaman secara manual.

## Penggunaan yang tidak dianjurkan

1. Pengambilan keputusan tunggal untuk tindakan pengendalian penyakit tanpa
   verifikasi manusia. *Recall* model masih rendah, sehingga sebagian besar
   gejala berpotensi terlewat.
2. Penggunaan pada komoditas selain padi, karena model tidak pernah dilatih
   maupun diuji pada tanaman lain.
3. Penggunaan pada kondisi pencitraan yang jauh berbeda dari dataset latih,
   misalnya citra satelit atau citra mikroskopis.
4. Klaim diagnosis yang bersifat final tanpa konfirmasi ahli, terutama pada
   kelas dengan AP rendah seperti Brown spot.

## Data pelatihan

Dataset resmi TELEPATI 8.0 AgriData dalam format COCO. Tidak ada dataset
eksternal yang digunakan.

| Split | Citra | Anotasi canonical |
|---|---:|---:|
| train | 10.133 | 20.163 |
| valid | 2.106 | 4.888 |
| test | 1.059 | 2.670 |

Sebelas kelas canonical: Bacterial leaf blight, Bacterial panicle blight,
Blast, Brown spot, False smut, Healthy, Leaf roller, Leaf scald, Narrow
brown, Sheath blight, Tungro. Pemetaan dari 21 kategori mentah
terdokumentasi pada `src/agridata/dataset/mapping.py`.

Satu pasangan citra identik lintas *split* latih dan uji dikeluarkan dari
*manifest* data latih. Dataset mentah tidak diubah.

## Prosedur pelatihan

| Parameter | Nilai |
|---|---|
| *Pretrained* | `False`, dibangun dari definisi arsitektur `yolov8s-p2.yaml` saja |
| *Epoch* | 250 (model terbaik pada *epoch* 238 menurut *fitness* validasi) |
| Ukuran citra | 640 |
| *Batch size* | 32 (16 per GPU) |
| *Optimizer* | SGD, *momentum* 0,937 |
| *Learning rate* | 0,01, jadwal linear |
| *Weight decay* | 0,0005 |
| *Seed* | 42 |
| Perangkat | Kaggle Notebooks, 2x NVIDIA Tesla T4, DDP dengan AMP |
| Durasi | 8,11 jam |

Konfigurasi dasar dipilih dari 21 percobaan penyaringan, lalu arsitekturnya
dipilih dari empat kandidat skala penuh hanya berdasarkan *split* validasi.
Alasannya tercatat pada `configs/final_model_config.yaml`,
`artifacts/reports/block14_final_model_selection.md`, dan
`artifacts/candidates/README.md`.

## Evaluasi

Dievaluasi pada *split* validasi. Data uji tidak pernah dipakai untuk
penyetelan apa pun.

Konvensi: mAP@50 dari `model.val()`, *F1-Score* sebagai rata-rata antar
kelas (*macro*) dari kurva *F1* pada titik operasi terbaik, ambang NMS IoU
0,5.

| Metrik | Valid | Test |
|---|---:|---:|
| **mAP@50** | **70,71%** | **70,65%** |
| **F1-Score macro** | **72,33%** | **71,45%** |
| mAP@0.5:0.95 | 0,4611 | 0,4830 |
| *Precision* pada titik operasi | 0,7353 | 0,7626 |
| *Recall* pada titik operasi | 0,7206 | 0,6904 |

AP@0.5 per kelas berkisar dari 0,9864 (Narrow brown) sampai 0,3755
(Brown spot) pada *split* valid. Rincian lengkap tersedia pada
`artifacts/reports/evaluation_valid.md`.

Evaluasi pada *split* test dijalankan satu kali setelah model dibekukan, dan
*split* itu tidak pernah dipakai untuk penyetelan maupun untuk memilih model
final. Selisih mAP@0.5 terhadap validasi hanya -0,0006, tanpa indikasi
*overfitting* terhadap *split* validasi.

## Keterbatasan

1. **Model dilatih dari nol** tanpa *external pretrained weights*, sesuai
   aturan kompetisi. Model tidak mewarisi representasi visual umum.
2. **Brown spot menjadi pembatas utama.** AP@0.5 hanya 0,3755, dan 846 dari
   1.461 kotaknya pada *split* validasi masih terlewat pada *confidence* 0,1.
   Menambah kapasitas model dan kepala deteksi objek kecil hampir tidak
   menolong kelas ini.
3. **Objek sangat kecil sulit dideteksi.** Median luas *bounding box* yang
   terlewat 719 px², kira-kira 27 x 27 piksel, sepersepuluh median keseluruhan.
4. **Performa antar kelas timpang**, dengan selisih AP@0.5 sekitar 0,61
   antara kelas terbaik dan terburuk.
5. **Ketidakseimbangan kelas nyata**, yaitu rasio 22,6 kali pada *split*
   latih. Mitigasi *oversampling* diuji dan tidak menunjukkan manfaat pada
   skala penyaringan, sehingga tidak diadopsi.
6. **Metrik lokal diagnostik berstatus sekunder** dan bukan *F1* yang
   dilaporkan. Pada model sebelumnya metrik ini sempat bervariasi antar
   pengulangan; pada model final dua eksekusi MPS dan satu eksekusi CPU
   menghasilkan angka identik.
7. **Tidak ada jaminan determinisme bit per bit** pada pelatihan GPU dengan
   DDP dan AMP.
8. **Belum ada validasi eksternal** di luar dataset kompetisi.

## Reproducibility

Prapemrosesan terverifikasi identik byte per byte. Konfigurasi tercatat
lengkap. Reproduksi pelatihan bit per bit tidak diklaim. Rincian tersedia
pada `artifacts/audit/reproducibility_checklist.md`.

## Pernyataan kepatuhan

Tanpa *external pretrained weights*, tanpa dataset eksternal, dan tanpa
pemrosesan dataset menggunakan LLM maupun API. Audit lengkap tersedia pada
`artifacts/audit/final_submission_readiness.md`.
