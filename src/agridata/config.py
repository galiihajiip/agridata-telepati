"""Central configuration loading for the AgriData pipeline.

All path-dependent parameters (dataset location, split directory names, seed,
etc.) are read from a single YAML source of truth so that no personal or
machine-specific paths are hardcoded in code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "base.yaml"


@dataclass(frozen=True)
class DatasetPaths:
    """Resolved, absolute filesystem paths for the official dataset splits."""

    root: Path
    train_dir: Path
    valid_dir: Path
    test_dir: Path
    annotation_filename: str

    def annotation_path(self, split_dir: Path) -> Path:
        """Return the COCO annotation file path for a given split directory."""
        return split_dir / self.annotation_filename


@dataclass(frozen=True)
class AppConfig:
    """Top-level, validated application configuration."""

    seed: int
    dataset: DatasetPaths
    raw: dict[str, Any]


def load_config(config_path: Path | str = DEFAULT_CONFIG_PATH) -> AppConfig:
    """Load and validate the project configuration from a YAML file.

    Raises:
        FileNotFoundError: if the config file does not exist.
        ValueError: if required fields are missing from the config.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not raw:
        raise ValueError(f"Config file is empty or invalid: {config_path}")

    if "seed" not in raw:
        raise ValueError("Config must define a top-level 'seed'")

    dataset_cfg = raw.get("dataset")
    if not dataset_cfg:
        raise ValueError("Config must define a 'dataset' section")

    required_keys = ("root", "train_dir", "valid_dir", "test_dir", "annotation_filename")
    missing = [key for key in required_keys if key not in dataset_cfg]
    if missing:
        raise ValueError(f"Config 'dataset' section is missing keys: {missing}")

    dataset_root = Path(dataset_cfg["root"])
    if not dataset_root.is_absolute():
        dataset_root = (PROJECT_ROOT / dataset_root).resolve()

    dataset = DatasetPaths(
        root=dataset_root,
        train_dir=dataset_root / dataset_cfg["train_dir"],
        valid_dir=dataset_root / dataset_cfg["valid_dir"],
        test_dir=dataset_root / dataset_cfg["test_dir"],
        annotation_filename=dataset_cfg["annotation_filename"],
    )

    return AppConfig(seed=int(raw["seed"]), dataset=dataset, raw=raw)
