# Phase 3 analysis plan — frozen before confirmation

Date: 2026-09-30

## Confirmation design
- Confirmation scenarios are scenario IDs 4–203 from the seed-controlled generator (200 scenarios), disjoint from tuning IDs 0–3.
- All six methods use the same 200 scenario IDs and the same scenario realization.
- No confirmation result may be used to change parameters.
- Maximum closed-loop duration: 45 ticks for this Phase-3 implementation run.

## Methods
HB, HBP, DR-T, DR-SAFE, space-time A*, and D* Lite + DWA-style local planner.

## Primary outcomes
1. Any-collision rate per run.
2. Time to goal; failures are retained and coded as 45 ticks for the prespecified tuning score. Confirmation reports failures separately and uses the protocol's primary endpoint definition.

## Secondary outcomes
Distance driven, minimum physical clearance, turn count, planning time, replans, and floor-relaxation behavior where applicable.

## Tuning rule
For the tuning set only, select the candidate minimizing:
`0.5 * any_collision_rate + 0.5 * median(time_to_goal_or_45) / 45`.
Ties are resolved by lower collision rate, then lower median time.

Each method received six candidate configurations. DR-T and DR-SAFE candidate sets included R=5.5. The tuning scenarios are intentionally treated as a small engineering tuning pilot; they are not confirmation evidence.

## Statistical analysis
- Paired scenario-level comparisons.
- Binary any-collision endpoint: paired binary analysis reported with paired rates.
- Continuous endpoints: paired differences, 95% CIs, Wilcoxon signed-rank tests and effect sizes where defined.
- Holm correction is applied to the frozen primary comparison family.
- No post-confirmation parameter selection.

## Scope decision rule
After confirmation, if the time-explicit planners outperform every ACO method on every primary and secondary axis, record the scope as obstacle-cost design inside ACO planners and assess journal fit. No outcome-dependent change is allowed before the confirmation data are frozen.
