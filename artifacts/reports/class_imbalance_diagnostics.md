# Class Imbalance Diagnostics (Block 12)

Split: `train` | Total instances: 20163 | Classes: 11
Max/min instance-count imbalance ratio: **22.6x**

Rare classes (< 20% of the most common class's count): **['Bacterial leaf blight', 'Bacterial panicle blight', 'False smut', 'Leaf roller', 'Narrow brown']**
Small-object / visually difficult classes (< 10% of the largest median bbox area): **['Bacterial leaf blight', 'Blast', 'Brown spot', 'Sheath blight', 'Tungro']**

| Class | Instances | Images | % of total | Median bbox area (px²) | Rare | Small-object |
|---|---:|---:|---:|---:|:---:|:---:|
| Brown spot | 5010 | 1122 | 24.85 | 1022.3 |  | YES |
| Blast | 4149 | 1919 | 20.58 | 7477.5 |  | YES |
| Tungro | 2540 | 773 | 12.6 | 12017.5 |  | YES |
| Healthy | 2374 | 2198 | 11.77 | 155844.1 |  |  |
| Sheath blight | 1762 | 629 | 8.74 | 11380.7 |  | YES |
| Leaf scald | 1438 | 837 | 7.13 | 38698.3 |  |  |
| False smut | 852 | 832 | 4.23 | 137300.8 | YES |  |
| Leaf roller | 812 | 803 | 4.03 | 114759.2 | YES |  |
| Bacterial panicle blight | 528 | 519 | 2.62 | 141993.3 | YES |  |
| Bacterial leaf blight | 476 | 234 | 2.36 | 13831.4 | YES | YES |
| Narrow brown | 222 | 222 | 1.1 | 147911.5 | YES |  |
