# Next steps after the v22 freeze (priority order, with owners' hand-off points)

Frozen (do not edit; hashes in docs/SHA256_v22.txt): `abaco/`, `danger_radius/`, `baselines/`, `experiments/drsafe_lib.py`, `experiments/fresh_run.py`. New work goes into new modules; re-run `experiments/verify_reproduction.py` if a frozen file must change.

## A. Blocking for resubmission (these answer the reviewer's core objections)
**A1. Closed-loop evaluation on a common clock** (code lead)
- New package `experiments/closedloop/`: at each world tick t plan from the robot's current cell against obstacle positions at t, execute one step, replan (every step or every k steps). Robot and obstacles get physical radii; collision = centre distance < r_robot + r_obstacle (report sensitivity to the radii).
- Metrics: physical collisions (any-collision rate per run), time to goal, distance driven, minimum clearance, planning time per replan.
- Unblocks: removes the start-cell artifact (Appendix B), the different convergence iterations per planner, and "iteration is not time"; every later comparison depends on it.
- Done when: HB, HBP, DR-T, DR-SAFE run in it deterministically; empty-grid and static-obstacle sanity tests pass.

**A2. Strong baselines, same information as DR-T** (code lead + second person)
- Space-time A* first (state (row, col, t); occupancy from the same predicted trajectories; cost = time). Then D* Lite with moving obstacles as dynamic blocked cells, and a DWA/MPC-style local planner on the grid. SIPP optional.
- Record wall-clock planning time for every method. Expect space-time A* to win on collisions and time on an 18x18 grid: decide now how the paper is scoped if it does (see D1).

**A3. Evaluation design, written and frozen before running** (statistics owner)
- >= 200 random scenarios (sizes, densities, 1-8 obstacles, speeds) plus non-constant-velocity motion (curved, stop-and-go, random walk); fresh tuning scenarios and fresh confirmation scenarios; tune every method with the same budget (DR-T: R incl. 5.5, K; APF: D0, eta; baselines' own parameters).
- Noise: several levels (`fresh_run.py` already supports `_n1` 5 deg / 10% and `_n3` 30 deg / 40%) and a real estimator (Kalman filter on noisy position observations) instead of perturbed ground-truth velocity.
- Primary metric = any-collision rate per run and time to goal; primary Holm family fixed in advance; hashes recorded as in `docs/FRESH_SEED_PROTOCOL.md`.

**A4. Decide the floor with the new data** (all co-authors)
- Rule in `docs/PAPER_POSITIONING.md`. If kept: redesign so it is not silently relaxed on the winning path (discard or penalise infeasible ants) and report the feasibility rate.

## B. High impact
- **B1. ABACO specification** (writer + code lead): pheromone update, the age variable (in the code it is a rank-based value assigned to sorted samples from uniform(10, 100)), pseudocode, per-iteration complexity O(ants x steps x 8 x obstacles), full parameter table. Files: `abaco/ABACO_baseline.py`, paper Section 3.
- **B2. Cost function**: the penalty jumps from 2/(4.5+0.1) = 0.44 to 0 at R, which is roughly a 6x drop in selection probability at the radius (beta = 5). Make it continuous (K(1/(d+eps) - 1/(R+eps)), clipped at 0) or stop calling it smooth; state how it differs from the APF form; rerun ablation and tuning.
- **B3. Use case + literature**: one concrete application (e.g. warehouse AMRs among people/forklifts), 20+ additional recent references on dynamic ACO planning, time-indexed planning, velocity obstacles, MPC; the paper has 26.
- **B4. Publish the package**: public repo, Zenodo DOI, data-availability statement (this repo is already structured for it).
- **B5. Runtime and memory**: store `computation_time` for every run. `drsafe_lib._flat` drops it and is hash-frozen, so capture it in the new closed-loop runner.

## C. Polish
- **C1. Language pass on the whole paper** (native-level editor). Known defects: leaked "Here is the input from the user:" in 5.1; garbled sentences in 4.1, 5.5, 5.7 ("The loud HBP situation", the sentence with "minus two point zero six"), 5.9 (last two sentences), 5.10, 5.11 (final sentence is cut off), Appendix B. After every editing pass run `python experiments/check_paper_numbers.py`.
- **C2. Structure**: state the cell size in metres, use one term for the protocol, add Highlights, check the abstract limit of the target journal (v22 abstract: 247 words), compress Sections 5.2-5.4 (pilot, snapshot floor, tuning) into an appendix.
- **C3. Response letter**: one row per reviewer point -> change -> location. Say plainly what was reframed (DR-SAFE -> DR-T) and why; never mark a point "done" that is only partly addressed (the v16 checklist did).

## D. Resubmission strategy notes
- D1. If time-explicit planners beat DR-T on every axis, the honest scope is "obstacle-cost design inside ACO planners" (which the abstract already states); consider whether the target journal fits. Do not hide the comparison.
- D2. Keep post hoc labels (Appendices A-C, floor-vs-soft under noise); the reviewer already spotted the weak points, so pre-empting them earns credibility.
- D3. Open item from this freeze: 4 of the 6 mismatching frozen-protocol hashes are undocumented (`danger_radius/ABACO_safety_pred.py`, `experiments/run_apf_main.py`, `experiments/analyze_apf_main.py`, plus the APF docstring). If the original release exists (git history or an earlier zip), diff them and record the result in `docs/FRESH_SEED_PROTOCOL.md`; until then word Section 5.10's hash statement carefully.
