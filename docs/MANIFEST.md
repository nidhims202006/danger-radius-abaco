# Manifest: manuscript tables / figures -> scripts -> stored results -> seeds

This manifest matches the current manuscript numbering. `experiments/check_paper_numbers.py` is the independent numerical check for the table families listed below; it reads the manuscript by caption number so inserted earlier tables do not break the mapping.

| Paper item | Script(s) | Stored results | Seeds / scope |
|---|---|---|---|
| Tables 1-2 (environment and simulation parameters) | `abaco/ABACO_baseline.py`, `danger_radius/` | configuration in manuscript/code | fixed main environment |
| Tables 3-4 (closed-loop primary and matched-interface baselines) | `phase3_runner_v3.py`, `phase4_runner_orca_mpc.py`, `check_orca_mpc_numbers.py` | `results/phase2_step3_v2/perrun.json`, `results/phase2_strong_baselines_perrun.json`, `results/phase4_orca_mpc_perrun.json` | 200 scenarios, IDs 4-203 |
| Tables 5-6 (closed-loop prediction-index and paired binary-outcome sensitivity) | `run_a1_sensitivity.py`, `analyze_a1_sensitivity.py`, `analyze_a3_paired_statistics.py` | `results/a1_sensitivity/`, `results/a3_paired_statistics/` | scenarios 4-203; post hoc |
| Table 7 (five-seed closed-loop variance study) | closed-loop seed-offset runner/analysis in the submission archive | stored closed-loop variance summary | 200 scenarios × 5 planner-seed offsets; descriptive only; turn counts are not used to claim a closed-loop smoothness advantage |
| Tables 8-9 (closed-loop stratification) | `phase3_runner_v3.py` and closed-loop analysis scripts | `results/phase2_step3_v2/`, `results/phase2_strong_baselines_perrun.json` | 200 scenarios; workspace, density, dynamic-obstacle count, motion and noise strata |
| Tables 10-11 (randomized scenario suite: means and paired comparisons) | `run_suite.py`, `scenario_suite.py`, `analyze_suite.py`, `analyze_suite_holm8.py` | `results/suite_results.json`, `results/suite_summary.json`, `results/suite_holm8.json` | 36 scenarios × 10 paired seeds for exact-estimate rows |
| Tables 12-13 (noisy-estimate suite and main-environment block) | `fresh_run.py`, `analyze_noise.py` | `results/suite_added.json`, `results/fresh_noise.json`, `results/noise_summary.json` | 36 scenarios × 5 seeds; main environment seeds 20000-20099 |
| Tables 14-15 (component ablation) | `run_ablation.py`, `analyze_ablation.py` | `results/ablation_main.json`, `results/ablation_summary.json` | main environment seeds 10000-10299 |
| Tables 16-17 (repulsive-potential ACO comparison) | `run_apf_main.py`, `analyze_apf_main.py` | `results/apf_main.json`, `results/apf_main_summary.json` | main environment seeds 10000-10299 |
| Tables 18-19 (development block and primary comparisons) | `run_main_new_arms.py`, `analyze_new_main.py`, `experiments/check_paper_numbers.py` | `results/main_new_arms.json`, `results/confirmatory_perrun.json` | 300 paired seeds, 10000-10299 |
| Tables 20-21 (new-seed confirmation and primary comparisons) | `fresh_run.py`, `analyze_fresh.py`, `experiments/check_paper_numbers.py` | `results/fresh_main.json`, `results/fresh_summary.json` | 300 paired seeds, 20000-20299 |
| Tables 22-23 (fresh multi-noise robustness and equal-budget tuning) | `priority13_multi_noise.py`, `priority13_add_drt_drsafe_v3.py`, equal-budget tuning scripts | `results/priority13/priority13_summary.json`, `results/priority13/selected_tuning.json`, `results/priority13_drt_extension_v3_clean/step6_clean_analysis.json` | fresh 300-run blocks; 30 tuning seeds per block |
| Table 24 (R = 4.5 vs R = 5.5 re-evaluation) | `analyze_r5p5_re_evaluation.py` and corresponding rerun scripts | stored R5.5 re-evaluation results under `results/` | fresh seeds 10300-10599 |
| Tables 25-26 (direct planning scaling and traced memory) | `benchmark_scaling_memory_direct.py`, `aggregate_scaling_cases.py`, `check_priority14_scaling.py` | `results/scaling_memory_direct.json`, `results/scaling_memory_median_iqr.json`, `results/scaling_memory_rss.jsonl` | three deterministic cases per grid size; 1, 3 and 5 dynamic obstacles |
| Table A.1 (fallback audit) | `fallback_audit.py`, `analyze_fallback.py` | `results/fallback_audit.json`, `results/fallback_summary.json` | confirmation seeds 20000-20299 |
| Tables B.1-B.2 (start-waypoint sensitivity) | `analyze_start_cell_coprimary.py`, `analyze_start_cell_adjusted.py` | `results/start_cell_coprimary.json`, `results/start_cell_adjusted.json` | development and confirmation blocks |
| Figure 1 | `generate_paper_figures.py` | `figures_eswa/Figure1_grid_environment.png` | fixed environment |
| Figure 2 | `generate_paper_figures.py` | `figures_eswa/Figure2_cost_comparison.png` | formulation illustration |
| Figure 3 (development + randomized results) | `make_figures_drsafe_t.py` | `figures_eswa/Figure12_drsafe_results.png` | 300 development seeds + 36 scenarios |
| Figure 4 (randomized exact/noisy estimates) | `make_figures_fresh.py` / suite analysis | `figures_eswa/Figure15_noisy_estimates_suite.png` | 36 scenarios |
| Figure 5 (ablation + APF comparison) | `make_figures_drsafe_t.py` | `figures_eswa/Figure13_ablation_apf.png` | main environment |
| Figure 6 (APF vs DR-SAFE path illustration) | `make_figures_progression.py` | `figures_eswa/Figure17_apf_vs_drsafe.png` | illustration seed 20000 |
| Figure 7 (DR-SAFE path progression) | `make_figures_progression.py` | `figures_eswa/Figure16_drsafe_progression.png` | illustration seed 20000 |
| Figure 8 (development vs new-seed confirmation) | `make_figures_fresh.py` | `figures_eswa/Figure14_fresh_confirmation.png` | seeds 10000-10299 and 20000-20299 |

