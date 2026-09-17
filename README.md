# AgriData Intelligence Race — TELEPATI 8.0

> **AgriTech: Growing The Golden Future**  
> *"Menanam inovasi, memanen keunggulan menuju Indonesia Emas 2045"*

Repository solusi untuk kompetisi **TELEPATI 8.0 — AgriData Intelligence Race** (HIMATEL POLBAN), cabang **AI Model Training & Case Study**.

## 📌 Studi Kasus
Pengembangan model Computer Vision & Object Detection untuk membantu monitoring tanaman pertanian secara otomatis dan mendeteksi berbagai penyakit tanaman padi (*Rice Plant Diseases*) dari citra lahan pertanian.

## 📂 Struktur Repositori
```text
agridata/
├── TELEPATI_8_AgriData_Master_Context.md  # Konteks & regulasi resmi kompetisi
├── Telepati 8.0 Datasets/                           # Dataset citra & anotasi COCO
│   ├── train/                                       # Split data latih & _annotations.coco.json
│   ├── valid/                                       # Split data validasi & _annotations.coco.json
│   └── test/                                        # Split data uji & _annotations.coco.json
├── scripts/                                         # Script otomatisasi & utility
│   ├── auto_commit_daemon.py                        # Watcher auto-commit & push
│   └── auto_commit.sh                               # CLI runner auto-commit
└── README.md
```

## 🚀 Setup & Otomatisasi Git
Otomatisasi auto-commit daemon berjalan di background untuk memantau perubahan file dan melakukan commit & push otomatis dengan pesan semantic:
```bash
./scripts/auto_commit.sh status   # Cek status daemon
./scripts/auto_commit.sh logs     # Pantau log aktivitas commit & push
./scripts/auto_commit.sh stop     # Hentikan daemon
./scripts/auto_commit.sh start    # Jalankan kembali daemon
```

## 👨‍💻 Kontributor
- **Galih Aji Pangestu** ([@galiihajiip](https://github.com/galiihajiip))
