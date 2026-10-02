# Fresh-seed confirmation protocol (frozen before any run on seeds 20000-20299)

Written: 2026-09-20 10:51 UTC. No result on seeds 20000-20299 (or any noisy-estimate run on the main environment) existed when this file was written.

## Why this exists
The main-environment evaluation on seeds 10000-10299 is NOT clean out-of-sample evidence for DR-SAFE: the time-aligned redesign was
diagnosed after the snapshot floor failed on those seeds, and the HBP arm, ablation, APF-predicted arm and start-cell analysis were
added afterwards. Seeds 10000-10299 are therefore reported as the development evaluation. Seeds 20000-20299 are the confirmation.

## Frozen design
- Environment: main 18x18 environment, 3 deterministic dynamic obstacles (seeds vary only the ants' random choices).
- Seeds: 20000-20299 (N = 300), all arms on identical seeds. Fixed N; no optional stopping; partial results are not inspected.
- Parameters, unchanged from tuning (seeds 6000-6029): DR-SAFE R=4.5, K=2.0, D_SAFE=1.0 (TA) and 1.5 (TB); plain DR R=3.5, K=2.0;
  soft-only (SOFT) D_SAFE=0, R=4.5, K=2.0; floor-only (F10/F15) K=0, R=4.5; APF-predicted D0=4.5, eta=2.0; APF-snapshot D0=3.5, eta=2.0;
  snapshot floor (DRS) R=3.5, K=2.0, D_SAFE=1.5. No parameter is re-tuned on the fresh block.
- Arms, priority order: HB, HBP, DR, TA, TB, SOFT, APFP (stage 1); F10, F15, DRS, APFS (stage 4).
- Primary family (Holm over 8): collisions/run and sharp turns for TA and TB against HB and against HBP (Wilcoxon signed-rank).
- Secondary, declared now: path length, clearance, runs with >=1 collision (exact McNemar), collisions excluding the start waypoint
  (obstacle on the start cell at the conv iteration), TA/TB vs SOFT, TA/TB vs floor-only, TA/TB vs APFP (each Holm over 8 within its family).
- Success statement is made only for what the primary family shows; nothing is added post hoc without being labelled post hoc.

## Noisy-estimate experiments (also frozen before running)
- Noise: heading error N(0, 15 deg), speed scale 1 + N(0, 0.20), drawn once per obstacle per run, same draws for every arm on a seed.
- Suite (36 scenarios x 5 seeds, seeds 500000+): added arms SOFT, SOFT_n, HBP_n, APFP, APFP_n (existing TA, TB, TA_n, TB_n, HB, HBP, DR reused).
- Main environment, seeds 20000-20099 (first 100 fresh seeds): TA_n, TB_n, HBP_n, SOFT_n, APFP_n against clean and noisy arms.
- Noisy planners are compared with NOISY HBP as well as with clean HBP.

## Code and parameter manifest (SHA-256)
```
8623e97ff6c08f61e0af52241d8f8f3f43cb03f383e67f9480250d644b1ff3d6  abaco/ABACO_baseline.py
ff4d6a7e580ad415f367add001405d9aed721e167d8b7de46d28814537d69859  abaco/ABACO_novelty.py
888136b05bb9688f3ae5af46f62ec9708d405fcc9c06a900ad83232d0b13916c  abaco/exec_aligned_metrics.py
c650ff3c42cdbacb2fbff49faf4d894c21ff4d44b34b42bdd5de40ae34aed4d6  baselines/ABACO_apf_baseline.py
e995b0bbdd5c3aaf8659c835af77b9673f53a367b27afb7e96154ed6b42a82e1  danger_radius/ABACO_safety_pred.py
cb87941a8ac856f8442e9d18c15186825aa6445778a7827120c8c80d02c736ff  danger_radius/ABACO_safety_radius.py
47eb09d0c0fa200efcbf0a5e06661fd90fa946b6db4b13068472c30fa4d65a1d  experiments/analyze_ablation.py
2fbc5e5ac22bb97ba2a1476b3c57a1a41733474aee7936d97f3e1ad8a6ca0af9  experiments/analyze_apf_main.py
b70774f124b5ccd6677207ba616748aeb4f743e5788c732ed4a49fa8aef7f5de  experiments/analyze_confirmatory.py
8ac527a68a8a37d8cb920c95bffb4db5104b48708e1a2069b2a1d9731f2f261e  experiments/analyze_new_main.py
3c131429f65ffc0db2777cac23259769f4d0ccebe193461b61a4116ac8adeb43  experiments/analyze_rk_sweep.py
9b444a3b84c3b4956197ae227a32d59818d5679ececc8d9e167e7546672b4769  experiments/analyze_start_cell_adjusted.py
c041bfdbbacf59394f814f28fbe3d70db2b302357a3ae91d889c109d6397f60f  experiments/analyze_suite.py
b0425038b914d3d0f26639d95d04269edb3993bcc020a30d290ceaa9b979d04e  experiments/broaden_validation.py
52412f0355e26ec6e464abdece1bd103af1aad5405a353a96ac9599c5bc8bc19  experiments/confirmatory_run.py
7d923d8eb03252ccba5b2bd0b7874fa32199342ab58a5cae1001d23834bdea35  experiments/drsafe_lib.py
ad8392754b8cf076498a0b691d9750ed7bf1b214ea00c67020cc12f318d3cf34  experiments/explore_time_aligned_floor.py
dedb229987842a0c15701d399075104e14aa798475effe7b245d35845520b18f  experiments/fresh_run.py
f66c9fb6652e024b79ced4d372c330941defba4fefd83f30b344ca41e4b824db  experiments/generate_paper_figures.py
439293534c7f7da0649771efe5bf6e9de3af852c7cee674a52b33d0f0dc0138e  experiments/make_figures_drsafe_t.py
d912a7a0d54a4019d16b31d508d670e450e58dcb6cce1eb97a2cb6dde66ae954  experiments/power_analysis.py
66e90845eff94a4ce5e6bfa4b76b81004e5c80c029879a54b736531c753a00b6  experiments/rerun_apf_methodb.py
557b355b547c708420de23563199f9716df0a5c2a870981d9545603cbac3642b  experiments/rerun_generalization_methodb.py
40e1726a33ea2fe96878d8eb25e9edc19bf857f1ed8c4c3d50d87e44abfeed8d  experiments/run_ablation.py
8066b8b65a81432fe91a3ffb73228769358b44f0d2594f7e66a72c778d04586c  experiments/run_apf_main.py
6b74611dc27c3e1c03a8936e65cd84a66ef4e30631bbd17ea70aa88f3c0c5b35  experiments/run_main_new_arms.py
0eb9be58ad942d0fd57fc68dcc03ac175a9ef42767689388ae554215c218f3a4  experiments/run_safety_batch.py
203ac1771856049637ed1f1d9ca33d1ee006a182dcaefe06448683e69d8737b3  experiments/run_suite.py
5209d8b184f9b4295affe7b2cfe0ee7a6590cc53aeb616ee3129b3abbd17b7aa  experiments/scenario_suite.py
17a952f038048a79ae95308369758dc450aaf81d9aeaa97d9391bfb83f0b73a4  experiments/select_drsafe_t.py
b2ca0e6fb9221a66d6379ed810eb879a9224595adea02ae3437119840eec5a19  experiments/sweep_drsafe_t.py
2ef530bce36a907beab82c4d315bd2df164a027c3d2c7c169077d787fc2f7df4  experiments/sweep_rk_drsafe.py
88d36b3e76c79552fdc7b3aa3a1e307d3abf15b90ca86875b3a1ac92e7b7f079  results/drsafe_t_selected.json
```

## Execution log (appended after the runs; the frozen text above is unchanged)
- Stage 1 (main environment, seeds 20000-20299; HB, HBP, DR, TA, TB, SOFT, APFP), stage 2 (suite additions SOFT, SOFT_n, HBP_n, APFP, APFP_n) and stage 3 (main-environment noisy arms, seeds 20000-20099) were run to completion.
- The runner process was terminated several times by the sandbox between sessions and resumed from its per-seed / per-scenario checkpoints; a resumed run recomputes only missing entries, and every arm is deterministic given its seed.
- Stage 4 (F10, F15, DRS, APFS on the fresh block) was NOT run; 32 partially completed entries of those arms were deleted from results/fresh_main.json before analysis. The floor-only ablation and snapshot baselines therefore exist only for the development block.
- analyze_fresh.py, analyze_noise.py and make_figures_fresh.py were written after the code hashes above were taken and before any fresh-seed result existed; they implement the analyses declared above. Extra noise levels (_n1, _n3) are supported by fresh_run.py but were not run.
- Post hoc (not declared above, labelled as such in the paper): pooled 600-seed comparison with HBP; DR-SAFE vs noisy soft-cost-only.
- Later additions (not in the frozen protocol; labelled post hoc or as extensions in the paper): experiments/fallback_audit.py + analyze_fallback.py (fallback audit on seeds 20000-20299; counts only, reproduces the stored fallback counts); experiments/sweep_drsafe_t_extend.py + select_drsafe_t_extended.py (tuning grid extended to R = 5.5, 6.5 on seeds 6000-6029; the frozen selection file is unchanged).
- Docstring-only edits (no code change) were made afterwards to experiments/sweep_drsafe_t.py and select_drsafe_t.py ("18 cells" -> "9 (R x K) cells of that D_SAFE", which is what the code does); their SHA-256 values in the manifest above therefore no longer match the files.
- Start-waypoint sensitivity analysis (Tables 18-19 of the paper) was planned after the start-excluded results had been seen; see docs/START_CELL_ANALYSIS_PLAN.md. No new planner runs.
- An abandoned hand-off re-scoring run (paths for 123 of 300 seeds, no scoring output) was removed from the release; see docs/START_CELL_ANALYSIS_PLAN.md.
- Provenance pass (v8): the pilot supplement's Figure S1 (radius sweep) could not be reproduced from the archived code (the archived script gives a different sweep) and was replaced by the reproducible version with revised text; Figures 1, 3, S4 and S8 were regenerated from scripts/data; the missing APF and generalization pilot result files were regenerated and reproduce Tables S5 and S4.
- Single-paper pass (v9): the supplement was folded into Section 5.2; the illustrative run of Figures 4 and 8 (seed 20000) was chosen by a rule declared in make_figures_progression.py before the pictures were drawn.
- ESWA preparation (v10): text compressed and two post hoc analyses moved to appendices; no analysis result changed (independent number check: 157 values agree).
- ESWA preparation part 2 (v11): no analysis result changed (independent number check: 157 values agree). The APF-style baseline's description was corrected to no longer attribute a potential-field method to Gong et al. (2022); their method uses rule-based local avoidance strategies, not a potential field.
- Recheck pass (v12-v13): no analysis result changed (independent number check: 157 values agree). A fabricated reference added during the previous references pass was caught and removed; every reference is now confirmed cited in the body text.
- Full read-through (v14): no analysis result changed (independent number check: 157 values agree). Confirmed by hand that every narrative number in Sections 5.5-5.10 and Appendices A-B matches its source table.
- Recheck + references pass (v15): no analysis result changed (independent number check: 157 values agree).
- Freeze audit (v22, 2026-09-30; nothing above changed): 6 of the 33 SHA-256 values in the manifest no longer match the files: experiments/select_drsafe_t.py and sweep_drsafe_t.py (docstring edits, documented above); baselines/ABACO_apf_baseline.py (its docstring names Gong et al. 2022, consistent with the v11 correction); and danger_radius/ABACO_safety_pred.py, experiments/run_apf_main.py and experiments/analyze_apf_main.py, whose changes are NOT documented. The original release is not in the repo, so the changes cannot be diffed here. Behaviour was checked instead: 69 stored runs (development and confirmation blocks, suite, noisy arms, APF arms; 14 drawn at random, the rest chosen by hand) re-run to identical records with the current code (experiments/verify_reproduction.py). Current hashes: docs/SHA256_v22.txt.

## Phase 0 provenance-audit update (2026-09-30)

The v22 resubmission checklist requested a direct diff of the three undocumented hash mismatches against the original release. The supplied v22 archive contains no Git history and no original-release copies of those three files, so a literal source diff is not possible from this archive. The current hashes are recorded in `docs/PHASE0_AUDIT.md`.

The existing behavioral audit remains the available evidence: 69 stored runs were re-run with the current code and matched their stored records exactly. This supports no detected behavioral change in the sampled reproduction checks, but it does not establish source-level identity with the unavailable original release. The manuscript's Section 5.10 has therefore been worded to describe the confirmation protocol and recorded hashes accurately, with this later provenance qualification.