## Independent number check

Run:

```bash
python experiments/check_paper_numbers.py /path/to/Danger-Radius_Paper_ESWA_revised_v24.docx
```

The checker independently recomputes Tables 10-13, 18-22 and compares the stored start-waypoint analyses in Tables B.1-B.2. It does not recompute bootstrap confidence intervals or d_z values; those remain covered by the analysis scripts listed above.

## Figure numbering

Figures are numbered strictly by first appearance in the manuscript: Figures 1-2 occur in Sections 2 and 4, Figure 3 is the first results figure, Figures 4-6 follow in Sections 5.4-5.7, Figure 7 is the path-progression illustration, and Figure 8 is the development/confirmation summary.

Submission figures should be exported without embedded figure titles, with vector PDF plus publication-quality PNG where applicable.

## Archive provenance

`docs/C6_SHA256_MANIFEST.json` is the authoritative package integrity manifest. `docs/DLITE_SOURCE_MANIFEST.json` records the D* Lite source-package hashes. The manifests are regenerated after package changes and verified against the files currently present in the archive.

The archive's historical D* Lite source was not recovered; `experiments/phase3_abaco.py` is a documented runner-compatible reconstruction. The stored compatibility check reproduces 199 of 200 stored D* Lite + DWA scenarios exactly, with the single documented discrepancy retained in the package audit.

## Other reproducibility records

- The pre-correction files in `results/archive/` are historical and are not used by the current manuscript tables.
- `experiments/verify_reproduction.py` provides a stored-result reproduction spot-check.
- `docs/ORCA_MPC_SHA256_MANIFEST.json` covers the post hoc ORCA/MPC additions.

## v29 review-closure additions

- `abaco/exec_aligned_metrics.py`: canonical execution-aligned metric now supports `exclude_start=True` for the pre-handoff start-waypoint convention.
- `experiments/check_paper_numbers.py`: verifies the start-waypoint-excluded primary collision values in Tables 18–21.
- `experiments/warehouse_scenario_generator.py`: deterministic 24-scenario warehouse-style validation protocol generator; no results are claimed by this generator alone.
- `docs/REVIEW_CLOSURE_v29.md`: review-closure scope and remaining external actions.
- `docs/DATA_AVAILABILITY.md`: current data/reproducibility statement.
- `.zenodo.json` (repository root): DOI-ready Zenodo metadata; no DOI is claimed until a public release is minted.

## v30 review-closure additions
- `docs/ORCA_MPC_RERUN_RECONCILIATION_v30.md` records the updated manuscript rerun values and the provenance status of the archived superseded raw ORCA/MPC run.
- `results/phase4_orca_mpc_manuscript_v30.json` records the updated Table 29 descriptive values without fabricating raw paired outcomes.
- `experiments/generate_fresh_audit_scenarios.py` and `results/fresh_audit_scenarios/` make the 40 held-out scenarios 204–243 reproducible as a separate audit block.
