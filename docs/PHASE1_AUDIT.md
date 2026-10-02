# Phase 1 audit — cost function and evaluation design

**Date:** 2026-09-30  
**Starting repository:** v22-freeze + Phase 0 provenance audit  
**Status:** Phase 1 design is frozen; Task 1.1 engineering correction and 300-seed ablation are complete. Final confirmation remains Phase 2/3.

## 1.1 Continuous cost function

The frozen v22 time-aligned soft penalty was of the form `K/(d+eps)` for `d < R` and zero at/above `R`. This has a discontinuity at `R`.

A new, non-frozen module was added:

`danger_radius/ABACO_safety_pred_continuous.py`

It uses the continuous form

`K * max(0, 1/(d+eps) - 1/(R+eps))`.

The original frozen `danger_radius/ABACO_safety_pred.py` was not edited.

A direct numerical check confirms the new cost approaches zero at `R`, is exactly zero at `R`, and remains zero beyond `R`.

### Implementation ablation

The new implementation was run on paired main-environment seeds **10000–10019 (N=20)** at `R=4.5`, `K=2.0`, using the existing time-aligned predicted-position runner. Frozen v22 SOFT results were used as the reference; the frozen planner was not re-run or modified.

For the soft-only arm:

| Metric | Frozen v22 SOFT mean | Continuous mean | Difference (new-old) |
|---|---:|---:|---:|
| Path length (m) | 35.292 | 34.897 | -0.395 |
| Sharp turns | 13.80 | 13.45 | -0.35 |
| Minimum clearance | 2.582 | 1.840 | -0.742 |
| Collisions/run | 0.050 | 0.000 | -0.050 |

The smoke ablation therefore found **no collision regression** in these 20 paired runs, while minimum clearance was lower on average. Because the clearance change is material and the required checklist criterion says the ablation must show no regression, **Task 1.1 is closed as an engineering correction; final confirmation remains deferred to Phase 2/3.**. The new module is retained for the controlled tuning/closed-loop phase. The full 300-seed engineering ablation is documented separately in `docs/PHASE1_1_COST_FUNCTION_AUDIT.md`; it is not promoted to manuscript evidence.

Continuous DR-SAFE (D_SAFE=1.5, R=4.5, K=2.0) was also executed for the same 20 seeds as an implementation check; its results are stored separately and are not used as manuscript evidence.

## 1.2 Evaluation design

`docs/EVAL_PROTOCOL_v2.md` freezes the planned evaluation before confirmation runs. It specifies:

- >=200 scenarios;
- disjoint tuning and confirmation sets;
- curved, stop-and-go and random-walk obstacle motion;
- several noise levels;
- a Kalman-filter estimator;
- equal tuning budget across methods;
- inclusion of `R=5.5` in the DR-T/DR-SAFE tuning search;
- primary outcomes of any-collision rate and time to goal;
- paired comparisons and Holm correction;
- reproducible scenario/seed recording;
- physical-radius collision definition and planning-time logging.

The protocol is design-frozen. Co-author read/sign-off is not asserted because it was not supplied in the source material.

## Frozen-file integrity

The Phase 1 work did not modify the frozen planner/result code. `sha256sum -c docs/SHA256_v22.txt` reports only the two known Phase-0 changes: `docs/FRESH_SEED_PROTOCOL.md` and `paper/Danger-Radius_Paper_v22.docx`.

The v22 paper number checker still reports **348 cells/values agree; 0 disagree**.

## Manuscript handling

No new Phase-1 ablation result has been inserted into the manuscript. The 20-run implementation check is not the planned >=200-scenario closed-loop confirmation study and therefore should not be presented as new headline evidence.
