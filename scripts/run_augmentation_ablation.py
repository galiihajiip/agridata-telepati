#!/usr/bin/env python3
"""Controlled augmentation ablation (Block 11).

Usage:
    python scripts/run_augmentation_ablation.py --config configs/experiments/augmentation_ablation.yaml

One-factor-at-a-time from a clean NO-AUGMENTATION reference point (distinct
from Block 10's baseline, which already had Ultralytics' default
augmentation bundle silently active). Each augmentation type is assessed for
physical/semantic plausibility for agricultural imagery *before* being run
(see the YAML config's `plausibility` field per variant), and every result
is logged to the same Block 9 experiment tracker used throughout this
project. Validation/test images are never touched, augmentation only
applies to the training dataloader (Ultralytics' default behavior, verified
by design: only `train:` split images pass through the augmentation
pipeline; `val:`/`test:` inference uses un-augmented images).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.device import detect_device  # noqa: E402
from agridata.experiments.tracker import (  # noqa: E402
    ExperimentRecord,
    append_experiment,
    build_markdown_table,
    compute_manifest_hash,
    load_experiments,
)
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.reproducibility.environment import get_git_commit  # noqa: E402
from agridata.seed import set_global_seed  # noqa: E402
from agridata.training.train import run_training  # noqa: E402

logger = logging.getLogger("agridata.scripts.run_augmentation_ablation")

# Visually verify bbox-vs-image consistency after augmentation for the two
# transform types most likely to hide a coordinate bug: flip (trivial to get
# wrong) and rotation (the most geometrically complex transform in the set).
VISUAL_VERIFICATION_VARIANTS = {"hflip_only", "rotation_only"}

BLUR_NOISE_ANALYSIS = """
## Candidate not empirically tested: mild blur/noise

Source inspection of `ultralytics/data/augment.py` (`Albumentations` class)
shows the exact default transforms and probabilities Ultralytics would apply
if the optional `albumentations` package were installed:

    A.Blur(p=0.01), A.MedianBlur(p=0.01), A.ToGray(p=0.01), A.CLAHE(p=0.01),
    A.RandomBrightnessContrast(p=0.0), A.RandomGamma(p=0.0), A.ImageCompression(p=0.0)

`albumentations` is NOT currently installed in this project, so none of this
fires today, confirmed, not assumed (`pip show albumentations` finds nothing).

Assessment:
- **Blur / MedianBlur (p=0.01 each)**: PLAUSIBLE, mild focus/motion blur is
  common in real field photography. But at 1% probability each, across ~800
  train images x 5 epochs (~4000 image-views), only ~80 image-views would
  ever see either transform, far too sparse to produce a measurable mAP
  difference at this screening scale. An empirical run would mostly measure
  noise, not the transform's effect.
- **ToGray (p=0.01)**: QUESTIONABLE for this domain specifically, lesion
  color is a genuine diagnostic feature for several canonical classes (e.g.
  Brown spot vs. Blast). Converting to grayscale removes exactly the signal
  the `color_only` variant above was deliberately kept conservative to
  protect.
- **CLAHE (p=0.01)**: PLAUSIBLE, adaptive contrast enhancement helps with
  lighting variability, similar reasoning to `brightness_only`.

**Decision**: do not add `albumentations` as a project dependency at this
stage. The effect is real but too sparse (1% probability) to justify a new
dependency and a live experiment whose result would be dominated by sampling
noise at this scale. This can be revisited in Block 13 (error analysis) if
blur-sensitivity turns out to be a real failure mode.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Block 11 controlled augmentation ablation.")
    parser.add_argument("--config", default=Path("configs/experiments/augmentation_ablation.yaml"), type=Path)
    parser.add_argument("--project", default=Path("runs/detect/augmentation_ablation"), type=Path)
    parser.add_argument("--manifest", default=Path("data/prepared/manifest_train.json"), type=Path)
    parser.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    parser.add_argument("--start-experiment-num", type=int, default=9, help="First experiment_id number (E09 by default, continuing from Block 10's E02-E08).")
    return parser.parse_args()


