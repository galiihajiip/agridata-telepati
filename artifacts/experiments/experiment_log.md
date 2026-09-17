# Experiment Log

| Experiment | Model | Image Size | Batch | Optimizer | LR | Weight Decay | Scheduler | Epochs | Device | Best mAP@50 | Best F1 | Precision | Recall | Duration (s) | Notes |
|---|---|---:|---:|---|---:|---:|---|---:|---|---:|---:|---:|---:|---:|---|
| E01 | yolov8n.yaml | 320 | 8 | AdamW | 0.000667 | 0.0005 | linear | 2 | mps | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 127.4 | Block 6 smoke test: 2 epochs, 5% of train, imgsz=320. Proves pipeline works end-to-end, not a real model. |
| E02 | yolov8n.yaml | 320 | 16 | AdamW | 0.001 | 0.0005 | linear | 5 | mps | 0.0018 | N/A | 0.1840 | 0.0073 | 145.7 | Block 10 baseline (OFAT reference point). |
| E03 | yolov8n.yaml | 640 | 16 | AdamW | 0.001 | 0.0005 | linear | 5 | mps | 0.0041 | N/A | 0.3724 | 0.0052 | 302.2 | OFAT variant: image_size changed from baseline; all else held fixed. |
| E04 | yolov8n.yaml | 320 | 32 | AdamW | 0.001 | 0.0005 | linear | 5 | mps | 0.0005 | N/A | 0.0004 | 0.0828 | 119.4 | OFAT variant: batch_size changed from baseline; all else held fixed. |
| E05 | yolov8n.yaml | 320 | 16 | AdamW | 0.0001 | 0.0005 | linear | 5 | mps | 0.0002 | N/A | 0.1820 | 0.0814 | 130.7 | OFAT variant: learning_rate changed from baseline; all else held fixed. |
| E06 | yolov8n.yaml | 320 | 16 | SGD | 0.001 | 0.0005 | linear | 5 | mps | 0.0003 | N/A | 0.0961 | 0.0003 | 127.8 | OFAT variant: optimizer changed from baseline; all else held fixed. |
| E07 | yolov8n.yaml | 320 | 16 | AdamW | 0.001 | 0.0005 | linear | 5 | mps | 0.0007 | N/A | 0.2759 | 0.0061 | 133.8 | OFAT variant: augmentation_strength changed from baseline; all else held fixed. |
| E08 | yolov8n.yaml | 320 | 16 | AdamW | 0.001 | 0.0005 | linear | 10 | mps | 0.0134 | N/A | 0.2921 | 0.0406 | 207.8 | OFAT variant: training_duration changed from baseline; all else held fixed. |
