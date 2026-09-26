# Analisis Kesalahan Model

Bobot: `runs/detect/final/model_100epoch/weights/best.pt` | Split: `valid` | Ambang confidence: 0.1

## Rincian jumlah

- True positive: 945
- Salah kelas (lokasi benar, label salah): 24
- False positive terhadap latar (mendeteksi objek yang tidak ada): 1542
- False negative (objek terlewat sepenuhnya): 3919

## Pasangan kelas yang paling sering tertukar

| Kelas sebenarnya | Diprediksi sebagai | Jumlah |
|---|---|---:|
| Brown spot | Blast | 9 |
| Blast | Brown spot | 3 |
| Leaf scald | Tungro | 3 |
| Blast | Sheath blight | 2 |
| Tungro | Leaf scald | 2 |
| Bacterial leaf blight | Healthy | 1 |
| Bacterial leaf blight | Tungro | 1 |
| Brown spot | Leaf scald | 1 |
| Healthy | Brown spot | 1 |
| Sheath blight | Leaf roller | 1 |

## Precision dan recall per kelas menurut pencocokan analisis ini

| Kelas | Precision | Recall | TP | FP | FN |
|---|---:|---:|---:|---:|---:|
| Bacterial leaf blight | 0.2796 | 0.2080 | 26 | 67 | 99 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0 | 1 | 45 |
| Blast | 0.3750 | 0.2091 | 198 | 330 | 749 |
| Brown spot | 0.3328 | 0.1451 | 212 | 425 | 1249 |
| False smut | 0.3333 | 0.0116 | 1 | 2 | 85 |
| Healthy | 0.7317 | 0.2123 | 90 | 33 | 334 |
| Leaf roller | 0.0000 | 0.0000 | 0 | 2 | 87 |
| Leaf scald | 0.3529 | 0.2000 | 78 | 143 | 312 |
| Narrow brown | 0.5161 | 0.2133 | 16 | 15 | 59 |
| Sheath blight | 0.3127 | 0.2275 | 111 | 244 | 377 |
| Tungro | 0.4120 | 0.2803 | 213 | 304 | 547 |

## Confidence: true positive dibanding false positive

- Confidence true positive: {'mean': 0.5179209865826778, 'median': 0.5306923389434814}
- Confidence false positive: {'mean': 0.21966816711871104, 'median': 0.1708322912454605}

## Analisis objek kecil yang terlewat

- Median luas bbox ground truth keseluruhan: 7051.6 px²
- Median luas bbox yang terlewat: 5328.1 px²
- Objek terlewat cenderung lebih kecil dari rata-rata: True

## Adegan padat dibanding adegan jarang

- Rasio false negative pada adegan padat, lebih dari 1 instance per citra: 0.8101
- Rasio false negative pada adegan jarang: 0.7808

## Kandidat latar belakang sulit, dengan false positive latar terbanyak

['BROWNSPOT6_194_jpg.rf.b2ef46a9b340f833592d72bea1058e0f.jpg', 'rb_wb_17_jpg.rf.719eb72094811f2f84d8ea74a7343157.jpg', 'BROWNSPOT2_098_jpg.rf.ae6f388c9b5867ff0292af5e89d12935.jpg', 'BROWNSPOT6_011_jpg.rf.b29dd13fd4d5d61fd59a2a6da1ec5249.jpg', 'brownspot_orig_096_jpg.rf.bd95a8ea989b7cb812af80662cdaa796.jpg']

## Contoh visual

- False positive: ['artifacts/figures/error_analysis/bg_fp_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/bg_fp_id501_SheathBlight_245_jpg.rf.684c2a577e91cc4995a38999932fb8b8.jpg', 'artifacts/figures/error_analysis/bg_fp_id503_BLAST9_150_JPG_jpg.rf.6b018c5dcf5292737747023ed7627597.jpg', 'artifacts/figures/error_analysis/bg_fp_id504_BLAST9_032_jpg.rf.6b0232049f6de25065d02a35d5e59ee7.jpg']
- False negative: ['artifacts/figures/error_analysis/fn_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/fn_id1_IMG-20241014-WA0258_jpg.rf.010c555e9aec70ddf42e72f285068311.jpg', 'artifacts/figures/error_analysis/fn_id2_IMG-20241012-WA0099_jpg.rf.052715be2fdca8f048e88ae49189c283.jpg', 'artifacts/figures/error_analysis/fn_id3_IMG-20240927-WA0215_jpg.rf.02427045292acba0cf19b92c6a42caf2.jpg']

## Peringatan sebelum menarik kesimpulan

Checkpoint ini tidak memiliki true positive pada 2 dari 11 kelas (Bacterial panicle blight, Leaf roller), sehingga kelas tersebut belum dipelajari sama sekali. Pola kebingungan yang melibatkan kelas itu lebih mencerminkan keadaan belum dipelajari, bukan kebingungan semantik yang bermakna. Hanya kelas dengan jumlah true positive memadai yang dapat ditafsirkan pada tahap ini.

## Pengamatan

Temuan berikut berasal dari kesalahan aktual checkpoint ini, bukan template umum:

1. **Objek yang terlewat cenderung lebih kecil daripada sebaran luas ground truth secara keseluruhan**, yaitu median 5328.1 berbanding 7051.6 px persegi. Temuan ini konsisten dengan kesulitan deteksi objek kecil yang dikenal luas dalam literatur.
2. **Adegan padat memiliki rasio false negative lebih tinggi**, yaitu 0.8101 berbanding 0.7808 pada adegan jarang. Lesi kecil yang berdesakan tetap menjadi kasus tersulit.
3. Kedua temuan dicatat sebagai keterbatasan model, bukan usulan eksperimen lanjutan. Lihat bagian keterbatasan pada README untuk pengungkapan lengkapnya.

## PENTING: tidak ada perubahan yang diterapkan otomatis

Skrip ini hanya menganalisis dan melaporkan. Setiap perubahan data maupun model yang disarankan oleh temuan di atas, misalnya pelabelan ulang, pengecualian citra, atau penyesuaian augmentasi suatu kelas, harus menjadi keputusan terpisah yang didokumentasikan secara eksplisit, tidak pernah diterapkan otomatis dari analisis ini.
