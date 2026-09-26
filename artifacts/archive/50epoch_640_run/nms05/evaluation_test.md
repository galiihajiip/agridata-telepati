# Laporan Evaluasi, split: `test`


> Catatan: berkas arsip ini merupakan evaluasi final model 50 *epoch* yang
> sudah digantikan model 100 *epoch*. Seluruh angka dipertahankan apa adanya;
> hanya labelnya yang diterjemahkan. Angka yang berlaku untuk submission ada
> pada `artifacts/reports/evaluation_valid.md` dan `evaluation_test.md`.

Bobot: `runs/detect/final/final_model/weights/best.pt`  |  Commit Git: `9072dc1f4028854461a89a976a5a7dc0dc0ec5d7`

## Metrik native Ultralytics, sumber kebenaran untuk mAP

- mAP@0.5: 0.6246
- mAP@0.5:0.95: 0.3940
- Precision dan recall pada titik F1 terbaik internal Ultralytics: 0.6420 / 0.6391

| Kelas canonical | AP@0.5 |
|---|---:|
| Bacterial leaf blight | 0.3230 |
| Bacterial panicle blight | 0.6249 |
| Blast | 0.4700 |
| Brown spot | 0.2794 |
| False smut | 0.9203 |
| Healthy | 0.9349 |
| Leaf roller | 0.8396 |
| Leaf scald | 0.3931 |
| Narrow brown | 0.9809 |
| Sheath blight | 0.4729 |
| Tungro | 0.6312 |

## Metrik lokal diagnostik, rata-rata micro pada confidence 0.25

- Precision keseluruhan: 0.6679
- Recall keseluruhan: 0.4112
- F1 keseluruhan: 0.5090
- TP=1098 FP=546 FN=1572

| Kelas canonical | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Brown spot | 0.6381 | 0.1952 | 0.2990 | 164 | 93 | 676 |
| Tungro | 0.6782 | 0.5742 | 0.6219 | 236 | 112 | 175 |
| Bacterial leaf blight | 0.5000 | 0.4237 | 0.4587 | 25 | 25 | 34 |
| Sheath blight | 0.5792 | 0.4349 | 0.4968 | 117 | 85 | 152 |
| Healthy | 0.8607 | 0.9402 | 0.8987 | 173 | 28 | 11 |
| Blast | 0.6431 | 0.3738 | 0.4728 | 200 | 111 | 335 |
| False smut | 0.7308 | 0.8837 | 0.8000 | 38 | 14 | 5 |
| Narrow brown | 0.6538 | 0.9444 | 0.7727 | 34 | 18 | 2 |
| Leaf scald | 0.6750 | 0.2432 | 0.3576 | 54 | 26 | 168 |
| Bacterial panicle blight | 0.5938 | 0.7037 | 0.6441 | 19 | 13 | 8 |
| Leaf roller | 0.6441 | 0.8636 | 0.7379 | 38 | 21 | 6 |

**PERINGATAN: ini evaluasi pada split test. Ground truth test tidak boleh dipakai untuk penyetelan model secara berulang.**
