# Direct planning scaling and memory benchmark

## Protocol
- Grid sizes: 12x12, 18x18, 25x25, 30x30, 40x40.
- Static obstacle density: 8%.
- Dynamic obstacles: 3.
- One deterministic benchmark scenario per grid size.
- Methods: HB, HBP, DR-T, DR-SAFE, space-time A*, D* Lite + DWA.
- Settings: retained from the frozen Phase-3 comparison; no new tuning.
- Runtime: measured planner computation time for one direct planning call.
- Memory: peak process RSS from `/usr/bin/time -v` for the same isolated call.

## Interpretation
The benchmark is an engineering scaling probe, not a statistical performance comparison. Runtime values are environment-specific. Peak RSS includes the Python interpreter and imported libraries, so it is not an algorithm-only memory requirement.

The observed peak RSS range was approximately 90.3–92.5 MB across the tested cases. A larger runtime increase was observed for space-time A* at 40x40 in the tested configuration, consistent with its time-expanded search state space.
