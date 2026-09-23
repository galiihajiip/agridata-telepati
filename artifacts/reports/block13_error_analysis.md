# Analisis Kesalahan Model

Weights: `runs/detect/final/final_model/weights/best.pt` | Split: `valid` | Confidence threshold: 0.1

## Rincian jumlah

- True positive: 4
- Salah kelas (lokasi benar, label salah): 1
- False positive terhadap latar (mendeteksi objek yang tidak ada): 4
- False negative (objek terlewat sepenuhnya): 4883

## Pasangan kelas yang paling sering tertukar

| Kelas sebenarnya | Diprediksi sebagai | Jumlah |
|---|---|---:|
| Blast | Brown spot | 1 |

## Precision dan recall per kelas menurut pencocokan analisis ini

| Kelas | Precision | Recall | TP | FP | FN |
|---|---:|---:|---:|---:|---:|
| Bacterial leaf blight | 0.0000 | 0.0000 | 0 | 0 | 125 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0 | 0 | 45 |
| Blast | 0.0000 | 0.0000 | 0 | 1 | 947 |
| Brown spot | 0.0000 | 0.0000 | 0 | 1 | 1461 |
| False smut | 0.5000 | 0.0116 | 1 | 1 | 85 |
| Healthy | 0.0000 | 0.0000 | 0 | 0 | 424 |
| Leaf roller | 0.0000 | 0.0000 | 0 | 0 | 87 |
| Leaf scald | 0.6000 | 0.0077 | 3 | 2 | 387 |
| Narrow brown | 0.0000 | 0.0000 | 0 | 0 | 75 |
| Sheath blight | 0.0000 | 0.0000 | 0 | 0 | 488 |
| Tungro | 0.0000 | 0.0000 | 0 | 0 | 760 |

## Confidence: true positive dibanding false positive

- Confidence true positive: {'mean': 0.4094606898725033, 'median': 0.3925985097885132}
- Confidence false positive: {'mean': 0.21785538792610168, 'median': 0.14223235845565796}

## Analisis objek kecil yang terlewat

- Median luas bbox ground truth keseluruhan: 7051.6 px²
- Median luas bbox yang terlewat: 7032.7 px²
- Objek terlewat cenderung lebih kecil dari rata-rata: True

## Adegan padat dibanding adegan jarang

- Crowded-scene (> 1 instances/image) false-negative rate: 0.9997
- Sparse-scene false-negative rate: 0.9971

## Kandidat latar belakang sulit, dengan false positive latar terbanyak

['leaf_scald-289-_jpg.rf.b1456c805a55fbc744aacdf567eb992b.jpg', 'IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'BLAST3_160_jpg.rf.ce82a246072316e4a902b17f5497cdf8.jpg']

## Contoh visual

- False positive: ['artifacts/figures/error_analysis/bg_fp_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/bg_fp_id1000_BLAST3_160_jpg.rf.ce82a246072316e4a902b17f5497cdf8.jpg', 'artifacts/figures/error_analysis/bg_fp_id2000_leaf_scald-289-_jpg.rf.b1456c805a55fbc744aacdf567eb992b.jpg']
- False negative: ['artifacts/figures/error_analysis/fn_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/fn_id1_IMG-20241014-WA0258_jpg.rf.010c555e9aec70ddf42e72f285068311.jpg', 'artifacts/figures/error_analysis/fn_id2_IMG-20241012-WA0099_jpg.rf.052715be2fdca8f048e88ae49189c283.jpg', 'artifacts/figures/error_analysis/fn_id3_IMG-20240927-WA0215_jpg.rf.02427045292acba0cf19b92c6a42caf2.jpg']

## Peringatan sebelum menarik kesimpulan

Checkpoint ini tidak memiliki true positive pada 9 dari 11 kelas (Bacterial leaf blight, Bacterial panicle blight, Blast, Brown spot, Healthy, Leaf roller, Narrow brown, Sheath blight, Tungro), sehingga kelas tersebut belum dipelajari sama sekali. Pola kebingungan yang melibatkan kelas itu lebih mencerminkan keadaan belum dipelajari, bukan kebingungan semantik yang bermakna. Hanya kelas dengan jumlah true positive memadai yang dapat ditafsirkan pada tahap ini.

## Pengamatan

Temuan berikut berasal dari kesalahan aktual checkpoint ini, bukan template umum:

1. **Objek yang terlewat cenderung lebih kecil daripada sebaran luas ground truth secara keseluruhan**, yaitu median 7032.7 berbanding 7051.6 px persegi. Temuan ini konsisten dengan kesulitan deteksi objek kecil yang dikenal luas dalam literatur.
2. **Adegan padat memiliki rasio false negative lebih tinggi**, yaitu 0.9997 berbanding 0.9971 pada adegan jarang. Lesi kecil yang berdesakan tetap menjadi kasus tersulit.
3. Kedua temuan dicatat sebagai keterbatasan model, bukan usulan eksperimen lanjutan. Lihat bagian keterbatasan pada README untuk pengungkapan lengkapnya.

## PENTING: tidak ada perubahan yang diterapkan otomatis

Skrip ini hanya menganalisis dan melaporkan. Setiap perubahan data maupun model yang disarankan oleh temuan di atas, misalnya pelabelan ulang, pengecualian citra, atau penyesuaian augmentasi suatu kelas, harus menjadi keputusan terpisah yang didokumentasikan secara eksplisit, tidak pernah diterapkan otomatis dari analisis ini.
