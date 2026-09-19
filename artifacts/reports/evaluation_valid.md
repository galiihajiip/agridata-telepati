# Laporan Evaluasi, split: `valid`

Weights: `/Users/macbookpro/Projects/agridata/runs/detect/final/final_model/weights/best.pt`  |  Git commit: `06741ed99e9097f4e5d00451a30b7b254d9462fe`

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

- Overall precision: 0.6210
- Overall recall: 0.0992
- Overall F1: 0.1711
- TP=485 FP=296 FN=4403

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.4082 | 0.0513 | 0.0911 | 20 | 29 | 370 |
| Brown spot | 0.5535 | 0.0602 | 0.1086 | 88 | 71 | 1373 |
| Healthy | 0.8649 | 0.2264 | 0.3589 | 96 | 15 | 328 |
| Leaf roller | 0.0000 | 0.0000 | 0.0000 | 0 | 4 | 87 |
| Tungro | 0.6125 | 0.0645 | 0.1167 | 49 | 31 | 711 |
| Blast | 0.6328 | 0.0855 | 0.1507 | 81 | 47 | 866 |
| Narrow brown | 0.7826 | 0.9600 | 0.8623 | 72 | 20 | 3 |
| Sheath blight | 0.5763 | 0.0697 | 0.1243 | 34 | 25 | 454 |
| Bacterial leaf blight | 0.4490 | 0.3520 | 0.3946 | 44 | 54 | 81 |
| False smut | 1.0000 | 0.0116 | 0.0230 | 1 | 0 | 85 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 45 |
