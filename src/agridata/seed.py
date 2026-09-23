"""Utilitas penyemaian deterministik untuk pipeline AgriData.

Modul ini menyemai setiap sumber keacakan yang diketahui dan dapat dijangkau.
PyTorch diperlakukan opsional dan hanya disemai bila terpasang, sehingga utilitas
ini tetap berfungsi baik sebelum maupun sesudah framework deteksi objek
ditambahkan ke project.
"""

from __future__ import annotations

import logging
import os
import random

import numpy as np

logger = logging.getLogger("agridata.seed")


def set_global_seed(seed: int) -> None:
    """Menyemai ``random`` bawaan Python, NumPy, dan PyTorch bila terpasang.

    Fungsi ini juga menetapkan ``PYTHONHASHSEED`` supaya pengacakan berbasis
    hash, misalnya urutan iterasi dict atau set pada konteks tertentu, tetap
    konsisten untuk proses yang sedang berjalan.

    Perlu dicatat bahwa ``PYTHONHASHSEED`` sesungguhnya hanya berpengaruh penuh
    pada proses yang sejak awal dimulai dengan variabel itu sudah tersetel di
    lingkungan. Menetapkannya di sini mendokumentasikan niat sekaligus
    memengaruhi setiap subproses yang dijalankan dari proses ini.
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
