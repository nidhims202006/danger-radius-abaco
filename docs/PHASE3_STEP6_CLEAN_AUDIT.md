# Phase 3 — Clean Step-6 Rerun Audit

Date: 2026-10-01
Status: COMPLETE — clean supplementary Step-6 block validated

## Scope

This audit covers `results/priority13_drt_extension_v3_clean/`, the corrected supplementary fixed-grid Priority-13 extension for DR-T and DR-SAFE-T under three observation-noise levels. It is distinct from the Phase-2 closed-loop confirmation.

## Execution completeness

- Noise levels: n1 = (5 deg, 10% velocity noise), n = (15 deg, 20%), n3 = (30 deg, 40%).
- Tuning seeds: 9000–9029 (30 per noise level).
- Confirmation seeds: 10300–10599 (300 per noise level).
- Methods: DR-T and DR-SAFE-T.
- Confirmation blocks: 6/6 complete.
- Confirmation runs: 1,800 total.
- Every block contains 300 unique confirmation seeds spanning 10300–10599.
- Candidate set contains R = 3.5, 4.5, 5.5 with matched candidate-budget structure.

## Mode-separation validation

The corrected implementation maps DR-T to the continuous `drt` mode and DR-SAFE-T to the `safe` mode. Across all 900 DR-T confirmation runs:

- floor fallback count = 0.

Across DR-SAFE-T:

- n1 fallback events = 580,756;
- n fallback events = 598,326;
- n3 fallback events = 187,810.

The paired outputs are not identical. The number of paired runs with different path lengths / turn counts is:

- n1: 267 / 276 of 300;
- n: 250 / 275 of 300;
- n3: 287 / 287 of 300.

This passes the mode-separation requirement and invalidates the earlier v2 concern for this clean block.

## Reproduction check

Six stored confirmation records were rerun directly from the stored selected parameters and seeds:

- seeds 10300 and 10301;
- all three noise levels;
- both methods.

Result: 6/6 exact record matches, 0 mismatches.

## Confirmation summaries

| Noise | Method | Success | Collision-run rate | Mean length | Mean turns | Mean clearance | Mean fallback events/run |
|---|---|---:|---:|---:|---:|---:|---:|
| n1 | DR-T | 100% | 7.0% | 35.527 | 13.650 | 2.330 | 0 |
| n1 | DR-SAFE-T | 100% | 5.33% | 34.622 | 11.847 | 2.496 | 1935.9 |
| n | DR-T | 100% | 14.33% | 34.270 | 11.130 | 1.654 | 0 |
| n | DR-SAFE-T | 100% | 7.67% | 34.597 | 11.597 | 2.475 | 1994.4 |
| n3 | DR-T | 100% | 11.0% | 35.572 | 13.530 | 2.051 | 0 |
| n3 | DR-SAFE-T | 100% | 7.67% | 37.472 | 16.793 | 2.648 | 626.0 |

These are descriptive supplementary results. They are not evidence that one method is globally preferable, and they must not be merged with the closed-loop six-method confirmation.

## Statistical status

`step6_clean_analysis.json` contains paired DR-T versus DR-SAFE-T analyses by noise level. The stored p-values are unadjusted exploratory paired tests; no new Holm family is retroactively declared from the observed results.

## Provenance

`SHA256.txt` hashes the 15 JSON files in the clean Step-6 result directory, including confirmation results, tuning results, selected parameters, protocol, and the clean analysis output.

## Disposition

The clean Step-6 rerun is now valid as a supplementary fixed-grid noise study. The quarantined `priority13_drt_extension_v2` results remain excluded.

Phase 3 itself remains open until the broader acceptance criteria in `PHASE3_CURRENT_AUDIT.md` are completed, including final manuscript numerical reconciliation and the final reproducibility-package freeze.
