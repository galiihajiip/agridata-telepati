# Laporan Evaluasi, split: `valid`

Weights: `/Users/macbookpro/Projects/agridata/runs/detect/final/final_model/weights/best.pt`  |  Git commit: `18f03e1cef34eaea85fa2b837a35c6338422e7de`

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

- Overall precision: 0.6632
- Overall recall: 0.3159
- Overall F1: 0.4279
- TP=1544 FP=784 FN=3344

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5856 | 0.1667 | 0.2595 | 65 | 46 | 325 |
| Brown spot | 0.6040 | 0.1431 | 0.2313 | 209 | 137 | 1252 |
| Healthy | 0.8338 | 0.7335 | 0.7804 | 311 | 62 | 113 |
| Blast | 0.6380 | 0.3052 | 0.4129 | 289 | 164 | 658 |
| Leaf roller | 0.7500 | 0.8621 | 0.8021 | 75 | 25 | 12 |
| Tungro | 0.6404 | 0.3211 | 0.4277 | 244 | 137 | 516 |
| Narrow brown | 0.7826 | 0.9600 | 0.8623 | 72 | 20 | 3 |
| Sheath blight | 0.5810 | 0.2500 | 0.3496 | 122 | 88 | 366 |
| Bacterial leaf blight | 0.4444 | 0.3520 | 0.3929 | 44 | 55 | 81 |
| False smut | 0.7941 | 0.9419 | 0.8617 | 81 | 21 | 5 |
| Bacterial panicle blight | 0.5246 | 0.7111 | 0.6038 | 32 | 29 | 13 |
