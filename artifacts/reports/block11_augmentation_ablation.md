# Ablasi Augmentasi

Skalanya sama dengan matriks percobaan, yaitu fraksi data kecil dengan sedikit *epoch*, agar langsung sebanding. Nilai mAP absolutnya rendah, dan yang bermakna di sini hanya efek relatifnya.

Sebagai pembanding, E02 pada matriks percobaan yang memakai paket augmentasi gabungan bawaan Ultralytics memperoleh mAP@0.5=0.0018. Ablasi ini justru mengisolasi setiap faktor satu per satu bertolak dari referensi bersih tanpa augmentasi, yaitu E09.

## Hasil

| Percobaan | Augmentasi | Kelayakan | mAP@0.5 | Precision | Recall | Durasi (detik) |
|---|---|---|---:|---:|---:|---:|
| E09 | none | Titik referensi dengan seluruh augmentasi dimatikan. | 0.0200 | 0.3004 | 0.0305 | 151.8 |
| E10 | horizontal_flip | MASUK AKAL | 0.0095 | 0.2853 | 0.0361 | 144.7 |
| E11 | vertical_flip | DIRAGUKAN | 0.0130 | 0.3860 | 0.0221 | 135.1 |
| E12 | rotation | MASUK AKAL bila dibatasi | 0.0091 | 0.2892 | 0.0183 | 148.5 |
| E13 | scaling | MASUK AKAL | 0.0064 | 0.1932 | 0.0495 | 129.4 |
| E14 | translation | MASUK AKAL | 0.0091 | 0.2966 | 0.0219 | 135.6 |
| E15 | brightness_contrast | MASUK AKAL | 0.0110 | 0.1929 | 0.0385 | 131.2 |
| E16 | color_transform | MASUK AKAL tetapi sengaja dibatasi. Pergeseran hue dijaga kecil (1,5 persen) karena warna lesi merupakan ciri diagnostik yang nyata bagi beberapa kelas canonical | 0.0081 | 0.1988 | 0.0256 | 132.2 |
| E17 | mosaic (tidak termasuk daftar kandidat awal, tetapi aktif secara bawaan pada Ultralytics; disertakan demi kelengkapan karena diam-diam memengaruhi seluruh percobaan matriks) | DIRAGUKAN untuk domain ini | 0.0140 | 0.3867 | 0.0167 | 113.9 |

## Efek tiap augmentasi, relatif terhadap referensi tanpa augmentasi

- **horizontal_flip**: mAP@0.5 turun sebesar -0.0105 terhadap referensi tanpa augmentasi.
- **vertical_flip**: mAP@0.5 turun sebesar -0.0070 terhadap referensi tanpa augmentasi.
- **rotation**: mAP@0.5 turun sebesar -0.0109 terhadap referensi tanpa augmentasi.
- **scaling**: mAP@0.5 turun sebesar -0.0136 terhadap referensi tanpa augmentasi.
- **translation**: mAP@0.5 turun sebesar -0.0109 terhadap referensi tanpa augmentasi.
- **brightness_contrast**: mAP@0.5 turun sebesar -0.0090 terhadap referensi tanpa augmentasi.
- **color_transform**: mAP@0.5 turun sebesar -0.0119 terhadap referensi tanpa augmentasi.
- **mosaic (tidak termasuk daftar kandidat awal, tetapi aktif secara bawaan pada Ultralytics; disertakan demi kelengkapan karena diam-diam memengaruhi seluruh percobaan matriks)**: mAP@0.5 turun sebesar -0.0060 terhadap referensi tanpa augmentasi.

## Kandidat yang tidak diuji secara empiris: blur dan derau ringan

Pemeriksaan kode sumber `ultralytics/data/augment.py` pada kelas
`Albumentations` menunjukkan transformasi bawaan beserta probabilitasnya
yang akan diterapkan Ultralytics bila paket opsional `albumentations`
terpasang:

    A.Blur(p=0.01), A.MedianBlur(p=0.01), A.ToGray(p=0.01), A.CLAHE(p=0.01),
    A.RandomBrightnessContrast(p=0.0), A.RandomGamma(p=0.0), A.ImageCompression(p=0.0)

