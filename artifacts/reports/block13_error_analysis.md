# Analisis Kesalahan Model

Bobot: `runs/detect/final/final_model/weights/best.pt` | Split: `valid` | Ambang confidence: 0.1

## Rincian jumlah

- True positive: 1381
- Salah kelas (lokasi benar, label salah): 83
- False positive terhadap latar (mendeteksi objek yang tidak ada): 1881
- False negative (objek terlewat sepenuhnya): 3424

## Pasangan kelas yang paling sering tertukar

| Kelas sebenarnya | Diprediksi sebagai | Jumlah |
|---|---|---:|
| Blast | Bacterial panicle blight | 17 |
| Bacterial panicle blight | Blast | 12 |
| Brown spot | Blast | 11 |
| Leaf roller | Healthy | 5 |
| Blast | Brown spot | 4 |
| Leaf scald | Tungro | 4 |
| Healthy | Blast | 3 |
| Leaf scald | Sheath blight | 3 |
| Bacterial leaf blight | Healthy | 2 |
| Blast | Healthy | 2 |

## Precision dan recall per kelas menurut pencocokan analisis ini

| Kelas | Precision | Recall | TP | FP | FN |
|---|---:|---:|---:|---:|---:|
| Bacterial leaf blight | 0.3043 | 0.1680 | 21 | 48 | 104 |
| Bacterial panicle blight | 0.3976 | 0.7333 | 33 | 50 | 12 |
| Blast | 0.4431 | 0.2344 | 222 | 279 | 725 |
| Brown spot | 0.2918 | 0.1697 | 248 | 602 | 1213 |
| False smut | 0.7364 | 0.9419 | 81 | 29 | 5 |
| Healthy | 0.7374 | 0.5165 | 219 | 78 | 205 |
| Leaf roller | 0.5540 | 0.8851 | 77 | 62 | 10 |
| Leaf scald | 0.3381 | 0.2436 | 95 | 186 | 295 |
| Narrow brown | 0.6154 | 0.2133 | 16 | 10 | 59 |
| Sheath blight | 0.3142 | 0.2807 | 137 | 299 | 351 |
| Tungro | 0.4195 | 0.3053 | 232 | 321 | 528 |

## Confidence: true positive dibanding false positive

- Confidence true positive: {'mean': 0.5284594952207731, 'median': 0.5515046119689941}
- Confidence false positive: {'mean': 0.2133797605174865, 'median': 0.16259922087192535}

## Analisis objek kecil yang terlewat

- Median luas bbox ground truth keseluruhan: 7051.6 px²
- Median luas bbox yang terlewat: 3376.0 px²
- Objek terlewat cenderung lebih kecil dari rata-rata: True

## Adegan padat dibanding adegan jarang

- Rasio false negative pada adegan padat, lebih dari 1 instance per citra: 0.7981
- Rasio false negative pada adegan jarang: 0.4542

## Kandidat latar belakang sulit, dengan false positive latar terbanyak

['BROWNSPOT5_095_jpg.rf.fab7517d8aad41ee4be007303ab845b7.jpg', 'brownspot_orig_098_jpg.rf.649a14071152ce62d7e9854c3963113f.jpg', 'brownspot_orig_099_jpg.rf.20a588798794f83ef7c61d6dd58f2dcd.jpg', 'sb_wb_78_jpg.rf.d935e1b711a8cb6b55cc8468eebbfbcc.jpg', 'BROWNSPOT3_198_jpg.rf.e8f570a3f27fd60a33072cae3fe3a677.jpg']

## Contoh visual

- False positive: ['artifacts/figures/error_analysis/bg_fp_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/bg_fp_id2_IMG-20241012-WA0099_jpg.rf.052715be2fdca8f048e88ae49189c283.jpg', 'artifacts/figures/error_analysis/bg_fp_id7_20240915_150129_jpg.rf.045091b7ad6b9cc08f3265fce3a6ad3a.jpg', 'artifacts/figures/error_analysis/bg_fp_id11_IMG-20240927-WA0076_jpg.rf.05ae64322751319f09f5888d2c1fe959.jpg']
- False negative: ['artifacts/figures/error_analysis/fn_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/fn_id25_IMG_20241020_083809_983_jpg.rf.1063f58081fd2d58e91a64f9cda425cc.jpg', 'artifacts/figures/error_analysis/fn_id32_20240915_103047_jpg.rf.115ee268b1b72aca1a9b64ffc32c0447.jpg', 'artifacts/figures/error_analysis/fn_id36_IMG-20240927-WA0178_jpg.rf.175403c448a9cadd98fb1ed023a43ffa.jpg']

## Peringatan sebelum menarik kesimpulan

Checkpoint ini memiliki minimal satu true positive pada seluruh 11 dari 11 kelas. Pola kebingungan di atas mencerminkan perilaku model yang sebenarnya, bukan sekadar kelas yang belum dipelajari model.

## Pengamatan

Temuan berikut berasal dari kesalahan aktual checkpoint ini, bukan template umum:

1. **Objek yang terlewat cenderung lebih kecil daripada sebaran luas ground truth secara keseluruhan**, yaitu median 3376.0 berbanding 7051.6 px persegi. Temuan ini konsisten dengan kesulitan deteksi objek kecil yang dikenal luas dalam literatur.
2. **Adegan padat memiliki rasio false negative lebih tinggi**, yaitu 0.7981 berbanding 0.4542 pada adegan jarang. Lesi kecil yang berdesakan tetap menjadi kasus tersulit.
3. Kedua temuan dicatat sebagai keterbatasan model, bukan usulan eksperimen lanjutan. Lihat bagian keterbatasan pada README untuk pengungkapan lengkapnya.

## PENTING: tidak ada perubahan yang diterapkan otomatis

Skrip ini hanya menganalisis dan melaporkan. Setiap perubahan data maupun model yang disarankan oleh temuan di atas, misalnya pelabelan ulang, pengecualian citra, atau penyesuaian augmentasi suatu kelas, harus menjadi keputusan terpisah yang didokumentasikan secara eksplisit, tidak pernah diterapkan otomatis dari analisis ini.
