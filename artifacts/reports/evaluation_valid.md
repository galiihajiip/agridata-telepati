# Evaluation Report — split: `valid`

Weights: `runs/detect/final/final_model/weights/best.pt`  |  Git commit: `cf1adab55eb96036ec97d067788af241130bf46a`

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

- Overall precision: 0.6213
- Overall recall: 0.2347
- Overall F1: 0.3407
- TP=1147 FP=699 FN=3741

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.6643 | 0.2385 | 0.3509 | 93 | 47 | 297 |
| Brown spot | 0.6424 | 0.1513 | 0.2449 | 221 | 123 | 1240 |
| Healthy | 0.8249 | 0.3443 | 0.4859 | 146 | 31 | 278 |
| Leaf roller | 0.0000 | 0.0000 | 0.0000 | 0 | 26 | 87 |
| Tungro | 0.6369 | 0.4224 | 0.5079 | 321 | 183 | 439 |
| Blast | 0.5499 | 0.2386 | 0.3328 | 226 | 185 | 721 |
| Narrow brown | 0.7143 | 0.2000 | 0.3125 | 15 | 6 | 60 |
| Sheath blight | 0.6154 | 0.2295 | 0.3343 | 112 | 70 | 376 |
| Bacterial leaf blight | 0.3000 | 0.0960 | 0.1455 | 12 | 28 | 113 |
| False smut | 1.0000 | 0.0116 | 0.0230 | 1 | 0 | 85 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 45 |
