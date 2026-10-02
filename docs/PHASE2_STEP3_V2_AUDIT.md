# Phase 2 Step 3 — closed-loop ACO failure correction audit

**Date:** 2026-10-01
**Status:** implementation correction validated; 200-scenario rerun not yet complete.

## Problem reproduced

The existing Phase-3 closed-loop adapter was independently rerun on five scenarios that had zero-distance DR-T/DR-SAFE outcomes (scenario IDs 11, 23, 38, 107, 186). Under the frozen Phase-3 budgets, the original adapter returned no executable path for DR-T and DR-SAFE on these cases. The first planning call therefore produced no movement.

The adapter's transition heuristic used only the local edge length (`1` or `sqrt(2)`) rather than a goal-directed heuristic. With no initial pheromone guidance, the stochastic no-revisit construction could consume the small colony without reaching the goal. The original runner also passed an empty dynamic-obstacle list to HB, so HB did not receive its intended current occupancy information in the closed-loop adapter.

## Correction

New modules were created; frozen planner files were not edited:

- `experiments/phase3_abaco_v2.py`
- `experiments/phase3_runner_v2.py`

Corrections:

1. Use a goal-directed transition heuristic based on candidate-cell distance to the goal.
2. Pass current dynamic-obstacle occupancy to HB; HBP/DR-T/DR-SAFE continue to use the estimator-derived prediction.
3. Record DR-SAFE floor-relaxation events instead of silently losing the diagnostic.
4. Cap individual path construction at 100 steps for the closed-loop adapter; this is above the path lengths observed in the validation cases and reduces wasted dead-end search.

The adapter remains an ABACO-family closed-loop adapter and continues to use eight-neighbour no-revisit construction, pheromone evaporation, the continuous DR-T cost, and the DR-SAFE floor/fallback semantics.

## Validation

The five previously selected zero-distance scenarios were rerun. All four ACO methods produced non-zero movement in every case; the zero-distance failure was therefore eliminated in this targeted reproduction set.

A 20-scenario smoke block (scenario IDs 4–23), using the same six methods and frozen parameter selections, also produced zero zero-distance runs for every method.

The smoke-block counts were:

| Method | N | Zero-distance | Successful runs | Collision runs |
|---|---:|---:|---:|---:|
| HB | 20 | 0 | 13 | 2 |
| HBP | 20 | 0 | 17 | 2 |
| DR-T | 20 | 0 | 16 | 0 |
| DR-SAFE | 20 | 0 | 11 | 3 |
| Space-time A* | 20 | 0 | 20 | 4 |
| D* Lite + DWA | 20 | 0 | 20 | 4 |

## Boundary

This validates the implementation correction, not the final confirmation result. The full 200-scenario Step-3 rerun remains outstanding. The existing manuscript Table 15 must not be updated from the 20-scenario smoke block.

Because the adapter implementation changed, its old tuning record should not be treated as a final tuning record for the corrected adapter. A fresh tuning pass is required before any new confirmation analysis is frozen.
