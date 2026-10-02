# Current package status

Date: 2026-10-02
Checkpoint: v66.0-c6-item13-practical-significance


## Smoothness-claim closure (2026-10-02)
- Closed the review items concerning unsupported closed-loop smoothness claims.
- The manuscript now states explicitly that Table 7 is a post hoc five-seed closed-loop variance study and that its sharp-turn counts are descriptive only, not evidence for a closed-loop smoothness advantage.
- Smoothness/path-quality comparisons are confined to the fixed-grid development and confirmation blocks, where sharp turns and path length were explicitly measured under the iteration-indexed protocol.
- Added `docs/SMOOTHNESS_EVIDENCE_AUDIT.md` to record the evidence boundary and affected manuscript claims.

## Deliverables
- Manuscript: supplied separately.
- Code/data archive: this package.
- No public repository or DOI is claimed until an actual deposit exists.

## Current corrections
- Restored the missing runner-facing `experiments/phase3_abaco.py` compatibility entry point.
- Corrected the A3 script documentation to state 4,000 bootstrap replicates.
- Added MIT LICENSE and CITATION.cff.
- Updated VERSION and README.
- Added an explicit A3 reproduction command and result pointer.
- Removed the stale root-level SHA256 manifest; `docs/C6_SHA256_MANIFEST.json` is authoritative.

## D* Lite note
The restored `phase3_abaco.py` wraps the packaged `DStarLite` implementation and exposes the historical
`FastDStarLite` runner API. It is a compatibility reconstruction because the standalone historical source was
not present in the prior archive. In C6 the module was rebuilt (per-call expansion budget in `update_blocked` and `path`). A full check on scenarios 4-203
reproduces 199 of 200 stored D* Lite + DWA runs exactly; scenario 189 differs in its collision flag (aggregate collisions
22.5% stored vs 22.0% rerun; success 100% in both; see `results/dstar_compat_check/`). The earlier C4/C5 wrapper did not
reproduce the stored outputs (6 of the first 13 scenarios matched, 6 hung) and that version is superseded. The module is a
newly authored runner-compatible replacement, not source-level recovery; stored per-run results remain the reference.

## Post-C4 executable consistency patch
- Updated `experiments/benchmark_one_case.py` and `experiments/benchmark_scaling_memory_direct.py` to unpack the current three-value `abaco_plan()` return signature.
- Smoke-tested HB, HBP, DR-T and DR-SAFE benchmark calls on a 12x12 / 3-dynamic-obstacle case; all returned a valid path.
- `python -m compileall -q .` passes.

## C6 D* Lite verification hardening (2026-10-02)
- `experiments/check_dstar_compat.py` is now location-independent and defaults to the full 200-scenario check (IDs 4–203).
- Full verification completed with 199/200 exact matches and 0 timeouts; scenario 189 remains the sole disclosed collision-flag mismatch.
- Added `docs/DSTAR_LITE_REPRODUCIBILITY.md` with the exact command, scope, and verified result.

## Post-C6 housekeeping (2026-10-02)
- `CITATION.cff` was an empty file; it now contains the citation metadata (no DOI or repository URL is claimed).
- Python bytecode caches (`__pycache__/`) removed from the archive, as `REPOSITORY_CONTENTS.md` already states they are excluded.
- `docs/C6_SHA256_MANIFEST.json` entries for `CITATION.cff` and `docs/PACKAGE_STATUS.md` updated; all 280 entries re-verified.

## Priority-7 repository refresh (2026-10-02)
- Refreshed `VERSION` to `v65.5-c6-dstar-verified-item7`.
- Refreshed README evidence/package documentation and repository contents.
- Added Table 22 checking to `experiments/check_paper_numbers.py`, using stored Priority-13 and Step-6 summary outputs.
- Table 22 is checked descriptively; no new inferential claims are introduced.

## Priority-8 computational scaling and memory (2026-10-02)
- Confirmed Section 5.12 and Tables 25–26 are present in the current manuscript.
- Added `experiments/check_priority8_scaling.py` for an explicit manuscript-table check against stored scaling/RSS outputs.
- Table 20: 30/30 runtime cells match the stored 3-dynamic-obstacle measurements within rounding tolerance.
- Table 21: 30/30 RSS cells match the stored isolated measurements within rounding tolerance.
- Existing 90-case scaling checker passes.
- No manuscript numerical values changed in this item.


## Priority-9 APF distinction (2026-10-02)

