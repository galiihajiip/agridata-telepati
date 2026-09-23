# Laporan Audit Forensik Dataset Mentah

Dihasilkan oleh `scripts/audit_dataset.py`. Audit ini HANYA MEMBACA: tidak ada berkas dataset mentah yang diubah, diganti nama, atau dihapus untuk menghasilkannya. Pemetaan kelas canonical belum diterapkan pada tahap ini, karena merupakan langkah tersendiri yang datang kemudian.

## Split: `train`

- JSON path: `Telepati 8.0 Datasets/train/_annotations.coco.json`
- Top-level keys: ['info', 'licenses', 'categories', 'images', 'annotations']
- Images: 10133
- Annotations: 20163
- Raw categories: 21

### Raw categories

| id | name | supercategory |
|---:|---|---|
| 0 | Leaf-blight | none |
| 1 | Bacterial panicle Blight | Leaf-blight |
| 2 | False-Smut | Leaf-blight |
| 3 | Healthy Rice Leaf | Leaf-blight |
| 4 | Healthy Rice beads | Leaf-blight |
| 5 | Infected Blast | Leaf-blight |
| 6 | Leaf-roller | Leaf-blight |
| 7 | Rice-Leaf-Diseasee | none |
| 8 | Blast | Rice-Leaf-Diseasee |
| 9 | BrownSpot | Rice-Leaf-Diseasee |
| 10 | Healthy | Rice-Leaf-Diseasee |
| 11 | Leaf Scald | Rice-Leaf-Diseasee |
| 12 | Rice-Tungro | Rice-Leaf-Diseasee |
| 13 | Sheath Blight | Rice-Leaf-Diseasee |
| 14 | paddy | none |
| 15 | Bacterial leaf blight | paddy |
| 16 | Brown spot | paddy |
| 17 | Leaf blast | paddy |
| 18 | Leaf scald | paddy |
| 19 | Narrow brown | paddy |
| 20 | healthy | paddy |

### Temuan integritas

- Kategori tanpa anotasi: 3 -> ['Leaf-blight', 'Rice-Leaf-Diseasee', 'paddy']
- Citra tanpa anotasi: 59
- Anotasi yang merujuk ID citra yang tidak ada (FATAL): 0
- ID anotasi ganda: 0
- Duplicate image IDs: 0
- Invalid bounding boxes (FATAL): 0
- Suspicious bounding boxes (WARNING): 515
- Missing image files referenced by JSON (FATAL): 0
- Corrupt/unreadable images: 0
- Declared-vs-actual dimension mismatches: 0
- Image formats: {'.jpg': 10133}

**Split status: OK (see warnings above)**

## Split: `valid`

- JSON path: `Telepati 8.0 Datasets/valid/_annotations.coco.json`
- Top-level keys: ['info', 'licenses', 'categories', 'images', 'annotations']
- Images: 2106
- Annotations: 4888
- Raw categories: 21

### Raw categories

| id | name | supercategory |
|---:|---|---|
| 0 | Leaf-blight | none |
| 1 | Bacterial panicle Blight | Leaf-blight |
| 2 | False-Smut | Leaf-blight |
| 3 | Healthy Rice Leaf | Leaf-blight |
| 4 | Healthy Rice beads | Leaf-blight |
| 5 | Infected Blast | Leaf-blight |
| 6 | Leaf-roller | Leaf-blight |
| 7 | Rice-Leaf-Diseasee | none |
| 8 | Blast | Rice-Leaf-Diseasee |
| 9 | BrownSpot | Rice-Leaf-Diseasee |
| 10 | Healthy | Rice-Leaf-Diseasee |
| 11 | Leaf Scald | Rice-Leaf-Diseasee |
| 12 | Rice-Tungro | Rice-Leaf-Diseasee |
| 13 | Sheath Blight | Rice-Leaf-Diseasee |
| 14 | paddy | none |
| 15 | Bacterial leaf blight | paddy |
| 16 | Brown spot | paddy |
| 17 | Leaf blast | paddy |
| 18 | Leaf scald | paddy |
| 19 | Narrow brown | paddy |
| 20 | healthy | paddy |

