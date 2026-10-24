# Laporan Evaluasi, split: `valid`

Bobot: `runs/detect/final/yolov8m_640_150ep/weights/best.pt`  |  Commit Git: `b169142419518eee111afc865136c80988a3bd76`

## Metrik native Ultralytics, sumber kebenaran untuk mAP

- mAP@0.5: 0.7139
- mAP@0.5:0.95: 0.4832
- Ambang NMS IoU: 0.5
- Test-Time Augmentation (TTA): False
- F1 macro pada titik operasi terbaik: 0.7138 (confidence 0.2132)
- Precision dan recall pada titik operasi tersebut: 0.7100 / 0.7261

| Kelas canonical | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.4937 |
| Bacterial panicle blight | 0.8298 |
| Blast | 0.5660 |
| Brown spot | 0.3773 |
| False smut | 0.9422 |
| Healthy | 0.8997 |
| Leaf roller | 0.9324 |
| Leaf scald | 0.4885 |
| Narrow brown | 0.9949 |
| Sheath blight | 0.6459 |
| Tungro | 0.6821 |

## Metrik lokal diagnostik, rata-rata micro pada confidence 0.25

- Precision keseluruhan: 0.6654
- Recall keseluruhan: 0.5115
- F1 keseluruhan: 0.5784
- TP=2500 FP=1257 FN=2388

| Kelas canonical | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5927 | 0.4179 | 0.4902 | 163 | 112 | 227 |
| Brown spot | 0.5997 | 0.2758 | 0.3779 | 403 | 269 | 1058 |
| Healthy | 0.8228 | 0.8868 | 0.8536 | 376 | 81 | 48 |
| Leaf roller | 0.7670 | 0.9080 | 0.8316 | 79 | 24 | 8 |
| Tungro | 0.6637 | 0.5974 | 0.6288 | 454 | 230 | 306 |
| Blast | 0.6657 | 0.4900 | 0.5645 | 464 | 233 | 483 |
| Narrow brown | 0.9605 | 0.9733 | 0.9669 | 73 | 3 | 2 |
| Sheath blight | 0.5814 | 0.6291 | 0.6043 | 307 | 221 | 181 |
| Bacterial leaf blight | 0.5727 | 0.5040 | 0.5362 | 63 | 47 | 62 |
| False smut | 0.8200 | 0.9535 | 0.8817 | 82 | 18 | 4 |
| Bacterial panicle blight | 0.6545 | 0.8000 | 0.7200 | 36 | 19 | 9 |
