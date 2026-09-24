# Laporan Evaluasi, split: `test`

Bobot: `runs/detect/final/model_100epoch/weights/best.pt`  |  Commit Git: `762b6e73bfce8bd4c0fba79253eaf76c6f2743f3`

## Metrik native Ultralytics, sumber kebenaran untuk mAP

- mAP@0.5: 0.6596
- mAP@0.5:0.95: 0.4330
- Ambang NMS IoU: 0.5
- F1 macro pada titik operasi terbaik: 0.6641 (confidence 0.2382)
- Precision dan recall pada titik operasi tersebut: 0.6983 / 0.6634

| Kelas canonical | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.3673 |
| Bacterial panicle blight | 0.7671 |
| Blast | 0.5066 |
| Brown spot | 0.2811 |
| False smut | 0.9471 |
| Healthy | 0.9357 |
| Leaf roller | 0.8966 |
| Leaf scald | 0.4180 |
| Narrow brown | 0.9729 |
| Sheath blight | 0.5094 |
| Tungro | 0.6533 |

## Metrik lokal diagnostik, rata-rata micro pada confidence 0.25

- Precision keseluruhan: 0.6435
- Recall keseluruhan: 0.2292
- F1 keseluruhan: 0.3380
- TP=612 FP=339 FN=2058

| Kelas canonical | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Brown spot | 0.6800 | 0.1214 | 0.2061 | 102 | 48 | 738 |
| Tungro | 0.6295 | 0.3431 | 0.4441 | 141 | 83 | 270 |
| Bacterial leaf blight | 0.5217 | 0.4068 | 0.4571 | 24 | 22 | 35 |
| Sheath blight | 0.5310 | 0.2230 | 0.3141 | 60 | 53 | 209 |
| Healthy | 0.8617 | 0.4402 | 0.5827 | 81 | 13 | 103 |
| Blast | 0.6506 | 0.2019 | 0.3081 | 108 | 58 | 427 |
| False smut | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 43 |
| Narrow brown | 0.8250 | 0.9167 | 0.8684 | 33 | 7 | 3 |
| Leaf scald | 0.5636 | 0.2793 | 0.3735 | 62 | 48 | 160 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 27 |
| Leaf roller | 0.1250 | 0.0227 | 0.0385 | 1 | 7 | 43 |

**PERINGATAN: ini evaluasi pada split test. Ground truth test tidak boleh dipakai untuk penyetelan model secara berulang.**
