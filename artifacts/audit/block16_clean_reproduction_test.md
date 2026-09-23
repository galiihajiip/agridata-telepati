# Uji Reproduksi pada Lingkungan Bersih

Pengujian ini menyimulasikan apa yang akan dialami mesin juri, yaitu
*virtual environment* Python 3.11 yang benar-benar baru, terpisah dari
`.venv` kerja project ini, dengan dependensi dipasang semata dari
`requirements.txt` tanpa bergantung pada kondisi lingkungan yang menumpuk
selama pengembangan.

## Metode

1. Audit statis seluruh berkas sumber yang terlacak, tanpa eksekusi
   dinamis, untuk mencari *path* personal yang dipatok keras, dependensi
   tersembunyi yang tidak dideklarasikan, dan *secret*.
2. Membuat `/tmp/audit_venv` dari nol, memasang paket hanya dari
   `requirements.txt`.
3. Menjalankan seluruh rangkaian pengujian pytest di lingkungan tersebut.
4. Memuat *checkpoint* model final
   (`runs/detect/final/final_model/weights/best.pt`) lalu menjalankan
   inferensi di lingkungan bersih itu.
5. Menjalankan `scripts/prepare_dataset.py` terhadap dataset mentah yang
   sesungguhnya dari lingkungan bersih, lalu membandingkan hasilnya dengan
   *manifest* yang sudah ada.
6. Menjalankan `scripts/evaluate.py`, mencakup *native val* dan *F1* lokal
   secara penuh, terhadap model final di lingkungan bersih.

## Pemeriksaan statis

| Pemeriksaan | Hasil |
|---|---|
| *Path* absolut personal pada kode terlacak | Tidak ditemukan. Satu kemunculan tidak berbahaya berada pada teks bukti di laporan audit hasil generate, bukan pada kode |
| *API key* dan *secret* | Tidak ditemukan. Satu kemunculan tidak berbahaya berupa komentar bagian pada `.gitignore` |
| Dependensi tersembunyi atau tidak dideklarasikan | Tidak ada. Setiap *import* pihak ketiga pada `src/`, `scripts/`, dan `tests/` sudah dideklarasikan pada `requirements.txt` |
| Ketergantungan jaringan eksternal | Tidak ada. `YOLO_OFFLINE=1` ditegakkan di seluruh alur, dan sudah diverifikasi bahwa setiap upaya pengunduhan berubah menjadi `ConnectionError` yang gagal secara keras |

## Temuan, perbaikan, dan verifikasi ulang

### Temuan 1 (KRITIS): pemasangan segar `pip install -r requirements.txt` langsung gagal

Pemasangan sekali jalan, persis seperti yang akan dilakukan juri mengikuti
petunjuk README, gagal dengan `ResolutionImpossible`.

Akar masalahnya, `ultralytics==8.4.154` secara eksplisit mengecualikan
`numpy` versi 2.0.x sampai 2.3.4 pada macOS, sedangkan `requirements.txt`
mematok `numpy==2.1.3`. Patokan itu ditetapkan pada tahap paling awal
project, sebelum ultralytics masuk ke dalam dependensi.

`.venv` project ini sendiri tidak pernah memunculkan konflik tersebut
karena pip tidak menyelesaikan ulang paket yang sudah terpasang pada
pemasangan inkremental. Hanya resolusi segar sekali jalan yang menangkapnya.

**Perbaikan:** patokan usang dihapus, pip dibiarkan memilih versi yang
kompatibel (`numpy==2.4.6`), lalu versi itu dipatok ulang secara eksak pada
`requirements.txt` demi reproduktibilitas. Diverifikasi ulang: pemasangan
segar berhasil, dan seluruh rangkaian pytest (59 dari 59) lulus di
lingkungan bersih.

### Temuan 2 (KRITIS): `evaluate.py` gagal pada split valid penuh di lingkungan bersih

`scripts/evaluate.py` menjalankan `model.val()` lalu memakai ulang objek
model yang sama untuk tahap pengumpulan prediksi *F1* lokal. Di lingkungan
bersih dengan numpy 2.4.6, tahap itu gagal dengan
`RuntimeError: MPSGraph does not support tensor dims larger than INT_MAX`.

Seluruh temuan penelusuran berikut diverifikasi melalui reproduksi langsung
yang terisolasi, bukan diasumsikan:

- Memuat ulang objek model yang segar di antara `val()` dan `predict()`
  tidak menyelesaikan masalah.
- Memanggil `torch.mps.empty_cache()` dan `gc.collect()` di antara kedua
  pemanggilan juga tidak menyelesaikannya.
- Subproses yang benar-benar baru, hanya menjalankan
  `predict(..., stream=True)` tanpa `val()` sama sekali sebelumnya, tetap
  gagal pada daftar 2.106 citra. Ini menggugurkan sepenuhnya hipotesis
  bahwa masalahnya terletak pada urutan `val()` lalu `predict()`.
- Pencarian biner menetapkan batasnya: daftar 50, 200, 500, dan 1.000
  *path* dalam satu pemanggilan `predict()` seluruhnya berhasil, sedangkan
  daftar penuh 2.106 *path* gagal pada item pertama, bahkan sebelum
  inferensi sungguhan berjalan.
