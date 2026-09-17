# Evaluation Report — split: `valid`

Weights: `/Users/macbookpro/Projects/agridata/runs/detect/final/final_model/weights/best.pt`  |  Git commit: `05725f1729bf6386c5cce84e508eec8f9b799ce8`

## Native metrics (Ultralytics, source of truth for mAP)

- mAP@0.5: 0.5620
- mAP@0.5:0.95: 0.3278
- Precision/Recall at Ultralytics' internal best-F1 point: 0.6073 / 0.5562

| canonical class | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.3153 |
| Bacterial panicle blight | 0.4728 |
| Blast | 0.4147 |
| Brown spot | 0.2656 |
| False smut | 0.9009 |
| Healthy | 0.8580 |
| Leaf roller | 0.7829 |
| Leaf scald | 0.3475 |
| Narrow brown | 0.9411 |
| Sheath blight | 0.3507 |
| Tungro | 0.5328 |

## Local F1 metrics (implementation detail, confidence threshold = 0.25)

- Overall precision: 0.6568
- Overall recall: 0.2052
- Overall F1: 0.3127
- TP=1003 FP=524 FN=3885

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.6436 | 0.1667 | 0.2648 | 65 | 36 | 325 |
| Brown spot | 0.6190 | 0.0801 | 0.1418 | 117 | 72 | 1344 |
| Healthy | 0.8261 | 0.4929 | 0.6174 | 209 | 44 | 215 |
| Leaf roller | 0.6635 | 0.7931 | 0.7225 | 69 | 35 | 18 |
| Tungro | 0.6381 | 0.2250 | 0.3327 | 171 | 97 | 589 |
| Blast | 0.5921 | 0.1732 | 0.2680 | 164 | 113 | 783 |
| Narrow brown | 0.7500 | 0.2000 | 0.3158 | 15 | 5 | 60 |
| Sheath blight | 0.6667 | 0.1598 | 0.2579 | 78 | 39 | 410 |
| Bacterial leaf blight | 0.3000 | 0.0960 | 0.1455 | 12 | 28 | 113 |
| False smut | 0.8000 | 0.8837 | 0.8398 | 76 | 19 | 10 |
| Bacterial panicle blight | 0.4286 | 0.6000 | 0.5000 | 27 | 36 | 18 |
