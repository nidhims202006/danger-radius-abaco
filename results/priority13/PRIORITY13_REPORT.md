# Priority 13 — Multi-noise robustness

## Design
- Tuning seeds: 9000–9029 (30 disjoint seeds).
- Confirmation seeds: 10300–10599 (300 fresh seeds per evaluated block).
- Noise levels: 5°/10%, 15°/20%, 30°/40% heading/speed-estimation error.
- Methods: HB, HBP, predicted-position APF-ACO (APFP).
- Six candidate settings per method/noise block; equal tuning budget.
- HB is noise-invariant and was tuned once; HBP and APFP were tuned separately at each noise level.
- No new multiplicity-adjusted inferential claim is made from this block.

## Confirmation summary
| Method | Noise | N | Runs with collision | Collisions/run | Success | Turns | Path | Clearance |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| HB | clean | 300 | 18.0% | 0.230 | 100% | 13.24 | 35.38 | 1.68 |
| HBP | 5°/10% | 300 | 20.3% | 0.270 | 100% | 17.25 | 37.59 | 1.41 |
| APFP | 5°/10% | 300 | 8.3% | 0.093 | 100% | 14.68 | 36.20 | 2.06 |
| HBP | 15°/20% | 300 | 15.0% | 0.197 | 100% | 13.64 | 35.54 | 1.67 |
| APFP | 15°/20% | 300 | 10.0% | 0.117 | 100% | 18.33 | 38.75 | 2.31 |
| HBP | 30°/40% | 300 | 15.3% | 0.183 | 100% | 12.48 | 34.61 | 1.55 |
| APFP | 30°/40% | 300 | 18.3% | 0.240 | 100% | 13.03 | 35.40 | 1.92 |

These are descriptive results. The three noise blocks were tuned separately, so they should not be read as a monotonic noise-response experiment.
