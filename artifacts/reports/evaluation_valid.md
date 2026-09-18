# Evaluation Report — split: `valid`

Weights: `runs/detect/final/final_model/weights/best.pt`  |  Git commit: `72da96fbcde2741c77037b4544e4df07975de4e8`

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

- Overall precision: 0.6757
- Overall recall: 0.3073
- Overall F1: 0.4224
- TP=1502 FP=721 FN=3386

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5946 | 0.1692 | 0.2635 | 66 | 45 | 324 |
| Brown spot | 0.5882 | 0.1369 | 0.2221 | 200 | 140 | 1261 |
| Healthy | 0.8571 | 0.7075 | 0.7752 | 300 | 50 | 124 |
| Leaf roller | 0.7353 | 0.8621 | 0.7937 | 75 | 27 | 12 |
| Tungro | 0.7104 | 0.3132 | 0.4347 | 238 | 97 | 522 |
| Blast | 0.6474 | 0.2714 | 0.3824 | 257 | 140 | 690 |
| Narrow brown | 0.7826 | 0.9600 | 0.8623 | 72 | 20 | 3 |
| Sheath blight | 0.5830 | 0.2807 | 0.3790 | 137 | 98 | 351 |
| Bacterial leaf blight | 0.4490 | 0.3520 | 0.3946 | 44 | 54 | 81 |
| False smut | 0.7941 | 0.9419 | 0.8617 | 81 | 21 | 5 |
| Bacterial panicle blight | 0.5246 | 0.7111 | 0.6038 | 32 | 29 | 13 |
