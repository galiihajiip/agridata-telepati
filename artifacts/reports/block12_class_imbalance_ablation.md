# Ablasi Mitigasi Ketidakseimbangan Kelas

Kedua eksekusi memakai JUMLAH citra latih yang identik (810), yaitu jumlah absolut melalui `fraction` bertipe bilangan bulat, yang sudah diverifikasi lewat kode sumber bahwa nilainya bukan persentase. Satu-satunya perbedaan adalah apakah citra kelas minoritas digandakan di dalam kumpulan penyampelan. Seed sama, hyperparameter sama, dan data validasi sama, dengan berkas yang identik byte per byte pada kedua kasus.

Kelas minoritas yang menjadi sasaran oversampling, yaitu kelas dengan jumlah instance kurang dari 20 persen kelas terbanyak menurut `artifacts/reports/class_imbalance_diagnostics.md`: ['Bacterial leaf blight', 'Bacterial panicle blight', 'False smut', 'Leaf roller', 'Narrow brown']

## Hasil keseluruhan

| Eksekusi | mAP@0.5 | Precision | Recall | Durasi (detik) |
|---|---:|---:|---:|---:|
| baseline, distribusi alami | 0.0071 | 0.1143 | 0.0550 | 135.2 |
| oversampled, kelas minoritas 3 kali | 0.0005 | 0.1825 | 0.0111 | 119.7 |

## AP@0.5 per kelas, khusus kelas minoritas, yang menjadi inti ablasi ini

| Kelas | AP@0.5 baseline | AP@0.5 oversampled | Selisih |
|---|---:|---:|---:|
| Bacterial leaf blight | 0.0003 | 0.0003 | +0.0000 |
| Bacterial panicle blight | 0.0080 | 0.0044 | -0.0036 |
| False smut | 0.0000 | 0.0000 | +0.0000 |
| Leaf roller | 0.0677 | 0.0001 | -0.0676 |
| Narrow brown | 0.0000 | 0.0000 | +0.0000 |

## AP@0.5 per kelas, seluruh kelas, untuk memastikan oversampling tidak merugikan kelas mayoritas

| Kelas | AP@0.5 baseline | AP@0.5 oversampled | Selisih |
|---|---:|---:|---:|
| Bacterial leaf blight (minoritas, disasar) | 0.0003 | 0.0003 | +0.0000 |
| Bacterial panicle blight (minoritas, disasar) | 0.0080 | 0.0044 | -0.0036 |
| Blast | 0.0021 | 0.0007 | -0.0014 |
| Brown spot | 0.0000 | 0.0000 | +0.0000 |
| False smut (minoritas, disasar) | 0.0000 | 0.0000 | +0.0000 |
| Healthy | 0.0000 | 0.0000 | +0.0000 |
| Leaf roller (minoritas, disasar) | 0.0677 | 0.0001 | -0.0676 |
| Leaf scald | 0.0000 | 0.0000 | +0.0000 |
| Narrow brown (minoritas, disasar) | 0.0000 | 0.0000 | +0.0000 |
| Sheath blight | 0.0000 | 0.0000 | +0.0000 |
| Tungro | 0.0000 | 0.0000 | +0.0000 |

## Kesimpulan

Rata-rata selisih AP@0.5 pada kelas minoritas yang disasar: -0.0142
Rata-rata selisih AP@0.5 pada kelas mayoritas yang tidak disasar: -0.0002

Oversampling TIDAK menunjukkan manfaat bersih yang jelas pada skala penyaringan ini, entah karena kelas minoritas tidak membaik, karena perbaikannya kalah oleh kerugian pada kelas mayoritas, atau keduanya sekaligus. Berdasarkan bukti ini, strategi tersebut TIDAK direkomendasikan untuk diadopsi. Pengujian ulang pada skala pelatihan penuh masih layak dipertimbangkan, karena efek ketidakseimbangan kelas dapat berperilaku berbeda dengan data dan epoch yang lebih banyak.