The manuscript Method section explicitly distinguishes the APF baseline from DR-T mathematically: APF uses the quadratic shifted-reciprocal potential `0.5·η·(1/d − 1/D0)^2`, while DR-T uses the single reciprocal `K/(d+ε)` term truncated at `R`. The distinction is stated before Section 4.2 and is therefore part of the Method presentation. No manuscript numerical values or algorithmic code were changed for this priority. See `docs/METHOD_APF_DISTINCTION.md`.


## Priority-11 tuning parity (2026-10-02)
- The fixed-grid evidence was audited for hyperparameter parity. The common ABACO parameters alpha=1.0, beta=5.0 and rho=0.3 were fixed rather than tuned for any method.
- DR-SAFE received a broader formulation-specific search over R, K and D_SAFE than HB, HBP and APF; the later radius extension included R=5.5 and 6.5.
- The extension selected R=5.5 for D_SAFE=1.5, but the confirmation protocol had already frozen R=4.5, so the reported D_SAFE=1.5 confirmation block was not rerun at R=5.5.
- No equal-budget rerun was performed in this priority. The manuscript now states this explicitly as a principal limitation on fixed-grid method-to-method comparisons.
- See `docs/PRIORITY11_TUNING_PARITY.md`.


## Priority-12 practical niche (2026-10-02)
- The manuscript now states a specific intended use case rather than implying general planner superiority: an existing ACO-based grid planner that needs time-aligned obstacle costing while retaining its ACO/grid planning architecture.
- The closed-loop results are retained as documented: DR-T 72.5% success and 18.0% any-collision; Space-time A* 88.0% success, 21.5% any-collision and about 0.020 s accumulated planning time per scenario; ACO+DWA 95.5% success and 16.0% any-collision.
- The practical section explicitly says these measurements do not support replacing the tested alternatives; the niche is architectural reuse of an existing ACO/grid pipeline.
- No numerical experiment was rerun for Priority 12. This item changes positioning and practical interpretation only.
- See `docs/PRIORITY12_PRACTICAL_NICHE.md`.


## Priority-13 practical significance (2026-10-02)
- Added percentage practical-magnitude reporting to the manuscript: 7.6% lower mean path length and 24.1% fewer mean sharp turns for DR-SAFE D_SAFE=1.5 versus HBP in the randomized exact-estimate suite.
- Restored a four-point practical-guidance list in the conclusion.
- These are secondary descriptive fixed-grid measures; the tuning-parity limitation remains explicit.
- No numerical experiment was rerun for Priority 13.
- See `docs/PRIORITY13_PRACTICAL_SIGNIFICANCE.md`.


## Priority-14 multi-case scaling and traced memory (2026-10-02)
- Revised Tables 25–26 to use the existing stored direct-planning matrix at 1, 3 and 5 dynamic obstacles: three deterministic cases per grid size.
- Table 20 now reports median [IQR] planner computation time across those three cases.
- Table 21 now reports median [IQR] peak `tracemalloc` Python allocations during the planner call, excluding the process RSS baseline but not capturing native/C-level allocations.
- Added `experiments/aggregate_scaling_cases.py` and `experiments/check_priority14_scaling.py`.
- No new numerical run was required; the underlying 90-case direct-planning matrix is unchanged.
- See `docs/PRIORITY14_SCALING_MEDIAN_IQR.md`.


## Priority-15 baseline coverage (2026-10-02)
- The manuscript now explicitly distinguishes implemented matched-interface/time-explicit baselines from contextual Gong et al. (2022) literature.
- ORCA and MPC are not numerically evaluated; this is stated as a limitation rather than silently omitted.
- No numerical baseline result was invented or changed.
- See `docs/PRIORITY15_BASELINE_COVERAGE.md`.

## Priority-18 ESWA literature update (2026-10-02)
- Added two recent, directly relevant Expert Systems with Applications references: Li et al. (2024) on adaptive-dynamic-programming mobile-robot path planning and Zhang et al. (2026) on hierarchical deep-reinforcement-learning path planning.
- Added corresponding citations in the dynamic-obstacle related-work discussion.
- Bibliographic metadata was checked against ScienceDirect publisher records.
- No numerical result, table value, algorithm, or baseline result was changed.
- See `docs/PRIORITY18_ESWA_LITERATURE_UPDATE.md`.


## Priority-19 archive tidy-up (2026-10-02)
- Moved superseded v22/v65 planning and freeze records to `docs/archive/legacy/` so the active documentation namespace contains current submission records.
- Retained historical numerical outputs needed for provenance; no accepted result or source module was removed.
- Confirmed Python caches/bytecode are absent.
- Refreshed package metadata and the authoritative SHA-256 manifest for v66.5.
- No numerical, algorithmic, or manuscript-result changes were made.
- See `docs/PRIORITY19_ARCHIVE_TIDY.md`.
