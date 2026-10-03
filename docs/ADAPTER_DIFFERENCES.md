# Closed-loop ABACO-family adapter: differences from the fixed-grid ABACO implementation

Applies to `experiments/phase3_abaco_v2.py` and `experiments/phase3_runner_v3.py`
(Phase-2 corrected closed-loop block, `results/phase2_step3_v2*`). Disclosed in manuscript Section 5.11.

| Item | Fixed-grid ABACO (`abaco/`, `danger_radius/`) | Closed-loop adapter (`phase3_abaco_v2.py`) |
|---|---|---|
| Heuristic | eta = 1/(d(i,j)+eps), edge length only (no goal information on an 8-neighbour grid) | eta = 1/(dist(candidate, goal)+1e-6), goal-directed |
| HB / HBP rule | eta divided by 1+10 within 0.5 cell of the obstacle position (HB: current position, HBP: predicted position); in every condition the obstacle's current cell is also removed from the snapshot grid | same eta/(1+10) rule (HB: current cells, HBP: Kalman-predicted cells); no current-cell grid removal in any condition |
| DR cost | truncated K/(d+eps) inside R (Eq. 7) | boundary-continuous K*max(0, 1/(d+0.1) - 1/(R+0.1)) inside R |
| Max construction steps | 500 | 100 |
| Pheromone | age-based Q sampling | evaporation 0.3, every successful ant deposits 1/L |
| Budget / parameters | 40 ants x 100 iterations; R=4.5, K=2.0 | tuned per method on scenarios 0-3 (see `results/phase2_step3_v2_tuning/`) |
| Prediction index | waypoint number of the chosen cell (1 for the first move) | number of moves already made (0 for the first move) |
| Replanning | none (single plan at convergence) | every 5 ticks, 50-step Kalman prediction, 45-tick horizon |

## Prediction-index sensitivity (resolved post hoc; manuscript Table 17B)
The prediction-index offset in the "Prediction index" row means the adapter evaluates predictions one step earlier than the
robot's execution time under the runner clock. It applies identically to HBP, DR-T and DR-SAFE (HB and ACO+DWA do not use it).
Its effect was measured in a post hoc sensitivity run: `experiments/phase3_abaco_v3.py` uses `predicted[min(step+1, len-1)]`;
HBP, DR-T and DR-SAFE were rerun on scenarios 4-203 with the frozen tuned settings (no retuning) via
`experiments/run_a1_sensitivity.py` and compared with the primary results by `experiments/analyze_a1_sensitivity.py`.
Results: `results/a1_sensitivity/` (`perrun_v3.json`, `a1_summary.json`). The primary results (Table 17) keep the original indexing.
Summary: success changed by at most 1.5 points; collisions changed by +6.5 (HBP), +3.5 (DR-T), -1.0 (DR-SAFE) points.

## Pseudocode
Manuscript Section 4.2 (Algorithm 2: time-aligned transition step, with complexity) and Section 5.11 (Algorithm 3: closed-loop protocol) give the pseudocode for these implementations.

## Legacy-pheromone rerun (post hoc; manuscript Tables 4A and 4B; release v36)
Item (iii) above (construction limit and pheromone deposit) was measured by restoring the fixed-grid age-based Q deposit and the 500-step limit
(`experiments/phase5_adapters.py`, `ADAPTER=legacy`). The age-based deposit, not the step limit, accounts for the change in closed-loop success.
Protocol, files, gates and caveats: `docs/PHASE5_POST_HOC.md`.
