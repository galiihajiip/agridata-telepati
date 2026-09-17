# Block 13 — Error Analysis

Weights: `runs/detect/matrix/E08/weights/best.pt` | Split: `valid` | Confidence threshold: 0.1

## Counts

- True positives: 97
- Class confusions (right place, wrong label): 399
- Background false positives (detected something where nothing is): 1843
- False negatives (missed entirely): 4392

## Top confused class pairs (true -> predicted)

| True class | Predicted as | Count |
|---|---|---:|
| Healthy | Leaf roller | 66 |
| Brown spot | Blast | 62 |
| Healthy | Bacterial panicle blight | 42 |
| False smut | Bacterial panicle blight | 38 |
| Blast | Bacterial panicle blight | 34 |
| Sheath blight | Leaf roller | 22 |
| Leaf scald | Blast | 16 |
| Tungro | Blast | 16 |
| Sheath blight | Bacterial panicle blight | 14 |
| Tungro | Bacterial panicle blight | 14 |

## Per-class precision/recall (this analysis's own matching)

| Class | Precision | Recall | TP | FP | FN |
|---|---:|---:|---:|---:|---:|
| Bacterial leaf blight | 0.0000 | 0.0000 | 0 | 0 | 125 |
| Bacterial panicle blight | 0.0174 | 0.2444 | 11 | 622 | 34 |
| Blast | 0.0402 | 0.0433 | 41 | 980 | 906 |
| Brown spot | 0.0000 | 0.0000 | 0 | 0 | 1461 |
| False smut | 0.0000 | 0.0000 | 0 | 0 | 86 |
| Healthy | 0.0000 | 0.0000 | 0 | 0 | 424 |
| Leaf roller | 0.0657 | 0.5172 | 45 | 640 | 42 |
| Leaf scald | 0.0000 | 0.0000 | 0 | 0 | 390 |
| Narrow brown | 0.0000 | 0.0000 | 0 | 0 | 75 |
| Sheath blight | 0.0000 | 0.0000 | 0 | 0 | 488 |
| Tungro | 0.0000 | 0.0000 | 0 | 0 | 760 |

## Confidence: true positives vs. false positives

- True positive confidence: {'mean': 0.25287995333831337, 'median': 0.21372385323047638}
- False positive confidence: {'mean': 0.19266902454975032, 'median': 0.16243627667427063}

## Small-object miss analysis

- Overall median GT bbox area: 7051.6 px²
- False-negative median bbox area: 4710.4 px²
- False negatives skew smaller than average: True

## Crowded vs. sparse scenes

- Crowded-scene (> 1 instances/image) false-negative rate: 0.9734
- Sparse-scene false-negative rate: 0.7094

## Difficult-background candidates (most background FPs)

['BROWNSPOT5_031_jpg.rf.43bd1f683ec8b1b1ca31113cb545bc84.jpg', 'BROWNSPOT3_039_jpg.rf.622da808d37afba4f55b4edbb9ea9311.jpg', 'BLAST4_160_jpg.rf.70a0e9491c83b59b0d0be7e3741a983e.jpg', 'BROWNSPOT5_130_jpg.rf.03ac43297f95c91693f9ec741e32e904.jpg', 'BROWNSPOT2_033_jpg.rf.0529c8dc7a8d38687ac93135eac83be1.jpg']

## Visual examples

- False positives: ['artifacts/figures/error_analysis/bg_fp_id2_IMG-20241012-WA0099_jpg.rf.052715be2fdca8f048e88ae49189c283.jpg', 'artifacts/figures/error_analysis/bg_fp_id4_IMG-20240927-WA0204_jpg.rf.08d9cd91a261a0fac5a9eddf03f8313b.jpg', 'artifacts/figures/error_analysis/bg_fp_id5_IMG-20240926-WA0174_jpg.rf.0877f8b16302ce982b768ca746a3185a.jpg', 'artifacts/figures/error_analysis/bg_fp_id7_20240915_150129_jpg.rf.045091b7ad6b9cc08f3265fce3a6ad3a.jpg']
- False negatives: ['artifacts/figures/error_analysis/fn_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/fn_id2_IMG-20241012-WA0099_jpg.rf.052715be2fdca8f048e88ae49189c283.jpg', 'artifacts/figures/error_analysis/fn_id3_IMG-20240927-WA0215_jpg.rf.02427045292acba0cf19b92c6a42caf2.jpg', 'artifacts/figures/error_analysis/fn_id4_IMG-20240927-WA0204_jpg.rf.08d9cd91a261a0fac5a9eddf03f8313b.jpg']

## IMPORTANT: no changes were applied automatically

This script only analyzes and reports. Any data or model change suggested by these findings (e.g. relabeling, excluding an image, adjusting a class's augmentation) must be a separate, explicitly documented decision — never applied automatically from this analysis, per the master spec.
