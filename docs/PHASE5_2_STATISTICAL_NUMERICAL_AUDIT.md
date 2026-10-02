# Phase 5.2 — Statistical and Numerical Final Audit

Date: 2026-10-02

## Status
COMPLETE.

## Independent manuscript number check
- Manuscript: `Danger-Radius_Paper_v64_phase5_stats_audit.docx`
- Existing independent checker: **324 cells/values agree; 0 disagree**.
- Checked tables include the stored development/confirmation blocks, paired tests, Holm-adjusted p-values, suite results, start-waypoint sensitivity, and the post-hoc soft-cost analysis covered by the checker.

## Clean Step-6 numerical reconciliation
The clean fixed-grid Step-6 results in `results/priority13_drt_extension_v3_clean/step6_clean_analysis.json` were checked against the manuscript robustness section.

Verified confirmation values:
- n1 (5°/10%): DR-T collision-run rate 0.070, DR-SAFE-T 0.057; mean turns 13.65/11.85; path length 35.53/34.62; clearance 2.33/2.50.
- n (15°/20%): DR-T 0.167, DR-SAFE-T 0.087; mean turns 11.13/11.60; path length 34.27/34.60; clearance 1.65/2.47.
- n3 (30°/40%): DR-T 0.130, DR-SAFE-T 0.090; mean turns 13.53/16.79; path length 35.57/37.47; clearance 2.05/2.65.
- All six blocks have N=300 and 100% success.
- DR-T floor fallback total is 0 in all three blocks; DR-SAFE-T has the documented floor-relaxation behavior.

The manuscript previously contained stale DR-SAFE-T collision-event rates in this section. Those rows and the corresponding prose were corrected in v64.

## Clean Step-6 paired inference
Recomputed from the clean per-run files:
- Collision Holm-adjusted p-values across the three noise levels: 0.493, 0.043, 0.440; therefore only the 15°/20% block is significant after Holm correction.
- Path-length Holm-adjusted p-values: 1.54e-10, 0.00224, 7.10e-19.
- Turn-count Holm-adjusted p-values: 6.32e-9, 0.08999, 3.95e-17.
- Minimum-clearance Holm-adjusted p-values: 0.11035, 5.22e-12, 9.43e-8.

These support the manuscript's stated supplementary inference bounds.

## Manuscript rendering
- LibreOffice conversion: PASS.
- Rendered PDF: `v64_render/Danger-Radius_Paper_v64_phase5_stats_audit.pdf`.
- Page count: 53.

## Result
Phase 5.2 is closed. The manuscript now has a verified numerical/statistical reconciliation for the final audited version.
