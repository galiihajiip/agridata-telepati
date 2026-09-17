# Evaluation Report — split: `valid`

Weights: `runs/detect/final/final_model/weights/best.pt`  |  Git commit: `a9e8483b54c717613f97a61aee04059b579e5ff5`

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

- Overall precision: 0.6220
- Overall recall: 0.2034
- Overall F1: 0.3065
- TP=994 FP=604 FN=3894

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5490 | 0.2154 | 0.3094 | 84 | 69 | 306 |
| Brown spot | 0.6098 | 0.1198 | 0.2002 | 175 | 112 | 1286 |
| Healthy | 0.8659 | 0.3656 | 0.5141 | 155 | 24 | 269 |
| Leaf roller | 0.0000 | 0.0000 | 0.0000 | 0 | 17 | 87 |
| Tungro | 0.6216 | 0.2724 | 0.3788 | 207 | 126 | 553 |
| Blast | 0.5789 | 0.1742 | 0.2679 | 165 | 120 | 782 |
| Narrow brown | 0.7778 | 0.9333 | 0.8485 | 70 | 20 | 5 |
| Sheath blight | 0.6500 | 0.1865 | 0.2898 | 91 | 49 | 397 |
| Bacterial leaf blight | 0.4107 | 0.3680 | 0.3882 | 46 | 66 | 79 |
| False smut | 1.0000 | 0.0116 | 0.0230 | 1 | 0 | 85 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 45 |
