# Laporan Evaluasi, split: `valid`

Weights: `runs/detect/final/final_model/weights/best.pt`  |  Git commit: `e37949ef2cf0d85cf3ef08d57a29977b5cce2f37`

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

- Overall precision: 0.6828
- Overall recall: 0.2836
- Overall F1: 0.4007
- TP=1386 FP=644 FN=3502

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.6458 | 0.1590 | 0.2551 | 62 | 34 | 328 |
| Brown spot | 0.5915 | 0.1239 | 0.2049 | 181 | 125 | 1280 |
| Healthy | 0.8540 | 0.6486 | 0.7373 | 275 | 47 | 149 |
| Leaf roller | 0.7353 | 0.8621 | 0.7937 | 75 | 27 | 12 |
| Tungro | 0.7104 | 0.3132 | 0.4347 | 238 | 97 | 522 |
| Blast | 0.6676 | 0.2545 | 0.3685 | 241 | 120 | 706 |
| Narrow brown | 0.7255 | 0.4933 | 0.5873 | 37 | 14 | 38 |
| Sheath blight | 0.5830 | 0.2807 | 0.3790 | 137 | 98 | 351 |
| Bacterial leaf blight | 0.4576 | 0.2160 | 0.2935 | 27 | 32 | 98 |
| False smut | 0.7941 | 0.9419 | 0.8617 | 81 | 21 | 5 |
| Bacterial panicle blight | 0.5246 | 0.7111 | 0.6038 | 32 | 29 | 13 |
