# Experiment Log

| Experiment | Model | Image Size | Batch | Optimizer | LR | Weight Decay | Scheduler | Epochs | Device | Best mAP@50 | Best F1 | Precision | Recall | Duration (s) | Notes |
|---|---|---:|---:|---|---:|---:|---|---:|---|---:|---:|---:|---:|---:|---|
| E01 | yolov8n.yaml | 320 | 8 | AdamW | 0.000667 | 0.0005 | linear | 2 | mps | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 127.4 | Block 6 smoke test: 2 epochs, 5% of train, imgsz=320. Proves pipeline works end-to-end, not a real model. |
