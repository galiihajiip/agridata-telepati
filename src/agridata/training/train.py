"""Compliant baseline training entrypoint (Block 6+).

This module NEVER references a pretrained checkpoint (.pt) — models are
always constructed from an architecture-only .yaml definition with
pretrained=False, per the competition's explicit prohibition on external
pretrained weights (master spec Section 8).

`YOLO_OFFLINE` is forced on *before* importing ultralytics, because
`ultralytics.utils.ONLINE` is computed once at import time from that
environment variable. With it set, any accidental network call this code
does not intend (telemetry sync, an update check, or — critically — a
checkpoint download) fails loudly with a `ConnectionError` instead of
silently succeeding. This gives a genuine, verifiable "network blocked" test
rather than just a configuration claim.
"""

from __future__ import annotations

import logging
import os

os.environ.setdefault("YOLO_OFFLINE", "1")

from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

from ultralytics import YOLO  # noqa: E402

logger = logging.getLogger("agridata.training")


def build_compliant_model(model_arch: str, pretrained: bool) -> YOLO:
    """Construct a YOLO model with zero external pretrained weights.

    Raises:
        ValueError: if `model_arch` looks like a pretrained checkpoint file
            (.pt) rather than an architecture-only definition (.yaml), or if
            `pretrained` is True — both would violate the competition's
            prohibition on external pretrained weights.
    """
    if pretrained:
        raise ValueError("pretrained=True is not permitted in this project — see master spec Section 8.")
    if model_arch.endswith((".pt", ".pth", ".ckpt")):
        raise ValueError(
            f"model_arch '{model_arch}' looks like a pretrained checkpoint file. "
            "Use an architecture-only .yaml definition instead (e.g. 'yolov8n.yaml')."
        )

    logger.info("Building model from architecture definition '%s' (pretrained=False)", model_arch)
    model = YOLO(model_arch)
    logger.info("Model built from architecture only. No external checkpoint was referenced or downloaded.")
    return model


def run_training(
    model_arch: str,
    data_yaml: Path,
    output_project: Path,
    run_name: str,
    image_size: int,
    batch_size: int,
    epochs: int,
    device: str,
    seed: int,
    workers: int = 2,
    fraction: float = 1.0,
    plots: bool = False,
    validate: bool = True,
    extra_train_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a compliant training job and return key result paths.

    `pretrained=False` is passed explicitly to `model.train()` as a
    belt-and-suspenders safeguard, even though the model was already built
    from a weights-free `.yaml` definition in `build_compliant_model`.

    `validate=False` skips Ultralytics' per-epoch validation on the full
    validation split (expensive when repeated every epoch across many
    experiments) — verified via source (`engine/trainer.py`) that `best.pt`
    selection still works correctly in this case, falling back to a
    loss-based fitness score. Use `agridata.metrics`/`scripts/evaluate.py`
    for the authoritative post-hoc mAP@0.5/F1 instead.

    `extra_train_kwargs` passes additional Ultralytics train() arguments
    through directly (e.g. optimizer, lr0, momentum, weight_decay,
    augmentation overrides) for controlled hyperparameter experiments
    (Block 10) without bloating this function's fixed signature.
    """
    model = build_compliant_model(model_arch, pretrained=False)

    logger.info(
        "Starting training: data=%s imgsz=%d batch=%d epochs=%d device=%s seed=%d fraction=%.3f",
        data_yaml, image_size, batch_size, epochs, device, seed, fraction,
    )

    # Ultralytics resolves a *relative* `project` path against the global,
    # machine-specific Ultralytics settings' `runs_dir` (see
    # ultralytics.cfg.get_save_dir) rather than the current working
    # directory — silently making output location depend on per-machine
    # global config. Passing an absolute path here bypasses that entirely,
    # so outputs always land exactly where this project's code says they
    # should, regardless of the audit machine's global Ultralytics settings.
    model.train(
        data=str(data_yaml),
        imgsz=image_size,
        batch=batch_size,
        epochs=epochs,
        device=device,
        seed=seed,
        workers=workers,
        fraction=fraction,
        pretrained=False,
        plots=plots,
        val=validate,
        project=str(Path(output_project).resolve()),
        name=run_name,
        exist_ok=True,
        verbose=True,
        **(extra_train_kwargs or {}),
    )

    trainer = model.trainer

    # `trainer.args.optimizer` stays "auto" (the raw config value) even after
    # Ultralytics auto-selects a concrete optimizer (e.g. AdamW) internally —
    # the resolved choice only exists on the instantiated optimizer object.
    # Read it there so the experiment tracker (Block 9) records what actually
    # ran, not the unresolved config string.
    # `param_groups[i]["lr"]` decays over training (scheduler-driven); the
    # value the scheduler was actually initialized with is preserved in
    # "initial_lr" (set once at optimizer/scheduler construction — see
    # torch.optim.lr_scheduler.LRScheduler.__init__). That, not the decayed
    # end-of-training value, is the meaningful "learning rate" hyperparameter
    # for experiment tracking.
    resolved_optimizer = type(trainer.optimizer).__name__ if trainer.optimizer is not None else trainer.args.optimizer
    resolved_lr = (
        trainer.optimizer.param_groups[0].get("initial_lr", trainer.optimizer.param_groups[0]["lr"])
        if trainer.optimizer is not None
        else trainer.args.lr0
    )
    resolved_weight_decay = (
        next((g["weight_decay"] for g in trainer.optimizer.param_groups if g.get("weight_decay")), 0.0)
        if trainer.optimizer is not None
        else trainer.args.weight_decay
    )

    augmentation_config = {
        key: getattr(trainer.args, key)
        for key in (
            "hsv_h", "hsv_s", "hsv_v", "degrees", "translate", "scale", "shear",
            "perspective", "flipud", "fliplr", "bgr", "mosaic", "mixup", "copy_paste",
        )
    }

    return {
        "save_dir": str(trainer.save_dir),
        "best_weights": str(trainer.best) if trainer.best and Path(trainer.best).exists() else None,
        "last_weights": str(trainer.last) if trainer.last and Path(trainer.last).exists() else None,
        "metrics": {k: float(v) for k, v in (trainer.metrics or {}).items()},
        "resolved_hyperparameters": {
            "optimizer": resolved_optimizer,
            "learning_rate": float(resolved_lr),
            "weight_decay": float(resolved_weight_decay),
            "scheduler": "cosine" if trainer.args.cos_lr else "linear",
            "augmentation": augmentation_config,
        },
    }
