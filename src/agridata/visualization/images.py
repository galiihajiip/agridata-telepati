"""Menggambar bounding box ground truth beserta label kelas canonical pada citra.

Modul ini dipakai untuk pemeriksaan visual yang wajib dilakukan. Setiap citra
yang disimpan harus menampilkan nama kelas canonical, kotak pembatasnya, serta
nama berkas atau ID citra asalnya, supaya manusia dapat memastikan sendiri bahwa
kotaknya benar-benar sejajar dengan objeknya dan tidak hanya mempercayai angka.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from agridata.dataset.mapping import CANONICAL_CLASSES
from agridata.dataset.stats import AnnotationRecord, ImageRecord

# Warna tetap dan deterministik per kelas canonical, tidak diturunkan dari
# hash, sehingga satu kelas selalu memakai warna yang sama di semua figur.
_PALETTE = [
    "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
    "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe", "#008080",
]
CLASS_COLORS: dict[str, str] = dict(zip(CANONICAL_CLASSES, _PALETTE, strict=True))


def draw_annotated_image(
    image_path: Path,
    image_record: ImageRecord,
    annotations: list[AnnotationRecord],
    title_suffix: str = "",
) -> Image.Image:
    """Mengembalikan salinan citra dengan kotak ground truth dan labelnya tergambar.

    Setiap kotak diberi nama kelas canonical. Nama berkas sengaja tidak
    ditanamkan ke dalam piksel citra; pemanggil sebaiknya memakainya pada nama
    berkas keluaran, mengikuti konvensi ramah audit yang dipakai di seluruh
    project ini.
    """
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.load_default(size=16)
    except TypeError:  # older Pillow without the `size` kwarg
        font = ImageFont.load_default()

    for ann in annotations:
        x, y, w, h = ann.bbox
        color = CLASS_COLORS.get(ann.canonical_class, "#ffffff")
        draw.rectangle([x, y, x + w, y + h], outline=color, width=3)

        label = ann.canonical_class
        text_bbox = draw.textbbox((x, y), label, font=font)
        label_h = text_bbox[3] - text_bbox[1]
        label_y = max(0, y - label_h - 4)
        draw.rectangle(
            [x, label_y, x + (text_bbox[2] - text_bbox[0]) + 6, label_y + label_h + 4],
            fill=color,
        )
        draw.text((x + 3, label_y + 1), label, fill="#000000", font=font)

    return image


def save_annotated_sample(
    dataset_root: Path,
    split: str,
    image_record: ImageRecord,
    annotations: list[AnnotationRecord],
    output_dir: Path,
    tag: str,
) -> Path:
    """Menggambar dan menyimpan satu citra contoh beranotasi, mengembalikan path keluaran.

    Nama berkas keluaran memuat split, penanda seperti "random", "rare_class",
    atau "crowded", ID citra, dan nama berkas aslinya, demi keterlacakan audit
    yang utuh.
    """
    image_path = dataset_root / split / image_record.file_name
    annotated = draw_annotated_image(image_path, image_record, annotations)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_name = f"{split}_{tag}_id{image_record.image_id}_{image_record.file_name}"
    out_path = output_dir / out_name
    annotated.save(out_path)
    return out_path
