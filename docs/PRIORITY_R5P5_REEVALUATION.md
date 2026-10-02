# R=5.5 Re-evaluation — Completed

## Protocol
- Extended-grid tuning seeds: 6000–6029
- Selected DR-SAFE setting: R=5.5, K=2.0, D_SAFE=1.5
- Re-evaluation seeds: 10300–10599 (N=300)
- Reference: R=4.5, K=2.0, D_SAFE=1.5
- Same paired seeds for R=4.5 and R=5.5
- No parameter search on the 300-run re-evaluation block

## Results
| Metric | R=4.5 | R=5.5 | R=5.5 − R=4.5 | Wilcoxon p |
|---|---:|---:|---:|---:|
| Success (%) | 100.0 | 100.0 | 0 | — |
| Any collision (%) | 14.0 | 12.3 | −1.7 pp | descriptive |
| Collisions/run | 0.190 | 0.160 | −0.030 | 0.528 |
| Path length | 35.09 | 35.53 | +0.442 | 0.0045 |
| Sharp turns | 12.55 | 12.24 | −0.303 | 0.294 |
| Min. clearance | 1.80 | 1.64 | −0.164 | 0.097 |

## Interpretation
R=5.5 does not provide a consistent advantage over R=4.5 on this fresh paired block. It is therefore retained as a sensitivity/re-evaluation configuration, while R=4.5 remains the primary frozen setting.

## Reproducibility
- `experiments/r5p5_drsafe_confirmation.py`
- `experiments/r4p5_drsafe_confirmation.py`
- `experiments/analyze_r5p5_re_evaluation.py`
- `results/drsafe_r5p5_confirmation.json`
- `results/drsafe_drsafe_r4p5_confirmation.json`
- `results/r5p5_re_evaluation_analysis.json`
