# Referensi dan Audit Sitasi

Dokumen ini mencatat setiap sitasi yang dipakai pada notebook final, kalimat
yang didukungnya, dan bukti verifikasi metadatanya. Tujuannya agar sitasi
dapat diperiksa satu per satu, bukan sekadar ditampilkan agar tulisan
terlihat ilmiah.

## Prinsip yang dipakai

1. Sitasi hanya ditambahkan bila pernyataan benar-benar bersumber dari
   literatur atau dokumentasi resmi.
2. Pernyataan yang berasal dari aturan kompetisi tidak diberi sitasi ilmiah,
   karena sumbernya adalah dokumen lomba.
3. Pernyataan yang berasal dari hasil eksekusi pada project ini tidak diberi
   sitasi, karena sumbernya adalah artefak pada repository ini.
4. Seluruh metadata diverifikasi terhadap halaman penerbit atau dokumentasi
   resmi. Tidak ada DOI, volume, atau halaman yang ditulis dari ingatan.
5. Tidak ada sitasi yang dipaksakan untuk pernyataan yang sudah jelas dengan
   sendirinya.

## Sumber ilmiah

| Sitasi | Mendukung pernyataan pada | Status verifikasi |
|---|---|---|
| Mohanty et al. (2016) | Bagian 1: kelayakan pembelajaran mendalam untuk pengenalan penyakit tanaman berbasis citra daun | Terverifikasi pada halaman Frontiers, DOI 10.3389/fpls.2016.01419, volume 7, artikel 1419 |
| Buda et al. (2018) | Bagian 6.4: pengaruh ketidakseimbangan kelas terhadap performa jaringan konvolusional | Terverifikasi pada dblp dan ACM DL, Neural Networks volume 106, halaman 249-259, DOI 10.1016/j.neunet.2018.07.011 |
| Feng et al. (2023) | Bagian 6.5: deteksi objek kecil sebagai persoalan sulit, dengan resolusi fitur masukan sebagai faktor utama | Terverifikasi langsung pada halaman penerbit AIMS Press, MBE volume 20 nomor 4, halaman 6551-6590, DOI 10.3934/mbe.2023282 |
| Loshchilov dan Hutter (2019) | Bagian 12: AdamW sebagai varian Adam dengan weight decay terpisah | Terverifikasi, ICLR 2019, arXiv 1711.05101 |
| Shorten dan Khoshgoftaar (2019) | Bagian 12: augmentasi citra sebagai pendekatan lazim untuk memperluas keragaman data latih | Terverifikasi pada Journal of Big Data, volume 6, artikel 60, DOI 10.1186/s40537-019-0197-0 |
| Lin et al. (2014) | Bagian 14: asal konvensi pengukuran deteksi objek berbasis IoU | Terverifikasi pada Springer, ECCV 2014, LNCS volume 8693, halaman 740-755, DOI 10.1007/978-3-319-10602-1_48 |

## Sumber dokumentasi framework

| Sitasi | Mendukung pernyataan pada | Status verifikasi |
|---|---|---|
| Ultralytics (2026) | Bagian 3: YOLOv8n sebagai varian terkecil pada keluarga YOLOv8 | Terverifikasi langsung pada halaman dokumentasi resmi, yang mencantumkan varian n, s, m, l, x dengan YOLOv8n sebagai varian dengan parameter paling sedikit |
| PyTorch (2026) | Bagian 19: hasil yang sepenuhnya dapat direproduksi tidak dijamin antar rilis dan platform, serta sebagian operasi tidak memiliki implementasi deterministik | Terverifikasi langsung pada halaman dokumentasi resmi Reproducibility |

## Sumber kompetisi

Dokumen guidebook dan regulasi TELEPATI 8.0 merupakan dokumen kompetisi yang
tidak dipublikasikan. Salinan konteks yang dipakai pada pekerjaan ini berada
pada `TELEPATI_8_AgriData_Master_Context.md` di root repository.

Seluruh pernyataan berikut bersumber dari dokumen tersebut dan **tidak**
diberi sitasi ilmiah, karena memang bukan klaim ilmiah:

- larangan penggunaan *external pretrained weights*;
- larangan penggunaan dataset di luar dataset resmi;
- larangan pemrosesan dataset menggunakan LLM atau API;
- penggunaan mAP@0.5 dan F1-Score sebagai metrik penilaian;
- kewajiban mempertahankan pembagian *split* resmi;
- daftar 11 kelas canonical.

## Pernyataan yang sengaja tidak diberi sitasi

Beberapa pernyataan pada notebook sengaja dibiarkan tanpa sitasi karena
merupakan hasil pengamatan pada project ini sendiri, bukan klaim literatur:

- dugaan bahwa manfaat augmentasi baru muncul pada anggaran pelatihan yang
  lebih panjang. Pernyataan ini disajikan sebagai penalaran atas arah tren
  yang teramati pada percobaan E09 sampai E21, dan secara eksplisit ditandai
  sebagai penilaian, bukan kesimpulan berbasis bukti langsung;
- dugaan bahwa nondeterminisme MPS memengaruhi tahap inferensi. Pernyataan
  ini ditandai sebagai indikasi yang belum dibuktikan melalui eksperimen
  terkontrol pada project ini. Dokumentasi PyTorch hanya mendukung fakta umum
  bahwa determinisme tidak dijamin, bukan penjelasan spesifik untuk pola
  variasi F1 yang teramati di sini;
- interpretasi mengenai kemiripan visual antar penyakit tertentu, yang
  didasarkan pada pasangan kelas tertukar hasil analisis kesalahan pada
  project ini.

## Pemeriksaan kelengkapan

- Setiap sitasi dalam teks memiliki entri pada daftar pustaka: **ya**.
- Setiap entri pada daftar pustaka digunakan dalam teks: **ya**.
- Format mengikuti APA 7: **ya**.
- DOI atau URL diverifikasi: **ya**, seluruhnya melalui penelusuran langsung
  ke halaman penerbit atau dokumentasi resmi.
- Tidak ada blog atau sumber non-ilmiah yang dipakai sebagai rujukan
  ilmiah: **ya**.
