# Tabel Provenance Metrik

Selama pengerjaan project ini muncul beberapa nilai metrik yang berbeda.
Dokumen ini membedakan seluruh nilai tersebut agar tidak ada dua angka yang
terlihat sama-sama seperti hasil final.

Aturan pembacaan: hanya baris bertanda **FINAL** yang merupakan angka yang
dilaporkan. Seluruh baris lain merupakan hasil historis atau metrik
diagnostik, dan tidak boleh disejajarkan dengan angka final.

## 1. Nilai mAP@0.5

| Nilai | Status | Model | Konfigurasi | Sumber artefak |
|---|---|---|---|---|
| 0,5620 | Historis | 20 *epoch*, resolusi 640 | NMS 0,7 | `artifacts/archive/20epoch_run/evaluation_valid.json` |
| 0,6277 | Historis | 50 *epoch*, resolusi 640 | NMS 0,7 | `artifacts/archive/50epoch_640_run/evaluation_valid.json` |
| 0,6401 | Historis, pernah final | 50 *epoch*, resolusi 640 | NMS 0,5 | `artifacts/archive/50epoch_640_run/nms05/evaluation_valid.json` |
| 0,6145 | Historis | 50 *epoch*, resolusi 640 | NMS 0,7, *split* test | `artifacts/archive/50epoch_640_run/evaluation_test.json` |
| 0,6246 | Historis, pernah final | 50 *epoch*, resolusi 640 | NMS 0,5, *split* test | `artifacts/archive/50epoch_640_run/nms05/evaluation_test.json` |
| 0,6567 | Historis | 100 *epoch*, resolusi 640 | NMS 0,7, saat pelatihan | `artifacts/archive/100epoch_v8n_run/final_training_history.csv` |
| 0,6678 | Historis, pernah final | YOLOv8n 100 *epoch*, resolusi 640 | NMS 0,5 | `artifacts/archive/100epoch_v8n_run/evaluation_valid.json` |
| 0,6596 | Historis, pernah final | YOLOv8n 100 *epoch*, resolusi 640 | NMS 0,5, *split* test | `artifacts/archive/100epoch_v8n_run/evaluation_test.json` |
| 0,7057 | Kandidat A | YOLOv8s 640, 300 *epoch* | NMS 0,5 | `artifacts/candidates/A/evaluation_valid.json` |
| 0,7139 | Kandidat D | YOLOv8m 640, 150 *epoch* | NMS 0,5 | `artifacts/candidates/D/evaluation_valid.json` |
| 0,7115 / 0,7177 | Tidak dipakai | Ensemble A+B / B+D | NMS 0,5 | `artifacts/candidates/ensembles.json` |
| 0,6997 | Historis | YOLOv8s-P2, saat pelatihan | NMS 0,7 | `artifacts/reports/final_training_history.csv` |
| **0,7071** | **FINAL, *split* valid** | **YOLOv8s-P2 640, 250 *epoch*** | **NMS 0,5** | `artifacts/reports/evaluation_valid.json` |
| **0,7065** | **FINAL, *split* test** | **YOLOv8s-P2 640, 250 *epoch*** | **NMS 0,5** | `artifacts/reports/evaluation_test.json` |
| 0,6759 | Tidak dipakai | 100 *epoch*, resolusi 640 | NMS 0,5, pengulangan lain | Lihat bagian 7 mengenai kestabilan pengukuran |
| 0,4200 | Eksperimen | 50 *epoch*, latih 640 | inferensi pada 960 | `artifacts/reports/inference_tuning_imgsz.json` |
| 0,1164 | Eksperimen | 50 *epoch*, latih 640 | inferensi pada 1280 | `artifacts/reports/inference_tuning_imgsz.json` |

## 2. Nilai F1

