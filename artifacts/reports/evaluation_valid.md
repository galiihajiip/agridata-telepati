# Laporan Evaluasi, split: `valid`

Bobot: `runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt`  |  Commit Git: `b169142419518eee111afc865136c80988a3bd76`

## Metrik native Ultralytics, sumber kebenaran untuk mAP

- mAP@0.5: 0.7071
- mAP@0.5:0.95: 0.4611
- Ambang NMS IoU: 0.5
- Test-Time Augmentation (TTA): False
- F1 macro pada titik operasi terbaik: 0.7233 (confidence 0.2142)
- Precision dan recall pada titik operasi tersebut: 0.7353 / 0.7206

| Kelas canonical | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.4787 |
| Bacterial panicle blight | 0.7723 |
| Blast | 0.5709 |
| Brown spot | 0.3755 |
| False smut | 0.9623 |
| Healthy | 0.8722 |
| Leaf roller | 0.9226 |
| Leaf scald | 0.5028 |
| Narrow brown | 0.9864 |
| Sheath blight | 0.6650 |
| Tungro | 0.6690 |

## Metrik lokal diagnostik, rata-rata micro pada confidence 0.25

- Precision keseluruhan: 0.6735
- Recall keseluruhan: 0.5237
- F1 keseluruhan: 0.5893
- TP=2560 FP=1241 FN=2328

| Kelas canonical | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5407 | 0.5282 | 0.5344 | 206 | 175 | 184 |
| Brown spot | 0.5846 | 0.2697 | 0.3691 | 394 | 280 | 1067 |
| Healthy | 0.8453 | 0.8892 | 0.8667 | 377 | 69 | 47 |
| Leaf roller | 0.8182 | 0.9310 | 0.8710 | 81 | 18 | 6 |
| Tungro | 0.6981 | 0.5934 | 0.6415 | 451 | 195 | 309 |
| Blast | 0.6741 | 0.5111 | 0.5814 | 484 | 234 | 463 |
| Narrow brown | 0.9481 | 0.9733 | 0.9605 | 73 | 4 | 2 |
| Sheath blight | 0.6488 | 0.6434 | 0.6461 | 314 | 170 | 174 |
| Bacterial leaf blight | 0.5118 | 0.5200 | 0.5159 | 65 | 62 | 60 |
| False smut | 0.8300 | 0.9651 | 0.8925 | 83 | 17 | 3 |
| Bacterial panicle blight | 0.6531 | 0.7111 | 0.6809 | 32 | 17 | 13 |
