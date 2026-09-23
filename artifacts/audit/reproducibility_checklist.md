# Daftar Periksa Reproduktibilitas

## Batas determinisme, baca ini sebelum mempercayai status LULUS di bawah

Prapemrosesan bersifat deterministik dan terverifikasi byte per byte, mencakup penyiapan dataset dan pemetaan canonical.

Pelatihan TIDAK diklaim deterministik bit per bit. PyTorch mencatat peringatan nyata bahwa `scatter_reduce_mps` dan `index_put_with_accumulate_mps` tidak memiliki implementasi deterministik pada backend Apple Silicon dengan MPS yang dipakai project ini. Pelatihan dapat direproduksi pada tingkat *konfigurasi*, yaitu seed, hyperparameter, dan versi kode yang sama, tetapi keluaran numeriknya tidak dijamin identik.

Konfigurasi percobaan dapat direproduksi dan hal ini sudah terverifikasi. Seed, hyperparameter, arsitektur model, dan commit git untuk setiap eksekusi tercatat pada laporan yang ikut dikomit.

## Daftar periksa

| # | Butir | Status | Rincian |
|---:|---|---|---|
| 1 | seed sama menghasilkan manifest dataset yang sama | LULUS | Manifest hasil eksekusi ulang (10132 citra) identik byte per byte dengan manifest yang terkomit. |
| 2 | seed sama menghasilkan pemetaan canonical yang sama | LULUS | Hash tabel pemetaan untuk versi 1.0.0: b88a0260138244fb. build_mapping_report bersifat deterministik, yaitu masukan identik menghasilkan keluaran identik. Bila hash ini berubah tak terduga pada eksekusi ulang, MAPPING_VERSION wajib dinaikkan. |
| 3 | konfigurasi sama menghasilkan metadata yang sama | LULUS | Field deterministik (seed, mapping_version, jumlah citra dan anotasi per split) identical across reruns of the same config; only the recorded timestamp and git commit (if code changed between runs) are expected to vary, these are provenance fields, not outputs of the computation itself. |
| 4 | konfigurasi pelatihan tercatat lengkap | LULUS | Seluruh field konfigurasi pelatihan yang wajib tersedia pada artifacts/reports/block6_baseline_smoke_summary.json. |
| 5 | seed acak tercatat | LULUS | Seed=42 tercatat pada konfigurasi percobaan sekaligus ringkasan eksekusi. |
| 6 | versi dependensi dapat dicatat | LULUS | `pip freeze` menghasilkan 125 paket dengan versi terkunci. |
| 7 | hash commit git tercatat bila memungkinkan | LULUS | Commit saat ini: 4bd79f4d69bceb9a608b2156c3efd9d998dc6c22. |
| 8 | konfigurasi model tercatat | LULUS | Tercatat model_arch=yolov8n.yaml dan pretrained=False. |
| 9 | path data dapat dikonfigurasi | LULUS | Tidak ditemukan path personal yang dipatok keras pada configs/. Skrip yang menyentuh dataset menerima --dataset-root atau --prepared-dir. |
| 10 | artefak hasil generate diversikan melalui metadata, bukan commit berukuran raksasa | LULUS | Direktori besar atau hasil generate sudah masuk gitignore: ['data/prepared', 'runs', '.venv'] |
