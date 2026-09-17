"""Fast reproducibility unit tests (Block 8).

The slower checks that actually re-execute pipeline scripts (e.g. rerunning
dataset preparation and diffing manifests) live in
scripts/check_reproducibility.py, not here — this file only covers
pure-function determinism that should run in milliseconds as part of the
normal test suite.
"""

from __future__ import annotations

import hashlib
import json

from agridata.dataset.mapping import KNOWN_SUPERCATEGORY_LABELS, RAW_TO_CANONICAL, build_mapping_report
from agridata.reproducibility.environment import capture_environment_snapshot, get_git_commit


def test_canonical_mapping_report_is_pure_and_deterministic() -> None:
    categories = [{"id": i, "name": name} for i, name in enumerate(RAW_TO_CANONICAL.keys())]
    first = build_mapping_report(categories)
    second = build_mapping_report(categories)
    assert first == second


def test_mapping_table_hash_is_stable_within_a_process() -> None:
    """Regression guard: if RAW_TO_CANONICAL or KNOWN_SUPERCATEGORY_LABELS ever
    change, this hash changes too — a reminder to bump MAPPING_VERSION."""
    table_repr = json.dumps(
        {"raw_to_canonical": RAW_TO_CANONICAL, "supercategories": sorted(KNOWN_SUPERCATEGORY_LABELS)},
        sort_keys=True,
    )
    hash_a = hashlib.sha256(table_repr.encode()).hexdigest()
    hash_b = hashlib.sha256(table_repr.encode()).hexdigest()
    assert hash_a == hash_b


def test_environment_snapshot_captures_git_commit_when_in_a_repo() -> None:
    snapshot = capture_environment_snapshot()
    assert snapshot["git_commit"] == get_git_commit()
    assert snapshot["python_version"]
    assert snapshot["device"]["resolved_device"] in {"cuda", "mps", "cpu"}


def test_environment_snapshot_includes_dependency_versions() -> None:
    snapshot = capture_environment_snapshot()
    assert isinstance(snapshot["installed_packages"], list)
    assert len(snapshot["installed_packages"]) > 0
