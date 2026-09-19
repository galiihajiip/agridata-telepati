# Laporan Evaluasi, split: `valid`

Weights: `/Users/macbookpro/Projects/agridata/runs/detect/final/final_model/weights/best.pt`  |  Git commit: `b6814894104467a178bf1a37e0510c4eb92f01ee`

## Native metrics (Ultralytics, source of truth for mAP)

- mAP@0.5: 0.6277
- mAP@0.5:0.95: 0.3905
- Precision/Recall at Ultralytics' internal best-F1 point: 0.6406 / 0.6237

| canonical class | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.3887 |
| Bacterial panicle blight | 0.6216 |
| Blast | 0.4855 |
| Brown spot | 0.2909 |
| False smut | 0.9436 |
| Healthy | 0.8712 |
| Leaf roller | 0.8734 |
| Leaf scald | 0.3880 |
| Narrow brown | 0.9631 |
| Sheath blight | 0.4804 |
| Tungro | 0.5980 |

## Local F1 metrics (implementation detail, confidence threshold = 0.25)

- Overall precision: 0.7014
- Overall recall: 0.2230
- Overall F1: 0.3384
- TP=1090 FP=464 FN=3798

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.7162 | 0.1359 | 0.2284 | 53 | 21 | 337 |
| Brown spot | 0.6193 | 0.0835 | 0.1472 | 122 | 75 | 1339 |
| Healthy | 0.8555 | 0.5165 | 0.6441 | 219 | 37 | 205 |
| Leaf roller | 0.7500 | 0.8621 | 0.8021 | 75 | 25 | 12 |
| Tungro | 0.7354 | 0.2487 | 0.3717 | 189 | 68 | 571 |
| Blast | 0.6608 | 0.1975 | 0.3041 | 187 | 96 | 760 |
| Narrow brown | 0.8421 | 0.2133 | 0.3404 | 16 | 3 | 59 |
| Sheath blight | 0.5852 | 0.2111 | 0.3102 | 103 | 73 | 385 |
| Bacterial leaf blight | 0.4483 | 0.1040 | 0.1688 | 13 | 16 | 112 |
| False smut | 0.7941 | 0.9419 | 0.8617 | 81 | 21 | 5 |
| Bacterial panicle blight | 0.5246 | 0.7111 | 0.6038 | 32 | 29 | 13 |