| Nilai | Status | Metode | Konfigurasi | Keterangan |
|---|---|---|---|---|
| 0,3326 | Historis, metodologi lama | *micro*, *threshold* tetap 0,25 | NMS 0,7 | Bukan konvensi pelaporan yang lazim, lihat `metrics_methodology.md` |
| 0,3479 | Diagnostik | *micro*, *threshold* 0,15 | NMS 0,7 | Puncak sapuan *threshold* pada metrik lokal |
| 0,6181 | Historis | *macro*, titik operasi terbaik | NMS 0,7 | Sebelum ambang NMS diturunkan |
| 0,6383 | Historis, pernah final | *macro*, titik operasi terbaik | NMS 0,5, 50 *epoch* | `artifacts/archive/50epoch_640_run/nms05/evaluation_valid.json` |
| 0,6272 | Historis, pernah final | *macro*, titik operasi terbaik | NMS 0,5, 50 *epoch*, *split* test | `artifacts/archive/50epoch_640_run/nms05/evaluation_test.json` |
| 0,2682 | Diagnostik | *micro*, *threshold* 0,10 | NMS 0,5, 100 *epoch* | Puncak sapuan *threshold* pada model final |
| 0,6826 | Historis, pernah final | *macro*, titik operasi terbaik | NMS 0,5, YOLOv8n 100 *epoch* | `artifacts/archive/100epoch_v8n_run/evaluation_valid.json` |
| 0,6641 | Historis, pernah final | *macro*, titik operasi terbaik | NMS 0,5, YOLOv8n 100 *epoch*, *split* test | `artifacts/archive/100epoch_v8n_run/evaluation_test.json` |
| 0,5893 | Diagnostik | *micro*, *threshold* 0,25 | NMS 0,5, YOLOv8s-P2 | Puncak sapuan *threshold* pada model final |
| **0,7233** | **FINAL, *split* valid** | ***macro*, titik operasi terbaik** | **NMS 0,5, YOLOv8s-P2** | `artifacts/reports/evaluation_valid.json` |
| **0,7145** | **FINAL, *split* test** | ***macro*, titik operasi terbaik** | **NMS 0,5, YOLOv8s-P2** | `artifacts/reports/evaluation_test.json` |
| 0,6321 | Tidak dipakai | *harmonic mean* dari *mean P* dan *mean R* | NMS 0,7 | Menggabungkan titik operasi berbeda antar kelas, lebih sulit direproduksi |

## 3. Mengapa Terdapat Banyak Nilai

Lima perubahan besar terjadi selama project berjalan, dan masing-masing
menghasilkan satu generasi angka:

1. **Perpanjangan pelatihan** dari 20 *epoch* menjadi 50 *epoch*.
   Menaikkan mAP@0.5 dari 0,5620 menjadi 0,6277.
2. **Koreksi metodologi F1** dari rata-rata *micro* menjadi *macro* pada
   titik operasi terbaik. Mengubah F1 dari 0,3326 menjadi 0,6181.
   Tidak mengubah mAP sama sekali.
3. **Penurunan ambang NMS** dari 0,7 menjadi 0,5. Menaikkan mAP@0.5 dari
   0,6277 menjadi 0,6401 dan F1 dari 0,6181 menjadi 0,6383, tanpa mengubah
   bobot model.
4. **Perpanjangan pelatihan kedua** dari 50 *epoch* menjadi 100 *epoch*.
   Menaikkan mAP@0.5 dari 0,6401 menjadi 0,6678 dan F1 macro dari 0,6383
   menjadi 0,6826 pada *split* valid.

5. **Penggantian arsitektur** dari YOLOv8n ke YOLOv8s-P2, dilatih 250
   *epoch* di Kaggle. Menaikkan mAP@0.5 dari 0,6678 menjadi 0,7071 dan F1
   macro dari 0,6826 menjadi 0,7233 pada *split* valid. Model ini dipilih
   dari empat kandidat hanya berdasarkan *split* valid, lihat
   `artifacts/candidates/README.md`.

Perubahan pertama, keempat, dan kelima mengubah model. Perubahan kedua mengubah cara
mengukur. Perubahan ketiga mengubah konfigurasi inferensi. Seluruhnya
terdokumentasi, dan tidak satu pun dilakukan setelah melihat hasil pada
*split* test.

Dasar perubahan keempat adalah kurva pelatihan model 50 *epoch* yang
menunjukkan model belum konvergen: mAP masih naik, *train loss* masih turun,
dan *val loss* juga masih turun pada epoch terakhir. Pemilihan model 100
*epoch* dilakukan sepenuhnya di atas *split* valid, dan *split* test baru
dievaluasi sekali setelah model dikunci.

## 4. Angka yang Dilaporkan

