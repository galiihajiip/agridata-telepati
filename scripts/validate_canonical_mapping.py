#!/usr/bin/env python3
"""CLI to validate the official 11-class canonical mapping against the actual
raw dataset categories (Block 3).

Usage:
    python scripts/validate_canonical_mapping.py --dataset-root "<PATH>"

Read-only: loads each split's COCO JSON to read `categories` only. Does not
mutate any raw file and does not mutate the annotations — this only checks
that every raw category name is covered by RAW_TO_CANONICAL or recognized as
a non-canonical supercategory placeholder.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agridata.dataset.mapping import CANONICAL_CLASSES, build_mapping_report  # noqa: E402

SPLITS = ("train", "valid", "test")
DEFAULT_ANNOTATION_FILENAME = "_annotations.coco.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the official canonical 11-class mapping against actual dataset categories."
    )
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("artifacts/audit"), type=Path)
    parser.add_argument("--annotation-filename", default=DEFAULT_ANNOTATION_FILENAME)
    return parser.parse_args()


def load_categories(json_path: Path) -> list[dict]:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["categories"]


def build_markdown(per_split_reports: dict[str, dict]) -> str:
    lines = [
        "# Canonical 11-Class Mapping Validation Report",
        "",
        f"Official canonical classes ({len(CANONICAL_CLASSES)}): {list(CANONICAL_CLASSES)}",
        "",
    ]
    for split, report in per_split_reports.items():
        lines.append(f"## Split: `{split}`")
        lines.append("")
        lines += [
            f"- Total raw categories: {report['total_raw_categories']}",
            f"- Mapped raw categories: {len(report['mapped'])}",
            "- Supercategory placeholders (excluded, zero annotations expected): "
            f"{[p['raw_name'] for p in report['supercategory_placeholders']]}",
            f"- Unmapped/unknown raw categories: {report['unmapped_raw_categories']}",
            f"- Canonical classes with zero raw labels in this split: {report['canonical_classes_with_zero_raw_labels']}",
            "",
            "| raw_id | raw_name | canonical_name | canonical_id |",
            "|---:|---|---|---:|",
        ]
        for m in report["mapped"]:
            lines.append(f"| {m['raw_id']} | {m['raw_name']} | {m['canonical_name']} | {m['canonical_id']} |")
        lines.append("")
        status = "PASS" if not report["unmapped_raw_categories"] else "FAIL (unmapped categories present)"
        lines.append(f"**Split mapping status: {status}**")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    if not args.dataset_root.exists():
        print(f"FATAL: dataset root does not exist: {args.dataset_root}", file=sys.stderr)
        return 2

    per_split_reports = {}
    for split in SPLITS:
        json_path = args.dataset_root / split / args.annotation_filename
        if not json_path.exists():
            print(f"FATAL: annotation file missing for split '{split}': {json_path}", file=sys.stderr)
            return 2
        per_split_reports[split] = build_mapping_report(load_categories(json_path))

    args.output_dir.mkdir(parents=True, exist_ok=True)

    json_path_out = args.output_dir / "canonical_mapping_report.json"
    with json_path_out.open("w", encoding="utf-8") as f:
        json.dump(per_split_reports, f, indent=2)

    markdown = build_markdown(per_split_reports)
    md_path_out = args.output_dir / "canonical_mapping_report.md"
    md_path_out.write_text(markdown, encoding="utf-8")

    print(markdown)
    print(f"\nJSON report: {json_path_out}")
    print(f"Markdown report: {md_path_out}")

    any_unmapped = any(r["unmapped_raw_categories"] for r in per_split_reports.values())
    if any_unmapped:
        print("\nVALIDATION RESULT: FAIL — unmapped raw categories found.", file=sys.stderr)
        return 1

    print("\nVALIDATION RESULT: PASS — every raw category is covered by the canonical mapping or is a recognized supercategory placeholder.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
