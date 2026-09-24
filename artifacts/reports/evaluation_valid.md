# Laporan Evaluasi, split: `valid`

Bobot: `runs/detect/final/model_100epoch/weights/best.pt`  |  Commit Git: `0d4cabd9f29e0d604c7a3d6107bc59e9b9718099`

## Metrik native Ultralytics, sumber kebenaran untuk mAP

- mAP@0.5: 0.6759
- mAP@0.5:0.95: 0.4304
- Ambang NMS IoU: 0.5
- Test-Time Augmentation (TTA): True
- F1 macro pada titik operasi terbaik: 0.6755 (confidence 0.3193)
- Precision dan recall pada titik operasi tersebut: 0.7164 / 0.6688

| Kelas canonical | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.5072 |
| Bacterial panicle blight | 0.6395 |
| Blast | 0.5360 |
| Brown spot | 0.3256 |
| False smut | 0.9346 |
| Healthy | 0.8923 |
| Leaf roller | 0.9455 |
| Leaf scald | 0.4746 |
| Narrow brown | 0.9581 |
| Sheath blight | 0.5682 |
| Tungro | 0.6533 |

## Metrik lokal diagnostik, rata-rata micro pada confidence 0.25

- Precision keseluruhan: 0.6764
- Recall keseluruhan: 0.2412
- F1 keseluruhan: 0.3556
- TP=1179 FP=564 FN=3709

| Kelas canonical | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5865 | 0.2000 | 0.2983 | 78 | 55 | 312 |
| Brown spot | 0.5877 | 0.0917 | 0.1587 | 134 | 94 | 1327 |
| Healthy | 0.8327 | 0.5165 | 0.6376 | 219 | 44 | 205 |
| Leaf roller | 0.7879 | 0.8966 | 0.8387 | 78 | 21 | 9 |
| Tungro | 0.6678 | 0.2592 | 0.3735 | 197 | 98 | 563 |
| Blast | 0.6472 | 0.2112 | 0.3185 | 200 | 109 | 747 |
| Narrow brown | 0.9375 | 0.2000 | 0.3297 | 15 | 1 | 60 |
| Sheath blight | 0.6263 | 0.2541 | 0.3615 | 124 | 74 | 364 |
| Bacterial leaf blight | 0.4545 | 0.1600 | 0.2367 | 20 | 24 | 105 |
| False smut | 0.7905 | 0.9651 | 0.8691 | 83 | 22 | 3 |
| Bacterial panicle blight | 0.5849 | 0.6889 | 0.6327 | 31 | 22 | 14 |
