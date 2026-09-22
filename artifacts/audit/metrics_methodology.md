# Metodologi Pengukuran Metrik dan Koreksinya

Dokumen ini mencatat secara terbuka bahwa cara project ini melaporkan
*F1-Score* pernah salah pilih konvensi, bagaimana hal itu ditemukan, dan
mengapa konvensi baru yang dipakai lebih tepat. Dokumen ini dibuat agar
perubahan angka pada dokumentasi dapat ditelusuri dan tidak terbaca sebagai
penggantian angka secara diam-diam.

## 1. Ringkasan Koreksi

| Metrik | Sebelum koreksi | Setelah koreksi |
|---|---:|---:|
| mAP@0.5 | 0,6277 | 0,6277 (tidak berubah) |
| *F1-Score* | 0,3326 | 0,6181 |

Nilai mAP tidak berubah sama sekali. Yang berubah hanya cara *F1* dihitung.
Model, bobot, dan data tidak disentuh.

## 2. Apa yang Salah

Project ini semula melaporkan *F1* memakai implementasi lokal pada
`src/agridata/metrics/detection.py` dengan sifat berikut:

1. **Rata-rata micro.** Seluruh deteksi dari semua kelas digabung menjadi
   satu kumpulan, lalu *precision* dan *recall* dihitung sekali atas kumpulan
   gabungan itu.
2. **Confidence threshold tetap**, yaitu 0,25, dipilih sebagai nilai bawaan
   dan bukan hasil optimasi.

Kedua pilihan itu sah secara matematis, tetapi **bukan konvensi yang lazim
dipakai untuk melaporkan model deteksi objek**. Konvensi yang lazim, dan yang
dipakai oleh implementasi bawaan Ultralytics maupun tolok ukur COCO, adalah:

1. **Rata-rata macro**, yaitu *F1* dihitung per kelas lebih dulu, baru
   dirata-ratakan antar kelas.
2. **Titik operasi optimal**, yaitu *confidence threshold* yang
   memaksimalkan rata-rata *F1* tersebut.

## 3. Mengapa Selisihnya Sangat Besar

Selisih 0,3326 berbanding 0,6181 bukan kesalahan aritmetika, melainkan
konsekuensi langsung dari karakteristik dataset ini.

Dataset memiliki ketidakseimbangan kelas 22,6 kali pada *split* latih, dan
yang penting: **kelas langka justru berperforma paling baik, sedangkan kelas
paling banyak justru berperforma paling buruk.**

| Kelas | Instance (train) | AP@0.5 |
|---|---:|---:|
| Narrow brown | 222 | 0,9631 |
| False smut | 845 | 0,9436 |
| Brown spot | 5.010 | 0,2909 |

Pada rata-rata micro, Brown spot dengan 5.010 *instance* mendominasi
perhitungan, sehingga nilai gabungan tertarik turun mendekati performa kelas
terburuk. Pada rata-rata macro, setiap kelas diberi bobot sama, sehingga
Narrow brown dan False smut yang sangat baik ikut terhitung penuh.

Ditambah pemilihan *threshold* tetap 0,25 yang ternyata bukan titik optimal,
kedua faktor itu menjelaskan seluruh selisihnya.

## 4. Bagaimana Ditemukan

Kejanggalan terlihat dari ketidakkonsistenan internal pada laporan kita
sendiri. Ultralytics melaporkan *mean precision* 0,6406 dan *mean recall*
0,6237 pada titik operasi terbaiknya. Harmonic mean dari kedua angka itu
adalah 0,6321.

Mustahil sebuah model memiliki *precision* dan *recall* masing-masing sekitar
0,62 tetapi *F1* hanya 0,33, karena *F1* selalu berada di antara keduanya.
Ketidakmungkinan itulah yang memicu penelusuran.

## 5. Angka Mana yang Dipakai dan Mengapa

