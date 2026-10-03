# Post hoc phase-5 analyses (release v36)

**Status: post hoc.** These analyses were added after the primary closed-loop results (manuscript Tables 3 and 4) were
frozen. They are reported alongside, not in place of, the primary results (manuscript Section 5.3, Tables 4A and 4B).
No parameter was retuned: every method uses the frozen settings of `results/phase2_step3_v2/perrun.json`
(ACO+DWA: `results/phase2_strong_chunks/`; hybrids use the DR-T settings R = 3.5, K = 0.5).

## What was run (scenarios 4-203, N = 200, same seeds as the primary runs)

1. **Legacy-pheromone adapter** (`ADAPTER=legacy`). The closed-loop adapter (`phase3_abaco_v2.abaco_plan`) with the two rules
   of the fixed-grid ABACO that it does not use (see `docs/ADAPTER_DIFFERENCES.md`, item iii) restored: age-based Q deposition
   (Q ~ Uniform(10, 100), sorted descending, paired with routes sorted shortest-first, deposit Q/L) and a 500-step construction
   limit. Everything else is unchanged. Methods: HB, HBP, DR-T, DR-SAFE.
2. **Single-factor arms** for DR-T: 500-step limit only (`P5_CAP=500 P5_AGEQ=0`) and age-based deposit only (`P5_CAP=100 P5_AGEQ=1`).
3. **ACO+DWA with a prediction-aware ACO stage.** `phase5_adapters.aco_dwa_hybrid_plan`: the ACO stage of ACO+DWA uses HB (the original),
   HBP or DR-T on Kalman-predicted obstacle positions; the DWA-style local step, 8 ants, 10 iterations and clearance weight 0.1 are
   unchanged. Run under the primary (flat-deposit) adapter and under the legacy-pheromone adapter.

## Files

| File | Purpose |
|---|---|
| `experiments/phase5_adapters.py` | `abaco_plan_legacy`, `aco_dwa_hybrid_plan` |
| `experiments/phase5_runner.py` | `phase3_runner_v3` plus adapter selection (`ADAPTER=legacy`) and the hybrid methods; simulation, Kalman filter and collision rule untouched |
| `experiments/phase5_run.py` | Resumable driver (`python3 phase5_run.py <tag> <methods> [first last]`) and the frozen parameter table |
| `experiments/verify_phase5_gate.py` | Reproducibility gate (about 1-2 min): the phase-5 runner with the primary adapter must match stored results exactly |
| `experiments/analyze_phase5.py` | All paired tests, Holm corrections and summaries |
| `experiments/check_phase5_numbers.py` | Checks Tables 4A and 4B of a manuscript .docx against the stored per-run results |
| `experiments/run_phase5.sh` | `--analysis-only` (seconds) or `--full` (about 40 min on one core) |
| `results/phase5/*.jsonl` | Per-run outcomes: `legacy`, `cap_only`, `ageq_only`, `hybrid`, `hybrid_legacy`; gate runs `gate_v2`, `gate_hb` |
| `results/phase5/*.json` | `phase5_summary`, `hybrid_legacy_tests`, `legacy_drt_vs_other_planners`, `single_factor_summary` |

## Reproduce

```bash
cd experiments
export PYTHONPATH=../abaco:../danger_radius:../baselines:.
python3 verify_phase5_gate.py          # expect: 30 runs compared; mismatches: 0
./run_phase5.sh --analysis-only        # regenerates results/phase5/*.json from the stored per-run files
python3 check_phase5_numbers.py /path/to/manuscript.docx   # expect: 0 disagree
```

## Results (as in manuscript Tables 4A, 4B)

| Condition (DR-T unless stated) | Success | Any collision |
|---|---|---|
| Primary adapter (flat deposit) | 72.5% | 18.0% |
| 500-step limit only | 72.0% | 18.0% |
| Age-based deposit only | 99.0% | 13.5% |
| Both rules restored | 100.0% | 17.0% |

With both rules restored, DR-T's collision advantage over HB and HBP is not statistically detectable and DR-SAFE has lower success than DR-T
(see `phase5_summary.json`). Inside ACO+DWA with the age-based deposit, replacing the hard block by DR-T lowered any-collision from
19.5% to 12.0% (`hybrid_legacy_tests.json`; Holm p = 0.047 over eight tests). That is a single post hoc result from one set of 200
scenarios and has not been replicated on fresh scenarios.

## Limits of this evidence

* Post hoc, one scenario set, no retuning of any method for the legacy-pheromone adapter.
* Planning times are not comparable with the stored primary runs: the phase-5 runs and the primary runs were executed on different hardware.
* The non-ACO baselines (D* Lite + DWA, space-time A*, SIPP-style) do not use these rules and were not rerun; comparisons with them are descriptive.
* ORCA and MPC: the per-run outcomes of the cadence-matched rerun reported in the manuscript are not archived
  (`docs/ORCA_MPC_RERUN_RECONCILIATION_v30.md`), so no paired test against them was computed.
* Simulation only; no physical-robot or ROS/Gazebo validation.

## Parameter records (clarification added in v36)

* `results/PHASE3_TUNED_PARAMETERS.json` is the **tuning-stage record** (selection on tuning scenarios 0-3). It is retained unchanged. It is
  not the parameter set of the confirmed closed-loop results, which is recorded in the `params` field of
  `results/phase2_step3_v2/perrun.json` and hard-coded in `experiments/run_phase2_step3_v2_chunk.py`
  (HB and HBP 16 ants x 20 iterations; DR-T and DR-SAFE R = 3.5, K = 0.5, 12 ants x 20 iterations).
* `experiments/run_phase2_step3_v2_confirmation.py` previously hard-coded the tuning-stage values (HB 8 x 10; DR-T R = 4.5, K = 1). It now
  uses the confirmed values.
