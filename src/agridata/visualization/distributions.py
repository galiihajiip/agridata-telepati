"""Dataset distribution plots for EDA (Block 4).

All functions save a figure to disk and close it. Nothing is shown
interactively, since this runs from a script/CI context.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: no display backend required
import matplotlib.pyplot as plt

from agridata.dataset.mapping import CANONICAL_CLASSES
from agridata.visualization.images import CLASS_COLORS


def _ordered_counts(counts: Counter[str]) -> tuple[list[str], list[int]]:
    """Return (labels, values) in fixed canonical class order (0 if absent)."""
    labels = list(CANONICAL_CLASSES)
    values = [counts.get(cls, 0) for cls in labels]
    return labels, values


def plot_class_counts(counts: Counter[str], title: str, output_path: Path) -> Path:
    """Bar chart of a per-class count (instance count or image count)."""
    labels, values = _ordered_counts(counts)
    colors = [CLASS_COLORS[label] for label in labels]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(labels, values, color=colors)
    ax.set_title(title)
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=45)
    for tick in ax.get_xticklabels():
        tick.set_ha("right")
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=120)
    plt.close(fig)
    return output_path


def plot_bbox_size_distribution(bbox_dims: list[tuple[float, float]], title: str, output_path: Path) -> Path:
    """Scatter of bbox width vs height, to visualize size/aspect-ratio spread."""
    widths = [w for w, _ in bbox_dims]
    heights = [h for _, h in bbox_dims]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(widths, heights, s=4, alpha=0.3)
    ax.set_xlabel("bbox width (px)")
    ax.set_ylabel("bbox height (px)")
    ax.set_title(title)
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=120)
    plt.close(fig)
    return output_path


def plot_image_dimension_distribution(image_dims: list[tuple[int, int]], title: str, output_path: Path) -> Path:
    """Scatter of image width vs height, to visualize resolution spread."""
    widths = [w for w, _ in image_dims]
    heights = [h for _, h in image_dims]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(widths, heights, s=8, alpha=0.4, color="#4363d8")
    ax.set_xlabel("image width (px)")
    ax.set_ylabel("image height (px)")
    ax.set_title(title)
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=120)
    plt.close(fig)
    return output_path


def _save(fig, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=120)
    plt.close(fig)
    return output_path


def plot_split_overview(split_counts: dict[str, dict[str, int]], output_path: Path) -> Path:
    """Grouped bars: jumlah citra dan jumlah anotasi per split."""
    splits = list(split_counts.keys())
    images = [split_counts[s]["images"] for s in splits]
    annotations = [split_counts[s]["annotations"] for s in splits]
    x = range(len(splits))
    width = 0.38

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar([i - width / 2 for i in x], images, width, label="Jumlah citra", color="#4363d8")
    ax.bar([i + width / 2 for i in x], annotations, width, label="Jumlah anotasi", color="#e6994c")
    ax.set_xticks(list(x))
    ax.set_xticklabels(splits)
    ax.set_ylabel("Jumlah")
    ax.set_title("Distribusi citra dan anotasi per split")
    ax.legend()
    for i, (im, an) in enumerate(zip(images, annotations)):
        ax.text(i - width / 2, im, f"{im:,}", ha="center", va="bottom", fontsize=8)
        ax.text(i + width / 2, an, f"{an:,}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    return _save(fig, output_path)


def plot_class_distribution_comparison(
    instance_counts: dict[str, int],
    image_counts: dict[str, int],
    title: str,
    output_path: Path,
) -> Path:
    """Bandingkan jumlah instance dan jumlah citra per kelas dalam satu grafik.

    Dua besaran ini berbeda: satu citra dapat memuat banyak instance, sehingga
    kelas dengan banyak instance belum tentu tersebar di banyak citra.
    """
    labels = list(CANONICAL_CLASSES)
    inst = [instance_counts.get(c, 0) for c in labels]
    imgs = [image_counts.get(c, 0) for c in labels]
    y = range(len(labels))
    height = 0.4

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh([i + height / 2 for i in y], inst, height, label="Jumlah instance", color="#4363d8")
    ax.barh([i - height / 2 for i in y], imgs, height, label="Jumlah citra", color="#9dc6e0")
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Jumlah")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return _save(fig, output_path)


def plot_relative_area_distribution(
    relative_areas: list[float],
    title: str,
    output_path: Path,
    small_object_threshold: float = 0.01,
) -> Path:
    """Histogram luas bounding box relatif terhadap luas citranya (skala log)."""
    values = [r for r in relative_areas if r > 0]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(values, bins=60, color="#4363d8", log=True)
    ax.axvline(
        small_object_threshold,
        color="#c1432f",
        linestyle="--",
        label=f"Ambang objek kecil ({small_object_threshold:.0%} luas citra)",
    )
    ax.set_xlabel("Luas bounding box relatif terhadap luas citra")
    ax.set_ylabel("Frekuensi (skala log)")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return _save(fig, output_path)


def plot_aspect_ratio_distribution(aspect_ratios: list[float], title: str, output_path: Path) -> Path:
    """Histogram rasio aspek bounding box (lebar dibagi tinggi)."""
    clipped = [min(r, 6.0) for r in aspect_ratios if r > 0]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(clipped, bins=60, color="#5a9367")
    ax.axvline(1.0, color="#333333", linestyle="--", label="Rasio 1:1 (persegi)")
    ax.set_xlabel("Rasio aspek bounding box (lebar / tinggi, dipotong pada 6,0)")
    ax.set_ylabel("Frekuensi")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return _save(fig, output_path)


def plot_instances_vs_performance(
    instance_counts: dict[str, int],
    per_class_ap: dict[str, float],
    output_path: Path,
) -> Path:
    """Sebar jumlah instance latih terhadap AP@0.5 per kelas.

    Hubungan yang ditampilkan bersifat observasional, bukan kausal.
    """
    classes = [c for c in CANONICAL_CLASSES if c in per_class_ap]
    x = [instance_counts.get(c, 0) for c in classes]
    y = [per_class_ap[c] for c in classes]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(x, y, s=60, color="#4363d8")
    for cls, xi, yi in zip(classes, x, y):
        ax.annotate(cls, (xi, yi), fontsize=8, xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("Jumlah instance pada split train")
    ax.set_ylabel("AP@0.5 pada split valid")
    ax.set_title("Hubungan observasional antara jumlah data dan performa per kelas")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return _save(fig, output_path)


def plot_training_curves(history: dict[str, list[float]], output_path: Path) -> Path:
    """Kurva training: komponen loss dan metrik validasi per epoch."""
    epochs = history.get("epoch", [])

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

    for key, label in (
        ("train/box_loss", "box loss"),
        ("train/cls_loss", "cls loss"),
        ("train/dfl_loss", "dfl loss"),
    ):
        if key in history:
            axes[0].plot(epochs, history[key], label=label)
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].set_title("Komponen loss pada data latih")
    axes[0].legend()
    axes[0].grid(alpha=0.25)

    for key, label in (
        ("metrics/mAP50(B)", "mAP@0.5"),
        ("metrics/mAP50-95(B)", "mAP@0.5:0.95"),
        ("metrics/precision(B)", "precision"),
        ("metrics/recall(B)", "recall"),
    ):
        if key in history:
            axes[1].plot(epochs, history[key], label=label)
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Nilai metrik")
    axes[1].set_title("Metrik pada data validasi")
    axes[1].legend()
    axes[1].grid(alpha=0.25)

    fig.tight_layout()
    return _save(fig, output_path)


def plot_per_class_ap(per_class_ap: dict[str, float], output_path: Path) -> Path:
    """Bar horizontal AP@0.5 per kelas, diurutkan dari tertinggi."""
    ordered = sorted(per_class_ap.items(), key=lambda kv: kv[1], reverse=True)
    labels = [k for k, _ in ordered]
    values = [v for _, v in ordered]
    colors = [CLASS_COLORS.get(label, "#4363d8") for label in labels]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(labels, values, color=colors)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("AP@0.5")
    ax.set_title("AP@0.5 per kelas canonical pada split valid")
    for i, v in enumerate(values):
        ax.text(v + 0.01, i, f"{v:.4f}", va="center", fontsize=8)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    return _save(fig, output_path)


def plot_ofat_deltas(baseline_id: str, rows: list[dict], output_path: Path) -> Path:
    """Selisih mAP@0.5 tiap varian OFAT terhadap baseline pada skala penyaringan."""
    labels = [f"{r['experiment_id']}: {r['factor']}" for r in rows]
    deltas = [r["delta"] for r in rows]
    colors = ["#5a9367" if d > 0 else "#c1432f" for d in deltas]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(labels, deltas, color=colors)
    ax.invert_yaxis()
    ax.axvline(0, color="#333333", linewidth=1)
    ax.set_xlabel(f"Selisih mAP@0.5 terhadap baseline {baseline_id}")
    ax.set_title("Pengaruh satu faktor pada satu waktu (skala penyaringan)")
    for i, d in enumerate(deltas):
        offset = 0.00015 if d >= 0 else -0.00015
        ax.text(d + offset, i, f"{d:+.4f}", va="center",
                ha="left" if d >= 0 else "right", fontsize=8)
    ax.margins(x=0.18)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    return _save(fig, output_path)


def plot_experiment_overview(experiments: list[dict], output_path: Path) -> Path:
    """Sebaran mAP@0.5 seluruh percobaan, diberi warna menurut ukuran citra."""
    ids = [e["experiment_id"] for e in experiments]
    values = [e["best_val_map50"] for e in experiments]
    colors = ["#4363d8" if e["image_size"] == 640 else "#9dc6e0" for e in experiments]

    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.bar(ids, values, color=colors)
    ax.set_ylabel("mAP@0.5 (skala penyaringan)")
    ax.set_xlabel("ID percobaan")
    ax.set_title("Hasil 21 percobaan terkontrol pada skala penyaringan")
    handles = [
        plt.Rectangle((0, 0), 1, 1, color="#4363d8"),
        plt.Rectangle((0, 0), 1, 1, color="#9dc6e0"),
    ]
    ax.legend(handles, ["image size 640", "image size 320"], loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    return _save(fig, output_path)


def plot_threshold_sensitivity(rows: list[dict], output_path: Path) -> Path:
    """Kurva precision, recall, dan F1 lokal terhadap confidence threshold."""
    thresholds = [r["threshold"] for r in rows]

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(thresholds, [r["precision"] for r in rows], marker="o", label="Precision")
    ax.plot(thresholds, [r["recall"] for r in rows], marker="s", label="Recall")
    ax.plot(thresholds, [r["f1"] for r in rows], marker="^", label="F1 lokal")

    best = max(rows, key=lambda r: r["f1"])
    ax.axvline(
        best["threshold"],
        color="#c1432f",
        linestyle="--",
        label=f"F1 tertinggi pada threshold {best['threshold']:.2f}",
    )
    ax.set_xlabel("Confidence threshold")
    ax.set_ylabel("Nilai metrik")
    ax.set_title("Sensitivitas metrik lokal terhadap confidence threshold (split valid)")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return _save(fig, output_path)