- Ini merupakan regresi yang dibawa oleh perbaikan numpy pada Temuan 1.
  Jalur kode yang sama persis berhasil dijalankan pada tahap evaluasi dan
  analisis kesalahan sebelumnya terhadap split 2.106 citra yang sama, di
  bawah numpy 2.1.3.

**Perbaikan:** daftar *path* dipecah menjadi potongan berisi 500 sebelum
memanggil `model.predict(..., stream=True)`, lalu hasilnya digabungkan di
Python (`scripts/evaluate.py::collect_predictions`, dengan pola yang sama
diterapkan pada `scripts/run_error_analysis.py::collect_predictions` yang
memiliki pola pemanggilan identik). Diverifikasi: pemecahan potongan
memproses seluruh 2.106 citra dengan berhasil.

Akar masalah di sisi hulu, yang kemungkinan merupakan interaksi antara
numpy 2.4.x dan torch MPS khusus untuk daftar *path* eksplisit yang sangat
panjang, tidak berhasil diisolasi sepenuhnya dalam cakupan pengujian ini.
Karena itu perbaikan di atas dinyatakan sebagai solusi sementara yang sudah
terverifikasi benar dan kokoh, bukan sebagai perbaikan akar masalah.

**Arsitektur evaluate.py juga dirombak** sekalian saat memperbaiki ini.
Tahap `val()` bawaan dan tahap `predict()` untuk *F1* lokal kini berjalan
pada subproses yang benar-benar terpisah, bukan sekadar objek model yang
berbeda. Isolasi pada tingkat proses merupakan satu-satunya mekanisme yang
terbukti andal menghindari sisa persoalan kondisi MPS di antara kedua
tahap, terlepas dari apa pun akar masalahnya.

### Verifikasi ulang: pipeline penuh, lingkungan bersih, model final sesungguhnya

| Langkah | Hasil |
|---|---|
| Pemasangan segar `pip install -r requirements.txt` | LULUS |
| Seluruh rangkaian pytest (59 pengujian) | LULUS |
| Memuat `runs/detect/final/final_model/weights/best.pt` | LULUS |
| Inferensi pada satu citra contoh | LULUS |
| `scripts/prepare_dataset.py` terhadap dataset mentah sesungguhnya | LULUS, jumlahnya identik dengan *manifest* yang sudah ada: 10.132 citra latih, 1 pengecualian akibat kebocoran, 2.106 valid, 1.059 test |
| `scripts/evaluate.py --split valid`, native val dan *F1* lokal, 2.106 citra penuh | LULUS, mAP@0.5=0,5620 dan mAP@0.5:0.95=0,3278, sama persis dengan hasil saat pelatihan |

> Catatan: angka mAP pada tabel di atas berasal dari model 20 *epoch* yang
> berlaku saat pengujian ini dijalankan. Model final yang disubmit adalah
> model 50 *epoch* dengan mAP@0.5 sebesar 0,6401 pada split valid. Seluruh
> nilai metrik historis dibedakan pada `metrics_provenance.md`.

## Pengamatan yang bukan cacat, tetapi layak dicatat

Beberapa kelas, yaitu Leaf roller, False smut, dan Bacterial panicle blight,
menunjukkan AP@0.5 yang kuat (0,78, 0,90, dan 0,47) tetapi *F1* lokal yang
nyaris nol pada *confidence threshold* 0,25.

Ini wajar dan bukan cacat. AP mengintegrasikan *precision* dan *recall* pada
seluruh *confidence threshold*, sedangkan *F1* lokal memakai satu ambang
tetap. Artinya model memang menghasilkan deteksi yang benar untuk kelas
tersebut, hanya saja pada skor keyakinan di bawah 0,25. Hal ini penting
diketahui saat mendokumentasikan pilihan *confidence threshold* pada README,
bukan sesuatu yang perlu diperbaiki di sini.

## Berkas yang berubah sebagai akibat langsung pengujian ini

- `requirements.txt`, numpy dipatok ulang ke versi yang kompatibel dengan
  batasan ultralytics pada macOS.
- `scripts/evaluate.py`, arsitektur dua tahap yang terisolasi pada tingkat
  proses, ditambah pengumpulan prediksi yang dipecah menjadi potongan.
- `scripts/run_error_analysis.py`, pengumpulan prediksi yang dipecah menjadi
  potongan.
- `artifacts/reports/evaluation_valid.json` dan `.md`, disegarkan dengan
  hasil evaluasi nyata model final, menggantikan angka uji asap yang sudah
  usang, karena inilah eksekusi `evaluate.py` penuh yang pertama terhadap
  model final.

## Kesimpulan

Dua cacat reproduktibilitas yang nyata dan sebelumnya tidak terdeteksi
berhasil ditemukan dan diperbaiki, masing-masing diverifikasi ulang di
lingkungan bersih sebelum dianggap selesai.

Keduanya akan membuat audit juri gagal, satu pada tahap penyiapan
lingkungan dan satu lagi pada tahap evaluasi. Justru kategori kegagalan
itulah yang menjadi alasan pengujian ini ada, yaitu menangkapnya sebelum
submission. Tidak ada galat yang dilewati diam-diam; setiap galat ditelusuri
sampai akar masalah yang terverifikasi atau solusi sementara yang
terverifikasi sebelum dilanjutkan.
