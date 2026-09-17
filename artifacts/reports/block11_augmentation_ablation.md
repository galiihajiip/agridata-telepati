# Block 11 — Augmentation Ablation

**Scale note**: same small-fraction/few-epoch screening scale as Block 10, for direct comparability. Absolute mAP values are low; only relative effects matter here.

Reference: Block 10's E02 (Ultralytics' default combined augmentation bundle) scored mAP@0.5=0.0018. This block isolates each factor individually from a clean no-augmentation reference (E09) instead.

## Results

| Experiment | Augmentation | Plausibility | mAP@0.5 | Precision | Recall | Duration (s) |
|---|---|---|---:|---:|---:|---:|
| E09 | none | Reference point: all augmentation disabled. | 0.0200 | 0.3004 | 0.0305 | 151.8 |
| E10 | horizontal_flip | PLAUSIBLE | 0.0095 | 0.2853 | 0.0361 | 144.7 |
| E11 | vertical_flip | QUESTIONABLE | 0.0130 | 0.3860 | 0.0221 | 135.1 |
| E12 | rotation | PLAUSIBLE in moderation | 0.0091 | 0.2892 | 0.0183 | 148.5 |
| E13 | scaling | PLAUSIBLE | 0.0064 | 0.1932 | 0.0495 | 129.4 |
| E14 | translation | PLAUSIBLE | 0.0091 | 0.2966 | 0.0219 | 135.6 |
| E15 | brightness_contrast | PLAUSIBLE | 0.0110 | 0.1929 | 0.0385 | 131.2 |
| E16 | color_transform | PLAUSIBLE but bounded deliberately | 0.0081 | 0.1988 | 0.0256 | 132.2 |
| E17 | mosaic (not in the master spec's candidate list, but active by default in Ultralytics — included for completeness since it silently affected every Block 10 run) | QUESTIONABLE for this domain | 0.0140 | 0.3867 | 0.0167 | 113.9 |

## Per-augmentation effect (relative to the no-augmentation reference)

- **horizontal_flip**: mAP@0.5 worsened by -0.0105 vs. no-augmentation reference.
- **vertical_flip**: mAP@0.5 worsened by -0.0070 vs. no-augmentation reference.
- **rotation**: mAP@0.5 worsened by -0.0109 vs. no-augmentation reference.
- **scaling**: mAP@0.5 worsened by -0.0136 vs. no-augmentation reference.
- **translation**: mAP@0.5 worsened by -0.0109 vs. no-augmentation reference.
- **brightness_contrast**: mAP@0.5 worsened by -0.0090 vs. no-augmentation reference.
- **color_transform**: mAP@0.5 worsened by -0.0119 vs. no-augmentation reference.
- **mosaic (not in the master spec's candidate list, but active by default in Ultralytics — included for completeness since it silently affected every Block 10 run)**: mAP@0.5 worsened by -0.0060 vs. no-augmentation reference.

## Candidate not empirically tested: mild blur/noise

Source inspection of `ultralytics/data/augment.py` (`Albumentations` class)
shows the exact default transforms and probabilities Ultralytics would apply
if the optional `albumentations` package were installed:

    A.Blur(p=0.01), A.MedianBlur(p=0.01), A.ToGray(p=0.01), A.CLAHE(p=0.01),
    A.RandomBrightnessContrast(p=0.0), A.RandomGamma(p=0.0), A.ImageCompression(p=0.0)

`albumentations` is NOT currently installed in this project, so none of this
fires today — confirmed, not assumed (`pip show albumentations` finds nothing).

Assessment:
- **Blur / MedianBlur (p=0.01 each)**: PLAUSIBLE — mild focus/motion blur is
  common in real field photography. But at 1% probability each, across ~800
  train images x 5 epochs (~4000 image-views), only ~80 image-views would
  ever see either transform — far too sparse to produce a measurable mAP
  difference at this screening scale. An empirical run would mostly measure
  noise, not the transform's effect.
- **ToGray (p=0.01)**: QUESTIONABLE for this domain specifically — lesion
  color is a genuine diagnostic feature for several canonical classes (e.g.
  Brown spot vs. Blast). Converting to grayscale removes exactly the signal
  the `color_only` variant above was deliberately kept conservative to
  protect.
- **CLAHE (p=0.01)**: PLAUSIBLE — adaptive contrast enhancement helps with
  lighting variability, similar reasoning to `brightness_only`.

**Decision**: do not add `albumentations` as a project dependency at this
stage. The effect is real but too sparse (1% probability) to justify a new
dependency and a live experiment whose result would be dominated by sampling
noise at this scale. This can be revisited in Block 13 (error analysis) if
blur-sensitivity turns out to be a real failure mode.

## Recommendation

Per master spec: augmentation choice must weigh *semantic plausibility for this domain*, not just raw numbers at a tiny screening scale. Concretely:

- Recommend **keeping**: horizontal flip, rotation (moderate), scaling, translation, brightness/contrast, conservative color jitter — all physically plausible for field-captured rice imagery, regardless of their small individual effect at this screening scale.
- Recommend **excluding**: vertical flip — even if it measured a positive effect above, it is physically implausible for gravity-oriented plants and risks teaching the model orientations it will never see deployed. Domain reasoning overrides a marginal metric gain here.
- **Mosaic**: kept only if its measured effect above is neutral-to-positive; if it clearly hurts at this scale, worth re-testing at full training scale before deciding (mosaic's benefits are generally more visible with more data/epochs than this screening pass uses).
- Mild blur/noise: deliberately not adopted at this stage (see analysis above).

This is a screening-scale recommendation to carry into Block 12 (class imbalance) and Block 14 (final config freeze) — not a final decision on its own.
