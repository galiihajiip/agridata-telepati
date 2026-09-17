# Block 10 — Baseline Experiment Matrix: Results & Recommendation

**Scale caveat**: this matrix uses a small fraction of train data and few epochs (a fast comparative screening pass), not the final training regime. Absolute mAP values are expected to be low here; only *relative* differences between variants and the baseline are meaningful at this stage.

## Results

| Experiment | Axis changed | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall | Duration (s) |
|---|---|---:|---:|---:|---:|---:|
| E02 | baseline | 0.0018 | 0.0005 | 0.1840 | 0.0073 | 145.7 |
| E03 | image_size | 0.0041 | 0.0017 | 0.3724 | 0.0052 | 302.2 |
| E04 | batch_size | 0.0005 | 0.0001 | 0.0004 | 0.0828 | 119.4 |
| E05 | learning_rate | 0.0002 | 0.0001 | 0.1820 | 0.0814 | 130.7 |
| E06 | optimizer | 0.0003 | 0.0001 | 0.0961 | 0.0003 | 127.8 |
| E07 | augmentation_strength | 0.0007 | 0.0002 | 0.2759 | 0.0061 | 133.8 |
| E08 | training_duration | 0.0134 | 0.0034 | 0.2921 | 0.0406 | 207.8 |

## Per-axis effect (relative to baseline)

- **image_size**: mAP@0.5 improved by +0.0023 vs. baseline (302s vs baseline's 146s).
- **batch_size**: mAP@0.5 worsened by -0.0013 vs. baseline (119s vs baseline's 146s).
- **learning_rate**: mAP@0.5 worsened by -0.0016 vs. baseline (131s vs baseline's 146s).
- **optimizer**: mAP@0.5 worsened by -0.0015 vs. baseline (128s vs baseline's 146s).
- **augmentation_strength**: mAP@0.5 worsened by -0.0011 vs. baseline (134s vs baseline's 146s).
- **training_duration**: mAP@0.5 improved by +0.0117 vs. baseline (208s vs baseline's 146s).

## Recommendation

Highest mAP@0.5 in this screening pass: **E08** (training_duration, mAP@0.5=0.0134).

This is NOT declared the final configuration — per the master spec, no configuration is called "best" until measured at full scale. This result should inform, not replace, the ablations in Blocks 11-13 (augmentation, class imbalance, error analysis) before Block 14 freezes a final configuration.
