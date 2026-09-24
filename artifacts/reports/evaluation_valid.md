# Laporan Evaluasi, split: `valid`

Bobot: `runs/detect/final/model_100epoch/weights/best.pt`  |  Commit Git: `4fc68783d1bd66ce7861ca4a7be877ad76d2b9f2`

## Metrik native Ultralytics, sumber kebenaran untuk mAP

- mAP@0.5: 0.6678
- mAP@0.5:0.95: 0.4141
- Ambang NMS IoU: 0.5
- F1 macro pada titik operasi terbaik: 0.6826 (confidence 0.2503)
- Precision dan recall pada titik operasi tersebut: 0.7188 / 0.6722

| Kelas canonical | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.4679 |
| Bacterial panicle blight | 0.6530 |
| Blast | 0.5358 |
| Brown spot | 0.3303 |
| False smut | 0.9528 |
| Healthy | 0.8717 |
| Leaf roller | 0.9134 |
| Leaf scald | 0.4490 |
| Narrow brown | 0.9755 |
| Sheath blight | 0.5502 |
| Tungro | 0.6460 |

## Metrik lokal diagnostik, rata-rata micro pada confidence 0.25

- Precision keseluruhan: 0.6580
- Recall keseluruhan: 0.3400
- F1 keseluruhan: 0.4483
- TP=1662 FP=864 FN=3226

| Kelas canonical | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5325 | 0.3154 | 0.3961 | 123 | 108 | 267 |
| Brown spot | 0.5625 | 0.1540 | 0.2418 | 225 | 175 | 1236 |
| Healthy | 0.8475 | 0.7075 | 0.7712 | 300 | 54 | 124 |
| Leaf roller | 0.7800 | 0.8966 | 0.8342 | 78 | 22 | 9 |
| Tungro | 0.6474 | 0.3237 | 0.4316 | 246 | 134 | 514 |
| Blast | 0.6337 | 0.2978 | 0.4052 | 282 | 163 | 665 |
| Narrow brown | 0.9091 | 0.9333 | 0.9211 | 70 | 7 | 5 |
| Sheath blight | 0.6066 | 0.3381 | 0.4342 | 165 | 107 | 323 |
| Bacterial leaf blight | 0.5413 | 0.4720 | 0.5043 | 59 | 50 | 66 |
| False smut | 0.7905 | 0.9651 | 0.8691 | 83 | 22 | 3 |
| Bacterial panicle blight | 0.5849 | 0.6889 | 0.6327 | 31 | 22 | 14 |
