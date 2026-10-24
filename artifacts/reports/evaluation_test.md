# Laporan Evaluasi, split: `test`

Bobot: `runs/detect/final/yolov8s_p2_640_250ep/weights/best.pt`  |  Commit Git: `b169142419518eee111afc865136c80988a3bd76`

## Metrik native Ultralytics, sumber kebenaran untuk mAP

- mAP@0.5: 0.7065
- mAP@0.5:0.95: 0.4830
- Ambang NMS IoU: 0.5
- Test-Time Augmentation (TTA): False
- F1 macro pada titik operasi terbaik: 0.7145 (confidence 0.2623)
- Precision dan recall pada titik operasi tersebut: 0.7626 / 0.6904

| Kelas canonical | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.3666 |
| Bacterial panicle blight | 0.8790 |
| Blast | 0.5427 |
| Brown spot | 0.3188 |
| False smut | 0.9612 |
| Healthy | 0.9595 |
| Leaf roller | 0.9312 |
| Leaf scald | 0.4898 |
| Narrow brown | 0.9950 |
| Sheath blight | 0.6282 |
| Tungro | 0.6996 |

## Metrik lokal diagnostik, rata-rata micro pada confidence 0.25

- Precision keseluruhan: 0.6879
- Recall keseluruhan: 0.4888
- F1 keseluruhan: 0.5715
- TP=1305 FP=592 FN=1365

| Kelas canonical | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Brown spot | 0.6486 | 0.2417 | 0.3521 | 203 | 110 | 637 |
| Tungro | 0.7278 | 0.6375 | 0.6796 | 262 | 98 | 149 |
| Bacterial leaf blight | 0.4737 | 0.4576 | 0.4655 | 27 | 30 | 32 |
| Sheath blight | 0.6174 | 0.6059 | 0.6116 | 163 | 101 | 106 |
| Healthy | 0.8670 | 0.9565 | 0.9096 | 176 | 27 | 8 |
| Blast | 0.6436 | 0.4355 | 0.5195 | 233 | 129 | 302 |
| False smut | 0.9111 | 0.9535 | 0.9318 | 41 | 4 | 2 |
| Narrow brown | 0.9444 | 0.9444 | 0.9444 | 34 | 2 | 2 |
| Leaf scald | 0.5829 | 0.4595 | 0.5139 | 102 | 73 | 120 |
| Leaf roller | 0.7736 | 0.9318 | 0.8454 | 41 | 12 | 3 |
| Bacterial panicle blight | 0.7931 | 0.8519 | 0.8214 | 23 | 6 | 4 |

**PERINGATAN: ini evaluasi pada split test. Ground truth test tidak boleh dipakai untuk penyetelan model secara berulang.**
