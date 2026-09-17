# Block 16 — Clean-Environment Reproduction Test

Simulated what a judge's machine would experience: a completely fresh Python
3.11 virtual environment (separate from this project's working `.venv`),
dependencies installed from `requirements.txt` alone, no reliance on any of
this session's accumulated environment state.

## Method

1. Static audit of all tracked source files (no dynamic execution): searched
   for hardcoded personal paths, undeclared/hidden dependencies, and
   secrets.
2. Created `/tmp/audit_venv` from scratch, installed only from
   `requirements.txt`.
3. Ran the full pytest suite in that environment.
4. Loaded the actual final model checkpoint (`runs/detect/final/final_model/weights/best.pt`)
   and ran inference in the clean environment.
5. Ran `scripts/prepare_dataset.py` against the real raw dataset from the
   clean environment, diffed results against the existing prepared manifest.
6. Ran `scripts/evaluate.py` (full native val + local F1 pipeline) against
   the actual final model in the clean environment.

## Static checks

| Check | Result |
|---|---|
| Hardcoded personal absolute paths in tracked code | None found (one benign hit in a generated audit report's evidence text, not code) |
| API keys / secrets | None found (one benign hit: a `.gitignore` section comment) |
| Hidden/undeclared dependencies | None — every third-party import used in `src/`/`scripts/`/`tests/` is declared in `requirements.txt` |
| External network dependency | None — `YOLO_OFFLINE=1` enforced throughout; verified in Block 6 that it turns any download attempt into a loud `ConnectionError` |

## Findings, fixes, and re-verification

### Finding 1 (CRITICAL): fresh `pip install -r requirements.txt` failed immediately

A single-shot install — exactly what a judge's README-instructed setup would
run — failed with `ResolutionImpossible`. Root cause: `ultralytics==8.4.154`
explicitly excludes `numpy` 2.0.x-2.3.4 on macOS, but `requirements.txt`
pinned `numpy==2.1.3` (set in Block 1, before ultralytics existed in this
project). This project's own incrementally-built `.venv` never surfaced the
conflict because pip does not retroactively re-resolve already-installed
packages on incremental `pip install` calls — only a fresh, single-shot
resolution catches it.

**Fix**: removed the stale pin, let pip's resolver pick a compatible version
(`numpy==2.4.6`), then re-pinned that exact version in `requirements.txt` for
reproducibility. Re-verified: fresh install succeeds; full pytest suite
(59/59) passes in the clean environment.

### Finding 2 (CRITICAL): `evaluate.py` crashed on the full valid split in the clean environment

`scripts/evaluate.py` ran `model.val()` then reused the same model object for
the local-F1 prediction-collection pass. In the clean environment (with the
new numpy 2.4.6), this crashed with `RuntimeError: MPSGraph does not support
tensor dims larger than INT_MAX`.

Investigation (all findings verified by direct, isolated reproduction, not
assumed):
- Reloading a fresh model object between `val()` and `predict()` did not
  fix it.
- Explicit `torch.mps.empty_cache()` + `gc.collect()` between calls did not
  fix it either.
- A **completely fresh subprocess** running `predict(..., stream=True)`
  alone, with **no** prior `val()` call at all, still failed at the full
  2,106-image path list — ruling out the `val()`-then-`predict()` sequencing
  hypothesis entirely.
- Binary search established: 50/200/500/1,000 paths in one `predict()` call
  all succeed; the full 2,106-path list fails, at the very first item,
  before any real inference runs.
- This is a regression introduced by Finding 1's numpy fix: this exact
  code path ran successfully in Blocks 7 and 13 against the same 2,106-image
  split, under numpy 2.1.3.

**Fix**: chunked the path list into batches of 500 before calling
`model.predict(..., stream=True)`, combining results across chunks in
Python (`scripts/evaluate.py::collect_predictions`, same pattern applied to
`scripts/run_error_analysis.py::collect_predictions`, which has the
identical call pattern). Verified: chunking processes all 2,106 images
successfully. The exact upstream root cause (likely a numpy 2.4.x / torch
MPS interaction specific to very large explicit path lists) was not fully
isolated within this block's scope — the workaround is verified correct and
robust, and is documented as such rather than presented as a root-cause fix.

**Also refactored evaluate.py's architecture** while fixing this: the native
`val()` stage and the local-F1 `predict()` stage now run in fully separate
subprocesses (not just separate model objects), since process-level
isolation is the only mechanism confirmed to reliably avoid any residual
MPS/graph state issues between the two stages, regardless of root cause.

### Re-verification: full pipeline, clean environment, actual final model

| Step | Result |
|---|---|
| Fresh `pip install -r requirements.txt` | PASS |
| Full pytest suite (59 tests) | PASS |
| Load `runs/detect/final/final_model/weights/best.pt` | PASS |
| Inference on a sample image | PASS |
| `scripts/prepare_dataset.py` (real raw dataset) | PASS — byte-identical counts to the existing prepared manifest (10,132 train images, 1 leakage exclusion, 2,106 valid, 1,059 test) |
| `scripts/evaluate.py --split valid` (native val + local F1, full 2,106 images) | PASS — mAP@0.5=0.5620, mAP@0.5:0.95=0.3278, matching Block 15's training-time result exactly |

## Non-bug observation worth recording

Several classes (Leaf roller, False smut, Bacterial panicle blight) show
strong AP@0.5 (0.78, 0.90, 0.47) but near-zero local F1 at the 0.25
confidence threshold. This is expected, not a defect: AP integrates
precision/recall across *all* confidence thresholds, while the local F1 uses
one fixed cutoff. It indicates the model produces correct detections for
these classes but at confidence scores below 0.25 — worth knowing for
Block 18 (README) when documenting the chosen inference confidence
threshold, not something to "fix" here.

## Files changed as a direct result of this block

- `requirements.txt` — numpy re-pinned to a version compatible with
  ultralytics' macOS constraint
- `scripts/evaluate.py` — process-isolated two-stage architecture; chunked
  prediction collection
- `scripts/run_error_analysis.py` — chunked prediction collection
- `artifacts/reports/evaluation_valid.json`/`.md` — refreshed with the
  actual final model's real evaluation (superseding the stale Block 6
  smoke-test numbers, since this is the first full evaluate.py run against
  the Block 15 final model)

## Verdict

Two genuine, previously-undetected reproducibility defects found and fixed,
each re-verified in a clean environment before being considered resolved.
Both would have caused a judge's audit run to fail at the environment-setup
or evaluation step respectively — exactly the failure category this block
exists to catch before submission. No error was silently bypassed; each was
investigated to a verified root cause or verified workaround before moving
on.
