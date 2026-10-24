# Analisis Kesalahan Model

Bobot: `runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt` | Split: `valid` | Ambang confidence: 0.1

## Rincian jumlah

- True positive: 3026
- Salah kelas (lokasi benar, label salah): 107
- False positive terhadap latar (mendeteksi objek yang tidak ada): 3560
- False negative (objek terlewat sepenuhnya): 1755

## Pasangan kelas yang paling sering tertukar

| Kelas sebenarnya | Diprediksi sebagai | Jumlah |
|---|---|---:|
| Brown spot | Blast | 22 |
| Blast | Brown spot | 14 |
| Bacterial panicle blight | Blast | 12 |
| Blast | Bacterial panicle blight | 9 |
| Brown spot | Leaf scald | 7 |
| Leaf scald | Tungro | 6 |
| Leaf roller | Healthy | 4 |
| Tungro | Leaf scald | 4 |
| Bacterial leaf blight | Blast | 3 |
| Bacterial leaf blight | Sheath blight | 3 |

## Precision dan recall per kelas menurut pencocokan analisis ini

| Kelas | Precision | Recall | TP | FP | FN |
|---|---:|---:|---:|---:|---:|
| Bacterial leaf blight | 0.4037 | 0.7040 | 88 | 130 | 37 |
| Bacterial panicle blight | 0.5926 | 0.7111 | 32 | 22 | 13 |
| Blast | 0.4453 | 0.6019 | 570 | 710 | 377 |
| Brown spot | 0.3463 | 0.4209 | 615 | 1161 | 846 |
| False smut | 0.7850 | 0.9767 | 84 | 23 | 2 |
| Healthy | 0.7803 | 0.8962 | 380 | 107 | 44 |
| Leaf roller | 0.7043 | 0.9310 | 81 | 34 | 6 |
| Leaf scald | 0.3511 | 0.6256 | 244 | 451 | 146 |
| Narrow brown | 0.6271 | 0.9867 | 74 | 44 | 1 |
| Sheath blight | 0.4768 | 0.7172 | 350 | 384 | 138 |
| Tungro | 0.4581 | 0.6684 | 508 | 601 | 252 |

## Confidence: true positive dibanding false positive

- Confidence true positive: {'mean': 0.5888195560194961, 'median': 0.6628991961479187}
- Confidence false positive: {'mean': 0.2516189454718185, 'median': 0.1816408485174179}

## Analisis objek kecil yang terlewat

- Median luas bbox ground truth keseluruhan: 7051.6 px²
- Median luas bbox yang terlewat: 719.2 px²
- Objek terlewat cenderung lebih kecil dari rata-rata: True

## Adegan padat dibanding adegan jarang

- Rasio false negative pada adegan padat, lebih dari 1 instance per citra: 0.4859
- Rasio false negative pada adegan jarang: 0.0389

## Kandidat latar belakang sulit, dengan false positive latar terbanyak

['05-leaf-Blast_jpg.rf.194eb375c4dbe4607bc3a86bd3058862.jpg', 'rbf_25_jpg.rf.6f17e640958938b64dad145d11ed3e1c.jpg', '05-Brown-spot_jpg.rf.d0415c0a315bf10c767bde9d3a55aec3.jpg', 'brownspot_orig_098_jpg.rf.649a14071152ce62d7e9854c3963113f.jpg', 'BROWNSPOT7_011_jpg.rf.1c81e18129ce2d7bc814b731ec1473d8.jpg']

## Contoh visual

- False positive: ['artifacts/figures/error_analysis/bg_fp_id4_IMG-20240927-WA0204_jpg.rf.08d9cd91a261a0fac5a9eddf03f8313b.jpg', 'artifacts/figures/error_analysis/bg_fp_id7_20240915_150129_jpg.rf.045091b7ad6b9cc08f3265fce3a6ad3a.jpg', 'artifacts/figures/error_analysis/bg_fp_id8_IMG-20241014-WA0430_jpg.rf.09ed00bf0dd83cf15e641fc083042c42.jpg', 'artifacts/figures/error_analysis/bg_fp_id10_IMG-20241012-WA0120_jpg.rf.072a372419edbd8c675d9168748dc681.jpg']
- False negative: ['artifacts/figures/error_analysis/fn_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/fn_id25_IMG_20241020_083809_983_jpg.rf.1063f58081fd2d58e91a64f9cda425cc.jpg', 'artifacts/figures/error_analysis/fn_id32_20240915_103047_jpg.rf.115ee268b1b72aca1a9b64ffc32c0447.jpg', 'artifacts/figures/error_analysis/fn_id36_IMG-20240927-WA0178_jpg.rf.175403c448a9cadd98fb1ed023a43ffa.jpg']

## Peringatan sebelum menarik kesimpulan

Checkpoint ini memiliki minimal satu true positive pada seluruh 11 dari 11 kelas. Pola kebingungan di atas mencerminkan perilaku model yang sebenarnya, bukan sekadar kelas yang belum dipelajari model.

## Pengamatan

Temuan berikut berasal dari kesalahan aktual checkpoint ini, bukan template umum:

1. **Objek yang terlewat cenderung lebih kecil daripada sebaran luas ground truth secara keseluruhan**, yaitu median 719.2 berbanding 7051.6 px persegi. Temuan ini konsisten dengan kesulitan deteksi objek kecil yang dikenal luas dalam literatur.
2. **Adegan padat memiliki rasio false negative lebih tinggi**, yaitu 0.4859 berbanding 0.0389 pada adegan jarang. Lesi kecil yang berdesakan tetap menjadi kasus tersulit.
3. Kedua temuan dicatat sebagai keterbatasan model, bukan usulan eksperimen lanjutan. Lihat bagian keterbatasan pada README untuk pengungkapan lengkapnya.

## PENTING: tidak ada perubahan yang diterapkan otomatis

Skrip ini hanya menganalisis dan melaporkan. Setiap perubahan data maupun model yang disarankan oleh temuan di atas, misalnya pelabelan ulang, pengecualian citra, atau penyesuaian augmentasi suatu kelas, harus menjadi keputusan terpisah yang didokumentasikan secara eksplisit, tidak pernah diterapkan otomatis dari analisis ini.
