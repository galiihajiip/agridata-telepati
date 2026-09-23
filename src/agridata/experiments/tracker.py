"""Pelacak percobaan yang ringan dan sepenuhnya luring.

MLflow maupun W&B sengaja tidak dipakai. Batasan audit project ini menuntut nol
dependensi eksternal, tanpa kebutuhan internet, tanpa paparan privasi, dan
sesedikit mungkin komponen bergerak agar juri mudah mereproduksinya. Pada skala
project ini, satu berkas JSON yang dapat dibaca skrip mana pun maupun manusia
sudah memadai.

Setiap percobaan tersimpan sebagai satu catatan dengan skema tetap, lihat
`ExperimentRecord`.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_LOG_PATH = Path("artifacts/experiments/experiment_log.json")


@dataclass
class ExperimentRecord:
    """Satu baris catatan percobaan beserta seluruh field yang diwajibkan."""

    experiment_id: str
    timestamp_utc: str
    git_commit: str | None
    seed: int
    model_architecture: str
    pretrained: bool
    dataset_manifest_hash: str
    image_size: int
    batch_size: int
    epochs: int
    optimizer: str
    learning_rate: float
    weight_decay: float
    scheduler: str
    augmentation_config: dict[str, Any] = field(default_factory=dict)
    device: str = "cpu"
    best_val_map50: float | None = None
    best_val_f1: float | None = None
    precision: float | None = None
    recall: float | None = None
    training_duration_seconds: float | None = None
    notes: str = ""
    compliance_notes: str = ""


def compute_manifest_hash(manifest_path: Path) -> str:
    """SHA-256 dari berkas manifest data siap latih.

    Nilai ini berfungsi sebagai sidik jari versi dataset yang konkret dan dapat
    diverifikasi, sehingga setiap percobaan terikat pada data persis yang
    dipakai melatih dan mengevaluasinya."""
    with manifest_path.open("rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_experiments(log_path: Path = DEFAULT_LOG_PATH) -> list[dict[str, Any]]:
    if not log_path.exists():
        return []
    with log_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def append_experiment(record: ExperimentRecord, log_path: Path = DEFAULT_LOG_PATH) -> None:
    """Menambahkan satu catatan percobaan ke log.

    Pola baca, ubah, lalu tulis pada satu array JSON sudah memadai untuk skala
    project ini. Memakai basis data sungguhan hanya akan menambah kerumitan yang
    tidak diperlukan untuk percobaan sebanyak ini."""
    records = load_experiments(log_path)
    existing_ids = {r["experiment_id"] for r in records}
    if record.experiment_id in existing_ids:
        raise ValueError(f"experiment_id '{record.experiment_id}' already exists in {log_path}, use a unique ID.")

    records.append(asdict(record))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def build_markdown_table(records: list[dict[str, Any]]) -> str:
    """Menyajikan log percobaan sebagai tabel Markdown, diurutkan menurut experiment_id."""
    lines = [
        "# Log Percobaan",
        "",
        "| Percobaan | Model | Ukuran Citra | Batch | Optimizer | LR | Weight Decay | Scheduler | Epoch | Perangkat | mAP@50 Terbaik | F1 Terbaik | Precision | Recall | Durasi (detik) | Catatan |",
        "|---|---|---:|---:|---|---:|---:|---|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in sorted(records, key=lambda r: r["experiment_id"]):
        lines.append(
            f"| {r['experiment_id']} | {r['model_architecture']} | {r['image_size']} | {r['batch_size']} | "
            f"{r['optimizer']} | {r['learning_rate']:.6g} | {r['weight_decay']:.6g} | {r['scheduler']} | "
            f"{r['epochs']} | {r['device']} | "
            f"{_fmt(r['best_val_map50'])} | {_fmt(r['best_val_f1'])} | {_fmt(r['precision'])} | {_fmt(r['recall'])} | "
            f"{_fmt(r['training_duration_seconds'], 1)} | {r['notes']} |"
        )
    return "\n".join(lines) + "\n"


def _fmt(value: float | None, ndigits: int = 4) -> str:
    return "N/A" if value is None else f"{value:.{ndigits}f}"
