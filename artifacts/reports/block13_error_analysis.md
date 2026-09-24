# Analisis Kesalahan Model

Bobot: `runs/detect/final/model_100epoch/weights/best.pt` | Split: `valid` | Ambang confidence: 0.1

## Rincian jumlah

- True positive: 1545
- Salah kelas (lokasi benar, label salah): 67
- False positive terhadap latar (mendeteksi objek yang tidak ada): 2547
- False negative (objek terlewat sepenuhnya): 3276

## Pasangan kelas yang paling sering tertukar

| Kelas sebenarnya | Diprediksi sebagai | Jumlah |
|---|---|---:|
| Blast | Brown spot | 23 |
| Brown spot | Blast | 13 |
| Leaf scald | Tungro | 6 |
| Healthy | Brown spot | 4 |
| Blast | Bacterial leaf blight | 3 |
| Tungro | Leaf scald | 3 |
| Bacterial leaf blight | Healthy | 2 |
| Bacterial leaf blight | Tungro | 2 |
| Blast | Sheath blight | 2 |
| Bacterial leaf blight | Blast | 1 |

## Precision dan recall per kelas menurut pencocokan analisis ini

| Kelas | Precision | Recall | TP | FP | FN |
|---|---:|---:|---:|---:|---:|
| Bacterial leaf blight | 0.3109 | 0.6640 | 83 | 184 | 42 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0 | 1 | 45 |
| Blast | 0.3854 | 0.3073 | 291 | 464 | 656 |
| Brown spot | 0.3015 | 0.2416 | 353 | 818 | 1108 |
| False smut | 0.3333 | 0.0116 | 1 | 2 | 85 |
| Healthy | 0.7703 | 0.4033 | 171 | 51 | 253 |
| Leaf roller | 0.0000 | 0.0000 | 0 | 5 | 87 |
| Leaf scald | 0.3455 | 0.3641 | 142 | 269 | 248 |
| Narrow brown | 0.5208 | 1.0000 | 75 | 69 | 0 |
| Sheath blight | 0.3174 | 0.3258 | 159 | 342 | 329 |
| Tungro | 0.3976 | 0.3553 | 270 | 409 | 490 |

## Confidence: true positive dibanding false positive

- Confidence true positive: {'mean': 0.5104493427141584, 'median': 0.5142697691917419}
- Confidence false positive: {'mean': 0.2212644206857353, 'median': 0.1725218966603279}

## Analisis objek kecil yang terlewat

- Median luas bbox ground truth keseluruhan: 7051.6 px²
- Median luas bbox yang terlewat: 3343.2 px²
- Objek terlewat cenderung lebih kecil dari rata-rata: True

## Adegan padat dibanding adegan jarang

- Rasio false negative pada adegan padat, lebih dari 1 instance per citra: 0.7269
- Rasio false negative pada adegan jarang: 0.527

## Kandidat latar belakang sulit, dengan false positive latar terbanyak

['05-leaf-Blast_jpg.rf.194eb375c4dbe4607bc3a86bd3058862.jpg', 'brown_spot-22-_jpg.rf.bf0db732c7e78d74d928b106b56436bc.jpg', 'BROWNSPOT6_194_jpg.rf.b2ef46a9b340f833592d72bea1058e0f.jpg', 'rb_wb_17_jpg.rf.719eb72094811f2f84d8ea74a7343157.jpg', 'BROWNSPOT2_098_jpg.rf.ae6f388c9b5867ff0292af5e89d12935.jpg']

## Contoh visual

- False positive: ['artifacts/figures/error_analysis/bg_fp_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/bg_fp_id501_SheathBlight_245_jpg.rf.684c2a577e91cc4995a38999932fb8b8.jpg', 'artifacts/figures/error_analysis/bg_fp_id503_BLAST9_150_JPG_jpg.rf.6b018c5dcf5292737747023ed7627597.jpg', 'artifacts/figures/error_analysis/bg_fp_id504_BLAST9_032_jpg.rf.6b0232049f6de25065d02a35d5e59ee7.jpg']
- False negative: ['artifacts/figures/error_analysis/fn_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/fn_id1_IMG-20241014-WA0258_jpg.rf.010c555e9aec70ddf42e72f285068311.jpg', 'artifacts/figures/error_analysis/fn_id2_IMG-20241012-WA0099_jpg.rf.052715be2fdca8f048e88ae49189c283.jpg', 'artifacts/figures/error_analysis/fn_id3_IMG-20240927-WA0215_jpg.rf.02427045292acba0cf19b92c6a42caf2.jpg']

## Peringatan sebelum menarik kesimpulan

Checkpoint ini tidak memiliki true positive pada 2 dari 11 kelas (Bacterial panicle blight, Leaf roller), sehingga kelas tersebut belum dipelajari sama sekali. Pola kebingungan yang melibatkan kelas itu lebih mencerminkan keadaan belum dipelajari, bukan kebingungan semantik yang bermakna. Hanya kelas dengan jumlah true positive memadai yang dapat ditafsirkan pada tahap ini.

## Pengamatan

Temuan berikut berasal dari kesalahan aktual checkpoint ini, bukan template umum:

1. **Objek yang terlewat cenderung lebih kecil daripada sebaran luas ground truth secara keseluruhan**, yaitu median 3343.2 berbanding 7051.6 px persegi. Temuan ini konsisten dengan kesulitan deteksi objek kecil yang dikenal luas dalam literatur.
2. **Adegan padat memiliki rasio false negative lebih tinggi**, yaitu 0.7269 berbanding 0.527 pada adegan jarang. Lesi kecil yang berdesakan tetap menjadi kasus tersulit.
3. Kedua temuan dicatat sebagai keterbatasan model, bukan usulan eksperimen lanjutan. Lihat bagian keterbatasan pada README untuk pengungkapan lengkapnya.

## PENTING: tidak ada perubahan yang diterapkan otomatis

Skrip ini hanya menganalisis dan melaporkan. Setiap perubahan data maupun model yang disarankan oleh temuan di atas, misalnya pelabelan ulang, pengecualian citra, atau penyesuaian augmentasi suatu kelas, harus menjadi keputusan terpisah yang didokumentasikan secara eksplisit, tidak pernah diterapkan otomatis dari analisis ini.
