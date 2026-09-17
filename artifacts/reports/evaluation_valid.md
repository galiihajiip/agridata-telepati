# Evaluation Report — split: `valid`

Weights: `/Users/macbookpro/Projects/agridata/runs/detect/final/final_model/weights/best.pt`  |  Git commit: `e92a129be4dee5d63961175b6bd922be9f5dc4fd`

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

- Overall precision: 0.6044
- Overall recall: 0.0953
- Overall F1: 0.1647
- TP=466 FP=305 FN=4422

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.4118 | 0.0897 | 0.1474 | 35 | 50 | 355 |
| Brown spot | 0.5887 | 0.0500 | 0.0921 | 73 | 51 | 1388 |
| Healthy | 0.8785 | 0.2217 | 0.3540 | 94 | 13 | 330 |
| Leaf roller | 0.0000 | 0.0000 | 0.0000 | 0 | 2 | 87 |
| Tungro | 0.5543 | 0.0671 | 0.1197 | 51 | 41 | 709 |
| Blast | 0.6098 | 0.0792 | 0.1402 | 75 | 48 | 872 |
| Narrow brown | 0.7865 | 0.9333 | 0.8537 | 70 | 19 | 5 |
| Sheath blight | 0.6000 | 0.0430 | 0.0803 | 21 | 14 | 467 |
| Bacterial leaf blight | 0.4107 | 0.3680 | 0.3882 | 46 | 66 | 79 |
| False smut | 1.0000 | 0.0116 | 0.0230 | 1 | 0 | 85 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 45 |
