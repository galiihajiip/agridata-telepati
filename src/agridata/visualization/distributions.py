"""Dataset distribution plots for EDA (Block 4).

All functions save a figure to disk and close it — nothing is shown
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
