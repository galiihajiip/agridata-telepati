# Status Eksperimen Resolusi 960

Catatan status eksperimen pelatihan pada resolusi 960. Dokumen ini dibuat agar
keputusan menjeda eksperimen tercatat dan dapat ditelusuri, bukan hilang tanpa
keterangan.

## 1. Tujuan Eksperimen

Menguji apakah melatih model pada resolusi 960 memberikan hasil lebih baik
daripada model final pada resolusi 640.

Dasar pengujian berasal dari analisis kesalahan model 640 yang seluruhnya
menunjuk ke arah yang sama:

- 63,5 persen kesalahan berupa *false negative*;
- median luas objek yang terlewat sekitar setengah median keseluruhan;
- 38 sampai 47 persen *bounding box* menutupi kurang dari satu persen luas citra;
- rasio *false negative* pada adegan padat 0,7981 berbanding 0,4542 pada adegan jarang.

Sebelumnya sudah diuji bahwa menaikkan resolusi hanya pada tahap inferensi
justru menurunkan performa secara drastis, dari mAP@0.5 sebesar 0,6277 menjadi
0,4200 pada 960 dan 0,1164 pada 1280. Penyebabnya ketidakcocokan antara
resolusi latih dan resolusi inferensi. Karena itu resolusi tinggi perlu
diterapkan sejak pelatihan.

## 2. Konfigurasi

| Parameter | Model final 640 | Eksperimen 960 |
|---|---|---|
| Ukuran citra | 640 | 960 |
| *Batch* | 16 | 8 |
| *Epoch* | 50 | 50 |
| *Seed* | 42 | 42 |
| Arsitektur | `yolov8n.yaml` | `yolov8n.yaml` |
| *Pretrained* | `False` | `False` |

**Keterbatasan metodologis yang harus dinyatakan:** eksperimen ini mengubah
dua variabel sekaligus. Penurunan *batch* dari 16 menjadi 8 dilakukan karena
keterbatasan memori, bukan karena alasan metodologis. Estimasi pemakaian
memori pada 960 dengan *batch* 16 mencapai sekitar 11,9 GB dari 16 GB RAM
terpadu yang tersedia.

Akibatnya, apabila hasil eksperimen berbeda dari model 640, perbedaan tersebut
**tidak dapat diatribusikan pada resolusi saja**.

## 3. Hasil Sementara Sebelum Dijeda

Pelatihan dijeda setelah epoch 7 dari 50 selesai, dengan durasi berjalan
sekitar 2 jam 40 menit.

Perbandingan terhadap model 640 pada epoch yang sama:

| Epoch | 640 mAP@0.5 | 960 mAP@0.5 |
|---:|---:|---:|
| 1 | 0,0366 | 0,0195 |
| 2 | 0,1120 | 0,0426 |
| 3 | 0,1863 | 0,0986 |
| 4 | 0,2042 | 0,1158 |
| 6 | tidak dicatat terpisah | 0,1957 |

Eksperimen 960 tertinggal kira-kira dua kali lipat terhadap lintasan model
640 pada epoch yang sama.

**Peringatan interpretasi:** ketertinggalan pada fase awal tidak otomatis
berarti hasil akhirnya akan lebih rendah. Model beresolusi lebih tinggi yang
dilatih dari inisialisasi acak memiliki lebih banyak posisi spasial yang harus
dipelajari, sehingga konvergensi awal yang lebih lambat merupakan hal yang
masuk akal. Lintasan pelatihan tidak bersifat linear, dan kurva masih dapat
menikung naik pada fase berikutnya. Karena itu hasil sementara ini tidak
cukup untuk menyimpulkan kegagalan eksperimen.

## 4. Alasan Dijeda

Pelatihan dijeda, bukan dibatalkan, karena alasan berikut:

1. Paket submission berada dalam kondisi berisiko **REJECTED**. Terdapat tiga
   sumber angka yang saling bertentangan di dalam repository, dengan selisih
   relatif *F1* mencapai sekitar 48 persen, jauh melampaui ambang 2 persen
   yang ditetapkan regulasi.
2. Perbaikan kondisi tersebut membutuhkan GPU untuk regenerasi artefak metrik
   dan eksekusi ulang notebook.
3. Menjalankan evaluasi bersamaan dengan pelatihan berisiko, karena project
   ini sudah mendokumentasikan bahwa dua proses MPS yang berjalan bersamaan
   dapat menghasilkan variasi metrik.
4. Regulasi menempatkan reproduktibilitas setara dengan skor, dan menempatkan
   performa model pada prioritas kelima dari tujuh.

Dengan kata lain, memperbaiki konsistensi paket submission memberikan manfaat
yang jauh lebih pasti daripada melanjutkan eksperimen yang hasilnya belum
dapat dipastikan.

## 5. Kondisi Checkpoint

Pelatihan dapat dilanjutkan tanpa mengulang dari awal.

| Field | Nilai |
|---|---|
| Berkas | `runs/detect/final/final_model_960/weights/last.pt` |
| Cadangan | `artifacts/archive/960_paused/last_epoch6_backup.pt` |
| Epoch terakhir selesai | 7 |
| Akan lanjut dari epoch | 8 |
| Sisa epoch | 42 |
| State optimizer | tersedia |
| EMA | tersedia |
| Jumlah update | 1.962 |
| *Best fitness* | 0,11513 |

Checkpoint diambil cadangannya terlebih dahulu sebelum proses dihentikan,
untuk menghindari risiko kerusakan berkas apabila proses dimatikan pada saat
penulisan checkpoint sedang berlangsung. Kedua salinan diverifikasi dapat
dimuat dan memuat state yang lengkap.

## 6. Cara Melanjutkan

```bash
# Periksa kelayakan tanpa menjalankan pelatihan
python scripts/resume_training_960.py --dry-run

# Lanjutkan pelatihan dari epoch 8 sampai 50
python scripts/resume_training_960.py
```

Estimasi waktu untuk 42 epoch sisa sekitar 12,3 jam pada perangkat yang sama.

Skrip melakukan pemeriksaan berikut sebelum melanjutkan:

1. checkpoint ada dan dapat dimuat;
2. state optimizer belum dilucuti;
3. epoch berikutnya belum mencapai total epoch;
4. `pretrained` bernilai `False`, dan menolak berjalan bila bernilai `True`.

## 7. Status Kandidat Final

Model final yang dibekukan untuk submission tetap **model resolusi 640**.

Eksperimen 960 diperlakukan sebagai eksperimen eksploratif. Eksperimen ini
hanya akan dipertimbangkan menggantikan model final apabila:

1. pelatihan diselesaikan sampai epoch 50;
2. dievaluasi dengan prosedur yang sama persis dengan model 640;
3. hasilnya mengungguli model 640 pada *split* validasi;
4. keunggulan tersebut dikonfirmasi pada *split* test.

Sampai seluruh syarat itu terpenuhi, tidak ada perubahan pada model final,
bobot, maupun angka yang dilaporkan.
