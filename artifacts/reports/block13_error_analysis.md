# Block 13 — Error Analysis

Weights: `runs/detect/final/final_model/weights/best.pt` | Split: `valid` | Confidence threshold: 0.1

## Counts

- True positives: 1441
- Class confusions (right place, wrong label): 79
- Background false positives (detected something where nothing is): 2325
- False negatives (missed entirely): 3368

## Top confused class pairs (true -> predicted)

| True class | Predicted as | Count |
|---|---|---:|
| Blast | Brown spot | 17 |
| Brown spot | Blast | 15 |
| Leaf scald | Tungro | 8 |
| Blast | Sheath blight | 4 |
| Healthy | Brown spot | 4 |
| Blast | Narrow brown | 3 |
| Leaf scald | Sheath blight | 3 |
| Bacterial leaf blight | Blast | 2 |
| Bacterial leaf blight | Healthy | 2 |
| Bacterial leaf blight | Tungro | 2 |

## Per-class precision/recall (this analysis's own matching)

| Class | Precision | Recall | TP | FP | FN |
|---|---:|---:|---:|---:|---:|
| Bacterial leaf blight | 0.3231 | 0.5920 | 74 | 155 | 51 |
| Bacterial panicle blight | 0.0000 | 0.0000 | 0 | 0 | 45 |
| Blast | 0.4211 | 0.2872 | 272 | 374 | 675 |
| Brown spot | 0.3000 | 0.2115 | 309 | 721 | 1152 |
| False smut | 0.5000 | 0.0116 | 1 | 1 | 85 |
| Healthy | 0.7545 | 0.3986 | 169 | 55 | 255 |
| Leaf roller | 0.0000 | 0.0000 | 0 | 17 | 87 |
| Leaf scald | 0.2857 | 0.3282 | 128 | 320 | 262 |
| Narrow brown | 0.5448 | 0.9733 | 73 | 61 | 2 |
| Sheath blight | 0.3153 | 0.2992 | 146 | 317 | 342 |
| Tungro | 0.4126 | 0.3539 | 269 | 383 | 491 |

## Confidence: true positives vs. false positives

- True positive confidence: {'mean': 0.48712447056602387, 'median': 0.47310924530029297}
- False positive confidence: {'mean': 0.21532583692902932, 'median': 0.16950666159391403}

## Small-object miss analysis

- Overall median GT bbox area: 7051.6 px²
- False-negative median bbox area: 3295.0 px²
- False negatives skew smaller than average: True

## Crowded vs. sparse scenes

- Crowded-scene (> 1 instances/image) false-negative rate: 0.7484
- Sparse-scene false-negative rate: 0.5393

## Difficult-background candidates (most background FPs)

['BROWNSPOT6_194_jpg.rf.b2ef46a9b340f833592d72bea1058e0f.jpg', 'sb_wb_52_jpg.rf.3d97d6ed4d7226295281e3074248f2b4.jpg', 'brown_spot-22-_jpg.rf.bf0db732c7e78d74d928b106b56436bc.jpg', 'BROWNSPOT2_098_jpg.rf.ae6f388c9b5867ff0292af5e89d12935.jpg', '05-leaf-Blast_jpg.rf.194eb375c4dbe4607bc3a86bd3058862.jpg']

## Visual examples

- False positives: ['artifacts/figures/error_analysis/bg_fp_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/bg_fp_id501_SheathBlight_245_jpg.rf.684c2a577e91cc4995a38999932fb8b8.jpg', 'artifacts/figures/error_analysis/bg_fp_id503_BLAST9_150_JPG_jpg.rf.6b018c5dcf5292737747023ed7627597.jpg', 'artifacts/figures/error_analysis/bg_fp_id504_BLAST9_032_jpg.rf.6b0232049f6de25065d02a35d5e59ee7.jpg']
- False negatives: ['artifacts/figures/error_analysis/fn_id0_IMG-20241014-WA0381_jpg.rf.02d81d946e4969027004eb331b2636b5.jpg', 'artifacts/figures/error_analysis/fn_id1_IMG-20241014-WA0258_jpg.rf.010c555e9aec70ddf42e72f285068311.jpg', 'artifacts/figures/error_analysis/fn_id2_IMG-20241012-WA0099_jpg.rf.052715be2fdca8f048e88ae49189c283.jpg', 'artifacts/figures/error_analysis/fn_id3_IMG-20240927-WA0215_jpg.rf.02427045292acba0cf19b92c6a42caf2.jpg']

## Important caveat before drawing conclusions

This checkpoint (E08, 10 epochs on a small training fraction) has zero true positives on 2/11 classes — it has not yet learned most classes at all. Confusion patterns above involving those classes mostly reflect "the model hasn't learned this yet", not a stable, meaningful semantic confusion. Only classes with non-trivial TP counts (Blast, Leaf roller, Bacterial panicle blight here) support any real interpretation at this stage.

## Proposed next experiment

Based on the findings above, not a generic guess:

1. **False negatives skew smaller than the overall GT area distribution** (3295.0 vs. 7051.6 px² median) — independent evidence, from actual missed detections rather than aggregate mAP alone, reinforcing Block 10's finding that larger image size (640 vs. 320) helps: more resolution should recover some of these small-object misses.
2. **Crowded scenes have a higher false-negative rate** (0.7484 vs. 0.5393 for sparse scenes) — consistent with (1): small, densely-packed lesions are the hardest case, and resolution should help here specifically.
3. Block 10 already found image size and training duration to be the two most impactful single factors (independently). This analysis provides an independent line of evidence (actual missed detections, not just an aggregate mAP number) pointing at the same lever (image size). **Recommended next experiment: combine larger image size (640) with more epochs in one run** (rather than continuing single-factor OFAT screening) to test whether the two effects compound, feeding directly into Block 14's final configuration decision.
4. Do NOT act on the Healthy-vs-disease confusion or specific confused-pair list yet — per the caveat above, this checkpoint hasn't learned most classes, so those patterns aren't reliable signal. Worth rechecking once a better-trained checkpoint exists (post-item-3 experiment).

## IMPORTANT: no changes were applied automatically

This script only analyzes and reports. Any data or model change suggested by these findings (e.g. relabeling, excluding an image, adjusting a class's augmentation) must be a separate, explicitly documented decision — never applied automatically from this analysis, per the master spec.
