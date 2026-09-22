"""Pemetaan label mentah menjadi 11 kelas canonical.

Memetakan nama kategori COCO pada dataset resmi menjadi 11 kelas canonical
yang ditetapkan regulasi kompetisi. Tabel pemetaan di bawah sudah diperiksa
silang terhadap dataset aktual, lihat artifacts/audit/dataset_audit_report.md:
ketiga split memuat tepat 21 kategori mentah, terdiri atas 3 supercategory
tanpa anotasi (Leaf-blight, Rice-Leaf-Diseasee, paddy) dan 18 label kondisi
tanaman yang seluruhnya tercakup di sini tanpa nama tak terduga.

Pemetaan bersifat deterministik dan sengaja menolak memetakan nama mentah
yang tidak dikenali. Label yang tidak dikenali harus diselidiki dan
ditambahkan secara eksplisit, tidak boleh ditebak.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Naikkan versi setiap kali RAW_TO_CANONICAL atau KNOWN_SUPERCATEGORY_LABELS
# berubah, agar keluaran dataset mencatat pemetaan mana yang menghasilkannya.
MAPPING_VERSION = "1.0.0"

CANONICAL_CLASSES: tuple[str, ...] = (
    "Bacterial leaf blight",
    "Bacterial panicle blight",
    "Blast",
    "Brown spot",
    "False smut",
    "Healthy",
    "Leaf roller",
    "Leaf scald",
    "Narrow brown",
    "Sheath blight",
    "Tungro",
)

CANONICAL_NUM_CLASSES = len(CANONICAL_CLASSES)  # 11, per competition regulation

# Id canonical (mulai dari 1, mengikuti penomoran resmi) menuju nama kelas.
CANONICAL_ID_TO_NAME: dict[int, str] = {i + 1: name for i, name in enumerate(CANONICAL_CLASSES)}
CANONICAL_NAME_TO_ID: dict[str, int] = {name: i for i, name in CANONICAL_ID_TO_NAME.items()}

# Raw category name -> canonical class name.
# Sumber: regulasi TELEPATI 8.0, diverifikasi terhadap kategori mentah dataset
# aktual pada audit forensik dataset.
RAW_TO_CANONICAL: dict[str, str] = {
    "Bacterial leaf blight": "Bacterial leaf blight",
    "Bacterial panicle Blight": "Bacterial panicle blight",
    "Blast": "Blast",
    "Leaf blast": "Blast",
    "Infected Blast": "Blast",
    "BrownSpot": "Brown spot",
    "Brown spot": "Brown spot",
    "False-Smut": "False smut",
    "Healthy Rice Leaf": "Healthy",
    "Healthy Rice beads": "Healthy",
    "Healthy": "Healthy",
    "healthy": "Healthy",
    "Leaf-roller": "Leaf roller",
    "Leaf Scald": "Leaf scald",
    "Leaf scald": "Leaf scald",
    "Narrow brown": "Narrow brown",
    "Sheath Blight": "Sheath blight",
    "Rice-Tungro": "Tungro",
}

# Label supercategory non-canonical yang ada pada dataset mentah. Ketiganya
# tidak memuat anotasi sama sekali, terverifikasi pada audit dataset, dan
# secara eksplisit dikecualikan sebagai target deteksi.
KNOWN_SUPERCATEGORY_LABELS: frozenset[str] = frozenset({"Leaf-blight", "Rice-Leaf-Diseasee", "paddy"})


class UnknownRawCategoryError(ValueError):
    """Dilempar ketika nama kategori mentah tidak memiliki pemetaan canonical dan
    not a recognized supercategory placeholder.

    Kegagalan ini disengaja agar terlihat jelas. Kategori mentah yang tidak
    label must never be silently mapped or dropped.
    """


@dataclass(frozen=True)
class CategoryMappingResult:
    """Hasil pemetaan satu kategori COCO mentah ke kelas canonical-nya."""

    raw_category_id: int
    raw_name: str
    canonical_name: str | None  # None if this is a supercategory placeholder
    canonical_id: int | None
    is_supercategory_placeholder: bool


def map_raw_category(raw_category_id: int, raw_name: str) -> CategoryMappingResult:
    """Memetakan satu kategori COCO mentah ke kelas canonical-nya.

    Raises:
        UnknownRawCategoryError: if `raw_name` is neither a known canonical
            raw name nor a recognized supercategory placeholder.
    """
    if raw_name in KNOWN_SUPERCATEGORY_LABELS:
        return CategoryMappingResult(raw_category_id, raw_name, None, None, True)

    canonical_name = RAW_TO_CANONICAL.get(raw_name)
    if canonical_name is None:
        raise UnknownRawCategoryError(
            f"Raw category '{raw_name}' (id={raw_category_id}) has no known canonical "
            "mapping and is not a recognized supercategory placeholder. Refusing to "
            "silently map it, verify against the official mapping and update "
            "RAW_TO_CANONICAL or KNOWN_SUPERCATEGORY_LABELS explicitly."
        )

    return CategoryMappingResult(
        raw_category_id, raw_name, canonical_name, CANONICAL_NAME_TO_ID[canonical_name], False
    )


def map_categories(categories: list[dict[str, Any]]) -> list[CategoryMappingResult]:
    """Memetakan daftar kategori COCO mentah yang memuat 'id' dan 'name'."""
    return [map_raw_category(c["id"], c["name"]) for c in categories]


def build_mapping_report(categories: list[dict[str, Any]]) -> dict[str, Any]:
    """Menyusun laporan terstruktur yang membandingkan kategori mentah dengan pemetaan resmi.

    Berbeda dengan `map_raw_category`, fungsi ini tidak melempar kesalahan pada
    kategori yang tidak dikenali,
    it records it in `unmapped_raw_categories` so a full audit report can
    still be produced. Use `map_raw_category`/`map_categories` directly
    wherever strict fail-loudly behavior is required (e.g. dataset
    preparation in a later block).
    """
    results: list[CategoryMappingResult] = []
    unmapped: list[dict[str, Any]] = []

    for c in categories:
        try:
            results.append(map_raw_category(c["id"], c["name"]))
        except UnknownRawCategoryError:
            unmapped.append(c)

    covered_canonical = {r.canonical_name for r in results if r.canonical_name is not None}
    canonical_with_zero_raw_labels = [name for name in CANONICAL_CLASSES if name not in covered_canonical]

    return {
        "total_raw_categories": len(categories),
        "mapped": [
            {
                "raw_id": r.raw_category_id,
                "raw_name": r.raw_name,
                "canonical_name": r.canonical_name,
                "canonical_id": r.canonical_id,
            }
            for r in results
            if not r.is_supercategory_placeholder
        ],
        "supercategory_placeholders": [
            {"raw_id": r.raw_category_id, "raw_name": r.raw_name}
            for r in results
            if r.is_supercategory_placeholder
        ],
        "unmapped_raw_categories": unmapped,
        "canonical_classes_with_zero_raw_labels": canonical_with_zero_raw_labels,
    }