| Metrik | *Split* valid | *Split* test | Sumber |
|---|---:|---:|---|
| mAP@50 | **70,71%** | **70,65%** | `official_metrics_{split}.json` |
| F1-Score macro | **72,33%** | **71,45%** | `official_metrics_{split}.json` |

Selisih valid terhadap test sebesar 0,06 poin pada mAP dan 0,88 poin pada F1.
*Split* test tidak pernah dipakai untuk penyetelan apa pun, termasuk memilih
di antara kandidat, dan baru dievaluasi sekali setelah model dikunci. Namun
satu evaluasi *held-out* tidak cukup untuk membuktikan ketiadaan
*overfitting*.

Konfigurasi yang menghasilkan angka tersebut:

- bobot `runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt`;
- resolusi inferensi 640, sama dengan resolusi pelatihan;
- ambang NMS IoU 0,5;
- IoU pencocokan 0,5;
- *confidence* titik operasi ditentukan otomatis sebagai titik yang
  memaksimalkan rata-rata F1 antar kelas.

Reproduksi:

```bash
python scripts/evaluate.py --weights runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt --split valid --nms-iou 0.5
python scripts/compute_official_metrics.py --split valid
```

## 5. Catatan mengenai Definisi F1

Regulasi menyebut F1 sebagai metrik penilaian tetapi tidak merinci metode
*averaging* maupun *confidence threshold* yang dipakai evaluator.

Karena itu angka F1 pada project ini dinyatakan sebagai **F1 macro hasil
implementasi evaluasi lokal**, bukan sebagai angka resmi panitia. Bila
panitia menerbitkan definisi resmi yang berbeda, definisi panitia yang
menjadi sumber kebenaran dan angka pada project ini harus dihitung ulang
mengikuti definisi tersebut.

Metrik lokal dengan rata-rata *micro* tetap dipertahankan sebagai metrik
diagnostik sekunder, dan nilainya sistematis lebih rendah pada dataset yang
timpang seperti ini. Kedua metrik mengukur hal yang berbeda dan tidak
sebanding secara langsung.

## 6. Sumber Kebenaran Tunggal

Seluruh angka final berasal dari satu jalur:

```
scripts/evaluate.py
        menghasilkan
artifacts/reports/evaluation_{split}.json
        dibaca oleh
scripts/compute_official_metrics.py
        menghasilkan
artifacts/reports/official_metrics_{split}.json
        dibaca oleh
notebook, README, dan model card
```

`compute_official_metrics.py` tidak melakukan perhitungan ulang. Skrip
tersebut hanya membaca artefak evaluasi dan menyusunnya ulang dalam format
pelaporan. Dengan demikian tidak mungkin terjadi dua nilai berbeda untuk hal
yang sama akibat dua jalur perhitungan yang terpisah.

## 7. Kestabilan Pengukuran pada Perangkat Ini

Satu hal kami temukan saat menyiapkan submission dan perlu kami sampaikan
terbuka, karena menyangkut apa yang akan dialami juri ketika menjalankan ulang
pipeline ini.

Evaluasi terhadap *checkpoint* yang sama persis, dengan konfigurasi yang sama
persis (resolusi 640, NMS IoU 0,5, IoU pencocokan 0,5), tidak selalu
menghasilkan mAP@0.5 yang identik pada perangkat ini:

| Waktu eksekusi | mAP@0.5 | mAP@0.5:0.95 | *F1* macro | Jumlah deteksi terkumpul |
|---|---:|---:|---:|---:|
| 24 Sep 07:39 | 0,6678 | 0,4141 | 0,6826 | 77.454 |
| 24 Sep 10:38 | 0,6759 | 0,4304 | 0,6755 | 68.639 |
| 24 Sep 23:54 | 0,6678 | 0,4141 | 0,6826 | 54.529 |

Selisih terbesarnya 0,0081 pada mAP@0.5, atau sekitar 1,2 persen secara
relatif. Nilai 0,6678 muncul pada dua eksekusi terpisah, sedangkan 0,6759
muncul sekali. Karena itu **kami melaporkan 0,6678**, yaitu nilai yang
tereproduksi berulang, bukan nilai tertinggi yang pernah kami lihat.

Perlu dicatat pula bahwa jumlah deteksi yang terkumpul berbeda pada ketiga
eksekusi meskipun metrik native-nya bisa identik. Hal ini konsisten dengan
nondeterminisme *backend* MPS yang sudah kami dokumentasikan: tahap yang tidak
deterministik adalah inferensinya, bukan pencocokannya.

