# Block 12. Class Imbalance Mitigation Ablation

Both runs use the identical training image COUNT (810, an absolute count via an integer `fraction`, verified via source not to be a percentage), the only difference is whether rare-class images are duplicated in the sampling pool. Same seed, same hyperparameters, same validation data (byte-identical files in both cases).

Rare classes targeted for oversampling (< 20% of the most common class's instance count, per `artifacts/reports/class_imbalance_diagnostics.md`): ['Bacterial leaf blight', 'Bacterial panicle blight', 'False smut', 'Leaf roller', 'Narrow brown']

## Overall results

| Run | mAP@0.5 | Precision | Recall | Duration (s) |
|---|---:|---:|---:|---:|
| baseline (natural distribution) | 0.0071 | 0.1143 | 0.0550 | 135.2 |
| oversampled (rare classes x3) | 0.0005 | 0.1825 | 0.0111 | 119.7 |

## Per-class AP@0.5, rare classes specifically (the actual point of this ablation)

| Class | Baseline AP@0.5 | Oversampled AP@0.5 | Delta |
|---|---:|---:|---:|
| Bacterial leaf blight | 0.0003 | 0.0003 | +0.0000 |
| Bacterial panicle blight | 0.0080 | 0.0044 | -0.0037 |
| False smut | 0.0000 | 0.0000 | +0.0000 |
| Leaf roller | 0.0677 | 0.0001 | -0.0676 |
| Narrow brown | 0.0000 | 0.0000 | +0.0000 |

## Per-class AP@0.5, all classes (checking oversampling didn't hurt common classes)

| Class | Baseline AP@0.5 | Oversampled AP@0.5 | Delta |
|---|---:|---:|---:|
| Bacterial leaf blight (rare, targeted) | 0.0003 | 0.0003 | +0.0000 |
| Bacterial panicle blight (rare, targeted) | 0.0080 | 0.0044 | -0.0037 |
| Blast | 0.0021 | 0.0007 | -0.0013 |
| Brown spot | 0.0000 | 0.0000 | +0.0000 |
| False smut (rare, targeted) | 0.0000 | 0.0000 | +0.0000 |
| Healthy | 0.0000 | 0.0000 | +0.0000 |
| Leaf roller (rare, targeted) | 0.0677 | 0.0001 | -0.0676 |
| Leaf scald | 0.0000 | 0.0000 | +0.0000 |
| Narrow brown (rare, targeted) | 0.0000 | 0.0000 | +0.0000 |
| Sheath blight | 0.0000 | 0.0000 | +0.0000 |
| Tungro | 0.0000 | 0.0000 | +0.0000 |

## Verdict

Average AP@0.5 delta on targeted rare classes: -0.0143
Average AP@0.5 delta on non-targeted (common) classes: -0.0002

Oversampling did NOT show a clear net benefit at this screening scale (either rare classes did not improve, or the improvement was outweighed by cost to common classes, or both). Per the master spec ('do not automatically oversample'), this strategy is NOT recommended for adoption based on this evidence. It may still be worth re-testing at full training scale in Block 14, since class-imbalance effects can behave differently with more data/epochs.
