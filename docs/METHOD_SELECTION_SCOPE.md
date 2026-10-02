# Method-selection scope: DR-T

## What the results do and do not support

The closed-loop results are not a general performance claim for DR-T. On the 200-scenario confirmation set, the reported success / any-collision rates are:

| Method | Success | Any collision |
|---|---:|---:|
| DR-T | 72.5% | 18.0% |
| ACO+DWA | 95.5% | 16.0% |
| D* Lite + DWA | 100.0% | 22.5% |
| ORCA | 100.0% | 9.5% |
| MPC | 100.0% | 3.0% |

These values do not justify presenting DR-T as a replacement for the tested alternatives. In particular, DR-T is not selected on the basis of a superior overall success/collision profile, and no general planner ranking is claimed.

## Architectural reason to use DR-T

The contribution is a dynamic-obstacle cost modification inside an existing ACO/grid transition rule. The intended use case is therefore a system for which retaining the grid/ACO search architecture and its replanning framework is an explicit design constraint. DR-T changes the obstacle-cost term by evaluating obstacles at the predicted position corresponding to the candidate waypoint's estimated arrival step; it does not require replacing the search representation with an explicitly time-expanded planner or adding a separate local controller.

This is an architectural integration option, not an end-to-end performance claim. If the planner architecture is unconstrained, the current experiments do not provide a performance-based reason to prefer DR-T over the tested alternatives.

## Evidence boundary

The package should therefore describe DR-T as a modular obstacle-cost contribution to an ACO/grid planner. Claims of superiority over ACO+DWA, D* Lite + DWA, ORCA, MPC, or other dynamic-obstacle planners are outside the evidence provided by this study.
