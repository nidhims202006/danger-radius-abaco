# Danger-Radius / ABACO — Submission Code & Reproducibility Package

**Package:** v67-orca-mpc-posthoc (v66.5-c6-item19-archive-tidy plus post hoc ORCA/MPC baselines)  
**Manuscript:** supplied separately; intentionally NOT included in this archive.

This archive contains the experiment code, stored outputs, figures, protocols, analysis scripts and
verification material corresponding to the current manuscript evidence.

## Evidence blocks

1. Historical fixed-grid ABACO / danger-radius studies and stored analyses.
2. Phase-2 corrected closed-loop confirmation on scenarios 4–203.
3. Matched-interface ACO+DWA and SIPP-style supplementary baselines.
4. Closed-loop stratification by workspace, density, dynamic-obstacle count, motion model and observation noise.
5. Clean Step-6 DR-T / DR-SAFE-T multi-noise study.
6. Runtime / memory / scaling benchmark.
7. A1 prediction-index sensitivity (post hoc).
8. A3 paired closed-loop binary-outcome analysis (post hoc; 10 tests, exact McNemar, Holm correction, 4,000 bootstrap replicates).
9. Priority-13 fresh 300-run fixed-grid multi-noise robustness block (Table 22) with stored summary checks.
10. Priority-8 computational scaling and memory benchmark (Tables 25–26) with stored runtime/RSS checks.
11. Priority-9 APF mathematical distinction verified in the Method section; see `docs/METHOD_APF_DISTINCTION.md`.
12. Priority-11 tuning-parity caveat documented for the fixed-grid evidence; see `docs/PRIORITY11_TUNING_PARITY.md`.
13. Priority-12 practical niche documented: DR-T is positioned as an incremental time-aligned cost modification for existing ACO/grid pipelines; see `docs/PRIORITY12_PRACTICAL_NICHE.md`.
14. Priority-13 practical significance documented: 7.6% path-length and 24.1% sharp-turn reductions for DR-SAFE D_SAFE=1.5 versus HBP in the randomized exact-estimate suite; see `docs/PRIORITY13_PRACTICAL_SIGNIFICANCE.md`.
15. Priority-14 scaling revision: Tables 25–26 aggregate three stored deterministic cases per grid size (1/3/5 dynamic obstacles) using median/IQR; Table 26 uses traced planner-side Python allocations rather than process RSS; see `docs/PRIORITY14_SCALING_MEDIAN_IQR.md`.
16. Priority-20 post hoc ORCA and MPC closed-loop baselines (scenarios 4–203; extends the A3 family from 10 to 14 tests); see `docs/PRIORITY20_ORCA_MPC_BASELINES.md`.

## Installation

```bash
pip install -r requirements.txt
export PYTHONPATH=abaco:danger_radius:baselines:experiments
```

## Main stored-result checks

```bash
python3 experiments/verify_reproduction.py 12
python3 experiments/check_scaling_benchmark.py
python3 experiments/check_priority8_scaling.py
python3 experiments/check_priority14_scaling.py
```

The first command performs the repository's stored-result reproduction spot-check; the second validates the
stored 90-case scaling matrix. The third validates the manuscript Tables 25-26 scaling and RSS cells against the stored
3-dynamic-obstacle benchmark slice. The fourth validates the revised median/IQR aggregation across the three stored cases
per grid size (1, 3 and 5 dynamic obstacles).

## Closed-loop results

Primary stored results:

- `results/phase2_step3_v2/perrun.json`
- `results/phase2_step3_v2/summary.json`
- `results/phase2_strong_baselines_perrun.json`

The common closed-loop runner is `experiments/phase3_runner_v3.py`.

### D* Lite compatibility module

`experiments/phase3_abaco.py` re-exports the closed-loop ABACO adapter and provides a newly authored `FastDStarLite` replacement
(built on `DStarLite` in `experiments/phase2_planners.py`, with the `max_expansions` budget applied to every
re-computation in `update_blocked` and `path`). The original standalone source was absent from the earlier archive, so this
is a newly authored runner-compatible replacement, not a recovered file.

Check (`python3 experiments/check_dstar_compat.py`, results in `results/dstar_compat_check/`): on all 200 scenarios (IDs 4-203)
199 stored D* Lite + DWA runs are reproduced exactly; scenario 189 differs in its collision flag (stored True, rerun False;
aggregate any-collision 22.5% stored vs 22.0% rerun, success 100.0% in both). The stored per-run results in
`results/phase2_step3_v2/perrun.json` remain the reference for the D* Lite + DWA rows of Table 4.
Planning-time values are environment-dependent.

## A1 prediction-index sensitivity

```bash
cd experiments
export PYTHONPATH=.:../abaco:../danger_radius:../baselines
ADAPTER=phase3_abaco_v3 python3 run_a1_sensitivity.py 4 203 ../results/a1_sensitivity/perrun_v3.json
cd ..
python3 experiments/analyze_a1_sensitivity.py
```

Stored outputs: `results/a1_sensitivity/`.

## A3 post hoc paired statistics

```bash
python3 experiments/analyze_a3_paired_statistics.py
```

Outputs are in `results/a3_paired_statistics/`, including `table_17C.md`, `table_17C.csv` and the JSON analysis.
The family contains 5 comparisons × 2 binary outcomes, exact two-sided McNemar tests, Holm correction across
all 10 tests, and 4,000-replicate percentile bootstrap CIs. This family is explicitly post hoc and separate from
the pre-specified primary statistical families.

## Manuscript number checking

```bash
python3 experiments/check_paper_numbers.py /path/to/Danger-Radius_Paper_v75_FINAL.docx
```

The manuscript is maintained separately and is not included in this archive. `check_paper_numbers.py` now also verifies Table 15 against the stored Priority-13 and Step-6 summary outputs.

## Integrity

`docs/C6_SHA256_MANIFEST.json` is the single authoritative file manifest for this package.
The obsolete root-level `SHA256_MANIFEST.txt` was removed to avoid conflicting manifests.

## Package exclusions

The manuscript DOCX/PDF is not included. Superseded intermediate results, Python caches and manuscript-editing
scripts are excluded unless required for reproduction of the current evidence.

## License and citation

Code is released under the MIT License. Citation metadata are provided in `CITATION.cff`.
No public GitHub repository or Zenodo DOI is claimed by this archive; those identifiers should be added only
once an actual public deposit exists.


## Priority 15 — baseline coverage
The manuscript explicitly distinguishes the implemented closed-loop baselines (space-time A*, D* Lite with DWA, ACO+DWA and SIPP-style) from contextual Gong et al. (2022) literature and states that ORCA/MPC are not numerically evaluated. See `docs/PRIORITY15_BASELINE_COVERAGE.md`.


Priority 17: D* Lite rerun completed on scenarios 4–203: 199/200 exact matches, 0 timeouts; scenario 189 remains a collision-flag mismatch. See `docs/PRIORITY17_DSTAR_RERUN.md`.

Priority 18: ESWA literature update completed. Added Li et al. (2024) and Zhang et al. (2026) with corresponding related-work citations. No experimental or numerical result changed. See `docs/PRIORITY18_ESWA_LITERATURE_UPDATE.md`.

16. Priority-19 archive tidy-up: superseded v22/v65 planning documents moved to `docs/archive/legacy/`; active metadata and manifest refreshed. See `docs/PRIORITY19_ARCHIVE_TIDY.md`.
