# Laporan Evaluasi, split: `valid`

Bobot: `kaggle_results/A_best.pt`  |  Commit Git: `469067a7e55584af125e2da26facd1cdd7860be7`

## Metrik native Ultralytics, sumber kebenaran untuk mAP

- mAP@0.5: 0.7057
- mAP@0.5:0.95: 0.4640
- Ambang NMS IoU: 0.5
- Test-Time Augmentation (TTA): False
- F1 macro pada titik operasi terbaik: 0.7137 (confidence 0.1972)
- Precision dan recall pada titik operasi tersebut: 0.7057 / 0.7304

| Kelas canonical | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.4891 |
| Bacterial panicle blight | 0.7731 |
| Blast | 0.5772 |
| Brown spot | 0.3732 |
| False smut | 0.9559 |
| Healthy | 0.8759 |
| Leaf roller | 0.9131 |
| Leaf scald | 0.4921 |
| Narrow brown | 0.9834 |
| Sheath blight | 0.6551 |
| Tungro | 0.6749 |

## Metrik lokal diagnostik, rata-rata micro pada confidence 0.25

- Precision keseluruhan: 0.6624
- Recall keseluruhan: 0.5235
- F1 keseluruhan: 0.5848
- TP=2559 FP=1304 FN=2329

| Kelas canonical | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5780 | 0.5128 | 0.5435 | 200 | 146 | 190 |
| Brown spot | 0.5840 | 0.2806 | 0.3791 | 410 | 292 | 1051 |
| Healthy | 0.8268 | 0.8892 | 0.8568 | 377 | 79 | 47 |
| Leaf roller | 0.8041 | 0.8966 | 0.8478 | 78 | 19 | 9 |
| Tungro | 0.6507 | 0.5908 | 0.6193 | 449 | 241 | 311 |
| Blast | 0.6733 | 0.5005 | 0.5742 | 474 | 230 | 473 |
| Narrow brown | 0.9359 | 0.9733 | 0.9542 | 73 | 5 | 2 |
| Sheath blight | 0.6157 | 0.6434 | 0.6293 | 314 | 196 | 174 |
| Bacterial leaf blight | 0.5276 | 0.5360 | 0.5317 | 67 | 60 | 58 |
| False smut | 0.8200 | 0.9535 | 0.8817 | 82 | 18 | 4 |
| Bacterial panicle blight | 0.6604 | 0.7778 | 0.7143 | 35 | 18 | 10 |
