"""Deterministic seeding utility for the AgriData pipeline.

Seeds every known source of randomness reachable at the current project
stage. PyTorch is optional here (not yet a required dependency) and is
seeded only if installed, so this utility works before and after the
object-detection framework is added in a later block.
"""

from __future__ import annotations

import logging
import os
import random

import numpy as np

logger = logging.getLogger("agridata.seed")


def set_global_seed(seed: int) -> None:
    """Seed Python's ``random``, NumPy, and (if installed) PyTorch.

    Also sets ``PYTHONHASHSEED`` so hash-based randomization (e.g. dict/set
    iteration order in some contexts) is fixed for the current process.
    Note: PYTHONHASHSEED only takes effect for processes started with it
    already set in the environment; setting it here documents intent and
    affects any subprocesses this process spawns.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
        import torch
    except ImportError:
        logger.info("torch not installed; skipped torch seeding (seed=%d)", seed)
        return

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    logger.info("Global seed set to %d (python, numpy, torch)", seed)
