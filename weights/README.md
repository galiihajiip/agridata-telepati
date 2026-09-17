# Model Weights

**Status: not yet published as a GitHub Release.** Release preparation is a
separate, later step (Block 19) — this file documents the current, local
state of the final trained weights so it is not left unrecorded in the
meantime.

## Current final model

| Field | Value |
|---|---|
| File | `runs/detect/final/final_model/weights/best.pt` |
| Format | PyTorch checkpoint (`.pt`) |
| Size | 6.3 MB |
| SHA-256 | `a48da07d91188b9985171bda8c2ebc745699fb21a1fa059291b014e6951b12e6` |
| Architecture | YOLOv8n (Ultralytics), built from `yolov8n.yaml`, `pretrained=False` |
| Training config | [`configs/final_model_config.yaml`](../configs/final_model_config.yaml) |
| Training summary | [`artifacts/reports/block15_final_training_summary.json`](../artifacts/reports/block15_final_training_summary.json) |
| Training git commit | `20222441681255a2312dc4edfc52be1a06f4a85d` |

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

## Planned: GitHub Release / Git LFS

Per the master spec (Section 31), the final submission requires the weights
to be published via a GitHub Release or Git LFS, with a direct link — not a
personal cloud-storage link. This will be completed in Block 19; this file
will be updated with the direct release link at that time.
