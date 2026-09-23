# Pemilihan Konfigurasi Model Final

Laporan ini meninjau seluruh 21 percobaan yang tercatat (E01 sampai E21). Yang dipilih dan dibekukan di sini adalah KONFIGURASI untuk pelatihan skala penuh; laporan ini sendiri tidak menghasilkan bobot final yang disubmit.

## Seluruh percobaan kandidat, diurutkan menurut mAP@0.5

| Percobaan | imgsz | epoch | optimizer | mAP@0.5 | Precision | Recall | Durasi (detik) | Catatan |
|---|---:|---:|---|---:|---:|---:|---:|---|
| E21 | 640 | 12 | AdamW | 0.0247 | 0.1403 | 0.0552 | 659 | Block 11 augmentation ablation: combined_no_aug. Block 14 confirmation |
| E20 | 640 | 12 | AdamW | 0.0234 | 0.1344 | 0.0622 | 671 | Block 11 augmentation ablation: combined_default_aug. Block 14 confirm |
| E09 | 320 | 5 | AdamW | 0.0200 | 0.3004 | 0.0305 | 152 | Block 11 augmentation ablation: none. Reference point: all augmentatio |
| E17 | 320 | 5 | AdamW | 0.0140 | 0.3867 | 0.0167 | 114 | Block 11 augmentation ablation: mosaic (not in the master spec's candi |
| E08 | 320 | 10 | AdamW | 0.0134 | 0.2921 | 0.0406 | 208 | OFAT variant: training_duration changed from baseline; all else held f |
| E11 | 320 | 5 | AdamW | 0.0130 | 0.3860 | 0.0221 | 135 | Block 11 augmentation ablation: vertical_flip. QUESTIONABLE — rice pla |
| E15 | 320 | 5 | AdamW | 0.0110 | 0.1929 | 0.0385 | 131 | Block 11 augmentation ablation: brightness_contrast. PLAUSIBLE — outdo |
| E10 | 320 | 5 | AdamW | 0.0095 | 0.2853 | 0.0361 | 145 | Block 11 augmentation ablation: horizontal_flip. PLAUSIBLE — a leaf/pl |
| E14 | 320 | 5 | AdamW | 0.0091 | 0.2966 | 0.0219 | 136 | Block 11 augmentation ablation: translation. PLAUSIBLE — subject frami |
| E12 | 320 | 5 | AdamW | 0.0091 | 0.2892 | 0.0183 | 149 | Block 11 augmentation ablation: rotation. PLAUSIBLE in moderation — si |
| E16 | 320 | 5 | AdamW | 0.0081 | 0.1988 | 0.0256 | 132 | Block 11 augmentation ablation: color_transform. PLAUSIBLE but bounded |
| E18 | 320 | 5 | AdamW | 0.0071 | 0.1143 | 0.0550 | 135 | Block 12 class-imbalance ablation: baseline, natural class distributio |
| E13 | 320 | 5 | AdamW | 0.0064 | 0.1932 | 0.0495 | 129 | Block 11 augmentation ablation: scaling. PLAUSIBLE — camera-to-subject |
| E03 | 640 | 5 | AdamW | 0.0041 | 0.3724 | 0.0052 | 302 | OFAT variant: image_size changed from baseline; all else held fixed. |
| E02 | 320 | 5 | AdamW | 0.0018 | 0.1840 | 0.0073 | 146 | Block 10 baseline (OFAT reference point). |
| E07 | 320 | 5 | AdamW | 0.0007 | 0.2759 | 0.0061 | 134 | OFAT variant: augmentation_strength changed from baseline; all else he |
| E19 | 320 | 5 | AdamW | 0.0005 | 0.1825 | 0.0111 | 120 | Block 12 class-imbalance ablation: rare classes ['Bacterial leaf bligh |
| E04 | 320 | 5 | AdamW | 0.0005 | 0.0004 | 0.0828 | 119 | OFAT variant: batch_size changed from baseline; all else held fixed. |
| E06 | 320 | 5 | SGD | 0.0003 | 0.0961 | 0.0003 | 128 | OFAT variant: optimizer changed from baseline; all else held fixed. |
| E05 | 320 | 5 | AdamW | 0.0002 | 0.1820 | 0.0814 | 131 | OFAT variant: learning_rate changed from baseline; all else held fixed |
| E01 | 320 | 2 | AdamW | 0.0000 | 0.0000 | 0.0000 | 127 | Block 6 smoke test: 2 epochs, 5% of train, imgsz=320. Proves pipeline  |

## Konfigurasi terpilih: lihat `configs/final_model_config.yaml`

Hasil penyaringan individual terbaik adalah **E21** (mAP@0.5=0.0247). Konfigurasi final yang dibekukan tidak sekadar menyalin pengaturan percobaan tersebut apa adanya, melainkan merangkum bukti dari seluruh 21 percobaan. Alasan untuk setiap hyperparameter tercantum sebagai komentar di dalam berkas konfigurasi, dan dilengkapi penalaran kelayakan semantik dari ablasi augmentasi serta bukti independen dari analisis kesalahan.

## Daftar periksa kepatuhan, berbasis bukti dan bukan sekadar pernyataan

| # | Butir | Status | Bukti |
|---:|---|---|---|
| 1 | Tanpa external pretrained weights | LULUS | Model selalu dibangun dari yolov8n.yaml yang hanya memuat arsitektur. build_compliant_model() melempar galat bila diberi pretrained=True atau berkas .pt/.pth/.ckpt. YOLO_OFFLINE ditegakkan pada seluruh skrip pelatihan dan evaluasi. Verifikasi cache checkpoint kosong dijalankan dengan membandingkan isi direktori sebelum dan sesudah pelatihan; tidak ada berkas .pt yang muncul di luar keluaran runs/ milik project ini sendiri. |
| 2 | Tanpa kebocoran data | SEBAGIAN, satu kasus terkonfirmasi sudah ditangani, risiko sisa didokumentasikan | Audit forensik menemukan tepat satu citra duplikat persis (identik menurut MD5) antara split train dan test ('leaf_scald-230...'), dan entri tersebut dikeluarkan dari manifest latih. Kandidat kemiripan berbasis perceptual hash belum dikonfirmasi satu per satu dan tidak ditelusuri lebih jauh; hal ini dicatat sebagai risiko sisa yang terdokumentasi, bukan diabaikan diam-diam. |
| 3 | Memakai 11 kelas canonical resmi | LULUS | Pemetaan canonical divalidasi terhadap dataset aktual tanpa menyisakan satu pun kategori mentah yang tidak terpetakan (versi pemetaan 1.0.0). Berkas data.yaml selalu mendeklarasikan tepat 11 kelas dalam urutan canonical: ['Bacterial leaf blight', 'Bacterial panicle blight', 'Blast', 'Brown spot', 'False smut', 'Healthy', 'Leaf roller', 'Leaf scald', 'Narrow brown', 'Sheath blight', 'Tungro']. |
| 4 | Prapemrosesan yang dapat direproduksi | LULUS | Menjalankan ulang scripts/prepare_dataset.py dengan seed yang sama menghasilkan manifest 10.132 citra yang identik byte per byte. Hal ini diverifikasi melalui eksekusi ulang dan pembandingan langsung, bukan diasumsikan. |
| 5 | Konfigurasi yang dapat direproduksi | LULUS | Pelacak percobaan mencatat seed, commit Git, dan hyperparameter untuk seluruh 21 percobaan yang tercatat. Konfigurasi beku pada laporan ini (configs/final_model_config.yaml) sendiri berada di bawah kendali versi. |
| 6 | Checkpoint yang valid | LULUS untuk checkpoint penyaringan, MENUNGGU untuk bobot final | Seluruh 21 percobaan penyaringan menghasilkan best.pt yang dapat dimuat, diverifikasi dengan memuat ulang secara segar pada proses evaluasi dan analisis kesalahan. Checkpoint final untuk submission belum ada pada tahap ini dan harus diverifikasi ulang setelah pelatihan skala penuh selesai. |
| 7 | Inferensi berhasil dijalankan | LULUS | Uji inferensi mandiri dijalankan pada checkpoint yang baru dimuat di dalam proses bersih. Selain itu evaluate.py dan run_error_analysis.py keduanya berhasil menjalankan inferensi pada checkpoint penyaringan di seluruh split validasi (2.106 citra). |
| 8 | Performa validasi yang memadai | MENUNGGU, BELUM TERPENUHI, dan sengaja tidak diklaim | Hasil penyaringan terbaik sejauh ini: E21 dengan mAP@0.5=0.0247, dilatih hanya pada sekitar 10 persen data latih selama 12 epoch. Angka ini berskala penyaringan, bukan hasil yang kompetitif, dan tidak disajikan sebagai hasil kompetitif. Pelatihan skala penuh (fraction=1.0, epochs=50, patience=15) diperlukan sebelum butir ini dapat dinilai secara jujur. |

## Risiko yang diketahui

- Kandidat tumpang tindih berbasis perceptual hash yang tersisa dari audit dataset (train terhadap valid: 426, train terhadap test: 210, valid terhadap test: 84) tidak pernah dikonfirmasi satu per satu secara visual, sehingga belum diketahui mana yang benar-benar duplikat dan mana yang merupakan false positive dari aHash 8x8 yang kasar. Hanya satu duplikat persis menurut MD5 yang ditindaklanjuti.
- Seluruh 21 percobaan penyaringan memakai sebagian kecil data latih (8 sampai 10 persen) dan sedikit epoch (5 sampai 12). Angka skala penuh pada konfigurasi beku (epochs=50, fraction=1.0) merupakan ekstrapolasi, bukan hasil pengukuran langsung. Perilaku skala penuh yang sebenarnya baru teramati pada pelatihan final.
- Backend MPS terbukti memiliki kernel yang tidak deterministik untuk `scatter_reduce_mps` dan `index_put_with_accumulate_mps`. Karena itu reproduksi pelatihan bit per bit tidak dijamin; yang dijamin hanya reproduksi konfigurasi dan prapemrosesan.
- Perkiraan waktu pelatihan skala penuh sekitar 8,2 jam pada perangkat yang dipakai project ini tergolong lama. Nilai `patience=15` berpotensi memperpendeknya, tetapi perkiraan ini harus diverifikasi ulang saat pelatihan final dijalankan.

Commit Git pada saat pemilihan: `50f89b1d370004cb884cdc09e4a0ae0037500979`
