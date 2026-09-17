#!/usr/bin/env python3
"""Deterministic dataset preparation for object detection training (Block 5).

Builds a training-ready representation from the RAW OFFICIAL DATASET without
altering it:

    raw dataset -> canonical class mapping -> YOLO-format labels + manifest

Images are exposed via symlinks (never copied), so the prepared output does
not duplicate the ~650MB of official dataset bytes and is safe to regenerate
locally at any time. A full JSON manifest per split preserves traceability
to original image IDs, raw category names, and canonical/model class IDs.

One confirmed cross-split exact-duplicate image (Block 2 forensic audit,
train vs test, identical MD5) is excluded from the TRAIN split here to
prevent training on data that is byte-identical to a held-out test image.

Usage:
    python scripts/prepare_dataset.py --dataset-root "<PATH>" --output-dir data/prepared
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.dataset.mapping import (  # noqa: E402
    CANONICAL_ID_TO_NAME,
    MAPPING_VERSION,
    map_raw_category,
)
from agridata.logging_utils import setup_logging  # noqa: E402
from agridata.seed import set_global_seed  # noqa: E402

logger = logging.getLogger("agridata.scripts.prepare_dataset")

SPLITS = ("train", "valid", "test")
DEFAULT_ANNOTATION_FILENAME = "_annotations.coco.json"
# Matches the Block 2 forensic audit's evidence-based tolerance: every
# observed "exceeds bounds" case in this dataset is <=0.5px (Roboflow float
# export rounding). Anything beyond this is treated as a genuine error.
BBOX_BOUNDARY_TOLERANCE_PX = 1.0


@dataclass
class PreparedAnnotation:
    annotation_id: int
    raw_category_id: int
    raw_category_name: str
    canonical_class: str
    canonical_id: int  # 1-indexed, matches the competition's official numbering
    model_class_id: int  # 0-indexed, for frameworks that expect zero-based indices
    bbox_xywh: list[float]  # absolute pixel coords [x, y, w, h], clamped to image bounds


@dataclass
class PreparedImage:
    original_image_id: int
    file_name: str
    width: int
    height: int
    split: str
    annotations: list[PreparedAnnotation] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a training-ready object-detection representation (read-only against the raw dataset).")
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--annotation-filename", default=DEFAULT_ANNOTATION_FILENAME)
    parser.add_argument(
        "--audit-report",
        default=Path("artifacts/audit/dataset_audit_report.json"),
        type=Path,
        help="Block 2 audit report, used to exclude confirmed cross-split exact duplicates.",
    )
    parser.add_argument("--summary-dir", default=Path("artifacts/reports"), type=Path)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def get_git_commit() -> str | None:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def load_train_exclusions(audit_report_path: Path) -> set[str]:
    """Return train filenames to exclude because Block 2 found them to be exact
    byte-duplicates of an image in valid or test (data leakage prevention)."""
    if not audit_report_path.exists():
        logger.warning("Audit report not found at %s; skipping cross-split leakage exclusion.", audit_report_path)
        return set()

    with audit_report_path.open("r", encoding="utf-8") as f:
        report = json.load(f)

    exclusions: set[str] = set()
    overlap = report.get("cross_split_overlap", {}).get("content_hash_overlap", {})
    for pair_key, matches in overlap.items():
        splits_in_pair = pair_key.split("_vs_")
        if "train" not in splits_in_pair:
            continue
        for match in matches:
            exclusions.add(match["train"])
            logger.warning(
                "Excluding train image '%s' from prepared set: confirmed exact byte-duplicate "
                "(md5=%s) with an image in another split (Block 2 finding) — prevents leakage.",
                match["train"], match["hash"],
            )
    return exclusions


def clamp_bbox(bbox: list[float], img_w: int, img_h: int) -> list[float]:
    """Clamp a COCO-style [x, y, w, h] box to the image bounds.

    Tolerates only sub-pixel overshoot (<= BBOX_BOUNDARY_TOLERANCE_PX), per
    the Block 2 finding that every observed overshoot in this dataset is a
    <=0.5px Roboflow export rounding artifact. Anything larger raises,
    since that would indicate a genuinely invalid box slipping through.
    """
    x, y, w, h = bbox
    overshoot = max(0.0, (x + w) - img_w, (y + h) - img_h)
    if overshoot > BBOX_BOUNDARY_TOLERANCE_PX:
        raise ValueError(
            f"bbox {bbox} exceeds image bounds ({img_w}x{img_h}) by {overshoot:.2f}px, "
            "beyond the tolerated rounding margin — this indicates a genuinely invalid box."
        )
    x = max(0.0, x)
    y = max(0.0, y)
    w = min(w, img_w - x)
    h = min(h, img_h - y)
    return [x, y, w, h]


def to_yolo_line(bbox_xywh: list[float], img_w: int, img_h: int, model_class_id: int) -> str:
    x, y, w, h = bbox_xywh
    cx = (x + w / 2) / img_w
    cy = (y + h / 2) / img_h
    return f"{model_class_id} {cx:.6f} {cy:.6f} {w / img_w:.6f} {h / img_h:.6f}"


def prepare_split(
    split: str, dataset_root: Path, annotation_filename: str, output_dir: Path, excluded_filenames: set[str]
) -> dict:
    json_path = dataset_root / split / annotation_filename
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    category_lookup = {c["id"]: c for c in data["categories"]}
    anns_by_image: dict[int, list[dict]] = {}
    for ann in data["annotations"]:
        anns_by_image.setdefault(ann["image_id"], []).append(ann)

    images_out_dir = output_dir / split / "images"
    labels_out_dir = output_dir / split / "labels"
    images_out_dir.mkdir(parents=True, exist_ok=True)
    labels_out_dir.mkdir(parents=True, exist_ok=True)

    prepared_images: list[PreparedImage] = []
    excluded_count = 0
    used_model_class_ids: set[int] = set()

    for img in data["images"]:
        image_id, file_name = img["id"], img["file_name"]
        if file_name in excluded_filenames:
            excluded_count += 1
            continue

        img_w, img_h = img["width"], img["height"]
        prepared_annotations: list[PreparedAnnotation] = []
        yolo_lines: list[str] = []

        for ann in anns_by_image.get(image_id, []):
            raw_cat = category_lookup[ann["category_id"]]
            result = map_raw_category(raw_cat["id"], raw_cat["name"])
            if result.is_supercategory_placeholder:
                continue  # not an object-detection target

            clamped_bbox = clamp_bbox(ann["bbox"], img_w, img_h)
            model_class_id = result.canonical_id - 1
            used_model_class_ids.add(model_class_id)

            prepared_annotations.append(
                PreparedAnnotation(
                    annotation_id=ann["id"],
                    raw_category_id=raw_cat["id"],
                    raw_category_name=raw_cat["name"],
                    canonical_class=result.canonical_name,
                    canonical_id=result.canonical_id,
                    model_class_id=model_class_id,
                    bbox_xywh=clamped_bbox,
                )
            )
            yolo_lines.append(to_yolo_line(clamped_bbox, img_w, img_h, model_class_id))

        source_image_path = (dataset_root / split / file_name).resolve()
        symlink_path = images_out_dir / file_name
        if symlink_path.is_symlink() or symlink_path.exists():
            symlink_path.unlink()
        symlink_path.symlink_to(source_image_path)

        label_path = labels_out_dir / (Path(file_name).stem + ".txt")
        label_path.write_text("\n".join(yolo_lines) + ("\n" if yolo_lines else ""), encoding="utf-8")

        prepared_images.append(
            PreparedImage(image_id, file_name, img_w, img_h, split, prepared_annotations)
        )

    invalid_class_ids = used_model_class_ids - set(range(len(CANONICAL_ID_TO_NAME)))
    if invalid_class_ids:
        raise ValueError(f"[{split}] produced out-of-range model class IDs: {invalid_class_ids}")

    manifest_path = output_dir / f"manifest_{split}.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(pi) for pi in prepared_images], f, indent=2)

    return {
        "split": split,
        "num_images_prepared": len(prepared_images),
        "num_images_excluded_leakage": excluded_count,
        "num_annotations_prepared": sum(len(pi.annotations) for pi in prepared_images),
        "manifest_path": str(manifest_path),
    }


def write_data_yaml(output_dir: Path) -> Path:
    lines = [
        "# Auto-generated by scripts/prepare_dataset.py — do not hand-edit.",
        "# Regenerate by rerunning the script; this file is not committed to git.",
        f"path: {output_dir.resolve()}",
        "train: train/images",
        "val: valid/images",
        "test: test/images",
        "",
        "names:",
    ]
    for canonical_id in sorted(CANONICAL_ID_TO_NAME):
        lines.append(f"  {canonical_id - 1}: {CANONICAL_ID_TO_NAME[canonical_id]}")
    path = output_dir / "data.yaml"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_readme(output_dir: Path, dataset_root: Path, seed: int, args: argparse.Namespace, split_results: list[dict]) -> Path:
    git_commit = get_git_commit() or "unknown (not a git repo or git unavailable)"
    timestamp = datetime.now(timezone.utc).isoformat()
    generation_command = (
        f"python scripts/prepare_dataset.py --dataset-root \"{dataset_root}\" "
        f"--output-dir {args.output_dir} --seed {seed}"
    )
    lines = [
        "# Prepared Dataset (Generated — Do Not Hand-Edit)",
        "",
        "This directory is a generated, training-ready view of the official TELEPATI 8.0",
        "AgriData dataset. It is NOT a copy: `images/` entries are symlinks into the raw",
        "dataset, so this directory must not be moved independently of the raw dataset",
        "it points to, and it is not committed to git (see project .gitignore) — it is",
        "fully regenerable from the raw dataset and this repository's code.",
        "",
        f"- Source dataset root (as given at generation time): `{dataset_root}`",
        f"- Generation command: `{generation_command}`",
        f"- Seed: {seed}",
        f"- Canonical mapping version: {MAPPING_VERSION} (see src/agridata/dataset/mapping.py)",
        f"- Generated at (UTC): {timestamp}",
        f"- Git commit at generation time: {git_commit}",
        "",
        "## Per-split summary",
        "",
        "| split | images prepared | images excluded (leakage) | annotations |",
        "|---|---:|---:|---:|",
    ]
    for r in split_results:
        lines.append(f"| {r['split']} | {r['num_images_prepared']} | {r['num_images_excluded_leakage']} | {r['num_annotations_prepared']} |")
    lines += [
        "",
        "Excluded images are confirmed exact byte-duplicates (MD5) found across splits",
        "by the Block 2 forensic audit (see artifacts/audit/dataset_audit_report.json,",
        "`cross_split_overlap.content_hash_overlap`) — excluded from `train` specifically",
        "so the model is never trained on data that is byte-identical to a held-out",
        "validation/test image.",
        "",
        "Labels are YOLO format (`class_id cx cy w h`, normalized 0-1). `class_id` is the",
        "zero-based `model_class_id` (`canonical_id - 1`); see `manifest_<split>.json` for",
        "full traceability back to the original raw category name and image ID.",
    ]
    path = output_dir / "README.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    setup_logging()
    args = parse_args()
    set_global_seed(args.seed)

    if not args.dataset_root.exists():
        print(f"FATAL: dataset root does not exist: {args.dataset_root}", file=sys.stderr)
        return 2

    train_exclusions = load_train_exclusions(args.audit_report)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    split_results = []
    for split in SPLITS:
        excluded = train_exclusions if split == "train" else set()
        result = prepare_split(split, args.dataset_root, args.annotation_filename, args.output_dir, excluded)
        split_results.append(result)
        logger.info(
            "[%s] prepared %d images (%d excluded), %d annotations",
            split, result["num_images_prepared"], result["num_images_excluded_leakage"], result["num_annotations_prepared"],
        )

    data_yaml_path = write_data_yaml(args.output_dir)
    readme_path = write_readme(args.output_dir, args.dataset_root, args.seed, args, split_results)

    args.summary_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "dataset_root": str(args.dataset_root),
        "output_dir": str(args.output_dir),
        "seed": args.seed,
        "mapping_version": MAPPING_VERSION,
        "git_commit": get_git_commit(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "splits": split_results,
        "data_yaml": str(data_yaml_path),
    }
    summary_path = args.summary_dir / "dataset_preparation_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"\nPrepared dataset written to: {args.output_dir}")
    print(f"data.yaml: {data_yaml_path}")
    print(f"README: {readme_path}")
    print(f"Summary (committed, small): {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
