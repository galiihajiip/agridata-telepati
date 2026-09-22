# Laporan Evaluasi, split: `valid`

Weights: `/Users/macbookpro/Projects/agridata/runs/detect/final/final_model/weights/best.pt`  |  Git commit: `faea78aeedf7ebb66deb831fd839774a13cba27a`

## Native metrics (Ultralytics, source of truth for mAP)

- mAP@0.5: 0.6401
- mAP@0.5:0.95: 0.3856
- Precision/Recall at Ultralytics' internal best-F1 point: 0.6526 / 0.6487

| canonical class | AP@0.5 |
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

## Local F1 metrics (implementation detail, confidence threshold = 0.25)

- Overall precision: 0.6390
- Overall recall: 0.2248
- Overall F1: 0.3326
- TP=1099 FP=621 FN=3789

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5728 | 0.1513 | 0.2394 | 59 | 44 | 331 |
| Brown spot | 0.6066 | 0.1383 | 0.2252 | 202 | 131 | 1259 |
| Healthy | 0.8325 | 0.3986 | 0.5391 | 169 | 34 | 255 |
| Blast | 0.6418 | 0.2270 | 0.3354 | 215 | 120 | 732 |
| Leaf roller | 0.0000 | 0.0000 | 0.0000 | 0 | 7 | 87 |
| Tungro | 0.6394 | 0.2987 | 0.4072 | 227 | 128 | 533 |
| Narrow brown | 0.7826 | 0.9600 | 0.8623 | 72 | 20 | 3 |
| Sheath blight | 0.5729 | 0.2254 | 0.3235 | 110 | 82 | 378 |
| Bacterial leaf blight | 0.4444 | 0.3520 | 0.3929 | 44 | 55 | 81 |
| False smut | 1.0000 | 0.0116 | 0.0230 | 1 | 0 | 85 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 45 |
