#!/usr/bin/env python3
"""Pelatihan dari nol di Kaggle yang tahan terhadap batas sesi 12 jam.

Pemakaian di sel notebook Kaggle (sesi pertama):
    !python scripts/kaggle_train.py --config configs/kaggle/yolov8s_640_300ep.yaml \
        --data-root /kaggle/input/agridata-yolo

Sesi berikutnya, setelah output sesi sebelumnya ditambahkan sebagai input:
    !python scripts/kaggle_train.py --config configs/kaggle/yolov8s_640_300ep.yaml \
        --data-root /kaggle/input/agridata-yolo \
        --resume-from /kaggle/input/<output-sesi-sebelumnya>/runs/yolov8s_640_300ep

Proses induk menjalankan pelatihan sebagai subproses dan mengawasinya. Begitu
anggaran waktu habis, subproses dihentikan sebelum Kaggle mematikan sesi,
sehingga last.pt yang masih memuat state optimizer tersimpan utuh di
/kaggle/working dan dapat dilanjutkan. Penghentian normal oleh Ultralytics
tidak dipakai karena akan melucuti state optimizer dari last.pt.

Model selalu dibangun dari definisi .yaml (pretrained=False) atau dilanjutkan
dari checkpoint milik project ini sendiri. Data uji tidak disentuh.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

AUGMENTATION_OVERRIDE_KEYS = {
    "hsv_h", "hsv_s", "hsv_v", "degrees", "translate", "scale", "shear",
    "perspective", "flipud", "fliplr", "mosaic", "mixup", "copy_paste",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Session-safe compliant training on Kaggle.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--data-root", required=True, type=Path, help="Folder hasil scripts/export_kaggle_dataset.py.")
    parser.add_argument("--work-dir", default=Path("/kaggle/working"), type=Path)
    parser.add_argument("--run-name", default=None, help="Bawaan: nama berkas config tanpa ekstensi.")
    parser.add_argument("--resume-from", default=None, type=Path, help="Folder run dari output sesi sebelumnya.")
    parser.add_argument("--device", default="0,1", help="'0,1' untuk T4 x2, '0' untuk P100.")
    parser.add_argument("--budget-hours", default=11.0, type=float, help="Sisakan margin di bawah batas 12 jam Kaggle.")
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg["pretrained"] is False, "REFUSING TO TRAIN: pretrained must be False."
    assert not cfg["model_arch"].endswith((".pt", ".pth", ".ckpt")), "REFUSING TO TRAIN: model_arch looks like a checkpoint."
    return cfg


def write_data_yaml(data_root: Path, work_dir: Path) -> Path:
    with (data_root / "data.yaml").open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["path"] = str(data_root.resolve())
    out = work_dir / "data.yaml"
    with out.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
    return out


def checkpoint_state(path: Path) -> str:
    """'resumable', 'finished', atau 'invalid' untuk sebuah last.pt."""
    import torch

    try:
        ckpt = torch.load(path, map_location="cpu", weights_only=False)
    except Exception:
        return "invalid"
    # Ultralytics menyetel epoch=-1 dan membuang optimizer saat pelatihan selesai normal.
    if ckpt.get("epoch", -1) == -1 or ckpt.get("optimizer") is None:
        return "finished"
    return "resumable"


def run_child(args: argparse.Namespace, cfg: dict, run_dir: Path, data_yaml: Path) -> int:
    from agridata.seed import set_global_seed
    from agridata.training.train import build_compliant_model

    from ultralytics import YOLO

    last = run_dir / "weights" / "last.pt"
    if last.exists():
        print(f"Melanjutkan dari {last}")
        model = YOLO(str(last))
        # Checkpoint menyimpan path absolut dari sesi sebelumnya. save_dir dan
        # data ditimpa agar keluaran tetap di run_dir milik sesi ini.
        model.train(resume=True, device=args.device, data=str(data_yaml), save_dir=str(run_dir.resolve()))
        return 0

    set_global_seed(cfg["seed"])
    model = build_compliant_model(cfg["model_arch"], pretrained=False)
    model.train(
        data=str(data_yaml),
        imgsz=cfg["image_size"],
        batch=cfg["batch_size"],
        epochs=cfg["epochs"],
        patience=cfg["patience"],
        optimizer=cfg["optimizer"],
        lr0=cfg["learning_rate"],
        momentum=cfg["momentum"],
        weight_decay=cfg["weight_decay"],
        cos_lr=cfg["cos_lr"],
        close_mosaic=cfg["close_mosaic"],
        device=args.device,
        seed=cfg["seed"],
        workers=cfg["workers"],
        pretrained=False,
        # plots dimatikan karena pembuatan plot mencoba mengunduh font, yang
        # gagal di bawah YOLO_OFFLINE. results.csv tetap ditulis setiap epoch.
        plots=False,
        val=True,
        project=str(run_dir.parent.resolve()),
        name=run_dir.name,
        exist_ok=True,
        verbose=True,
        **{k: cfg[k] for k in AUGMENTATION_OVERRIDE_KEYS if k in cfg},
    )
    return 0


def backup_if_stable(last: Path, backup: Path, settle_seconds: float = 30.0) -> None:
    """Menyalin last.pt ke cadangan bila berubah dan sudah tidak sedang ditulis."""
    if not last.exists():
        return
    mtime = last.stat().st_mtime
    if time.time() - mtime < settle_seconds:
        return
    if backup.exists() and backup.stat().st_mtime >= mtime:
        return
    shutil.copy2(last, backup)


def summarize(run_dir: Path) -> None:
    results = run_dir / "results.csv"
    if not results.exists():
        print("results.csv belum ada.")
        return
    with results.open("r", encoding="utf-8") as f:
        rows = [{k.strip(): v.strip() for k, v in r.items()} for r in csv.DictReader(f)]
    if not rows:
        return
    best = max(rows, key=lambda r: float(r["metrics/mAP50(B)"]))
    print(f"Epoch selesai: {rows[-1]['epoch']}")
    print(f"mAP@0.5 valid terbaik sejauh ini: {float(best['metrics/mAP50(B)']):.4f} (epoch {best['epoch']})")


def run_parent(args: argparse.Namespace, run_dir: Path) -> int:
    if args.resume_from and not run_dir.exists():
        print(f"Menyalin run sebelumnya dari {args.resume_from}")
        shutil.copytree(args.resume_from, run_dir)

    last = run_dir / "weights" / "last.pt"
    backup = run_dir / "weights" / "last_backup.pt"
    if last.exists():
        state = checkpoint_state(last)
        if state == "finished":
            print("Pelatihan sudah selesai sebelumnya. Tidak ada yang dilanjutkan.")
            summarize(run_dir)
            return 0
        if state == "invalid" and backup.exists():
            print("last.pt rusak, memakai last_backup.pt.")
            shutil.copy2(backup, last)

    cmd = [sys.executable, __file__, *sys.argv[1:], "--child"]
    child = subprocess.Popen(cmd, start_new_session=True)
    deadline = time.time() + args.budget_hours * 3600
    print(f"Pelatihan berjalan (pid {child.pid}), anggaran {args.budget_hours} jam.")

    while child.poll() is None:
        time.sleep(60)
        backup_if_stable(last, backup)
        if time.time() > deadline:
            print("Anggaran waktu habis, menghentikan pelatihan agar checkpoint tetap dapat dilanjutkan.")
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=120)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            break

    if last.exists() and checkpoint_state(last) == "invalid" and backup.exists():
        print("last.pt tertulis sebagian saat dihentikan, dipulihkan dari last_backup.pt.")
        shutil.copy2(backup, last)

    summarize(run_dir)
    if last.exists() and checkpoint_state(last) == "resumable":
        print("\nBELUM SELESAI. Jalankan sesi berikutnya dengan --resume-from menunjuk folder run ini.")
    elif child.returncode not in (0, None, -signal.SIGTERM, -signal.SIGKILL):
        print(f"Subproses pelatihan gagal dengan kode {child.returncode}.")
        return child.returncode
    return 0


def main() -> int:
    args = parse_args()
    os.environ.setdefault("YOLO_OFFLINE", "1")
    cfg = load_config(args.config)
    run_name = args.run_name or args.config.stem
    run_dir = args.work_dir / "runs" / run_name
    args.work_dir.mkdir(parents=True, exist_ok=True)

    if args.child:
        return run_child(args, cfg, run_dir, args.work_dir / "data.yaml")

    write_data_yaml(args.data_root, args.work_dir)
    return run_parent(args, run_dir)


if __name__ == "__main__":
    raise SystemExit(main())
