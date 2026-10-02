# Priority 20 — post hoc ORCA and MPC closed-loop baselines

Added after the v66.5 freeze, in response to the reviewer comment that ORCA, MPC and related baselines were
not evaluated.  Everything here is **post hoc**; no frozen file was modified.

## Files
- `experiments/orca_mpc_baselines.py` — ORCA (RVO2-style half-planes, full responsibility, exact selection over
  the nine admissible displacements) and finite-horizon discrete MPC (DP over step x cell).
- `experiments/phase4_runner_orca_mpc.py` — copy of `phase3_runner_v3.py` plus the `orca` / `mpc` branches.
- `experiments/verify_orca_mpc_runner.py` — regression check: the copy reproduces the stored SIPP and ACO+DWA
  per-run results (all fields except wall-clock time) on scenarios 4-43 (80 runs, 0 mismatches at v67).
- `experiments/run_orca_mpc_tuning.py`, `run_orca_mpc_eval.py` — equal-budget tuning and the 200-scenario run.
- `experiments/analyze_orca_mpc_paired.py` — exact McNemar + bootstrap CIs; 4-test and 14-test Holm families.
- `experiments/check_orca_mpc_numbers.py` — recomputes every inserted manuscript number from per-run files.
- Results: `results/phase4_orca_mpc_tuning/`, `results/phase4_orca_mpc_perrun.json`, `results/phase4_orca_mpc_stats/`.

## Protocol
Six candidate configurations per method on tuning scenarios 0-3; selection rule
0.5*collision_rate + 0.5*median_time_to_goal/45 (failures = 45 ticks); ties broken by listing order.
Candidate grids were fixed before any of scenarios 4-203 was run.  Selected: ORCA tau=2, buffer=0.15;
MPC horizon=4, r_safe=1.5, w_coll=5.  Many candidates tied on the four tuning scenarios.
During development both planners were smoke-tested on scenarios 0-3 only (one bug fixed: MPC procrastination,
resolved by making the goal cell absorbing).

## Caveats (also in the manuscript)
- Matched-interface re-implementations, not source reproductions.
- ORCA/MPC are single-step controllers re-solved every tick (like the DWA-based baselines); the ACO family,
  space-time A* and SIPP replan every fifth tick.  Method and replanning cadence are confounded.
- ORCA/MPC use Kalman estimates only.
- Holm family extended from 10 to 14 tests; the three affected original Holm values are listed in Table 17C's caption.
