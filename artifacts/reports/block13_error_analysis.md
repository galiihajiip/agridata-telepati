# Block 13. Error Analysis

Weights: `runs/detect/final/final_model/weights/best.pt` | Split: `valid` | Confidence threshold: 0.1

## Counts

- True positives: 1381
- Class confusions (right place, wrong label): 83
- Background false positives (detected something where nothing is): 1881
- False negatives (missed entirely): 3424

## Top confused class pairs (true -> predicted)

| True class | Predicted as | Count |
|---|---|---:|
| Blast | Bacterial panicle blight | 17 |
| Bacterial panicle blight | Blast | 12 |
| Brown spot | Blast | 11 |
| Leaf roller | Healthy | 5 |
| Blast | Brown spot | 4 |
| Leaf scald | Tungro | 4 |
| Healthy | Blast | 3 |
| Leaf scald | Sheath blight | 3 |
| Bacterial leaf blight | Healthy | 2 |
| Blast | Healthy | 2 |

## Per-class precision/recall (this analysis's own matching)

| Class | Precision | Recall | TP | FP | FN |
|---|---:|---:|---:|---:|---:|
| Bacterial leaf blight | 0.3043 | 0.1680 | 21 | 48 | 104 |
| Bacterial panicle blight | 0.3976 | 0.7333 | 33 | 50 | 12 |
| Blast | 0.4431 | 0.2344 | 222 | 279 | 725 |
| Brown spot | 0.2918 | 0.1697 | 248 | 602 | 1213 |
| False smut | 0.7364 | 0.9419 | 81 | 29 | 5 |
| Healthy | 0.7374 | 0.5165 | 219 | 78 | 205 |
| Leaf roller | 0.5540 | 0.8851 | 77 | 62 | 10 |
| Leaf scald | 0.3381 | 0.2436 | 95 | 186 | 295 |
| Narrow brown | 0.6154 | 0.2133 | 16 | 10 | 59 |
| Sheath blight | 0.3142 | 0.2807 | 137 | 299 | 351 |
| Tungro | 0.4195 | 0.3053 | 232 | 321 | 528 |

## Confidence: true positives vs. false positives

- True positive confidence: {'mean': 0.5284594952207731, 'median': 0.5515046119689941}
- False positive confidence: {'mean': 0.2133797605174865, 'median': 0.16259922087192535}

## Small-object miss analysis

- Overall median GT bbox area: 7051.6 px²
- False-negative median bbox area: 3376.0 px²
- False negatives skew smaller than average: True

## Crowded vs. sparse scenes

- Crowded-scene (> 1 instances/image) false-negative rate: 0.7981
- Sparse-scene false-negative rate: 0.4542

## Difficult-background candidates (most background FPs)

['BROWNSPOT5_095_jpg.rf.fab7517d8aad41ee4be007303ab845b7.jpg', 'brownspot_orig_098_jpg.rf.649a14071152ce62d7e9854c3963113f.jpg', 'brownspot_orig_099_jpg.rf.20a588798794f83ef7c61d6dd58f2dcd.jpg', 'sb_wb_78_jpg.rf.d935e1b711a8cb6b55cc8468eebbfbcc.jpg', 'BROWNSPOT3_198_jpg.rf.e8f570a3f27fd60a33072cae3fe3a677.jpg']

## Visual examples

- False positives: ['artifacts/figures/error_analysis/bg_fp_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/bg_fp_id2_IMG-20241012-WA0099_jpg.rf.052715be2fdca8f048e88ae49189c283.jpg', 'artifacts/figures/error_analysis/bg_fp_id7_20240915_150129_jpg.rf.045091b7ad6b9cc08f3265fce3a6ad3a.jpg', 'artifacts/figures/error_analysis/bg_fp_id11_IMG-20240927-WA0076_jpg.rf.05ae64322751319f09f5888d2c1fe959.jpg']
- False negatives: ['artifacts/figures/error_analysis/fn_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/fn_id25_IMG_20241020_083809_983_jpg.rf.1063f58081fd2d58e91a64f9cda425cc.jpg', 'artifacts/figures/error_analysis/fn_id32_20240915_103047_jpg.rf.115ee268b1b72aca1a9b64ffc32c0447.jpg', 'artifacts/figures/error_analysis/fn_id36_IMG-20240927-WA0178_jpg.rf.175403c448a9cadd98fb1ed023a43ffa.jpg']

## Important caveat before drawing conclusions

This checkpoint has at least one true positive on all 11/11 classes, confusion patterns above reflect genuine model behavior, not simply classes the model has not learned yet.

## Observations

Findings from this specific checkpoint's actual errors (not a generic template):

1. **False negatives skew smaller than the overall GT area distribution** (3376.0 vs. 7051.6 px² median), consistent with the well-known difficulty of small-object detection; this checkpoint already uses the largest image size (640) and full training budget evaluated in this project.
2. **Crowded scenes have a higher false-negative rate** (0.7981 vs. 0.4542 for sparse scenes), small, densely-packed lesions remain the hardest case even at this checkpoint's training scale.
3. These are documented as known limitations of the final submitted model, not a proposal for further experimentation, see the project README's Known Limitations section for the final disclosure.

## IMPORTANT: no changes were applied automatically

This script only analyzes and reports. Any data or model change suggested by these findings (e.g. relabeling, excluding an image, adjusting a class's augmentation) must be a separate, explicitly documented decision, never applied automatically from this analysis, per the master spec.
