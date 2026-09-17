# Model Card (Draft) — AgriData TELEPATI 8.0 Rice Disease Detector

**Status: DRAFT.** Training config is frozen (`configs/final_model_config.yaml`); weights, final metrics, and
evaluation results will be filled in after Block 15 (final training run) and Block 16 (clean
reproduction test). Do not treat any number in this draft as final.

## Intended use

Object detection of rice plant disease/health conditions from field-captured imagery (drone or
handheld camera), as a component of a Smart Agriculture monitoring system — per the TELEPATI 8.0
AgriData Intelligence Race case study (assisting a farmer in monitoring large plots without
exhaustive manual inspection).

## Model architecture

YOLOv8n (Ultralytics), initialized from an architecture-only definition (no external pretrained
weights — `pretrained=False`, verified via source inspection and empty-checkpoint-cache checks in
Block 6). ~3.0M parameters, 11-class detection head.

## Training data

Official TELEPATI 8.0 AgriData dataset (COCO-format, Roboflow export). 11 canonical classes
(see `src/agridata/dataset/mapping.py` for the verified raw-to-canonical mapping):
Bacterial leaf blight, Bacterial panicle blight, Blast, Brown spot, False smut, Healthy, Leaf roller, Leaf scald, Narrow brown, Sheath blight, Tungro.

One confirmed exact-duplicate image across train/test was excluded from training (Block 2/5).

## Training procedure

See `configs/final_model_config.yaml` for the complete, version-controlled configuration. Selected from 21
controlled screening experiments (Blocks 10-13) — see
`artifacts/reports/block14_final_model_selection.md` for full reasoning per hyperparameter.

## Evaluation

*Pending Block 15/16.* Metrics will be computed via `scripts/evaluate.py` (mAP@0.5 — Ultralytics'
native implementation; F1 — a documented local implementation via greedy IoU≥0.5 matching at a
configurable confidence threshold, since Ultralytics' own reported precision/recall uses an
internally auto-selected threshold that is not configurable — see
`src/agridata/metrics/detection.py`).

## Known limitations (as of this draft)

- All findings so far come from small-fraction, low-epoch screening experiments; full-scale
  behavior may differ.
- Residual, unconfirmed perceptual-hash near-duplicate candidates across splits (Block 2) were
  not individually resolved.
- No bit-for-bit training determinism guarantee on Apple Silicon / MPS (confirmed non-deterministic
  kernels for two operations used in this pipeline).
- Class imbalance is real (22.6x max/min instance ratio); a targeted-oversampling mitigation was
  tested (Block 12) and did not show a clear benefit at screening scale — not adopted in the final
  config as of this draft; may be revisited after Block 15's full-scale results.

## Compliance statement

No external pretrained weights, no external dataset, no LLM/API dataset processing. See
`artifacts/reports/block14_final_model_selection.md` for the full evidence-based compliance
checklist.
