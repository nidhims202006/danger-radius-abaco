# Evaluation Protocol v2 — Phase 1 design freeze

**Date:** 2026-09-30  
**Version:** v2.0  
**Status:** design frozen before any Phase-1 confirmation/ablation run

## 1. Purpose

This protocol defines the evaluation that follows the Phase-1 cost-function correction and is the design basis for the later closed-loop work. It is intentionally fixed before confirmation results are inspected.

The manuscript framing remains **DR-T = time-aligned soft danger-radius cost**; DR-SAFE is DR-T plus a hard clearance floor.

## 2. Cost function

The Phase-1 soft penalty is

`C(d; R, K, eps) = K * max(0, 1/(d+eps) - 1/(R+eps))`.

It is continuous at `d = R` and equals zero at and beyond the danger radius. `eps` remains the planner's existing numerical epsilon. The penalty is incorporated into the same transition heuristic used by the ABACO planner.

The hard-floor rule remains separate from the soft cost. A floor is feasible only when at least one candidate satisfies the clearance threshold; if no candidate is feasible, the existing fallback mechanism may relax the floor. Such relaxation must be counted and reported, not hidden.

## 3. Methods and information

Primary method family:
- HB: hard occupancy/blocking only.
- HBP: hard blocking with time-aligned predicted obstacle positions.
- DR-T: continuous time-aligned soft cost only.
- DR-SAFE: continuous DR-T plus hard clearance floor.

Additional baselines required for the full evaluation:
- Space-time A* using the same predicted trajectories, with state `(row, col, t)` and cost = time.
- D* Lite with moving obstacles represented as dynamic blocked cells.
- A DWA/MPC-style local planner on the same grid/world interface.

All methods must receive the same scenario information that is available to the corresponding comparison. Planning time is measured for every replan.

## 4. Scenario design

At least **200 independent scenarios** are required. The design must include:

- multiple grid/workspace sizes;
- multiple obstacle densities;
- 1–8 dynamic obstacles;
- multiple obstacle speeds;
- curved motion;
- stop-and-go motion;
- random-walk motion;
- several observation/estimate noise levels;
- solvability checks before scoring.

A real Kalman-filter estimator is used for noisy position observations. Perturbed ground-truth velocity is not treated as the final estimator model.

Scenario generation is seed-controlled and reproducible. Scenario IDs and seeds are retained with every result.

## 5. Tuning and confirmation split

Tuning and confirmation scenarios are disjoint.

- **Tuning set:** used only to select parameters.
- **Confirmation set:** untouched until parameters, code hashes, and this analysis plan are frozen.

Every method receives the same tuning budget. For DR-T/DR-SAFE the tuning search includes `R = 5.5` as required by the resubmission checklist, together with the selected `K` values. APF tuning includes its radius and strength parameters. Each competing planner receives an equivalently bounded parameter-search budget appropriate to its own parameterization.

No confirmation result may be used to change parameters.

## 6. Primary outcomes

Primary metrics:
1. **Any-collision rate per run** — a run is a collision run if the physical collision criterion is met at least once.
2. **Time to goal** — world-clock ticks/time until the robot reaches the goal; failed runs are retained and reported explicitly.

Secondary metrics:
- distance driven;
- minimum physical clearance;
- planning time per replan;
- total computation time;
- path/trajectory turn count where defined consistently across methods;
- floor-relaxation count/rate for floor-based methods.

Physical collision is defined using robot and obstacle radii: collision occurs when centre distance is less than the sum of radii.

## 7. Statistical plan

Paired comparisons use the same scenario/seed across methods.

The primary inferential family is the pre-specified set of primary comparisons involving the primary methods and baselines. The exact membership of that family is frozen in the run manifest before confirmation execution. The family uses Holm adjustment for multiple comparisons.

For continuous paired outcomes, report paired mean/median difference as appropriate, 95% confidence intervals, effect size, and a paired non-parametric test (Wilcoxon signed-rank) unless a justified alternative is specified before unblinding.

For binary any-collision outcomes, report paired rates and an appropriate paired binary analysis; do not substitute a continuous-test interpretation for a binary endpoint.

Two-sided alpha = 0.05 unless a later protocol amendment is made before confirmation execution.

## 8. Noise / estimator conditions

At minimum, evaluate:
- exact/noiseless estimates;
- low observation noise;
- moderate observation noise;
- high observation noise.

The estimator is a Kalman filter driven by noisy observations. Noise settings and filter parameters are fixed before confirmation runs.

## 9. Phase-1 implementation ablation

Before the full closed-loop evaluation, the corrected continuous cost is checked against the frozen v22 implementation on the existing 300-seed main-environment ablation block (`10000–10299`). This is an implementation sanity check, not the final resubmission evidence.

The same paired seeds and planner budget are used. The corrected soft-cost arm is compared with the frozen soft-only arm; continuous-cost DR-SAFE variants are also rerun for the component check. Results are stored separately from the frozen v22 results.

No claim of equivalence is made if the corrected cost changes the resulting paths. The purpose is to identify regression or material behavioural change before Phase 2.

## 10. Freeze / provenance

Before any Phase-1 implementation ablation is run, record SHA-256 hashes for:
- this protocol;
- the new continuous-cost planner module;
- the Phase-1 runner/analysis code.

No result is used to alter the cost definition or primary analysis plan after this freeze. Any later change is a protocol amendment and must be labelled as such.

## 11. Explicit exclusions

This document does not constitute the Phase-2 closed-loop implementation. The existing frozen files remain unchanged. The final confirmation study must not be reconstructed from the existing v22 results alone.
