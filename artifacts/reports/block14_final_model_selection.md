# Block 14 — Final Model Configuration Selection

Reviewed all 21 logged experiments (E01-E21). This block selects and freezes a CONFIGURATION for full-scale training (Block 15) — it does not itself produce the final submitted weights.

## All candidate experiments (sorted by mAP@0.5)

| Experiment | imgsz | epochs | optimizer | mAP@0.5 | Precision | Recall | Duration (s) | Notes |
|---|---:|---:|---|---:|---:|---:|---:|---|
| E21 | 640 | 12 | AdamW | 0.0247 | 0.1403 | 0.0552 | 659 | Block 11 augmentation ablation: combined_no_aug. Block 14 confirmation |
| E20 | 640 | 12 | AdamW | 0.0234 | 0.1344 | 0.0622 | 671 | Block 11 augmentation ablation: combined_default_aug. Block 14 confirm |
| E09 | 320 | 5 | AdamW | 0.0200 | 0.3004 | 0.0305 | 152 | Block 11 augmentation ablation: none. Reference point: all augmentatio |
| E17 | 320 | 5 | AdamW | 0.0140 | 0.3867 | 0.0167 | 114 | Block 11 augmentation ablation: mosaic (not in the master spec's candi |
| E08 | 320 | 10 | AdamW | 0.0134 | 0.2921 | 0.0406 | 208 | OFAT variant: training_duration changed from baseline; all else held f |
| E11 | 320 | 5 | AdamW | 0.0130 | 0.3860 | 0.0221 | 135 | Block 11 augmentation ablation: vertical_flip. QUESTIONABLE — rice pla |
| E15 | 320 | 5 | AdamW | 0.0110 | 0.1929 | 0.0385 | 131 | Block 11 augmentation ablation: brightness_contrast. PLAUSIBLE — outdo |
| E10 | 320 | 5 | AdamW | 0.0095 | 0.2853 | 0.0361 | 145 | Block 11 augmentation ablation: horizontal_flip. PLAUSIBLE — a leaf/pl |
| E14 | 320 | 5 | AdamW | 0.0091 | 0.2966 | 0.0219 | 136 | Block 11 augmentation ablation: translation. PLAUSIBLE — subject frami |
| E12 | 320 | 5 | AdamW | 0.0091 | 0.2892 | 0.0183 | 149 | Block 11 augmentation ablation: rotation. PLAUSIBLE in moderation — si |
| E16 | 320 | 5 | AdamW | 0.0081 | 0.1988 | 0.0256 | 132 | Block 11 augmentation ablation: color_transform. PLAUSIBLE but bounded |
| E18 | 320 | 5 | AdamW | 0.0071 | 0.1143 | 0.0550 | 135 | Block 12 class-imbalance ablation: baseline, natural class distributio |
| E13 | 320 | 5 | AdamW | 0.0064 | 0.1932 | 0.0495 | 129 | Block 11 augmentation ablation: scaling. PLAUSIBLE — camera-to-subject |
| E03 | 640 | 5 | AdamW | 0.0041 | 0.3724 | 0.0052 | 302 | OFAT variant: image_size changed from baseline; all else held fixed. |
| E02 | 320 | 5 | AdamW | 0.0018 | 0.1840 | 0.0073 | 146 | Block 10 baseline (OFAT reference point). |
| E07 | 320 | 5 | AdamW | 0.0007 | 0.2759 | 0.0061 | 134 | OFAT variant: augmentation_strength changed from baseline; all else he |
| E19 | 320 | 5 | AdamW | 0.0005 | 0.1825 | 0.0111 | 120 | Block 12 class-imbalance ablation: rare classes ['Bacterial leaf bligh |
| E04 | 320 | 5 | AdamW | 0.0005 | 0.0004 | 0.0828 | 119 | OFAT variant: batch_size changed from baseline; all else held fixed. |
| E06 | 320 | 5 | SGD | 0.0003 | 0.0961 | 0.0003 | 128 | OFAT variant: optimizer changed from baseline; all else held fixed. |
| E05 | 320 | 5 | AdamW | 0.0002 | 0.1820 | 0.0814 | 131 | OFAT variant: learning_rate changed from baseline; all else held fixed |
| E01 | 320 | 2 | AdamW | 0.0000 | 0.0000 | 0.0000 | 127 | Block 6 smoke test: 2 epochs, 5% of train, imgsz=320. Proves pipeline  |

## Selected configuration: see `configs/final_model_config.yaml`

Best individual screening result: **E21** (mAP@0.5=0.0247). The frozen final config does not simply copy this one experiment's settings verbatim — it synthesizes evidence across all 21 experiments (see the config file's inline rationale comments for each hyperparameter) plus Block 11's semantic-plausibility reasoning and Block 13's independent error-analysis evidence.

## Compliance checklist (evidence-based, not asserted)

| # | Item | Status | Evidence |
|---:|---|---|---|
| 1 | No external pretrained weights | PASS | Block 6: model always built from yolov8n.yaml (architecture only); build_compliant_model() raises if pretrained=True or given a .pt/.pth/.ckpt file. YOLO_OFFLINE enforced across all training/eval scripts. Empty pretrained-checkpoint-cache verification performed in Block 6 (before/after directory diff, zero .pt files appeared anywhere outside this project's own runs/ output). |
| 2 | No data leakage | PARTIAL — one confirmed case fixed, residual risk documented | Block 2 forensic audit found exactly one exact-duplicate image (MD5-identical) across train/test ('leaf_scald-230...'); Block 5 excludes it from the prepared train manifest. Perceptual-hash overlap candidates (Block 2) are unconfirmed and were not further investigated — flagged as a residual, documented risk, not silently ignored. |
| 3 | Official canonical 11 classes | PASS | Block 3: canonical mapping validated against the actual dataset with zero unmapped raw categories (mapping version 1.0.0). Block 5's data.yaml always declares exactly 11 classes in canonical order: ['Bacterial leaf blight', 'Bacterial panicle blight', 'Blast', 'Brown spot', 'False smut', 'Healthy', 'Leaf roller', 'Leaf scald', 'Narrow brown', 'Sheath blight', 'Tungro']. |
| 4 | Reproducible preprocessing | PASS | Block 8: rerunning scripts/prepare_dataset.py with the same seed produced a byte-for-byte identical 10,132-image manifest, verified via a live rerun-and-diff, not assumed. |
| 5 | Reproducible configuration | PASS | Block 9 tracker records seed/git-commit/hyperparameters for every one of the 21 logged experiments. This report's frozen config (configs/final_model_config.yaml) is itself version-controlled. |
| 6 | Valid checkpoint | PASS for screening checkpoints — PENDING for final weights | All 21 screening experiments produced a loadable best.pt (verified by reloading fresh in evaluate.py/error-analysis runs). The actual final-submission checkpoint does not exist yet — it is produced by Block 15 and must be re-verified there. |
| 7 | Successful inference | PASS | Block 6: standalone inference test on a freshly-loaded checkpoint in a clean process. Blocks 7/13: evaluate.py and run_error_analysis.py both successfully ran inference on screening checkpoints across the full valid split (2,106 images). |
| 8 | Acceptable validation performance | PENDING — NOT YET MET, explicitly not claimed | Best screening result so far: E21 at mAP@0.5=0.0247, trained on only ~10% of train data for 12 epochs. This is a screening-scale number, not a competitive result, and is not represented as one. Full-scale training (Block 15: fraction=1.0, epochs=50, patience=15) is required before this item can be assessed honestly. |

## Known risks

- Residual, unconfirmed perceptual-hash overlap candidates from Block 2 (train-vs-valid: 426, train-vs-test: 210, valid-vs-test: 84) were never individually visually confirmed as true duplicates or false positives from the coarse 8x8 aHash. Only the one exact-MD5 duplicate was acted on.
- All 21 screening experiments used a small fraction of train data (8-10%) and few epochs (5-12); the frozen config's full-scale numbers (epochs=50, fraction=1.0) are extrapolated, not directly measured — Block 15 is the first point at which the real full-scale behavior is observed.
- MPS backend has confirmed non-deterministic kernels for `scatter_reduce_mps` and `index_put_with_accumulate_mps` (Block 6/8 finding) — exact bit-for-bit reproducibility of training is not guaranteed, only reproducible configuration/preprocessing.
- Estimated full-scale training time (~8.2 hours on this project's hardware) is long; `patience=15` may shorten it, but Block 15 must re-verify this estimate before committing.

Git commit at selection time: `9724a9b25a4c36e9ebf414fca841824afcedf74f`
