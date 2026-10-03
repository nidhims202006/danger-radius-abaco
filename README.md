# Danger-Radius / ABACO — ESWA Reproducibility Package

**Release:** `v36-eswa-post-hoc-legacy-pheromone-and-aco-dwa-hybrids`

The manuscript is a separate deliverable and is intentionally **not** included in this archive.
This repository contains the experiment code, stored results, figures, analysis scripts, protocols and
integrity records needed to inspect and reproduce the reported numerical evidence.

## Evidence scope

- **DR-T is the primary design contribution.** It evaluates the obstacle cost at the predicted
  obstacle position for the step at which a candidate cell would be reached.
- **DR-SAFE is a secondary hard-clearance-floor extension.** The exact-estimate ablation did not
  detect an incremental floor benefit, so the floor is not presented as a safety guarantee or as the
  mechanism responsible for the main DR-T result. See `docs/FLOOR_EVIDENCE_BOUNDARY.md`.
- The principal closed-loop confirmation uses the common world/observation clock, Kalman state
  estimation, five-tick scheduled replanning and execution-level collision checks.
- The held-out high-fidelity validation (`N=8`, scenarios 204–211) uses continuous-kinematic
  simulation, noisy CV-Kalman estimation, five-tick replanning and swept-segment collision checks.
  It is **simulation/interface evidence only**, not physical-robot or ROS/Gazebo validation.
- A deterministic warehouse-style scenario generator is included, but no full warehouse validation
  result is claimed.
- Equal-budget tuning utilities are included. The historical fixed-grid development results retain
  an asymmetric tuning history; that limitation is documented rather than presented as a retroactively
  equal-budget comparison.
- Post hoc phase-5 analyses (legacy-pheromone adapter; ACO+DWA with a prediction-aware ACO stage; manuscript Tables 4A and 4B) are
  included with a reproducibility gate; see `docs/PHASE5_POST_HOC.md`. They are post hoc, use one scenario set and no retuning.
- ORCA and MPC are included as post hoc matched-interface closed-loop baselines; their results are
  reported descriptively where the manuscript specifies the applicable inference boundary.

## Public release identifiers

- GitHub: https://github.com/nidhims202006/danger-radius-abaco.git
- Zenodo: https://doi.org/10.5281/zenodo.23106834

## Installation

```bash
pip install -r requirements.txt
export PYTHONPATH=abaco:danger_radius:baselines:experiments
```

## Stored-result verification

Run the lightweight checks first:

```bash
python3 experiments/verify_reproduction.py 12
python3 experiments/check_scaling_benchmark.py
python3 experiments/check_priority8_scaling.py
python3 experiments/check_priority14_scaling.py
python3 experiments/check_dstar_compat.py
```

The checks operate on stored results and do not require a full experiment rerun.

### D* Lite compatibility

`experiments/phase3_abaco.py` provides a newly authored, runner-compatible `FastDStarLite` replacement
built on the packaged `DStarLite` implementation. The historical standalone `FastDStarLite` source was
not recovered from the available archives, so this is a compatibility reconstruction, not source-level
recovery.

The full check on scenarios 4–203 gives:

- 199/200 exact stored-run matches;
- one disclosed mismatch (scenario 189, collision flag only);
- 0 timeouts;
- stored success 100.0%, replacement success 100.0%;
- stored any-collision 22.5%, replacement any-collision 22.0%.

The stored per-run results remain the reference values for the manuscript D* Lite + DWA rows.
See `docs/DSTAR_LITE_REPLACEMENT.md`, `docs/DSTAR_LITE_REPRODUCIBILITY.md` and
`docs/DLITE_SOURCE_MANIFEST.json`.

## Main reproducibility material

| Area | Main files |
|---|---|
| Fixed-grid / historical results | `results/`, `abaco/`, `danger_radius/` |
| Closed-loop confirmation | `experiments/phase3_runner_v3.py`, `results/phase2_step3_v2/` |
| A1 prediction-index sensitivity | `experiments/run_a1_sensitivity.py`, `experiments/analyze_a1_sensitivity.py` |
| A3 paired statistics | `experiments/analyze_a3_paired_statistics.py`, `results/a3_paired_statistics/` |
| High-fidelity validation | `experiments/high_fidelity_kinematic_validation.py`, `results/high_fidelity_kinematic_validation/` |
| Scaling / memory checks | `experiments/aggregate_scaling_cases.py`, `experiments/check_priority14_scaling.py`, `results/scaling_memory_*.json*` |
| ORCA / MPC baselines | `experiments/*orca_mpc*`, `results/phase4_orca_mpc*`, `docs/ORCA_MPC_RERUN_RECONCILIATION_v30.md` |
| Warehouse generator | `experiments/warehouse_scenario_generator.py` |
| Protocols and evidence boundaries | `docs/` |

## Manuscript number checking

The manuscript is maintained separately. The repository includes the checker:

```bash
python3 experiments/check_paper_numbers.py /path/to/Danger-Radius_Paper_ESWA_revised_v39.docx
python3 experiments/check_phase5_numbers.py /path/to/Danger-Radius_Paper_ESWA_revised_v39.docx   # Tables 4A and 4B (run from experiments/)
```

## Integrity

`docs/C6_SHA256_MANIFEST.json` is the authoritative SHA-256 manifest for the package contents,
excluding the manifest itself to avoid a self-hash cycle. The D* Lite-specific source manifest and
ORCA/MPC manifest provide additional targeted integrity checks.

## Limitations that must remain explicit

This package does **not** establish physical-robot validation, ROS/Gazebo validation, or a completed
warehouse-scale execution study. It also does not retroactively rebuild the historical fixed-grid
baseline results under a common tuning budget. These are disclosed limitations of the evidence package,
not omitted experiments.

## License and citation

Code is released under the MIT License. Citation metadata are provided in `CITATION.cff`.
The Zenodo DOI is the persistent archival identifier for the released reproducibility materials.
