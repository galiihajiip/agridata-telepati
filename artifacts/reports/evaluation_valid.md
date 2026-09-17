# Evaluation Report — split: `valid`

Weights: `runs/detect/final/final_model/weights/best.pt`  |  Git commit: `0b5b43942ed16ea915bdb7ce1140e8e59cf485b4`

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

- Overall precision: 0.6096
- Overall recall: 0.2070
- Overall F1: 0.3091
- TP=1012 FP=648 FN=3876

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5037 | 0.1744 | 0.2590 | 68 | 67 | 322 |
| Brown spot | 0.6310 | 0.1253 | 0.2090 | 183 | 107 | 1278 |
| Healthy | 0.8367 | 0.3868 | 0.5290 | 164 | 32 | 260 |
| Leaf roller | 0.0000 | 0.0000 | 0.0000 | 0 | 13 | 87 |
| Tungro | 0.6136 | 0.2842 | 0.3885 | 216 | 136 | 544 |
| Blast | 0.5599 | 0.2122 | 0.3078 | 201 | 158 | 746 |
| Narrow brown | 0.7778 | 0.9333 | 0.8485 | 70 | 20 | 5 |
| Sheath blight | 0.5676 | 0.1291 | 0.2104 | 63 | 48 | 425 |
| Bacterial leaf blight | 0.4107 | 0.3680 | 0.3882 | 46 | 66 | 79 |
| False smut | 1.0000 | 0.0116 | 0.0230 | 1 | 0 | 85 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 45 |
