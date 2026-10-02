# Phase 4 manuscript revision audit

Date: 2026-09-30
Status: manuscript revision completed; numerical and rendering checks passed; final submission checks remain.

## Completed
- Reframed the manuscript around DR-T as the proposed method; DR-SAFE is an extension.
- Rewrote the abstract to 248 words and removed unsupported safety/general-planner claims.
- Added a precise ABACO implementation description: pheromone update, rank-based Q assignment, parameters, and dominant complexity.
- Corrected terminology around the reported reciprocal cost: the historical formulation is distance-decaying but truncated at R, so it is no longer called smooth or continuous.
- Documented the separate Phase-1 continuous-boundary engineering check without substituting those results into the historical manuscript tables.
- Added a representative warehouse/service-robot use case as motivation, explicitly marked as illustrative rather than validated.
- Added recent literature, including 20 additional ESWA references.
- Added Elsevier-style Highlights as a separate Word document.
- Rewrote the limitations and conclusion to preserve the provenance limits from Phase 3.
- Clarified that the repository does not specify an independent metre-per-cell calibration; no physical cell size was invented.

## Not silently changed
- Historical result tables were not overwritten with Phase-3 closed-loop adapter results.
- No Holm-adjusted inference from the Phase-3 confirmation block was inserted.
- No safety guarantee was added.
- Frozen planner/source files were not edited.

## Verification completed
- `experiments/check_paper_numbers.py` reports **348 cells/values agree; 0 disagree**.
- Abstract length: **248 words**.
- Highlights: 5 bullets, each 58–64 characters.
- LibreOffice conversion completed successfully; rendered manuscript is **41 pages**.
- First-page visual inspection passed; title, author block, abstract and keywords render correctly.

## Remaining before submission
1. Run `experiments/check_paper_numbers.py` on the Phase-4 manuscript and resolve any mismatches.
2. Verify all reference metadata against publisher pages/reference manager.
3. Decide whether the absence of a physical metre-per-cell calibration is acceptable; if the authors have the intended calibration, insert it rather than infer it.
4. Complete Zenodo/data-availability and response-letter work.
5. Perform final visual inspection of figures, tables, equations and page breaks.
