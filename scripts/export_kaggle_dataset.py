#!/usr/bin/env python3
"""Mengekspor data/prepared menjadi folder mandiri untuk diunggah ke Kaggle.

Pemakaian:
    python scripts/export_kaggle_dataset.py --out ~/agridata_kaggle_dataset

data/prepared merujuk citra lewat symlink ke dataset resmi, sehingga tidak bisa
diunggah apa adanya. Skrip ini menyalin isi sebenarnya (citra dan label YOLO
11 kelas canonical) tanpa mengubah satu byte pun, mempertahankan split resmi,
dan menulis data.yaml dengan path relatif. Folder keluaran berada di luar
repository karena berisi dataset mentah yang tidak boleh di-commit.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import yaml

SPLITS = ("train", "valid", "test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export prepared YOLO dataset (symlinks dereferenced) for Kaggle.")
    parser.add_argument("--prepared-dir", default=Path("data/prepared"), type=Path)
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out = args.out.expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        print(f"Menolak menimpa: {out} sudah berisi berkas.", file=sys.stderr)
        return 1

    with (args.prepared_dir / "data.yaml").open("r", encoding="utf-8") as f:
        src_yaml = yaml.safe_load(f)

    for split in SPLITS:
        for kind in ("images", "labels"):
            src = args.prepared_dir / split / kind
            dst = out / split / kind
            dst.mkdir(parents=True, exist_ok=True)
            n = 0
            for p in sorted(src.iterdir()):
                # copyfile mengikuti symlink, sehingga yang tersalin adalah isi citra asli.
                shutil.copyfile(p, dst / p.name)
                n += 1
            print(f"{split}/{kind}: {n} berkas")

    data_yaml = {
        "path": ".",  # ditimpa oleh scripts/kaggle_train.py dengan path input Kaggle
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "names": src_yaml["names"],
    }
    with (out / "data.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(data_yaml, f, sort_keys=False, allow_unicode=True)

    print(f"\nSelesai: {out}")
    print("Unggah folder ini sebagai Kaggle Dataset PRIVATE (dataset lomba tidak boleh dipublikasikan).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
