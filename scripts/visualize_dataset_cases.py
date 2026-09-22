#!/usr/bin/env python3
"""Visualisasi kasus khas pada dataset: adegan padat, objek kecil, kasus sulit.

Setiap kelompok dipilih dengan aturan eksplisit dan deterministik, bukan
dipilih berdasarkan penampilan. Aturan dicetak bersama gambar dan disimpan
pada laporan JSON.

Penggunaan:
    python scripts/visualize_dataset_cases.py
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.dataset.stats import load_canonical_split  # noqa: E402
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.visualization.images import draw_annotated_image  # noqa: E402

logger = logging.getLogger("agridata.scripts.visualize_dataset_cases")

SMALL_OBJECT_THRESHOLD = 0.01


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualisasi kasus khas pada dataset.")
    parser.add_argument("--dataset-root", default=Path("Telepati 8.0 Datasets"), type=Path)
    parser.add_argument("--split", default="train")
    parser.add_argument("--num-examples", type=int, default=3)
    parser.add_argument("--figures-dir", default=Path("artifacts/figures/final_submission"), type=Path)
    parser.add_argument("--report-dir", default=Path("artifacts/reports"), type=Path)
    return parser.parse_args()


def render(split_data, image_ids, dataset_root, split, title, output_path, subtitles):
    n = len(image_ids)
    fig, axes = plt.subplots(1, n, figsize=(6.5 * n, 6.5))
    if n == 1:
        axes = [axes]
    ann_by_image: dict[int, list] = {}
    for ann in split_data.annotations:
        ann_by_image.setdefault(ann.image_id, []).append(ann)

    for ax, image_id, sub in zip(axes, image_ids, subtitles):
        rec = split_data.images_by_id[image_id]
        img = draw_annotated_image(dataset_root / split / rec.file_name, rec, ann_by_image[image_id])
        ax.imshow(img)
        ax.set_title(sub, fontsize=10)
        ax.axis("off")
    fig.suptitle(title, y=1.0)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return output_path


def main() -> int:
    setup_logging()
    args = parse_args()

    split_data = load_canonical_split(args.dataset_root, args.split, "_annotations.coco.json")

    ann_by_image: dict[int, list] = {}
    for ann in split_data.annotations:
        ann_by_image.setdefault(ann.image_id, []).append(ann)

    # Adegan padat: jumlah anotasi terbanyak dalam satu citra.
    crowded = sorted(ann_by_image, key=lambda i: (-len(ann_by_image[i]), i))[: args.num_examples]

    # Objek kecil: citra dengan proporsi kotak di bawah ambang paling tinggi,
    # dibatasi pada citra yang memuat minimal tiga anotasi agar bermakna.
    def small_share(image_id: int) -> float:
        rec = split_data.images_by_id[image_id]
        area = rec.width * rec.height
        if area <= 0:
            return 0.0
        anns = ann_by_image[image_id]
        small = sum(1 for a in anns if (a.bbox[2] * a.bbox[3]) / area < SMALL_OBJECT_THRESHOLD)
        return small / len(anns)

    eligible = [i for i in ann_by_image if len(ann_by_image[i]) >= 3]
    small_objects = sorted(eligible, key=lambda i: (-small_share(i), i))[: args.num_examples]

    # Kasus sulit: padat sekaligus didominasi objek kecil.
    def difficulty(image_id: int) -> float:
        return len(ann_by_image[image_id]) * small_share(image_id)

    difficult = sorted(ann_by_image, key=lambda i: (-difficulty(i), i))[: args.num_examples]

    groups = {
        "crowded": (
            crowded,
            "Adegan padat: citra dengan jumlah anotasi terbanyak",
            [f"{len(ann_by_image[i])} anotasi" for i in crowded],
        ),
        "small_objects": (
            small_objects,
            f"Objek kecil: proporsi kotak di bawah {SMALL_OBJECT_THRESHOLD:.0%} luas citra tertinggi",
            [f"{small_share(i):.0%} objek kecil, {len(ann_by_image[i])} anotasi" for i in small_objects],
        ),
        "difficult": (
            difficult,
            "Kasus sulit: padat sekaligus didominasi objek kecil",
            [f"{len(ann_by_image[i])} anotasi, {small_share(i):.0%} kecil" for i in difficult],
        ),
    }

    outputs = {}
    for key, (ids, title, subs) in groups.items():
        path = args.figures_dir / f"{key}_{args.split}.png"
        render(split_data, ids, args.dataset_root, args.split, title, path, subs)
        outputs[key] = {"figure": str(path), "image_ids": ids}
        logger.info("%s: %s", key, path)

    report = {
        "split": args.split,
        "small_object_threshold": SMALL_OBJECT_THRESHOLD,
        "aturan_pemilihan": {
            "crowded": "jumlah anotasi terbanyak dalam satu citra, diurutkan menurun lalu image_id",
            "small_objects": "proporsi kotak di bawah ambang objek kecil tertinggi, minimal 3 anotasi per citra",
            "difficult": "hasil kali jumlah anotasi dengan proporsi objek kecil, tertinggi",
        },
        "catatan": "Seluruh pemilihan bersifat deterministik dan tidak berdasarkan penampilan visual.",
        "groups": outputs,
    }
    args.report_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.report_dir / f"dataset_cases_{args.split}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Anotasi terbanyak dalam satu citra: {len(ann_by_image[crowded[0]])}")
    print(f"Laporan: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
