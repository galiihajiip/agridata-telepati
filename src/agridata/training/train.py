"""Titik masuk pelatihan yang patuh terhadap batasan kompetisi.

Modul ini tidak pernah merujuk berkas checkpoint. Model selalu dibangun dari
definisi arsitektur .yaml dengan pretrained=False, sesuai larangan penggunaan
external pretrained weights.

`YOLO_OFFLINE` diaktifkan sebelum ultralytics diimpor karena
`ultralytics.utils.ONLINE` dihitung sekali saat impor dari variabel
lingkungan tersebut. Dengan begitu setiap panggilan jaringan yang tidak
diinginkan, termasuk pengunduhan checkpoint, gagal dengan ConnectionError
dan bukan berhasil secara diam-diam.
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
    """Membangun model YOLO tanpa external pretrained weights.

    Raises:
        ValueError: bila `model_arch` menyerupai berkas checkpoint
            (.pt) rather than an architecture-only definition (.yaml), or if
            atau bila `pretrained` bernilai True. Keduanya melanggar
            larangan penggunaan external pretrained weights.
    """
    if pretrained:
        raise ValueError("pretrained=True tidak diizinkan pada project ini.")
    if model_arch.endswith((".pt", ".pth", ".ckpt")):
        raise ValueError(
            f"model_arch '{model_arch}' menyerupai berkas checkpoint. "
            "Use an architecture-only .yaml definition instead (e.g. 'yolov8n.yaml')."
        )

    logger.info("Membangun model dari definisi arsitektur '%s' (pretrained=False)", model_arch)
    model = YOLO(model_arch)
    logger.info("Model dibangun dari arsitektur saja. Tidak ada checkpoint eksternal yang dirujuk maupun diunduh.")
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
    """Menjalankan pelatihan yang patuh dan mengembalikan lokasi hasil utama.

    `pretrained=False` tetap diteruskan ke `model.train()` sebagai pengaman
    berlapis, meskipun model sudah dibangun dari definisi `.yaml` tanpa bobot
    pada `build_compliant_model`.

    `validate=False` melewati validasi per epoch pada seluruh split validasi,
    yang mahal bila diulang setiap epoch pada banyak percobaan. Diverifikasi
    melalui sumber `engine/trainer.py` bahwa pemilihan `best.pt` tetap bekerja
    dengan jatuh kembali ke skor fitness berbasis loss. Gunakan
    `agridata.metrics` atau `scripts/evaluate.py`
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

    # Path `project` yang relatif diselesaikan Ultralytics terhadap `runs_dir`
    # pada setelan globalnya, bukan terhadap direktori kerja saat ini, sehingga
    # lokasi keluaran bergantung pada konfigurasi tiap mesin. Path absolut
    # menghindari hal itu agar keluaran selalu berada di lokasi yang ditentukan
    # kode project ini.
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

    # `trainer.args.optimizer` tetap bernilai "auto" meskipun Ultralytics sudah
    # memilih optimizer konkret secara internal. Pilihan yang sudah diselesaikan
    # hanya ada pada objek optimizer, sehingga dibaca dari sana agar pencatatan
    # percobaan merekam yang benar-benar dipakai.
    # `param_groups[i]["lr"]` menurun sepanjang pelatihan karena scheduler.
    # value the scheduler was actually initialized with is preserved in
    # "initial_lr" (set once at optimizer/scheduler construction, see
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
