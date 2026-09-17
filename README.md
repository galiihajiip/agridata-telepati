# AgriData Intelligence Race — TELEPATI 8.0
## Rice Plant Disease Object Detection

> **AgriTech: Growing The Golden Future**
> *"Menanam inovasi, memanen keunggulan menuju Indonesia Emas 2045"*

Submission repository for **TELEPATI 8.0 — AgriData Intelligence Race**
(HIMATEL POLBAN), **AI Model Training & Case Study** track.

---

## 1. Competition

TELEPATI 8.0 is a national technology competition organized by HIMATEL
POLBAN. AgriData Intelligence Race tests scientific analysis and
problem-solving through Computer Vision and Object Detection applied to a
real agricultural case study. Official regulation:
https://polbantelepati.tech/regulasi/ai

## 2. Problem Statement

A young farmer (the competition's case study, "Arif") manages family
farmland and must monitor thousands of rice plants across multiple plots.
Manual monitoring is slow, labor-intensive, dependent on individual
experience, and prone to delayed problem detection. This project builds an
object detection model that identifies rice plant disease/health conditions
from field-captured imagery (drone or handheld camera), as a component of a
Smart Agriculture monitoring system — automatically localizing and
classifying conditions in an image rather than requiring exhaustive manual
inspection.

## 3. Dataset

Official TELEPATI 8.0 AgriData dataset (COCO-format annotations, Roboflow
export). Not included in this repository — obtain it from the competition
organizers and place it at the project root (see [Dataset Path
Configuration](#14-dataset-path-configuration)).

| Split | Images | Annotations | Raw categories |
|---|---:|---:|---:|
| train | 10,133 | 20,163 | 21 |
| valid | 2,106 | 4,888 | 21 |
| test | 1,059 | 2,670 | 21 |

A full forensic audit (duplicate detection, bounding-box validation,
corruption checks) was performed — see
[`artifacts/audit/dataset_audit_report.md`](artifacts/audit/dataset_audit_report.md).
One confirmed exact-duplicate image across train/test was found and
excluded from the prepared training set (10,132 images used for training).

## 4. Canonical 11 Classes

The raw dataset's 21 categories include 3 non-detection supercategory
placeholders (`Leaf-blight`, `Rice-Leaf-Diseasee`, `paddy` — zero
annotations, per the official regulation) plus 18 raw disease/health labels
mapped deterministically to 11 canonical classes
(`src/agridata/dataset/mapping.py`, verified against the actual dataset with
zero unmapped categories — see
[`artifacts/reports/class_imbalance_diagnostics.md`](artifacts/reports/class_imbalance_diagnostics.md)):

| ID | Canonical Class | Instances (train) |
|---:|---|---:|
| 0 | Bacterial leaf blight | 476 |
| 1 | Bacterial panicle blight | 528 |
| 2 | Blast | 4,149 |
| 3 | Brown spot | 5,010 |
| 4 | False smut | 852 |
| 5 | Healthy | 2,374 |
| 6 | Leaf roller | 812 |
| 7 | Leaf scald | 1,438 |
| 8 | Narrow brown | 222 |
| 9 | Sheath blight | 1,762 |
| 10 | Tungro | 2,540 |

Class imbalance ratio (max/min instance count): **22.6×**. A targeted
oversampling mitigation was experimentally evaluated
([`artifacts/reports/block12_class_imbalance_ablation.md`](artifacts/reports/block12_class_imbalance_ablation.md))
and did not show a clear benefit at screening scale — not adopted in the
final configuration.

## 5. Methodology

Raw dataset → forensic audit → canonical class mapping → deterministic
preprocessing (YOLO-format conversion, leakage exclusion) → controlled
hyperparameter/augmentation screening experiments (21 logged runs) →
evidence-based final configuration selection → full-scale training →
clean-environment reproduction verification. Every step is a separate,
committed, auditable stage — see `artifacts/` for the full trail and
`artifacts/experiments/experiment_log.json` for every experiment's recorded
configuration and result.

## 6. Architecture

**YOLOv8n** (Ultralytics), built from an architecture-only `.yaml`
definition — **never** from a pretrained `.pt` checkpoint. `pretrained=False`
is enforced in code (`src/agridata/training/train.py::build_compliant_model`
raises if given a checkpoint-looking path or `pretrained=True`), and
`YOLO_OFFLINE=1` is set before Ultralytics is imported in every
training/evaluation script so any accidental network call (telemetry,
checkpoint download) fails loudly instead of silently succeeding.

- Input: 640×640 RGB
- Output: bounding boxes (xyxy) + class + confidence, 11 canonical classes
- Parameters: ~3.0M

## 7. Training Configuration

Frozen final configuration: [`configs/final_model_config.yaml`](configs/final_model_config.yaml)
(every hyperparameter's rationale is documented inline, citing the specific
screening experiment that justified it).

| Parameter | Value |
|---|---|
| Seed | 42 |
| Image size | 640 |
| Batch size | 16 |
| Epochs | 20 (originally 50; reduced given competition deadline proximity — see config file's inline note) |
| Optimizer | AdamW |
| Learning rate | 0.001 |
| Weight decay | 0.0005 |
| Scheduler | linear |
| Patience (early stopping) | 8 |
| Training data fraction | 1.0 (full set) |
| Device | MPS (Apple Silicon); CPU fallback supported, CUDA never assumed |

Selected from **21 controlled screening experiments** (Blocks 10–14) —
see [`artifacts/reports/block14_final_model_selection.md`](artifacts/reports/block14_final_model_selection.md)
for the full evidence-based reasoning behind every choice.

## 8. Augmentation

Ultralytics' default augmentation pipeline, with one deliberate override:
**vertical flip disabled** (`flipud=0.0`) — physically implausible for
gravity-oriented plants (a real camera/drone would never capture an
upside-down plant), overriding a marginal screening-scale metric in favor of
domain reasoning. Every other augmentation (horizontal flip, moderate
rotation, scale, translation, brightness/contrast, conservative color
jitter, mosaic) was individually assessed for physical plausibility in field
photography — see [`artifacts/reports/block11_augmentation_ablation.md`](artifacts/reports/block11_augmentation_ablation.md).
Hue jitter is kept conservative (1.5%) because lesion color is a genuine
diagnostic feature for several classes.

## 9. Evaluation Metrics

- **mAP@0.5**: Ultralytics' native `model.val()` implementation (101-point
  interpolated precision-recall integration, IoU=0.50). This project does
  not reimplement AP integration — Ultralytics' implementation is the
  source of truth.
- **F1-score**: a local implementation via greedy IoU≥0.5 matching at a
  configurable confidence threshold (`src/agridata/metrics/detection.py`),
  because Ultralytics' own reported precision/recall uses an internally
  auto-selected threshold that is not configurable. Explicitly labeled as
  an implementation detail, not the official scoring formula.

## 10. Results

Final model, evaluated on the official **validation** split (2,106 images,
4,887 annotations after one duplicate removal), weights:
`runs/detect/final/final_model/weights/best.pt`.

| Metric | Value |
|---|---:|
| mAP@0.5 | **0.5620** |
| mAP@0.5:0.95 | 0.3278 |
| Precision (native, Ultralytics' internal best-F1 point) | 0.6073 |
| Recall (native, Ultralytics' internal best-F1 point) | 0.5562 |
| F1 (local, confidence≥0.25) | ~0.31–0.34* |

*See [Known Limitations](#20-known-limitations) — the local F1 metric showed
observed run-to-run variance on this hardware; mAP@0.5 was exactly identical
across every run performed.

**Per-class AP@0.5:**

| Canonical class | AP@0.5 |
|---|---:|
| Narrow brown | 0.9411 |
| False smut | 0.9009 |
| Healthy | 0.8580 |
| Leaf roller | 0.7829 |
| Tungro | 0.5328 |
| Bacterial panicle blight | 0.4728 |
| Blast | 0.4147 |
| Sheath blight | 0.3507 |
| Leaf scald | 0.3475 |
| Bacterial leaf blight | 0.3153 |
| Brown spot | 0.2656 |

Classes with the smallest bounding boxes on average (disease lesions:
Brown spot, Blast, Bacterial leaf blight — see
[`artifacts/reports/class_imbalance_diagnostics.md`](artifacts/reports/class_imbalance_diagnostics.md))
score lowest, consistent with the well-known difficulty of small-object
detection — confirmed independently via error analysis
([`artifacts/reports/block13_error_analysis.md`](artifacts/reports/block13_error_analysis.md)),
not just this final result.

Full evaluation report: [`artifacts/reports/evaluation_valid.md`](artifacts/reports/evaluation_valid.md).

## 11. Reproducibility

- **Deterministic preprocessing**: verified bit-for-bit — rerunning
  `scripts/prepare_dataset.py` with the same seed produces a byte-for-byte
  identical manifest (Block 8, live rerun-and-diff, not assumed).
- **Deterministic training**: **not** claimed bit-for-bit. Apple Silicon
  MPS has confirmed non-deterministic kernels for `scatter_reduce_mps` and
  `index_put_with_accumulate_mps` (observed as explicit PyTorch warnings
  during every training run). Reproducible *configuration* is guaranteed;
  bit-exact numerical output is not.
- **Reproducible configuration**: every experiment's seed, hyperparameters,
  model architecture, and git commit are recorded in
  `artifacts/experiments/experiment_log.json`.
- **Clean-environment reproduction test** (Block 16): a completely fresh
  virtualenv, installed from `requirements.txt` alone, was used to
  re-verify dataset preparation, model loading, inference, and full
  evaluation. This caught and fixed two real defects (see
  [`artifacts/audit/block16_clean_reproduction_test.md`](artifacts/audit/block16_clean_reproduction_test.md)):
  a `numpy` version conflicting with `ultralytics` on macOS, and an
  MPS-backend crash on large-batch inference (worked around via chunking).

## 12. How to Run

### 13. Environment Setup

```bash
git clone <this-repository-url>
cd agridata-telepati8
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Requires Python 3.11.x. All dependencies are pinned to exact versions in
[`requirements.txt`](requirements.txt) (fresh-install-verified — see Block
16). No CUDA is assumed; MPS (Apple Silicon) is used automatically if
available, with CPU fallback always supported.

### 14. Dataset Path Configuration

Obtain the official dataset from the competition organizers and place it at
the project root as `Telepati 8.0 Datasets/` (containing `train/`, `valid/`,
`test/` subdirectories, each with images and a `_annotations.coco.json`
file), **or** point `--dataset-root` at wherever you placed it — every
script accepts this as an explicit CLI argument; no personal absolute path
is hardcoded anywhere in this codebase.

```bash
python scripts/prepare_dataset.py --dataset-root "Telepati 8.0 Datasets" --output-dir data/prepared --seed 42
```

### 15. Notebook

The primary end-to-end submission notebook:
[`notebooks/final_agriData_telepati8.ipynb`](notebooks/final_agriData_telepati8.ipynb).
Restart & Run All completes in a few minutes by default (loads the existing
final model rather than retraining); set `SKIP_TRAINING = False` in the
training cell to reproduce the full ~5.2-hour training run from the frozen
configuration.

### 16. Inference

```bash
python scripts/evaluate.py \
  --weights runs/detect/final/final_model/weights/best.pt \
  --split valid \
  --conf-threshold 0.25
```

Or programmatically:

```python
from ultralytics import YOLO
model = YOLO("runs/detect/final/final_model/weights/best.pt")
results = model.predict("path/to/image.jpg")
```

## 17. Model Weights

- Local path: `runs/detect/final/final_model/weights/best.pt` (6.3MB)
- SHA-256: `a48da07d91188b9985171bda8c2ebc745699fb21a1fa059291b014e6951b12e6`
- See [`weights/README.md`](weights/README.md) for release/download details.

## 18. Repository Structure

```text
agridata-telepati8/
├── README.md                      # this file
├── requirements.txt                # pinned, fresh-install-verified dependencies
├── configs/
│   ├── base.yaml
│   ├── final_model_config.yaml     # frozen final training configuration
│   └── experiments/                # screening experiment configs (Blocks 10-12)
├── notebooks/
│   └── final_agriData_telepati8.ipynb   # primary submission notebook
├── src/agridata/                   # core package (dataset, training, metrics, analysis, viz)
├── scripts/                        # CLI entrypoints for every pipeline stage
├── data/prepared/                  # generated training-ready view (gitignored, regenerable)
├── artifacts/
│   ├── audit/                      # forensic audit, reproducibility checklist, clean-env test
│   ├── reports/                    # per-block reports, experiment selection, evaluation results
│   ├── figures/                    # EDA and prediction visualizations
│   └── experiments/                # structured experiment tracker (21 logged runs)
├── runs/detect/final/              # final training run output (gitignored; weights released separately)
├── weights/                        # model weight release info
└── tests/                          # unit tests (59, covering mapping/metrics/analysis/tracker/reproducibility)
```

## 19. Compliance Statement

- **No external pretrained weights**: model built from an architecture-only
  `.yaml` definition, `pretrained=False` enforced in code and verified via
  empty-checkpoint-cache checks (Block 6).
- **Official dataset only**: no external dataset used.
- **No LLM/API dataset processing**: all preprocessing is local, deterministic
  Python code.
- **Canonical 11-class mapping**: verified against the actual dataset with
  zero unmapped raw categories.
- **Deterministic seeding**: `seed=42` applied to Python `random`, NumPy,
  and PyTorch throughout.
- **No data leakage**: one confirmed exact-duplicate image (train/test)
  found and excluded; see [Known Limitations](#20-known-limitations) for
  residual, unconfirmed candidates.
- **Audit-ready pipeline**: every stage (dataset audit → mapping →
  preparation → screening experiments → final training → clean-environment
  verification) is a separate, committed, reproducible step with a
  machine-readable report under `artifacts/`.
- **`YOLO_OFFLINE=1`** enforced in every training/evaluation script.

## 20. Known Limitations

- **Local F1 metric shows observed run-to-run variance** on this project's
  Apple Silicon/MPS hardware: standalone script runs measured F1@0.25 in the
  range ~0.31–0.34, but one run (executed from within a live Jupyter kernel
  subprocess) measured 0.16 — native mAP@0.5 was **exactly** 0.5620 in every
  single run, including that one. This suggests GPU resource contention
  between a long-lived parent process and a spawned subprocess, not a
  pipeline defect, but was not exhaustively root-caused. **Recommendation
  for audit purposes: treat mAP@0.5 as the primary, stable point of
  comparison; treat the local F1 as an approximate secondary metric.**
- **Residual, unconfirmed perceptual-hash overlap candidates** across splits
  (Block 2: 426 train-valid, 210 train-test, 84 valid-test candidates from a
  coarse 8×8 average-hash) were never individually visually confirmed as
  true duplicates or false positives. Only the one exact-MD5 duplicate was
  acted on.
- **Class imbalance remains** (22.6× max/min): a tested oversampling
  mitigation did not show a clear benefit at screening scale and was not
  adopted; results show correspondingly weaker performance on some rare and
  small-object classes (Brown spot, Bacterial leaf blight).
- **Training determinism**: not bit-exact on MPS (see Reproducibility).
- **Screening-to-full-scale extrapolation**: hyperparameter/augmentation
  choices were validated at a small-fraction, few-epoch screening scale
  (Blocks 10–13) before being applied to full-scale training (Block 15);
  this is standard practice but full-scale behavior was only directly
  observed for the final configuration itself, not for every rejected
  alternative.

## Contributors

- **Galih Aji Pangestu** ([@galiihajiip](https://github.com/galiihajiip))
