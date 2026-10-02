# Phase 3 — Method, Reproducibility, and Provenance Audit

Date: 2026-10-01
Status: IN PROGRESS — audit checkpoint completed

## 1. Scope

This Phase 3 pass audits the post-Phase-2 code/results/manuscript package for:
- reproducibility and frozen-code integrity;
- parameter/protocol provenance;
- method specification and implementation boundaries;
- runtime/scaling evidence;
- consistency between the current manuscript and the verified stored results.

No Phase-4 manuscript rewrite is treated as complete by this document.

## 2. Checks completed

### 2.1 Frozen-code integrity
- Phase-2 final freeze manifest: PASS.
- Phase-2 Step-3/4 new-module hashes: PASS.
- Phase-3 pre-confirmation freeze manifest: PASS.
- Existing stored-run reproduction guard: PASS, 12/12 runs reproduced with 0 mismatches.
- Scaling benchmark matrix: PASS, 90/90 grid-method-obstacle cases present.

### 2.2 Current manuscript numerical check
`check_paper_numbers.py` against `Danger-Radius_Paper_v57_step6_crosschecked.docx`:
- 324 cells/values agree.
- 0 direct disagreement with the values that the checker currently knows about.

This check is a consistency check against the checker’s registered expectations; it does not prove that those expectations are the latest experimental results.

## 3. Critical provenance finding

The previously generated `results/priority13_drt_extension_v2/` Step-6 output is not acceptable as final evidence.

The stored DRT and DRSAFE records in that directory are numerically identical for each noise block and contain nonzero floor-fallback counts for DRT. That is incompatible with the intended implementation distinction:
- DR-T: continuous time-aligned soft cost, **no hard floor**;
- DR-SAFE-T: same soft cost plus the D_SAFE hard floor.

A direct same-seed smoke test of the current implementation (`priority13_add_drt_drsafe_v2.py`) confirms the intended separation: DRT produced `fb=0` while DRSAFE produced `fb=1610` for seed 10300 under n1, with different path/turn/clearance results.

Therefore the earlier Step-6 v2 statistical output and manuscript values derived from it are quarantined and must not be cited as final evidence.

## 4. Corrective action started

A clean rerun has been launched from the current corrected implementation under:
`results/priority13_drt_extension_v3_clean/`

The clean rerun uses:
- n1 = (5 deg, 10% velocity noise);
- n = (15 deg, 20% velocity noise);
- n3 = (30 deg, 40% velocity noise);
- 30 tuning seeds per noise level;
- 300 confirmation seeds per noise level;
- six matched candidates for DR-T and DR-SAFE-T;
- R values including 3.5, 4.5 and 5.5;
- D_SAFE = 1.5 for DR-SAFE-T only;
- identical candidate-budget structure for the two methods.

The clean rerun must finish and pass a mode-separation check before its results are used in the manuscript.

## 5. Method specification status

The manuscript already documents several important boundaries:
- legacy fixed-grid ABACO versus the separate closed-loop ABACO-family adapter;
- truncated historical DR-T formulation versus the boundary-continuous closed-loop variant;
- DR-T versus DR-SAFE definition;
- closed-loop tuning and common-clock evaluation;
- computational complexity at the algorithmic level.

Remaining Phase-3 work is to make the reproducibility package internally consistent with the latest Phase-2 results and to freeze a single parameter/protocol manifest for the final package.

## 6. Known manuscript consistency issues for Phase 4

The current manuscript still contains older closed-loop values in its closed-loop table (e.g. the table reporting DR-T success at 30.0% and DR-SAFE success at 18.5%). Those values belong to the earlier bounded-adapter run and do not match the corrected Phase-2 v2 confirmation results.

The manuscript also states in the closed-loop discussion that a separate ACO+DWA implementation was not included, while Phase 2 has since produced a matched-interface ACO+DWA baseline. This must be reconciled in Phase 4 rather than silently mixing the two evidence blocks.

The current Step-6 noise table also contains values derived from the quarantined v2 extension and must be replaced only after the clean rerun is validated.

## 7. Phase-3 acceptance criteria

Phase 3 will be closed only after:
1. the clean Step-6 rerun finishes;
2. DRT/DRSAFE mode separation is verified across the stored confirmation records;
3. all final result files receive hashes;
4. the final parameter/protocol manifest is frozen;
5. the manuscript's numerical claims are reconciled against the verified result files;
6. the repository reproduction checks pass again;
7. unresolved limitations are explicitly recorded for Phase 4.
