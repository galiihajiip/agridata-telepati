# Laporan Evaluasi, split: `valid`


> Catatan: berkas arsip ini merupakan evaluasi final model 50 *epoch* yang
> sudah digantikan model 100 *epoch*. Seluruh angka dipertahankan apa adanya;
> hanya labelnya yang diterjemahkan. Angka yang berlaku untuk submission ada
> pada `artifacts/reports/evaluation_valid.md` dan `evaluation_test.md`.

Bobot: `/Users/macbookpro/Projects/agridata/runs/detect/final/final_model/weights/best.pt`  |  Commit Git: `81dfbc040e725b1f321a4452db110fc4bb10d5f5`

## Metrik native Ultralytics, sumber kebenaran untuk mAP

- mAP@0.5: 0.6401
- mAP@0.5:0.95: 0.3856
- Precision dan recall pada titik F1 terbaik internal Ultralytics: 0.6526 / 0.6487

| Kelas canonical | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.4069 |
| Bacterial panicle blight | 0.6330 |
| Blast | 0.5017 |
| Brown spot | 0.3153 |
| False smut | 0.9485 |
| Healthy | 0.8722 |
| Leaf roller | 0.8768 |
| Leaf scald | 0.4051 |
| Narrow brown | 0.9717 |
| Sheath blight | 0.4974 |
| Tungro | 0.6125 |

## Metrik lokal diagnostik, rata-rata micro pada confidence 0.25

- Precision keseluruhan: 0.6788
- Recall keseluruhan: 0.2936
- F1 keseluruhan: 0.4099
- TP=1435 FP=679 FN=3453

| Kelas canonical | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.6058 | 0.1615 | 0.2551 | 63 | 41 | 327 |
| Brown spot | 0.5862 | 0.1280 | 0.2101 | 187 | 132 | 1274 |
| Healthy | 0.8512 | 0.6745 | 0.7526 | 286 | 50 | 138 |
| Leaf roller | 0.7353 | 0.8621 | 0.7937 | 75 | 27 | 12 |
| Tungro | 0.7104 | 0.3132 | 0.4347 | 238 | 97 | 522 |
| Blast | 0.6613 | 0.2619 | 0.3752 | 248 | 127 | 699 |
| Narrow brown | 0.7857 | 0.7333 | 0.7586 | 55 | 15 | 20 |
| Sheath blight | 0.5830 | 0.2807 | 0.3790 | 137 | 98 | 351 |
| Bacterial leaf blight | 0.4400 | 0.2640 | 0.3300 | 33 | 42 | 92 |
| False smut | 0.7941 | 0.9419 | 0.8617 | 81 | 21 | 5 |
| Bacterial panicle blight | 0.5246 | 0.7111 | 0.6038 | 32 | 29 | 13 |
