# Review-closure v29

Implemented in the manuscript/code package:
- one-cell reporting convention is explicit (1.0 m per cell);
- no closed-loop smoothness advantage is claimed; sharp-turn evidence is fixed-grid only;
- fixed-grid iteration is explicitly the declared discrete simulation clock, while closed-loop is the primary execution-level evidence;
- start-waypoint exclusion is implemented in the canonical metric and is the primary collision convention for Tables 18–21; start exposure remains separately audited;
- Gong et al. (2022) is explicitly scoped as related work rather than represented by a non-equivalent reproduction;
- α/β/ρ equal-budget tuning, matched five-tick replanning, and the fresh frozen-seed audit are retained from v25.

Completed publication actions:
- public GitHub repository: https://github.com/nidhims202006/danger-radius-abaco.git
- public Zenodo deposit and DOI assignment: 10.5281/zenodo.23106834

Remaining validation limitations:
- no physical-robot or ROS/Gazebo validation;
- no full warehouse-style execution of the newly generated 24-scenario protocol (the generator is included, but no results are claimed here).
## Review item 19 update (v32)

A held-out high-fidelity continuous-kinematic validation was added for scenarios 204–211 (N=8). It executes the grid plan with bounded unicycle dynamics, noisy CV-Kalman state estimation, five-tick replanning, and continuous swept-segment collision checks. The results are descriptive and are not presented as physical-robot or ROS/Gazebo validation. See `experiments/high_fidelity_kinematic_validation.py`, `results/high_fidelity_kinematic_validation/`, and `docs/HIGH_FIDELITY_VALIDATION.md`.

## Review item 2 — floor evidence boundary (v35)

The hard floor is no longer presented as a mechanism responsible for the main DR-T result. The manuscript now identifies DR-T as the primary design contribution and retains DR-SAFE only as a secondary, explicitly negative-result extension. The exact-estimate confirmation ablation shows no incremental collision or turn benefit from the floor; the floor is relaxed on the winning path in 29% of confirmation runs. Limited noisy-estimate signals are retained as exploratory evidence and are not used as a primary claim. The N=8 continuous-kinematic check is likewise not presented as evidence that the floor improves safety.
