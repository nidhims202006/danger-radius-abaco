# Phase 3 closure record

Date: 2026-09-30
Status: CLOSED WITH DOCUMENTED LIMITATIONS

## 1. Scope completed

Phase 3 confirmation execution and the prespecified paired analysis are complete.

- Tuning: six methods, six candidates per method, engineering tuning scenarios 0–3.
- Confirmation: scenario IDs 4–203, 200 scenarios per method.
- Methods: HB, HBP, DR-T, DR-SAFE, space-time A*, D* Lite + DWA.
- Total confirmation runs: 1,200.
- No confirmation result was used to change parameters.
- The pre-confirmation hashes for the frozen analysis plan, tuned parameters, Phase-3 modules, and scenario generator still pass.

## 2. Confirmation result used for the scope decision

The logged-axis comparison does not trigger the frozen scope rule. The time-explicit planners do not outperform every ACO method on every logged primary and secondary axis. In particular, their minimum-clearance results are lower than the ACO methods, and their collision rates are not uniformly lower than all ACO methods.

Therefore no scope change is made on the basis of the Phase-3 confirmation results.

## 3. Statistical limitation

The evaluation protocol requires Holm correction over a primary comparison family frozen before confirmation. The Phase-3 freeze manifest records that requirement but does not enumerate the exact membership of that family. The confirmation analysis therefore reports paired estimates, confidence intervals, effect sizes, and unadjusted tests, but does not manufacture a Holm-adjusted family after seeing the results.

This means the Phase-3 record does **not** make Holm-adjusted inferential claims from this confirmation block. This is a provenance limitation, not a parameter-selection change.

## 4. Floor-relaxation limitation

The protocol lists floor-relaxation count/rate as a secondary outcome for floor-based methods. The frozen Phase-3 runner did not emit that field. Consequently, the literal all-secondary-axis scope rule cannot be evaluated on that unlogged axis.

The scope decision is nevertheless already negative on the logged axes, so no outcome-dependent scope change is required.

## 5. Scientific interpretation boundary

The Phase-3 closed-loop ABACO module is a new evaluation adapter created for this phase. It is not asserted to be a source-level reproduction of the frozen v22 ABACO implementation. The existing reproduction guard passed for the stored v22 runs, but that guard tests the existing reproduction workflow rather than equivalence of the new Phase-3 adapter.

Accordingly, the Phase-3 confirmation results are recorded as closed-loop engineering evaluation evidence for the Phase-3 implementation, not as a direct replacement for the manuscript's frozen v22 evidence.

## 6. Disposition

Phase 3 is closed. The documented limitations must remain visible in the Phase-4 manuscript work. No manuscript claim of Holm-adjusted significance should be generated from this Phase-3 confirmation block unless a valid pre-confirmation comparison family can be demonstrated from contemporaneous records.

Next phase: Phase 4 manuscript revision and number/provenance checks.
