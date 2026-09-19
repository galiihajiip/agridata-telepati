# Reproducibility Checklist (Block 8)

## Determinism boundary, read this before trusting any PASS below

- **Deterministic PREPROCESSING**: verified bit-for-bit (dataset preparation, canonical mapping).
- **Deterministic TRAINING**: NOT claimed bit-for-bit. Block 6 logged real PyTorch warnings, `scatter_reduce_mps` and `index_put_with_accumulate_mps` have no deterministic implementation on this project's Apple Silicon / MPS backend. Training is reproducible in *configuration* (same seed/hyperparameters/code version), not guaranteed bit-exact in numerical output.
- **Reproducible EXPERIMENT CONFIGURATION**: verified, every run's seed, hyperparameters, model architecture, and git commit are captured in a committed report.

## Checklist

| # | Item | Status | Detail |
|---:|---|---|---|
| 1 | same seed -> same dataset manifest | PASS | Rerun manifest (10132 images) is byte-for-byte identical to the checked-in manifest. |
| 2 | same seed -> same canonical mapping | PASS | Mapping table hash for version 1.0.0: b88a0260138244fb. build_mapping_report is deterministic (identical input -> identical output). If this hash ever changes unexpectedly on a rerun, MAPPING_VERSION must be bumped. |
| 3 | same config -> same generated metadata | PASS | Deterministic fields (seed, mapping_version, per-split image/annotation counts) are identical across reruns of the same config; only the recorded timestamp and git commit (if code changed between runs) are expected to vary, these are provenance fields, not outputs of the computation itself. |
| 4 | training configuration is fully logged | PASS | All required training configuration fields present in /Users/macbookpro/Projects/agridata/artifacts/reports/block6_baseline_smoke_summary.json. |
| 5 | random seeds are recorded | PASS | Seed=42 recorded in both the experiment config and the run summary. |
| 6 | dependency versions are recordable | PASS | `pip freeze` returned 44 pinned packages. |
| 7 | git commit hash is recorded where possible | PASS | Current commit: 9a05573a88416d9c7ac303cb26f578f6a5c73fa1. |
| 8 | model configuration is recorded | PASS | model_arch=yolov8n.yaml, pretrained=False recorded. |
| 9 | data path is configurable | PASS | No hardcoded personal paths found in configs/; dataset-facing scripts accept --dataset-root/--prepared-dir. |
| 10 | generated artifacts are versioned through metadata, not giant commits | PASS | Large/generated directories are gitignored: ['data/prepared', 'runs', '.venv'] |