Implikasinya bagi audit juri, dan kami nyatakan ini sebagai pengakuan dan bukan
pembelaan:

1. Angka yang juri peroleh mungkin tidak identik dengan angka kami, dan selisih
   pada orde 0,008 pada mAP@0.5 masih dalam rentang yang kami amati sendiri.
2. Kami tidak mengklaim reproduksi bit per bit, dan hal ini sudah dinyatakan
   sejak awal pada `reproducibility_checklist.md`.
3. Dokumen audit kami sebelumnya menyatakan bahwa mAP@0.5 tercatat identik
   pada beberapa kali pengulangan. Pernyataan itu benar untuk model 50 *epoch*
   pada pengujian yang kami lakukan saat itu, tetapi tidak berlaku umum, dan
   kami memperbaikinya di sini alih-alih membiarkannya berdiri.

Analisis yang dihitung ulang dari prediksi tersimpan, misalnya sensitivitas
*threshold*, tetap deterministik sepenuhnya, karena tidak menjalankan inferensi
ulang.

### 7.1 Instabilitas pada analisis kesalahan jauh lebih besar

Ketidakstabilan yang sama, tetapi dengan amplitudo jauh lebih besar, kami amati
pada analisis kesalahan. Dua eksekusi `scripts/run_error_analysis.py` terhadap
*checkpoint* yang sama, split yang sama, dan *confidence threshold* yang sama
(0,1) menghasilkan:

| Eksekusi | *True positive* | Salah kelas | *FP* latar | *False negative* |
|---|---:|---:|---:|---:|
| 24 Sep 07:24 | 1.545 | 67 | 2.547 | 3.276 |
| 26 Sep 12:05 | 945 | 24 | 1.542 | 3.919 |

Selisihnya besar, yaitu 39 persen pada jumlah *true positive*. Penyebabnya
adalah tahap pengumpulan prediksi yang memakai inferensi MPS, bukan tahap
pencocokannya yang sepenuhnya deterministik.

Angka yang kami pakai pada laporan, README, dan notebook adalah eksekusi 24 Sep
07:24, karena itulah eksekusi yang keluarannya benar-benar tertanam di dalam
notebook sebagai bukti. Eksekusi 26 Sep kami simpan pada
`artifacts/archive/error_analysis_reruns/rerun_26sep.json` supaya selisihnya
dapat diperiksa sendiri, bukan kami sembunyikan.

Kesimpulan yang kami tarik dari analisis kesalahan tidak berubah di antara
kedua eksekusi: *false negative* tetap mendominasi, salah kelas tetap porsi
terkecil, objek yang terlewat tetap lebih kecil daripada rata-rata, dan adegan
padat tetap memiliki rasio *false negative* lebih tinggi. Yang tidak stabil
adalah angka absolutnya, bukan arah temuannya. Karena itu kami memperlakukan
analisis kesalahan sebagai bukti kualitatif mengenai jenis kegagalan model,
bukan sebagai pengukuran presisi.

### 7.2 Model final: tidak ada pergeseran yang teramati

Untuk model final YOLOv8s-P2 kami mengulang pengukuran yang sama dengan sengaja,
justru karena riwayat di atas. Hasilnya identik sampai digit terakhir:

| Eksekusi | Perangkat | mAP@0.5 | *F1* macro | Deteksi terkumpul | *TP* analisis kesalahan |
|---|---|---:|---:|---:|---:|
| 24 Okt 09:22 | CPU | 0,7071 | 0,7233 | tidak dicatat | tidak dijalankan |
| 24 Okt 10:47 | MPS | 0,7071 | 0,7233 | 89.827 | 3.026 |
| 24 Okt 17:10 | MPS | 0,7071 | 0,7233 | 89.827 | 3.026 |

Di antara kedua periode, pengumpulan prediksi pada `evaluate.py` dan
`run_error_analysis.py` kami ubah dari potongan 500 citra menjadi potongan 16
citra, karena potongan 500 kehabisan memori MPS untuk model yang lebih besar.
Kami belum memastikan apakah perubahan itu juga yang menghilangkan
ketidakstabilan pada model lama, sehingga tidak kami klaim sebagai penyebabnya.
