# Phase 2 Steps 3-4 status

Date: 2026-10-01

## Step 3 — corrected closed-loop ACO confirmation

The corrected v2 adapter was tuned on scenarios 0-3 and confirmed on scenarios 4-203 (200 scenarios) together with the four existing comparison methods.

Frozen parameters used for the 200-scenario confirmation:
- HB: 16 ants, 20 iterations
- HBP: 16 ants, 20 iterations
- DR-T: R=3.5, K=0.5, 12 ants, 20 iterations
- DR-SAFE: R=3.5, K=0.5, D_SAFE=0.75, 12 ants, 20 iterations
- Space-time A*: horizon 30
- D* Lite + DWA: progress=1, clearance=0.1, max expansions=50

Results:

| Method | N | Success | Collision | Zero-distance | Mean planning time (s) |
|---|---:|---:|---:|---:|---:|
| HB | 200 | 69.0% | 31.0% | 0 | 2.127 |
| HBP | 200 | 75.0% | 26.5% | 0 | 1.946 |
| DR-T | 200 | 72.5% | 18.0% | 0 | 1.903 |
| DR-SAFE | 200 | 67.5% | 23.0% | 1 | 2.370 |
| Space-time A* | 200 | 88.0% | 21.5% | 7 | 0.020 |
| D* Lite + DWA | 200 | 100.0% | 22.5% | 0 | 0.137 |

DR-SAFE had floor-relaxation events in 193/200 runs (7618 total). The isolated DR-SAFE zero-distance case was scenario 80; all 12 ants exhausted the first construction without producing a route despite floor fallback. This is treated as an isolated search/floor interaction, not the original systematic zero-distance adapter failure.

## Step 4 — stronger baselines

Two additional matched-interface baselines were implemented in `experiments/strong_baselines.py` and runner v3:

1. SIPP-style safe-interval planner using the same predicted occupancy representation.
2. ACO+DWA hybrid using ACO for a global/static route and a DWA-style local selector for current dynamic occupancy.

These are matched-interface implementations, not source-code reproductions of published methods.

The literature check identified Gong et al. (2022), *An improved ant colony algorithm for integrating global path planning and local obstacle avoidance for mobile robot in dynamic environment*, DOI 10.3934/mbe.2022579, as a relevant ACO + local-avoidance reference. Exact reproduction is not claimed because the published method uses its own robot/environment model; the implemented baseline is explicitly labelled ACO+DWA matched baseline.

Tuning on scenarios 0-3 selected:
- SIPP: horizon 30
- ACO+DWA: 8 ants, 10 iterations, clearance weight 0.1, goal weight 1.0

Confirmation on scenarios 4-203:

| Method | N | Success | Collision | Zero-distance | Mean planning time (s) |
|---|---:|---:|---:|---:|---:|
| SIPP | 200 | 84.5% | 18.5% | 7 | 0.0137 |
| ACO+DWA | 200 | 95.5% | 16.0% | 0 | 1.961 |

The additional baselines materially change the comparison set and therefore must be included in any subsequent statistical family if they remain in the final paper.

## Not yet complete

- Step 5: scale beyond the 200-scenario confirmation block and stratify the results by workspace, density, dynamic-obstacle count, motion type and noise level.
- Step 6: multi-noise DR-T/DR-SAFE block with fresh equal-budget tuning.
- Step 7: final paired statistical analysis with the predeclared Holm family.
- Step 8: optional high-fidelity/real-data evaluation.

No manuscript files were modified by this status update.
