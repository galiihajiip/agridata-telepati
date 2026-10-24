# Kandidat Model Skala Penuh

Empat kandidat dilatih dari nol (`pretrained=False`) pada seluruh data latih
dengan *split* resmi, sesudah model YOLOv8n 100 *epoch* diarsipkan. Resep
pelatihan masing-masing ada di `configs/kaggle/`, cara menjalankannya di
[`docs/kaggle_training.md`](../../docs/kaggle_training.md).

Pemilihan model final hanya memakai *split* valid. *Split* test dievaluasi
satu kali, untuk model terpilih saja, setelah pilihan dikunci.

## Hasil pada split valid

Seluruh angka dari `scripts/evaluate.py` dengan NMS IoU 0,5, prosedur yang sama
persis dengan model final.

| Kandidat | Arsitektur | Resolusi | *Epoch* (selesai) | Platform | mAP@50 | *F1* macro | mAP@50-95 |
|---|---|---:|---:|---|---:|---:|---:|
| A | YOLOv8s | 640 | 300 (271, *early stop*) | Kaggle 2x T4 | 70,57% | 71,37% | 46,40% |
| **B** | **YOLOv8s-P2** | **640** | **250 (250)** | **Kaggle 2x T4** | **70,71%** | **72,33%** | **46,11%** |
| C | YOLOv8s | 1024 | 150 (49, terputus) | Colab A100 | tidak dievaluasi | tidak dievaluasi | tidak dievaluasi |
| D | YOLOv8m | 640 | 150 (147, *early stop*) | Kaggle 2x T4 | 71,39% | 71,38% | 48,32% |

Pembanding, model sebelumnya (YOLOv8n 640, 100 *epoch*, Apple Silicon): mAP@50
66,78%, *F1* macro 68,26%.

## Alasan memilih B

Lomba menilai dua metrik, mAP@50 dan *F1-Score*. B dan D masing-masing unggul
pada satu metrik dengan selisih di bawah satu poin, yang masih dalam rentang
variasi antar-run. Kami memilih B karena jumlah kedua metrik lombanya paling
tinggi (143,04 berbanding 142,77 untuk D) dan bobotnya 2,4 kali lebih kecil
(21,8 MB berbanding 52,1 MB). Keunggulan D pada mAP@50 dan mAP@50-95 kami
catat apa adanya.

## Catatan per kandidat

- **A** berhenti karena *early stopping* di *epoch* 271, dengan model terbaik
  di sekitar *epoch* 221. Kurvanya mendatar jauh sebelum jadwal selesai.
- **B** tidak memicu *early stopping*. Pada *epoch* yang sama, kurva B hampir
  identik dengan A (mAP@50 0,671 berbanding 0,672 di *epoch* 66), jadi kepala
  P2 tidak mempercepat belajar. Keunggulan akhirnya terutama pada *F1*.
- **C** dihentikan di *epoch* 49 karena sesi Colab terputus, dan tidak kami
  lanjutkan. Di *epoch* 30 mAP@50 validasinya 0,57, di bawah A (0,579) dan
  B (0,584) pada *epoch* yang sama, sementara kandidat lain sudah melampauinya.
  Karena tidak selesai, C tidak kami evaluasi dan tidak kami bandingkan.
- **D** paling unggul per *epoch* (mAP@50 0,646 berbanding 0,614 untuk A di
  *epoch* 40) dan memberi mAP@50-95 tertinggi, tanda kotaknya paling presisi.

## Ensemble

Dua ensemble NMS kami uji pada *split* valid, lihat
[`ensembles.json`](ensembles.json). Aturan keputusannya kami tetapkan sebelum
melihat hasil: ensemble dipakai hanya bila jumlah kedua metrik naik minimal dua
poin, karena menambah kerumitan reproduksi. Kenaikan terbesar kurang dari satu
poin, sehingga keduanya tidak dipakai.

## Isi folder

Setiap folder kandidat memuat `results.csv` (riwayat per *epoch* dari
Ultralytics), `best.pt.sha256`, dan `evaluation_valid.json` beserta versi
Markdown-nya. Bobot kandidat yang tidak terpilih tidak didistribusikan.
