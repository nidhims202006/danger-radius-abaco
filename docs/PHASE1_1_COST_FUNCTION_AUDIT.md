# Phase 1.1 — Continuous cost-function correction audit

**Date:** 2026-09-30
**Status:** **Completed as an engineering correction; final confirmation remains Phase 3 work.**

## 1. Requirement

Task 1.1 requires a new, non-frozen danger-radius cost that is continuous at `R`, without editing the frozen v22 planner, followed by an ablation check for regression.

## 2. Implemented cost

The new module is:

`danger_radius/ABACO_safety_pred_continuous.py`

For distance `d` to a predicted obstacle position, the soft penalty is:

`C(d;R,K,eps) = K * max(0, 1/(d+eps) - 1/(R+eps))`.

Therefore `C(R)=0` and `C(d)=0` for `d >= R`. The frozen file `danger_radius/ABACO_safety_pred.py` was not modified.

## 3. Parameter check

An exploratory 20-seed tuning check on seeds `10000–10019` examined the continuous formulation around the Phase-1 search region. The candidate used for the full engineering ablation was:

- `R = 5.5`
- `K = 4.5`
- `D_SAFE = 0` for the soft-only arm

This parameter choice is **not confirmation evidence** because the same 20 seeds were inspected during selection. It is recorded only to identify the implementation candidate that was subsequently stress-checked on the complete 300-seed block.

## 4. 300-seed engineering ablation

The candidate was then run on the complete paired main-environment block, seeds `10000–10299`, against the frozen v22 soft-only reference.

| Metric | Frozen v22 SOFT | Continuous candidate | Difference (new − old) | 95% CI for paired difference | Wilcoxon p |
|---|---:|---:|---:|---:|---:|
| Path length (m) | 34.6458 | 34.8561 | +0.2104 | [-0.0237, 0.4444] | 0.1085 |
| Sharp turns | 12.2867 | 12.3267 | +0.0400 | [-0.5237, 0.6037] | 0.9739 |
| Minimum clearance | 2.2699 | 2.3322 | +0.0622 | [-0.1442, 0.2686] | 0.6474 |
| Collisions/run | 0.0500 | 0.0367 | -0.0133 | [-0.0505, 0.0238] | 0.4978 |

Total collision events in the compared records were 15 for the frozen reference and 11 for the continuous candidate.

No metric showed a statistically detectable degradation in this 300-run engineering ablation; the collision count decreased from 15 to 11. This closes the checklist's **engineering ablation** criterion for 1.1.

## 5. Important limitation

The 300-seed block is the existing main-environment ablation block, not the final closed-loop confirmation study specified in `docs/EVAL_PROTOCOL_v2.md`. The candidate parameters were selected after inspecting a 20-seed exploratory subset, so the p-values above must **not** be presented as preregistered confirmation evidence.

The final parameter selection and confirmation claims remain subject to Phase 2/3, where the disjoint tuning/confirmation split and the frozen evaluation protocol are used.

## 6. Integrity checks

- Frozen planner code was not edited.
- The original Phase-0 provenance changes remain the only expected mismatches against `docs/SHA256_v22.txt`.
- `experiments/check_paper_numbers.py`: **348 agree, 0 disagree**.
- No Phase-1.1 ablation result has been inserted into the manuscript, because the run is engineering evidence rather than the final confirmation study.
