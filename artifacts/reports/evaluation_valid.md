# Evaluation Report — split: `valid`

Weights: `runs/detect/block6_baseline_smoke/weights/best.pt`  |  Git commit: `b727684d299797f42b726c7a4c6e9ee488a4e64d`

## Native metrics (Ultralytics, source of truth for mAP)

- mAP@0.5: 0.0000
- mAP@0.5:0.95: 0.0000
- Precision/Recall at Ultralytics' internal best-F1 point: 0.0000 / 0.0000

| canonical class | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.0000 |
| Bacterial panicle blight | 0.0000 |
| Blast | 0.0000 |
| Brown spot | 0.0000 |
| False smut | 0.0000 |
| Healthy | 0.0000 |
| Leaf roller | 0.0000 |
| Leaf scald | 0.0000 |
| Narrow brown | 0.0000 |
| Sheath blight | 0.0000 |
| Tungro | 0.0000 |

## Local F1 metrics (implementation detail, confidence threshold = 0.25)

- Overall precision: 0.0000
- Overall recall: 0.0000
- Overall F1: 0.0000
- TP=0 FP=0 FN=4888

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 390 |
| Brown spot | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 1461 |
| Healthy | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 424 |
| Leaf roller | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 87 |
| Tungro | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 760 |
| Blast | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 947 |
| Narrow brown | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 75 |
| Sheath blight | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 488 |
| Bacterial leaf blight | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 125 |
| False smut | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 86 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 45 |