Paket `albumentations` TIDAK terpasang pada project ini, sehingga tidak ada
satu pun transformasi di atas yang aktif. Hal ini dikonfirmasi, bukan
diasumsikan, melalui `pip show albumentations` yang tidak menemukan apa pun.

Penilaian kami atas ketiganya:

- **Blur dan MedianBlur, masing-masing p=0,01.** MASUK AKAL, karena blur
  ringan akibat fokus atau gerakan lazim terjadi pada fotografi lapangan.
  Namun pada probabilitas 1 persen, terhadap sekitar 800 citra latih
  dikali 5 epoch atau kurang lebih 4.000 tampilan citra, hanya sekitar 80
  tampilan yang akan menerima salah satu transformasi tersebut. Terlalu
  jarang untuk menghasilkan perbedaan mAP yang terukur pada skala
  penyaringan ini, sehingga eksekusi empirisnya akan lebih banyak mengukur
  derau daripada efek transformasinya.
- **ToGray, p=0,01.** DIRAGUKAN khusus untuk domain ini, karena warna lesi
  merupakan ciri diagnostik yang nyata bagi beberapa kelas canonical,
  misalnya Brown spot terhadap Blast. Mengubah citra menjadi skala abu-abu
  justru menghapus sinyal yang sengaja dijaga oleh varian `color_only` di
  atas melalui pembatasan pergeseran hue.
- **CLAHE, p=0,01.** MASUK AKAL, karena penguatan kontras adaptif membantu
  menghadapi variasi pencahayaan, dengan penalaran serupa varian
  `brightness_only`.

**Keputusan:** `albumentations` tidak ditambahkan sebagai dependensi project
pada tahap ini. Efeknya nyata tetapi terlalu jarang muncul pada probabilitas
1 persen untuk membenarkan penambahan dependensi baru sekaligus percobaan
langsung yang hasilnya akan didominasi derau penyampelan pada skala ini.
Keputusan ini dapat ditinjau ulang pada analisis kesalahan bila kepekaan
terhadap blur ternyata merupakan mode kegagalan yang nyata.

## Rekomendasi

Pemilihan augmentasi harus menimbang *kelayakan semantik untuk domain ini*, bukan semata angka mentah pada skala penyaringan yang kecil. Secara konkret:

- Direkomendasikan **dipertahankan**: pembalikan horizontal, rotasi sedang, penskalaan, translasi, kecerahan dan kontras, serta pergeseran warna yang konservatif. Seluruhnya masuk akal secara fisik untuk citra padi hasil tangkapan lapangan, terlepas dari kecilnya efek individual pada skala penyaringan ini.
- Direkomendasikan **dikeluarkan**: pembalikan vertikal. Sekalipun terukur berefek positif di atas, transformasi itu tidak masuk akal secara fisik untuk tanaman yang orientasinya ditentukan gravitasi, dan berisiko mengajarkan model orientasi yang tidak akan pernah ditemuinya saat dipakai. Penalaran domain mengungguli perolehan metrik yang marginal.
- **Mosaic**: dipertahankan hanya bila efek terukurnya di atas netral sampai positif. Bila jelas merugikan pada skala ini, sebaiknya diuji ulang pada skala pelatihan penuh sebelum diputuskan, karena manfaat mosaic umumnya baru terlihat dengan data dan *epoch* yang lebih banyak daripada tahap penyaringan ini.
- Blur dan derau ringan: sengaja tidak diadopsi pada tahap ini, lihat analisis di atas.

Ini merupakan rekomendasi berskala penyaringan yang dibawa ke ablasi ketidakseimbangan kelas dan pembekuan konfigurasi final, bukan keputusan final yang berdiri sendiri.
