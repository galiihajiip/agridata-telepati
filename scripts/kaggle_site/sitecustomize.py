"""Dimuat otomatis oleh setiap proses Python pelatihan Kaggle lewat PYTHONPATH.

check_amp() bawaan Ultralytics mengunduh bobot pretrained yolo26n.pt hanya
untuk membandingkan keluaran FP32 dan AMP. Bobot itu tidak masuk ke model
kita, tetapi tetap merupakan berkas pretrained eksternal yang terunduh ke
lingkungan, sehingga dilarang pada project ini. YOLO_OFFLINE tidak
mencegahnya, dan proses DDP dibuat Ultralytics dari berkas sementara sehingga
patch biasa di dalam skrip tidak ikut terbawa. Karena itu patch dipasang di
sini, yang dijalankan interpreter pada awal setiap proses turunan.

AMP tetap aktif. Tesla T4 dan P100 tidak termasuk daftar GPU bermasalah AMP
milik Ultralytics.
"""

import logging


def _check_amp_without_download(model):
    logging.getLogger("agridata.kaggle").warning(
        "AMP check dilewati tanpa mengunduh bobot pretrained; AMP diaktifkan."
    )
    return True


try:
    import ultralytics.utils.checks as _checks

    _checks.check_amp = _check_amp_without_download
except ImportError:
    pass
