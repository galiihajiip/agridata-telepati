#!/usr/bin/env python3
"""Validasi pemetaan 11 kelas canonical terhadap kategori dataset yang sebenarnya.

Pemakaian:
    python scripts/validate_canonical_mapping.py --dataset-root "<PATH>"

Skrip hanya membaca: berkas COCO JSON setiap split dimuat semata untuk membaca
`categories`. Tidak ada berkas mentah maupun anotasi yang diubah. Yang diperiksa
hanyalah apakah setiap nama kategori mentah tercakup oleh RAW_TO_CANONICAL atau
dikenali sebagai penanda supercategory yang memang bukan kelas canonical.
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
        "# Laporan Validasi Pemetaan 11 Kelas Canonical",
        "",
        f"Kelas canonical resmi ({len(CANONICAL_CLASSES)}): {list(CANONICAL_CLASSES)}",
        "",
    ]
    for split, report in per_split_reports.items():
        lines.append(f"## Split: `{split}`")
        lines.append("")
        lines += [
            f"- Total kategori mentah: {report['total_raw_categories']}",
            f"- Kategori mentah yang terpetakan: {len(report['mapped'])}",
            "- Penanda supercategory yang dikecualikan, diharapkan tanpa anotasi: "
            f"{[p['raw_name'] for p in report['supercategory_placeholders']]}",
            f"- Kategori mentah yang tidak terpetakan atau tidak dikenali: {report['unmapped_raw_categories']}",
            f"- Kelas canonical tanpa label mentah pada split ini: {report['canonical_classes_with_zero_raw_labels']}",
            "",
            "| raw_id | raw_name | canonical_name | canonical_id |",
            "|---:|---|---|---:|",
        ]
        for m in report["mapped"]:
            lines.append(f"| {m['raw_id']} | {m['raw_name']} | {m['canonical_name']} | {m['canonical_id']} |")
        lines.append("")
        status = "LULUS" if not report["unmapped_raw_categories"] else "GAGAL, ada kategori yang tidak terpetakan"
        lines.append(f"**Status pemetaan split: {status}**")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    if not args.dataset_root.exists():
        print(f"FATAL: akar dataset tidak ditemukan: {args.dataset_root}", file=sys.stderr)
        return 2

    per_split_reports = {}
    for split in SPLITS:
        json_path = args.dataset_root / split / args.annotation_filename
        if not json_path.exists():
            print(f"FATAL: berkas anotasi untuk split '{split}' tidak ditemukan: {json_path}", file=sys.stderr)
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
        print("\nHASIL VALIDASI: GAGAL, ditemukan kategori mentah yang tidak terpetakan.", file=sys.stderr)
        return 1

    print("\nHASIL VALIDASI: LULUS, seluruh kategori mentah tercakup pemetaan canonical atau merupakan penanda supercategory yang dikenali.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
