# Phase 2 Step 5 — scale/stratification status

The 200-scenario confirmation block (IDs 4–203) was stratified by workspace, static density, dynamic-obstacle count, motion type and estimator noise. Each workspace has 50 scenarios. The 200-scenario block covers all four workspaces, three densities, four dynamic-obstacle counts, four motion types and four noise levels, with unequal counts per factor because the generator cycles across factors.

The principal qualitative pattern is that performance degrades on the largest 30x24 workspace and with 8 dynamic obstacles, while the ACO+DWA and D* Lite+DWA hybrids retain high goal-reaching rates. DR-T has zero zero-distance runs in the 200-scenario block; DR-SAFE has one, associated with a floor/search interaction. The detailed machine-readable stratification is stored in `results/phase2_step3_step4_stratification.json`.

This is a stratified analysis of the existing 200-scenario block, not yet the requested several-hundred-scenario expansion. A larger fresh block remains outstanding if the final paper needs that stronger scaling claim.
