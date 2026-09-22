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
| **0,6401** | **FINAL** | 50 *epoch*, resolusi 640 | **NMS 0,5** | `artifacts/reports/evaluation_valid.json` |
| 0,6145 | Historis | 50 *epoch*, resolusi 640 | NMS 0,7, *split* test | `artifacts/archive/50epoch_640_run/evaluation_test.json` |
| 0,4200 | Eksperimen | 50 *epoch*, latih 640 | inferensi pada 960 | `artifacts/reports/inference_tuning_imgsz.json` |
| 0,1164 | Eksperimen | 50 *epoch*, latih 640 | inferensi pada 1280 | `artifacts/reports/inference_tuning_imgsz.json` |

## 2. Nilai F1

| Nilai | Status | Metode | Konfigurasi | Keterangan |
|---|---|---|---|---|
| 0,3326 | Historis, metodologi lama | *micro*, *threshold* tetap 0,25 | NMS 0,7 | Bukan konvensi pelaporan yang lazim, lihat `metrics_methodology.md` |
| 0,3479 | Diagnostik | *micro*, *threshold* 0,15 | NMS 0,7 | Puncak sapuan *threshold* pada metrik lokal |
| 0,6181 | Historis | *macro*, titik operasi terbaik | NMS 0,7 | Sebelum ambang NMS diturunkan |
| **0,6383** | **FINAL** | ***macro*, titik operasi terbaik** | **NMS 0,5** | `artifacts/reports/evaluation_valid.json` |
| 0,6321 | Tidak dipakai | *harmonic mean* dari *mean P* dan *mean R* | NMS 0,7 | Menggabungkan titik operasi berbeda antar kelas, lebih sulit direproduksi |

## 3. Mengapa Terdapat Banyak Nilai

Tiga perubahan besar terjadi selama project berjalan, dan masing-masing
menghasilkan satu generasi angka:

1. **Perpanjangan pelatihan** dari 20 *epoch* menjadi 50 *epoch*.
   Menaikkan mAP@0.5 dari 0,5620 menjadi 0,6277.
2. **Koreksi metodologi F1** dari rata-rata *micro* menjadi *macro* pada
   titik operasi terbaik. Mengubah F1 dari 0,3326 menjadi 0,6181.
   Tidak mengubah mAP sama sekali.
3. **Penurunan ambang NMS** dari 0,7 menjadi 0,5. Menaikkan mAP@0.5 dari
   0,6277 menjadi 0,6401 dan F1 dari 0,6181 menjadi 0,6383, tanpa mengubah
   bobot model.

Perubahan pertama mengubah model. Perubahan kedua mengubah cara mengukur.
Perubahan ketiga mengubah konfigurasi inferensi. Ketiganya terdokumentasi dan
tidak ada yang dilakukan setelah melihat hasil pada *split* test.

## 4. Angka yang Dilaporkan

| Metrik | Nilai | Sumber |
|---|---:|---|
| mAP@50 | **64,01%** | `artifacts/reports/official_metrics_valid.json` |
| F1-Score macro | **63,83%** | `artifacts/reports/official_metrics_valid.json` |

Konfigurasi yang menghasilkan angka tersebut:

- bobot `runs/detect/final/final_model/weights/best.pt`;
- resolusi inferensi 640, sama dengan resolusi pelatihan;
- ambang NMS IoU 0,5;
- IoU pencocokan 0,5;
- *confidence* titik operasi ditentukan otomatis sebagai titik yang
  memaksimalkan rata-rata F1 antar kelas.

Reproduksi:

```bash
python scripts/evaluate.py --weights runs/detect/final/final_model/weights/best.pt --split valid
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
