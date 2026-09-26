# Evaluasi Model 50 Epoch dengan Ambang NMS 0,5

Berkas di direktori ini merupakan evaluasi final model 50 *epoch*, yaitu model
yang sebelumnya dibekukan untuk submission sebelum digantikan model 100
*epoch*. Angka inilah yang dulu dilaporkan pada README dan notebook:

| Metrik | Valid | Test |
|---|---:|---:|
| mAP@0.5 | 0,6401 | 0,6246 |
| *F1-Score* macro | 0,6383 | 0,6272 |

Berkas pada direktori induk (`../evaluation_valid.json` dan
`../evaluation_test.json`) merupakan evaluasi model yang sama tetapi dari versi
lebih awal, yaitu sebelum ambang NMS disetel ke 0,5 dan sebelum *F1* macro
dihitung. Karena itu angkanya berbeda (0,6277 dan 0,6145) dan kolom *F1*-nya
bernilai nol. Keduanya kami simpan agar riwayat pengukurannya utuh.

Pembeda seluruh nilai metrik historis ada pada
[`../../../audit/metrics_provenance.md`](../../../audit/metrics_provenance.md).
