# Daftar Periksa Reproduktibilitas

## Batas determinisme, baca ini sebelum mempercayai status LULUS di bawah

Prapemrosesan bersifat deterministik dan terverifikasi byte per byte, mencakup penyiapan dataset dan pemetaan canonical.

Pelatihan TIDAK diklaim deterministik bit per bit. Model final dilatih dengan DDP pada dua GPU CUDA dengan AMP, dan percobaan penyaringan berjalan pada Apple Silicon dengan MPS. PyTorch mencatat peringatan nyata bahwa `scatter_reduce_mps` dan `index_put_with_accumulate_mps` tidak memiliki implementasi deterministik, dan sebagian operasi CUDA pun demikian. Pelatihan dapat direproduksi pada tingkat *konfigurasi*, yaitu seed, hyperparameter, dan versi kode yang sama, tetapi keluaran numeriknya tidak dijamin identik.

Konfigurasi percobaan dapat direproduksi dan hal ini sudah terverifikasi. Seed, hyperparameter, arsitektur model, dan commit git untuk setiap eksekusi tercatat pada laporan yang ikut dikomit.

## Daftar periksa

| # | Butir | Status | Rincian |
|---:|---|---|---|
| 1 | seed sama menghasilkan manifest dataset yang sama | LULUS | Manifest hasil eksekusi ulang (10132 citra) identik byte per byte dengan manifest yang terkomit. |
| 2 | seed sama menghasilkan pemetaan canonical yang sama | LULUS | Hash tabel pemetaan untuk versi 1.0.0: b88a0260138244fb. build_mapping_report bersifat deterministik, yaitu masukan identik menghasilkan keluaran identik. Bila hash ini berubah tak terduga pada eksekusi ulang, MAPPING_VERSION wajib dinaikkan. |
| 3 | konfigurasi sama menghasilkan metadata yang sama | LULUS | Field deterministik (seed, mapping_version, jumlah citra dan anotasi per split) identik antar eksekusi ulang pada konfigurasi yang sama. Yang wajar berbeda hanya timestamp dan commit git, itu pun bila kode berubah di antara dua eksekusi. Keduanya merupakan field provenance, bukan keluaran dari komputasinya sendiri. |
| 4 | konfigurasi pelatihan tercatat lengkap | LULUS | Seluruh field konfigurasi pelatihan final tersedia pada artifacts/reports/block15_final_training_summary.json (configs/kaggle/yolov8s_p2_640_250ep.yaml). |
| 5 | seed acak tercatat | LULUS | Seed=42 tercatat pada config final dan cocok dengan seed di dalam checkpoint. |
| 6 | versi dependensi dapat dicatat | LULUS | `pip freeze` menghasilkan 125 paket dengan versi terkunci. |
| 7 | hash commit git tercatat bila memungkinkan | PERINGATAN | Commit saat ini: b169142419518eee111afc865136c80988a3bd76. PERINGATAN: working tree tidak bersih (109 berkas berubah), sehingga artefak yang dihasilkan sekarang tidak dapat ditelusuri ke commit yang bersih. |
| 8 | konfigurasi model tercatat | LULUS | Tercatat model_arch=yolov8s-p2.yaml dan pretrained=False, cocok dengan checkpoint bobot final. |
| 9 | path data dapat dikonfigurasi | LULUS | Tidak ditemukan path personal yang dipatok keras pada configs/. Skrip yang menyentuh dataset menerima --dataset-root atau --prepared-dir. |
| 10 | artefak hasil generate diversikan melalui metadata, bukan commit berukuran raksasa | LULUS | Direktori besar atau hasil generate sudah masuk gitignore: ['data/prepared', 'runs', '.venv'] |
