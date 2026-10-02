# Review-closure v29

Implemented in the manuscript/code package:
- one-cell reporting convention is explicit (1.0 m per cell);
- no closed-loop smoothness advantage is claimed; sharp-turn evidence is fixed-grid only;
- fixed-grid iteration is explicitly the declared discrete simulation clock, while closed-loop is the primary execution-level evidence;
- start-waypoint exclusion is implemented in the canonical metric and is the primary collision convention for Tables 18–21; start exposure remains separately audited;
- Gong et al. (2022) is explicitly scoped as related work rather than represented by a non-equivalent reproduction;
- α/β/ρ equal-budget tuning, matched five-tick replanning, and the fresh frozen-seed audit are retained from v25.

Remaining external actions:
- public GitHub/Zenodo publication and DOI minting;
- physical/ROS-Gazebo/high-fidelity validation;
- full warehouse-style execution of the newly generated 24-scenario protocol (the generator is included, but no results are claimed here).
## Review item 19 update (v31)

A held-out high-fidelity continuous-kinematic validation was added for scenarios 204–211 (N=8). It executes the grid plan with bounded unicycle dynamics, noisy CV-Kalman state estimation, five-tick replanning, and continuous swept-segment collision checks. The results are descriptive and are not presented as physical-robot or ROS/Gazebo validation. See `experiments/high_fidelity_kinematic_validation.py`, `results/high_fidelity_kinematic_validation/`, and `docs/HIGH_FIDELITY_VALIDATION.md`.
