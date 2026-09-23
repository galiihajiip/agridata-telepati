# Matriks Percobaan Baseline: Hasil dan Rekomendasi

Perlu dicatat soal skalanya. Matriks ini memakai sebagian kecil data latih dengan sedikit *epoch* sebagai tahap penyaringan yang cepat, bukan rezim pelatihan final. Nilai mAP absolutnya memang rendah, dan pada tahap ini hanya perbedaan *relatif* antar varian terhadap baseline yang bermakna.

## Hasil

| Percobaan | Faktor yang diubah | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall | Durasi (detik) |
|---|---|---:|---:|---:|---:|---:|
| E02 | baseline | 0.0018 | 0.0005 | 0.1840 | 0.0073 | 145.7 |
| E03 | image_size | 0.0041 | 0.0017 | 0.3724 | 0.0052 | 302.2 |
| E04 | batch_size | 0.0005 | 0.0001 | 0.0004 | 0.0828 | 119.4 |
| E05 | learning_rate | 0.0002 | 0.0001 | 0.1820 | 0.0814 | 130.7 |
| E06 | optimizer | 0.0003 | 0.0001 | 0.0961 | 0.0003 | 127.8 |
| E07 | augmentation_strength | 0.0007 | 0.0002 | 0.2759 | 0.0061 | 133.8 |
| E08 | training_duration | 0.0134 | 0.0034 | 0.2921 | 0.0406 | 207.8 |

## Efek tiap faktor, relatif terhadap baseline

- **image_size**: mAP@0.5 naik sebesar +0.0023 terhadap baseline (durasi 302 detik berbanding 146 detik pada baseline).
- **batch_size**: mAP@0.5 turun sebesar -0.0013 terhadap baseline (durasi 119 detik berbanding 146 detik pada baseline).
- **learning_rate**: mAP@0.5 turun sebesar -0.0016 terhadap baseline (durasi 131 detik berbanding 146 detik pada baseline).
- **optimizer**: mAP@0.5 turun sebesar -0.0015 terhadap baseline (durasi 128 detik berbanding 146 detik pada baseline).
- **augmentation_strength**: mAP@0.5 turun sebesar -0.0011 terhadap baseline (durasi 134 detik berbanding 146 detik pada baseline).
- **training_duration**: mAP@0.5 naik sebesar +0.0117 terhadap baseline (durasi 208 detik berbanding 146 detik pada baseline).

## Rekomendasi

mAP@0.5 tertinggi pada tahap penyaringan ini: **E08** (training_duration, mAP@0.5=0.0134).

Hasil ini TIDAK dinyatakan sebagai konfigurasi final. Tidak ada konfigurasi yang disebut terbaik sebelum diukur pada skala penuh. Temuan di sini menjadi masukan, bukan pengganti, bagi ablasi augmentasi, ablasi ketidakseimbangan kelas, dan analisis kesalahan, sebelum konfigurasi final dibekukan.
