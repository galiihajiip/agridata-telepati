# Model Weights

**Status: release prepared (Block 19), pending explicit publish confirmation.**
The checksum file (`best.pt.sha256`) and metadata (`../artifacts/reports/final_model_metadata.json`)
are finalized and committed. The weights file itself is a large generated
binary and is intentionally not committed to git (see `.gitignore`); it is
distributed via a GitHub Release attachment instead. See "Planned: GitHub
Release" below for the exact prepared command and asset list.

## Current final model

| Field | Value |
|---|---|
| File | `runs/detect/final/final_model/weights/best.pt` |
| Format | PyTorch checkpoint (`.pt`) |
| Size | 6.3 MB |
| SHA-256 | `9d74fffdd977a7bb6749bc828fe908278c5d3eaa24c3cfdbbe5a560d41f5d308` |
| Architecture | YOLOv8n (Ultralytics), built from `yolov8n.yaml`, `pretrained=False` |
| Training config | [`configs/final_model_config.yaml`](../configs/final_model_config.yaml) — 50 epochs |
| Training summary | [`artifacts/reports/block15_final_training_summary.json`](../artifacts/reports/block15_final_training_summary.json) |
| Training git commit | `28668899fb000cee3a2a8386ac65ddeba2d04d02` |
| Results | mAP@0.5=0.6277, mAP@0.5:0.95=0.3905 (see [`README.md`](../README.md#10-results)) |

An earlier 20-epoch model (mAP@0.5=0.5620) was superseded at the user's
request to extend training for a better result; its full result set is
preserved at [`artifacts/archive/20epoch_run/`](../artifacts/archive/20epoch_run/).

This file is not committed to git (see `.gitignore` — `*.pt` and `runs/` are
excluded, consistent with the master spec's guidance against storing large
generated binaries directly in the repository). It is currently available
locally only, at the path above, produced by running
`scripts/run_final_training.py` with the frozen configuration.

## Verification

Loading and inference from a clean process is verified —
see the `clean_process_load_validation` field in
[`artifacts/reports/block15_final_training_summary.json`](../artifacts/reports/block15_final_training_summary.json)
and the full clean-environment reproduction test:
[`artifacts/audit/block16_clean_reproduction_test.md`](../artifacts/audit/block16_clean_reproduction_test.md).

To verify the checksum of your own copy:

```bash
shasum -a 256 runs/detect/final/final_model/weights/best.pt
```

## Planned: GitHub Release

Per the master spec (Section 31), the final submission requires the weights
to be published via a GitHub Release or Git LFS, with a direct link — not a
personal cloud-storage link. Given the file size (6.3MB, well under GitHub's
per-file limits), a plain GitHub Release attachment was chosen over Git LFS
as the simpler, equally-compliant option.

The release is prepared but **not yet published** — publishing is a
public, hard-to-reverse action on the repository and is deferred until
explicitly confirmed. The prepared command:

```bash
gh release create v1.0.0-final-model \
  runs/detect/final/final_model/weights/best.pt \
  weights/best.pt.sha256 \
  artifacts/reports/final_model_metadata.json \
  --title "Final Model v1.0.0 — YOLOv8n Rice Disease Detector" \
  --notes-file <release notes>
```

Once published, this section will be updated with the direct asset URL and
`artifacts/reports/final_model_metadata.json`'s `release` field will be set
to `published: true` with the method and URL.
