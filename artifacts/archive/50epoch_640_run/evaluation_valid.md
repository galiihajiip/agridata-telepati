# Laporan Evaluasi, split: `valid`


> Catatan: laporan arsip ini dihasilkan oleh versi templat evaluasi yang lebih lama,
> sehingga belum memuat F1 macro dan ambang NMS. Seluruh angka dipertahankan apa adanya;
> hanya label yang diterjemahkan. Angka yang berlaku untuk submission ada pada
> `artifacts/reports/evaluation_valid.md`.

Bobot: `/Users/macbookpro/Projects/agridata/runs/detect/final/final_model/weights/best.pt`  |  Commit Git: `424747e1a390787b017f3528d602a4beaaf2584f`

## Metrik native Ultralytics, sumber kebenaran untuk mAP

- mAP@0.5: 0.6277
- mAP@0.5:0.95: 0.3905
- Precision dan recall pada titik F1 terbaik internal Ultralytics: 0.6406 / 0.6237

| kelas canonical | AP@0.5 |
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

## Metrik lokal diagnostik, rata-rata micro pada confidence 0.25

- Precision keseluruhan: 0.6390
- Recall keseluruhan: 0.2248
- F1 keseluruhan: 0.3326
- TP=1099 FP=621 FN=3789

| kelas canonical | precision | recall | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Leaf scald | 0.5728 | 0.1513 | 0.2394 | 59 | 44 | 331 |
| Brown spot | 0.6066 | 0.1383 | 0.2252 | 202 | 131 | 1259 |
| Healthy | 0.8325 | 0.3986 | 0.5391 | 169 | 34 | 255 |
| Blast | 0.6418 | 0.2270 | 0.3354 | 215 | 120 | 732 |
| Leaf roller | 0.0000 | 0.0000 | 0.0000 | 0 | 7 | 87 |
| Tungro | 0.6394 | 0.2987 | 0.4072 | 227 | 128 | 533 |
| Narrow brown | 0.7826 | 0.9600 | 0.8623 | 72 | 20 | 3 |
| Sheath blight | 0.5729 | 0.2254 | 0.3235 | 110 | 82 | 378 |
| Bacterial leaf blight | 0.4444 | 0.3520 | 0.3929 | 44 | 55 | 81 |
| False smut | 1.0000 | 0.0116 | 0.0230 | 1 | 0 | 85 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 45 |
