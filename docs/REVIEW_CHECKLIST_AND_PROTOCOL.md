# Review checklist and frozen protocol (DR-SAFE paper)

Goal: fewer sharp turns and fewer collisions than hard block (HB); shorter paths if possible.
Method under test: DR-SAFE-T (danger-radius cost + hard floor, both evaluated at the obstacle's
predicted position for each path step). Old snapshot DR-SAFE is kept only as the motivating failure.

## A. Reviewer items -> status

| # | Reviewer item | Status | What closes it |
|---|---|---|---|
| 1 | N=50 too small / power | Done | Power analysis done (results/power_analysis.json). Confirmatory N=300 on fresh seeds run and reported (paper Sections 5.7, 5.9). |
| 2 | R/K never re-swept for DR-SAFE | Done | Old snapshot-floor DR-SAFE swept (24 cells). Time-aligned DR-SAFE swept on tuning seeds 6000-6029 (experiments/sweep_drsafe_t.py); selected R=4.5, K=2.0. |
| 3 | Single environment | Done (36 randomized scenarios) | Randomized obstacle starts/speeds/headings; grids 12/18/25; densities; 1/3/5 obstacles. Seeds currently vary only the ants: obstacle setup is fixed. |
| 4 | Only constant-velocity obstacles | Done (heading-change + noisy prediction) | Heading-change and intersecting scenarios; noisy-prediction test for DR-SAFE-T. |
| 5 | Stats: t/Wilcoxon, d, CIs | Done (in revised paper, Tables 11-14) | analyze_confirmatory.py (Holm-corrected primary family). Must be applied to the new runs and written into the paper. |
| 6 | External baseline | Done (APF-ACO vs DR-SAFE, N=300, snapshot and predicted; HB+prediction) | APF-ACO in Section 5.6 (no significant differences). Add: HB-with-prediction ablation (implemented). |
| 7 | Abstract/conclusion consistent and honest | Done in paper/Danger-Radius_Paper_DR-SAFE_revised.docx | Rewrite after final numbers. Current text still claims collisions "roughly halved" (did not replicate at N=300). |
| 8 | Novelty statement vs closest prior work | Done (Introduction, paragraph on DR-SAFE vs Gong et al. 2022) | One sentence contrasting single-level transition-rule cost with layered APF/local-avoidance methods (Gong 2022, Montiel 2015). |
| 9 | Language pass; remove revision-log phrases | Revision-log phrases removed; full language pass still open | Delete "the review correctly noted", "earlier, uncorrected pass", "submission review" phrasing. |
| 10 | Expert Systems with Applications references | Not done | Only 2 of 16 refs are ESWA. Needs a literature search; no invented citations. |

## B. Frozen design for the confirmatory run
- Arms (same seed per index): HB, HBP (HB with prediction), DR (3.5, 2.0), DR-SAFE old (3.5, 2.0, 1.5),
  DR-SAFE-T with D_SAFE = 1.0 and D_SAFE = 1.5, each at the (R, K) chosen by the sweep rule.
- Fresh seed block for the main environment; N = 300.
- Primary outcomes: collisions per run and sharp turns per run. Secondary: path length, clearance,
  iterations to converge, fallback rate.
- Primary tests: paired Wilcoxon, Holm-corrected over {collisions, turns} x {vs HB, vs HBP}; report d_z and 95% CI.
- Success rule: DR-SAFE-T reduces collisions vs HB and vs HBP (Holm p < 0.05) AND its turn count is not
  more than 0.5 turns above DR's. If not met, report as a trade-off or a null result.
- Sweep selection rule (per D_SAFE): lowest z(turns) + z(coll) across the 18 cells; ties -> shorter length.

## C. Order of remaining work
1. Finish sweep -> pick (R, K) per D_SAFE -> run N=300 confirmatory on fresh seeds.
2. Build randomized multi-environment suite; re-run the arms there (smaller N per scenario, total stated).
3. Noisy-prediction test.
4. Rewrite abstract/intro/method/results/conclusion; literature search for ESWA references; language pass.
