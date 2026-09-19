# Laporan Evaluasi, split: `valid`

Weights: `/Users/macbookpro/Projects/agridata/runs/detect/final/final_model/weights/best.pt`  |  Git commit: `3230fa6a574da9c000ed3ab14aaf310e7b3c0a54`

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

- Overall precision: 0.6818
- Overall recall: 0.1320
- Overall F1: 0.2211
- TP=645 FP=301 FN=4243

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.7121 | 0.1205 | 0.2061 | 47 | 19 | 343 |
| Brown spot | 0.6250 | 0.0787 | 0.1398 | 115 | 69 | 1346 |
| Healthy | 0.8953 | 0.1816 | 0.3020 | 77 | 9 | 347 |
| Leaf roller | 0.0000 | 0.0000 | 0.0000 | 0 | 7 | 87 |
| Tungro | 0.7446 | 0.2263 | 0.3471 | 172 | 59 | 588 |
| Blast | 0.6848 | 0.1193 | 0.2032 | 113 | 52 | 834 |
| Narrow brown | 0.8421 | 0.2133 | 0.3404 | 16 | 3 | 59 |
| Sheath blight | 0.5759 | 0.1865 | 0.2817 | 91 | 67 | 397 |
| Bacterial leaf blight | 0.4483 | 0.1040 | 0.1688 | 13 | 16 | 112 |
| False smut | 1.0000 | 0.0116 | 0.0230 | 1 | 0 | 85 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 45 |
