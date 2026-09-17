"""Smoke tests verifying the bootstrap development environment is functional."""

from __future__ import annotations

import random

from agridata.config import load_config
from agridata.device import detect_device
from agridata.seed import set_global_seed


def test_python_and_imports_work() -> None:
    assert 1 + 1 == 2


def test_config_loads() -> None:
    config = load_config()
    assert config.seed == 42
    assert config.dataset.root.name == "Telepati 8.0 Datasets"
    assert config.dataset.train_dir.exists()
    assert config.dataset.valid_dir.exists()
    assert config.dataset.test_dir.exists()


def test_seed_is_deterministic() -> None:
    set_global_seed(42)
    first = [random.random() for _ in range(5)]
    set_global_seed(42)
    second = [random.random() for _ in range(5)]
    assert first == second


def test_device_detection_returns_valid_string() -> None:
    assert detect_device() in {"cuda", "mps", "cpu"}