def run_one(experiment_id: str, axis: str, plausibility: str, extra_kwargs: dict, common: dict, project: Path, git_commit: str, manifest_hash: str, plots: bool) -> dict:
    device = detect_device() if common["device"] == "auto" else common["device"]
    set_global_seed(common["seed"])

    logger.info("=== Experiment %s (augmentation: %s) ===", experiment_id, axis)
    logger.info("Plausibility assessment: %s", plausibility)
    logger.info("Augmentation overrides: %s", extra_kwargs)

    started_at = time.monotonic()
    result = run_training(
        model_arch=common["model_arch"],
        data_yaml=Path(common["data_yaml"]),
        output_project=project,
        run_name=experiment_id,
        image_size=common["image_size"],
        batch_size=common["batch_size"],
        epochs=common["epochs"],
        device=device,
        seed=common["seed"],
        workers=common["workers"],
        fraction=common["fraction"],
        plots=plots,
        validate=common["validate_during_training"],
        extra_train_kwargs={
            "optimizer": common["optimizer"],
            "lr0": common["learning_rate"],
            "momentum": common["momentum"],
            "weight_decay": common["weight_decay"],
            **extra_kwargs,
        },
    )
    duration = time.monotonic() - started_at

    from ultralytics import YOLO

    model = YOLO(result["best_weights"])
    val_results = model.val(data=common["data_yaml"], split="val", plots=False, verbose=False, device=device)

    record = ExperimentRecord(
        experiment_id=experiment_id,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=git_commit,
        seed=common["seed"],
        model_architecture=common["model_arch"],
        pretrained=common["pretrained"],
        dataset_manifest_hash=manifest_hash,
        image_size=common["image_size"],
        batch_size=common["batch_size"],
        epochs=common["epochs"],
        optimizer=result["resolved_hyperparameters"]["optimizer"],
        learning_rate=result["resolved_hyperparameters"]["learning_rate"],
        weight_decay=result["resolved_hyperparameters"]["weight_decay"],
        scheduler=result["resolved_hyperparameters"]["scheduler"],
        augmentation_config=result["resolved_hyperparameters"]["augmentation"],
        device=device,
        best_val_map50=float(val_results.box.map50),
        best_val_f1=None,
        precision=float(val_results.box.mp),
        recall=float(val_results.box.mr),
        training_duration_seconds=duration,
        notes=f"Block 11 augmentation ablation: {axis}. {plausibility}",
        compliance_notes="No external pretrained weights. YOLO_OFFLINE enforced. Augmentation applies to train split only.",
    )

    saved_batch_images = []
    if plots:
        save_dir = Path(result["save_dir"])
        saved_batch_images = sorted(str(p) for p in save_dir.glob("train_batch*.jpg"))

    return {"axis": axis, "plausibility": plausibility, "record": record, "saved_batch_images": saved_batch_images}


