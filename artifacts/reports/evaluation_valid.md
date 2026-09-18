# Evaluation Report — split: `valid`

Weights: `/Users/macbookpro/Projects/agridata/runs/detect/final/final_model/weights/best.pt`  |  Git commit: `f10a20cb9194692adfa8ba1250efee3f47d8d1d8`

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

- Overall precision: 0.6679
- Overall recall: 0.2576
- Overall F1: 0.3718
- TP=1259 FP=626 FN=3629

| canonical class | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.7167 | 0.2205 | 0.3373 | 86 | 34 | 304 |
| Brown spot | 0.6397 | 0.1567 | 0.2518 | 229 | 129 | 1232 |
| Healthy | 0.8427 | 0.3538 | 0.4983 | 150 | 28 | 274 |
| Blast | 0.6640 | 0.2608 | 0.3745 | 247 | 125 | 700 |
| Leaf roller | 0.0000 | 0.0000 | 0.0000 | 0 | 10 | 87 |
| Tungro | 0.6917 | 0.4605 | 0.5529 | 350 | 156 | 410 |
| Narrow brown | 0.8421 | 0.2133 | 0.3404 | 16 | 3 | 59 |
| Sheath blight | 0.5739 | 0.3422 | 0.4288 | 167 | 124 | 321 |
| Bacterial leaf blight | 0.4333 | 0.1040 | 0.1677 | 13 | 17 | 112 |
| False smut | 1.0000 | 0.0116 | 0.0230 | 1 | 0 | 85 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 45 |
