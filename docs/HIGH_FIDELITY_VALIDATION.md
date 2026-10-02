# High-fidelity continuous-kinematic validation

This artifact addresses review item 19 by adding a held-out continuous-kinematic stress test. It is deliberately **not** described as a physical-robot, ROS/Gazebo, or real-trajectory validation.

## Protocol

- Scenarios: IDs 204–211 (8 held-out scenarios from the existing deterministic generator).
- Conditions: DR-T and DR-SAFE, same planner interface and scenario IDs.
- Execution: continuous unicycle-style robot state rather than cell-to-cell teleportation.
- Robot radius: 0.35 cells.
- Dynamic-obstacle radius: 0.35 cells.
- Maximum speed: 0.85 cells/tick.
- Maximum acceleration: 0.18 cells/tick².
- Maximum heading rate: 30°/tick.
- Replanning: every 5 ticks.
- Estimation: constant-velocity Kalman filter with the scenario's observation noise.
- Collision metric: continuous swept-segment distance, including robot and obstacle radii.
- Planner budget: 8 ants × 10 iterations per replan for this stress-test adapter. These settings are intentionally reported because this is an engineering validation, not a replacement for the primary statistical runs.

## Results

| Metric | DR-T | DR-SAFE |
|---|---:|---:|
| Success rate | 75.0% | 62.5% |
| Any-collision rate | 50.0% | 25.0% |
| Mean collision events | 1.50 | 0.88 |
| Mean minimum continuous clearance (cells) | −0.061 | 0.125 |
| Mean distance driven (cells) | 42.03 | 44.34 |
| Mean replans | 20.0 | 22.6 |
| Mean planning time per run (s) | 1.141 | 1.656 |

The result is descriptive. It is not pooled with the 200/300-run inferential analyses.
