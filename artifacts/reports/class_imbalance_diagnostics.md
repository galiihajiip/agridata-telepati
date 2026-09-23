# Diagnostik Ketidakseimbangan Kelas

Split: `train` | Total instance: 20163 | Jumlah kelas: 11
Rasio ketidakseimbangan jumlah instance terbanyak terhadap tersedikit: **22.6 kali**

Kelas minoritas, kurang dari 20 persen jumlah kelas terbanyak: **['Bacterial leaf blight', 'Bacterial panicle blight', 'False smut', 'Leaf roller', 'Narrow brown']**
Kelas berobjek kecil atau sulit secara visual, kurang dari 10 persen median luas bbox terbesar: **['Bacterial leaf blight', 'Blast', 'Brown spot', 'Sheath blight', 'Tungro']**

| Kelas | Instance | Citra | Persen total | Median luas bbox (px²) | Minoritas | Objek kecil |
|---|---:|---:|---:|---:|:---:|:---:|
| Brown spot | 5010 | 1122 | 24.85 | 1022.3 |  | YES |
| Blast | 4149 | 1919 | 20.58 | 7477.5 |  | YES |
| Tungro | 2540 | 773 | 12.6 | 12017.5 |  | YES |
| Healthy | 2374 | 2198 | 11.77 | 155844.1 |  |  |
| Sheath blight | 1762 | 629 | 8.74 | 11380.7 |  | YES |
| Leaf scald | 1438 | 837 | 7.13 | 38698.3 |  |  |
| False smut | 852 | 832 | 4.23 | 137300.8 | YES |  |
| Leaf roller | 812 | 803 | 4.03 | 114759.2 | YES |  |
| Bacterial panicle blight | 528 | 519 | 2.62 | 141993.3 | YES |  |
| Bacterial leaf blight | 476 | 234 | 2.36 | 13831.4 | YES | YES |
| Narrow brown | 222 | 222 | 1.1 | 147911.5 | YES |  |
