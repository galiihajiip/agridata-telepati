# Model Card: Detektor Penyakit Padi AgriData TELEPATI 8.0

**Status: FINAL.** Konfigurasi pelatihan dibekukan pada
`configs/final_model_config.yaml`, dan seluruh metrik pada dokumen ini
berasal dari hasil evaluasi aktual terhadap bobot final, bukan angka
sementara.

## Identitas model

| Field | Nilai |
|---|---|
| Nama | `agridata-telepati8-yolov8n` |
| Tugas | *Object detection* |
| Jumlah kelas | 11 kelas canonical |
| Arsitektur | YOLOv8n (Ultralytics), sekitar 3,0 juta parameter |
| Masukan | Citra RGB, ukuran 640 x 640 |
| Keluaran | *Bounding box* format xyxy, kelas, dan *confidence score* |
| Ukuran berkas | 6.260.394 byte |
| SHA-256 | `c631a363ab580ca614c52b51eaaf798e31c44a3ba92f2aa05efcfe27f5a86965` |
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
| *Pretrained* | `False`, dibangun dari definisi arsitektur saja |
| *Epoch* | 100 |
| Ukuran citra | 640 |
| *Batch size* | 16 |
| *Optimizer* | AdamW |
| *Learning rate* | 0,001 |
| *Weight decay* | 0,0005 |
| *Seed* | 42 |
| Perangkat | Apple Silicon MPS |
| Durasi | 20,84 jam |

Konfigurasi dipilih dari 21 percobaan terkontrol. Alasan setiap parameter
tercatat pada `configs/final_model_config.yaml` dan
`artifacts/reports/block14_final_model_selection.md`.

## Evaluasi

Dievaluasi pada *split* validasi. Data uji tidak pernah dipakai untuk
penyetelan apa pun.

Konvensi: mAP@50 dari `model.val()`, *F1-Score* sebagai rata-rata antar
kelas (*macro*) dari kurva *F1* pada titik operasi terbaik, ambang NMS IoU
0,5.

| Metrik | Valid | Test |
|---|---:|---:|
| **mAP@50** | **66,78%** | **65,96%** |
| **F1-Score macro** | **68,26%** | **66,41%** |
| mAP@0.5:0.95 | 0,4141 | 0,4330 |
| *Precision* pada titik operasi | 0,7188 | 0,6983 |
| *Recall* pada titik operasi | 0,6722 | 0,6634 |

AP@0.5 per kelas berkisar dari 0,9755 (Narrow brown) sampai 0,3303
(Brown spot) pada *split* valid. Rincian lengkap tersedia pada
`artifacts/reports/evaluation_valid.md`.

Evaluasi pada *split* test dijalankan satu kali setelah model dibekukan, dan
*split* itu tidak pernah dipakai untuk penyetelan maupun untuk memilih model
final. Selisih mAP@0.5 terhadap validasi hanya -0,0082, tanpa indikasi
*overfitting* terhadap *split* validasi.

## Keterbatasan

1. **Model dilatih dari nol** tanpa *external pretrained weights*, sesuai
   aturan kompetisi. Model tidak mewarisi representasi visual umum.
2. ***Recall* merupakan pembatas utama.** Pada sapuan *confidence threshold*
   dengan metrik lokal *micro*, *recall* tertinggi hanya 0,2365. Komposisi
   kesalahan didominasi *false negative* sebesar 55,6 persen, sedangkan salah
   kelas hanya 1,1 persen.
3. **Objek kecil sulit dideteksi.** Median luas *bounding box* yang terlewat
   sekitar setengah dari median keseluruhan.
4. **Performa antar kelas timpang**, dengan selisih AP@0.5 melebihi 0,64
   antara kelas terbaik dan terburuk.
5. **Ketidakseimbangan kelas nyata**, yaitu rasio 22,6 kali pada *split*
   latih. Mitigasi *oversampling* diuji dan tidak menunjukkan manfaat pada
   skala penyaringan, sehingga tidak diadopsi.
6. **Metrik lokal diagnostik tidak stabil**, bervariasi pada rentang 0,22
   sampai 0,42 antar pengulangan. Metrik ini berstatus sekunder dan bukan
   *F1* yang dilaporkan. *F1* macro yang dilaporkan dihitung dari `model.val()`
   dan stabil.
7. **Tidak ada jaminan determinisme bit per bit** pada Apple Silicon dengan
   *backend* MPS.
8. **Belum ada validasi eksternal** di luar dataset kompetisi.

## Reproducibility

Prapemrosesan terverifikasi identik byte per byte. Konfigurasi tercatat
lengkap. Reproduksi pelatihan bit per bit tidak diklaim. Rincian tersedia
pada `artifacts/audit/reproducibility_checklist.md`.

## Pernyataan kepatuhan

Tanpa *external pretrained weights*, tanpa dataset eksternal, dan tanpa
pemrosesan dataset menggunakan LLM maupun API. Audit lengkap tersedia pada
`artifacts/audit/final_submission_readiness.md`.