### Temuan integritas

- Kategori tanpa anotasi: 3 -> ['Leaf-blight', 'Rice-Leaf-Diseasee', 'paddy']
- Citra tanpa anotasi: 13
- Anotasi yang merujuk ID citra yang tidak ada (FATAL): 0
- ID anotasi ganda: 0
- Duplicate image IDs: 0
- Invalid bounding boxes (FATAL): 0
- Suspicious bounding boxes (WARNING): 66
- Missing image files referenced by JSON (FATAL): 0
- Corrupt/unreadable images: 0
- Declared-vs-actual dimension mismatches: 0
- Image formats: {'.jpg': 2106}

**Split status: OK (see warnings above)**

## Split: `test`

- JSON path: `Telepati 8.0 Datasets/test/_annotations.coco.json`
- Top-level keys: ['info', 'licenses', 'categories', 'images', 'annotations']
- Images: 1059
- Annotations: 2670
- Raw categories: 21

### Raw categories

| id | name | supercategory |
|---:|---|---|
| 0 | Leaf-blight | none |
| 1 | Bacterial panicle Blight | Leaf-blight |
| 2 | False-Smut | Leaf-blight |
| 3 | Healthy Rice Leaf | Leaf-blight |
| 4 | Healthy Rice beads | Leaf-blight |
| 5 | Infected Blast | Leaf-blight |
| 6 | Leaf-roller | Leaf-blight |
| 7 | Rice-Leaf-Diseasee | none |
| 8 | Blast | Rice-Leaf-Diseasee |
| 9 | BrownSpot | Rice-Leaf-Diseasee |
| 10 | Healthy | Rice-Leaf-Diseasee |
| 11 | Leaf Scald | Rice-Leaf-Diseasee |
| 12 | Rice-Tungro | Rice-Leaf-Diseasee |
| 13 | Sheath Blight | Rice-Leaf-Diseasee |
| 14 | paddy | none |
| 15 | Bacterial leaf blight | paddy |
| 16 | Brown spot | paddy |
| 17 | Leaf blast | paddy |
| 18 | Leaf scald | paddy |
| 19 | Narrow brown | paddy |
| 20 | healthy | paddy |

### Temuan integritas

- Kategori tanpa anotasi: 3 -> ['Leaf-blight', 'Rice-Leaf-Diseasee', 'paddy']
- Citra tanpa anotasi: 5
- Anotasi yang merujuk ID citra yang tidak ada (FATAL): 0
- ID anotasi ganda: 0
- Duplicate image IDs: 0
- Invalid bounding boxes (FATAL): 0
- Suspicious bounding boxes (WARNING): 40
- Missing image files referenced by JSON (FATAL): 0
- Corrupt/unreadable images: 0
- Declared-vs-actual dimension mismatches: 0
- Image formats: {'.jpg': 1059}

**Split status: OK (see warnings above)**

## Cross-split overlap (data leakage check)

- Filename overlap train_vs_valid: 0 shared filenames
- Filename overlap train_vs_test: 0 shared filenames
- Filename overlap valid_vs_test: 0 shared filenames
- Exact content (md5) overlap train_vs_valid: 0 shared files
- Exact content (md5) overlap train_vs_test: 1 shared files
- Exact content (md5) overlap valid_vs_test: 0 shared files
- Perceptual hash (aHash, exact-bucket) overlap train_vs_valid: 426 candidate near-duplicates
- Perceptual hash (aHash, exact-bucket) overlap train_vs_test: 210 candidate near-duplicates
- Perceptual hash (aHash, exact-bucket) overlap valid_vs_test: 84 candidate near-duplicates

Catatan: pemeriksaan tumpang tindih berbasis perceptual hash merupakan pemeriksaan aHash dengan pencocokan bucket persis, bukan pencarian tetangga terdekat berbasis jarak Hamming secara penuh. Setiap kecocokan harus diperlakukan sebagai kandidat yang masih memerlukan konfirmasi visual, bukan sebagai bukti kebocoran.
