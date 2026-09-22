# Laporan Evaluasi, split: `test`

Weights: `runs/detect/final/final_model/weights/best.pt`  |  Git commit: `bf1559abfa2207922af3083ffd48c03d01fece75`

## Native metrics (Ultralytics, source of truth for mAP)

- mAP@0.5: 0.6145
- mAP@0.5:0.95: 0.3998
- Precision/Recall at Ultralytics' internal best-F1 point: 0.6595 / 0.6160

| canonical class | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.3182 |
| Bacterial panicle blight | 0.6313 |
| Blast | 0.4602 |
| Brown spot | 0.2582 |
| False smut | 0.9151 |
| Healthy | 0.9347 |
| Leaf roller | 0.8335 |
| Leaf scald | 0.3600 |
| Narrow brown | 0.9809 |
| Sheath blight | 0.4535 |
| Tungro | 0.6136 |

## Local F1 metrics (implementation detail, confidence threshold = 0.25)

- Overall precision: 0.6755
- Overall recall: 0.2199
- Overall F1: 0.3317
- TP=587 FP=282 FN=2083

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Brown spot | 0.6220 | 0.0940 | 0.1634 | 79 | 48 | 761 |
| Tungro | 0.7133 | 0.2603 | 0.3815 | 107 | 43 | 304 |
| Bacterial leaf blight | 0.4615 | 0.1017 | 0.1667 | 6 | 7 | 53 |
| Sheath blight | 0.5727 | 0.2342 | 0.3325 | 63 | 47 | 206 |
| Healthy | 0.8319 | 0.5380 | 0.6535 | 99 | 20 | 85 |
| Blast | 0.6627 | 0.2056 | 0.3138 | 110 | 56 | 425 |
| False smut | 0.7308 | 0.8837 | 0.8000 | 38 | 14 | 5 |
| Narrow brown | 0.5333 | 0.2222 | 0.3137 | 8 | 7 | 28 |
| Leaf scald | 0.6452 | 0.0901 | 0.1581 | 20 | 11 | 202 |
| Bacterial panicle blight | 0.5938 | 0.7037 | 0.6441 | 19 | 13 | 8 |
| Leaf roller | 0.7037 | 0.8636 | 0.7755 | 38 | 16 | 6 |

**WARNING: this is a test-split evaluation. Test ground truth must never be used for iterative model tuning.**
