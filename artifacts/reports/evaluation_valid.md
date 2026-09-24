# Laporan Evaluasi, split: `valid`

Bobot: `runs/detect/final/model_100epoch/weights/best.pt`  |  Commit Git: `e27127fb482ebe6941d7ffe54f4a3bd2127bfa29`

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

- Precision keseluruhan: 0.6336
- Recall keseluruhan: 0.2547
- F1 keseluruhan: 0.3633
- TP=1245 FP=720 FN=3643

| Kelas canonical | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5183 | 0.2897 | 0.3717 | 113 | 105 | 277 |
| Brown spot | 0.6016 | 0.1540 | 0.2452 | 225 | 149 | 1236 |
| Healthy | 0.8750 | 0.3962 | 0.5455 | 168 | 24 | 256 |
| Leaf roller | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 87 |
| Tungro | 0.6152 | 0.3092 | 0.4116 | 235 | 147 | 525 |
| Blast | 0.6557 | 0.2534 | 0.3656 | 240 | 126 | 707 |
| Narrow brown | 0.9091 | 0.9333 | 0.9211 | 70 | 7 | 5 |
| Sheath blight | 0.5533 | 0.2766 | 0.3689 | 135 | 109 | 353 |
| Bacterial leaf blight | 0.5413 | 0.4720 | 0.5043 | 59 | 50 | 66 |
| False smut | 0.0000 | 0.0000 | 0.0000 | 0 | 2 | 86 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 45 |
