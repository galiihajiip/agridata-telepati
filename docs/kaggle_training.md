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

| Kandidat | Config | Arsitektur | Tujuan |
|---|---|---|---|
| A | `configs/kaggle/yolov8s_640_300ep.yaml` | YOLOv8s, 640 | Kapasitas lebih besar dan jadwal pelatihan dari nol yang lazim |
| B | `configs/kaggle/yolov8s_p2_640_250ep.yaml` | YOLOv8s + head P2, 640 | Objek sangat kecil (Brown spot, Blast) |
| C | `configs/kaggle/yolov8s_1024_150ep.yaml` | YOLOv8s, 1024 | Objek kecil lewat resolusi latih lebih tinggi |
| D | `configs/kaggle/yolov8m_640_150ep.yaml` | YOLOv8m, 640 | Kapasitas model lebih besar lagi |

Setiap config dipangkas agar muat dalam satu sesi Kaggle 11 jam.

Hasil, alasan memilih B sebagai model final, dan catatan per kandidat ada di
[`artifacts/candidates/README.md`](../artifacts/candidates/README.md).

## Google Colab

Kandidat C kami jalankan di Google Colab (A100) dengan skrip yang sama. Dataset
diunggah sebagai zip ke Google Drive lalu diekstrak ke disk lokal runtime:

```python
from google.colab import drive
drive.mount('/content/drive')
!mkdir -p /content/agridata-yolo && unzip -q -o /content/drive/MyDrive/agridata-yolo.zip -d /content/agridata-yolo
```

```bash
python scripts/kaggle_train.py --config configs/kaggle/yolov8s_1024_150ep.yaml \
    --data-root /content/agridata-yolo --local-data-dir "" \
    --work-dir /content/drive/MyDrive/agridata_runs --device 0
```

Sesi Colab dapat terputus kapan saja, dan runtime yang di-reset menghapus isi
`/content`. Run C terputus di *epoch* 49 dan tidak kami lanjutkan.

## Catatan kepatuhan pada GPU

Pengecekan AMP bawaan Ultralytics mengunduh bobot pretrained `yolo26n.pt`
setiap kali pelatihan dimulai di GPU CUDA, dan `YOLO_OFFLINE` tidak
mencegahnya. `kaggle_train.py` menambahkan `scripts/kaggle_site/` ke
`PYTHONPATH` setiap proses pelatihan, termasuk proses DDP, sehingga
`sitecustomize.py` di sana mengganti pengecekan tersebut sebelum Ultralytics
memakainya. Log setiap run memuat baris `AMP check dilewati tanpa mengunduh
bobot pretrained; AMP diaktifkan.` sebagai bukti.

Pada mode commit Kaggle, menyalin dataset dari `/kaggle/input` ke disk lokal
memakan 20 sampai 60 menit, dan log tampak diam selama itu.
