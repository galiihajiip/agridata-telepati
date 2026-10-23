# Pelatihan di Kaggle

Pelatihan pada Apple M1 Pro memakan sekitar 9 menit per epoch untuk YOLOv8n,
sehingga model lebih besar dengan jadwal 300 epoch tidak realistis dijalankan
secara lokal. Dokumen ini mencatat cara menjalankannya di GPU Kaggle tanpa
melanggar batasan lomba: model tetap dibangun dari `.yaml` tanpa bobot
pretrained, data hanya dataset resmi, dan split test tidak dipakai untuk
memilih apa pun.

## 1. Siapkan dataset (sekali saja, di Mac)

```bash
python scripts/export_kaggle_dataset.py --out ~/agridata_kaggle_dataset
```

Unggah folder `~/agridata_kaggle_dataset` ke Kaggle sebagai **Dataset
private**, misalnya dengan slug `agridata-yolo`. Dataset lomba tidak boleh
dipublikasikan.

## 2. Sesi pertama

Buat notebook baru: Accelerator **GPU T4 x2**, Internet **On** (hanya untuk
`git clone` dan `pip install`), lalu tambahkan dataset `agridata-yolo` sebagai
input.

```python
!git clone https://github.com/galiihajiip/agridata-telepati.git
%cd agridata-telepati
!pip install -q ultralytics==8.4.154
!python scripts/kaggle_train.py --config configs/kaggle/yolov8s_640_300ep.yaml \
    --data-root /kaggle/input/agridata-yolo
```

Jalankan lewat **Save Version, Save & Run All (Commit)** agar berjalan di
latar belakang dan isi `/kaggle/working` tersimpan sebagai output. Skrip
berhenti sendiri setelah 11 jam, sebelum batas 12 jam Kaggle, dengan
`last.pt` yang masih dapat dilanjutkan.

## 3. Sesi lanjutan

Tambahkan output versi notebook sebelumnya sebagai input (Add Input, Notebook
Output), cek path-nya dengan `!ls /kaggle/input`, lalu:

```python
!python scripts/kaggle_train.py --config configs/kaggle/yolov8s_640_300ep.yaml \
    --data-root /kaggle/input/agridata-yolo \
    --resume-from /kaggle/input/<output-sebelumnya>/runs/yolov8s_640_300ep
```

Ulangi sampai skrip mencetak bahwa pelatihan sudah selesai.

## 4. Evaluasi

Unduh `runs/<nama-run>/weights/best.pt`, lalu evaluasi dengan prosedur yang
sama persis dengan model final:

```bash
python scripts/evaluate.py --weights <best.pt> --split valid --nms-iou 0.5
python scripts/compute_official_metrics.py --split valid
```

Kandidat hanya menggantikan model final bila unggul pada split valid. Split
test dievaluasi satu kali setelah pilihan dibekukan.

## Kandidat

| Config | Arsitektur | Tujuan |
|---|---|---|
| `configs/kaggle/yolov8s_640_300ep.yaml` | YOLOv8s | Kapasitas lebih besar dan jadwal pelatihan dari nol yang lazim |
| `configs/kaggle/yolov8s_p2_640_300ep.yaml` | YOLOv8s + head P2 | Objek sangat kecil (Brown spot, Blast) |