Tersedia dua kandidat dari perhitungan bawaan Ultralytics:

| Kandidat | Nilai | Keterangan |
|---|---:|---|
| Harmonic mean dari *mean precision* dan *mean recall* | 0,6321 | Kedua komponen diambil pada titik operasi terbaik masing-masing kelas, sehingga sedikit optimistis |
| Maksimum kurva *F1* macro | **0,6181** | Terikat pada satu *confidence threshold* tunggal, yaitu 0,265 |

**Yang dilaporkan adalah 0,6181.** Alasannya bukan karena lebih besar atau
lebih kecil, melainkan karena angka itu terikat pada satu titik operasi
eksplisit yang dapat direproduksi persis oleh juri: jalankan model pada
*confidence* 0,265, maka *F1* macro yang keluar adalah angka itu.

Angka 0,6321 sengaja tidak dipakai meskipun lebih tinggi, karena merupakan
gabungan titik operasi yang berbeda-beda antar kelas sehingga lebih sulit
direproduksi sebagai satu konfigurasi tunggal.

## 6. Status Metrik Lokal yang Lama

Implementasi lokal **tidak dihapus**. Statusnya diturunkan menjadi metrik
diagnostik sekunder, dan tetap berguna untuk dua hal:

1. **Analisis sensitivitas *threshold***, karena dihitung ulang dari prediksi
   tersimpan sehingga bersifat deterministik dan tidak terpengaruh
   nondeterminisme *backend* MPS.
2. **Menunjukkan sisi pesimistis**, yaitu bagaimana performa terlihat bila
   seluruh kelas diperlakukan sebagai satu kumpulan tanpa memandang kelas.

Setiap penyebutan angka lokal pada dokumentasi diberi label eksplisit sebagai
*F1* lokal beserta *threshold*-nya, agar tidak tertukar dengan metrik yang
dilaporkan.

## 7. Temuan Tambahan: Parameter Inferensi

Penelusuran ini juga memicu pengujian parameter inferensi. Bobot model tidak
diubah, dan seluruh pencarian dilakukan pada *split* validasi.

### 7.1 Ambang NMS

| NMS IoU | mAP@0.5 | *F1* macro |
|---:|---:|---:|
| 0,5 | **0,6401** | **0,6383** |
| 0,6 | 0,6380 | 0,6325 |
| 0,7 (bawaan) | 0,6277 | 0,6181 |
| 0,8 | 0,6038 | 0,5795 |

Menurunkan ambang NMS dari 0,7 ke 0,5 menaikkan mAP@0.5 sebesar 0,0124 dan
*F1* sebesar 0,0202. Ini konsisten dengan karakteristik data: objek kecil
yang berdesakan membuat ambang longgar meloloskan terlalu banyak kotak yang
saling tumpang tindih.

### 7.2 Resolusi Inferensi

| Ukuran citra saat inferensi | mAP@0.5 |
|---:|---:|
| 640 (sama dengan resolusi latih) | **0,6277** |
| 960 | 0,4200 |
| 1280 | 0,1164 |

Menaikkan resolusi hanya pada tahap inferensi justru menurunkan performa
secara drastis. Penjelasan yang paling masuk akal: model dilatih dari nol
tanpa bobot pra-latih, sehingga tidak mewarisi ketahanan terhadap perubahan
skala. Fitur yang dipelajari terikat pada skala resolusi latih, dan
ketidakcocokan antara resolusi latih dan inferensi merusak deteksi.

Temuan ini dilaporkan sebagai hasil negatif yang berguna, dan menjadi dasar
keputusan untuk menguji resolusi tinggi **sejak tahap pelatihan**, bukan
menambahkannya saat inferensi.

## 8. Reproduksi

```bash
python scripts/compute_official_metrics.py --split val
python scripts/compute_official_metrics.py --split test
python scripts/tune_inference.py --imgsz 640 --iou 0.5 0.6 0.7 0.8
```
