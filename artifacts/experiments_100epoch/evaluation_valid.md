# Laporan Evaluasi, split: `valid`

Bobot: `runs/detect/final/model_100epoch/weights/best.pt`  |  Commit Git: `9dbba82b01014b326c1f3467e9064587ac5beb60`

## Metrik native Ultralytics, sumber kebenaran untuk mAP

- mAP@0.5: 0.6678
- mAP@0.5:0.95: 0.4141
- Ambang NMS IoU: 0.5
- Test-Time Augmentation (TTA): False
- F1 macro pada titik operasi terbaik: 0.6826 (confidence 0.2503)
- Precision dan recall pada titik operasi tersebut: 0.7188 / 0.6722

| Kelas canonical | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.4679 |
| Bacterial panicle blight | 0.6530 |
| Blast | 0.5358 |
| Brown spot | 0.3303 |
| False smut | 0.9528 |
| Healthy | 0.8717 |
| Leaf roller | 0.9134 |
| Leaf scald | 0.4490 |
| Narrow brown | 0.9755 |
| Sheath blight | 0.5502 |
| Tungro | 0.6460 |

## Metrik lokal diagnostik, rata-rata micro pada confidence 0.25

- Precision keseluruhan: 0.6473
- Recall keseluruhan: 0.1479
- F1 keseluruhan: 0.2408
- TP=723 FP=394 FN=4165

| Kelas canonical | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5868 | 0.1821 | 0.2779 | 71 | 50 | 319 |
| Brown spot | 0.5880 | 0.0869 | 0.1515 | 127 | 89 | 1334 |
| Healthy | 0.9167 | 0.1816 | 0.3031 | 77 | 7 | 347 |
| Leaf roller | 0.0000 | 0.0000 | 0.0000 | 0 | 1 | 87 |
| Tungro | 0.6767 | 0.2368 | 0.3509 | 180 | 86 | 580 |
| Blast | 0.6471 | 0.1278 | 0.2134 | 121 | 66 | 826 |
| Narrow brown | 0.9375 | 0.2000 | 0.3297 | 15 | 1 | 60 |
| Sheath blight | 0.6222 | 0.2295 | 0.3353 | 112 | 68 | 376 |
| Bacterial leaf blight | 0.4545 | 0.1600 | 0.2367 | 20 | 24 | 105 |
| False smut | 0.0000 | 0.0000 | 0.0000 | 0 | 2 | 86 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 45 |