def build_report(results: list[dict], baseline_default_map50: float) -> str:
    lines = [
        "# Block 11. Augmentation Ablation",
        "",
        "**Scale note**: same small-fraction/few-epoch screening scale as Block 10, for direct "
        "comparability. Absolute mAP values are low; only relative effects matter here.",
        "",
        f"Reference: Block 10's E02 (Ultralytics' default combined augmentation bundle) scored "
        f"mAP@0.5={baseline_default_map50:.4f}. This block isolates each factor individually from "
        "a clean no-augmentation reference (E09) instead.",
        "",
        "## Results",
        "",
        "| Experiment | Augmentation | Plausibility | mAP@0.5 | Precision | Recall | Duration (s) |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for r in results:
        rec = r["record"]
        plausibility_short = r["plausibility"].split(", ")[0]
        lines.append(
            f"| {rec.experiment_id} | {r['axis']} | {plausibility_short} | {rec.best_val_map50:.4f} | "
            f"{rec.precision:.4f} | {rec.recall:.4f} | {rec.training_duration_seconds:.1f} |"
        )

    no_aug = next(r for r in results if r["axis"] == "none")
    lines += ["", "## Per-augmentation effect (relative to the no-augmentation reference)", ""]
    for r in results:
        if r["axis"] == "none":
            continue
        delta = r["record"].best_val_map50 - no_aug["record"].best_val_map50
        direction = "improved" if delta > 0 else ("worsened" if delta < 0 else "no change")
        lines.append(f"- **{r['axis']}**: mAP@0.5 {direction} by {delta:+.4f} vs. no-augmentation reference.")

    lines.append(BLUR_NOISE_ANALYSIS)

    lines += [
        "## Recommendation",
        "",
        "Per master spec: augmentation choice must weigh *semantic plausibility for this domain*, not "
        "just raw numbers at a tiny screening scale. Concretely:",
        "",
        "- Recommend **keeping**: horizontal flip, rotation (moderate), scaling, translation, "
        "brightness/contrast, conservative color jitter, all physically plausible for field-captured "
        "rice imagery, regardless of their small individual effect at this screening scale.",
        "- Recommend **excluding**: vertical flip, even if it measured a positive effect above, it is "
        "physically implausible for gravity-oriented plants and risks teaching the model orientations "
        "it will never see deployed. Domain reasoning overrides a marginal metric gain here.",
        "- **Mosaic**: kept only if its measured effect above is neutral-to-positive; if it clearly hurts "
        "at this scale, worth re-testing at full training scale before deciding (mosaic's benefits are "
        "generally more visible with more data/epochs than this screening pass uses).",
        "- Mild blur/noise: deliberately not adopted at this stage (see analysis above).",
        "",
        "This is a screening-scale recommendation to carry into Block 12 (class imbalance) and Block 14 "
        "(final config freeze), not a final decision on its own.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    setup_logging()
    args = parse_args()

    with args.config.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    common = config["common"]
    git_commit = get_git_commit()
    manifest_hash = compute_manifest_hash(args.manifest)

    results = []
    exp_num = args.start_experiment_num

    # No-augmentation reference point.
    no_aug_id = f"E{exp_num:02d}"
    results.append(run_one(no_aug_id, "none", "Reference point: all augmentation disabled.", config["no_augmentation"], common, args.project, git_commit, manifest_hash, plots=False))
    append_experiment(results[-1]["record"])
    exp_num += 1

    for variant in config["variants"]:
        exp_id = f"E{exp_num:02d}"
        plots = variant["id"] in VISUAL_VERIFICATION_VARIANTS
        result = run_one(
            exp_id, variant["augmentation"], variant["plausibility"],
            {**config["no_augmentation"], **variant["overrides"]},
            common, args.project, git_commit, manifest_hash, plots,
        )
        append_experiment(result["record"])
        results.append(result)
        logger.info("Experiment %s done: mAP@0.5=%.4f (%.1fs)", exp_id, result["record"].best_val_map50, result["record"].training_duration_seconds)
        exp_num += 1

    args.report_dir.mkdir(parents=True, exist_ok=True)
    # Baseline reference from Block 10's tracked E02.
    all_records = load_experiments()
    e02 = next(r for r in all_records if r["experiment_id"] == "E02")
    report = build_report(results, e02["best_val_map50"])
    (args.report_dir / "block11_augmentation_ablation.md").write_text(report, encoding="utf-8")

    (Path("artifacts/experiments") / "experiment_log.md").write_text(build_markdown_table(all_records), encoding="utf-8")

    verification_images = [img for r in results for img in r["saved_batch_images"]]

    print(report)
    print(f"\nVisual verification batch images saved: {verification_images}")
    print("Experiment log updated: artifacts/experiments/experiment_log.json")
    print("Report: artifacts/reports/block11_augmentation_ablation.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
