# Current package status

**Release:** `v36-eswa-post-hoc-legacy-pheromone-and-aco-dwa-hybrids`  
**Date:** 2026-10-03

## Release state

The repository is the current ESWA reproducibility package corresponding to the supplied manuscript.
The manuscript itself is intentionally maintained as a separate deliverable.

Public release identifiers:

- GitHub: https://github.com/nidhims202006/danger-radius-abaco.git
- Zenodo DOI: 10.5281/zenodo.23106834

## v36 changes

- Added the post hoc phase-5 analyses (`docs/PHASE5_POST_HOC.md`): legacy-pheromone adapter rerun and ACO+DWA with a prediction-aware ACO stage.
- Corrected the hard-coded parameters in `experiments/run_phase2_step3_v2_confirmation.py` to the confirmed values.
- The Zenodo DOI above identifies release v35; a new Zenodo version (and DOI) is needed for v36 before the manuscript cites these analyses.

## Evidence position

- DR-T is the primary design contribution.
- DR-SAFE is a secondary hard-clearance-floor extension. Exact-estimate ablation did not detect an
  incremental floor benefit, and the floor is not presented as a safety guarantee.
- Closed-loop evidence uses a common world/observation clock, Kalman estimation, five-tick scheduled
  replanning and execution-level collision checks.
- The N=8 high-fidelity validation is continuous-kinematic simulation/interface evidence only.
- The warehouse generator is included, but no full warehouse validation result is claimed.

## D* Lite reproducibility status

The historical standalone `FastDStarLite` source was not recovered from the available archives.
The package therefore contains a newly authored runner-compatible replacement in
`experiments/phase3_abaco.py` / `baselines/dstar_lite_dwa/fast_dstar_lite.py`.

Full validation on scenarios 4–203 produced 199/200 exact stored-run matches, zero timeouts, and one
disclosed collision-flag mismatch (scenario 189). Stored success is 100.0% and replacement success is
100.0%; stored any-collision is 22.5% and replacement any-collision is 22.0%.

This is compatibility reconstruction, not recovery of the historical source. The stored per-run file
remains the reference for the manuscript D* Lite + DWA results.

## Baseline-tuning boundary

Equal-budget tuning utilities are included and the closed-loop protocol uses a common tuning-budget
framework where reported. The historical fixed-grid development block retains an asymmetric tuning
history: DR-SAFE received a broader formulation-specific search than HB, HBP and APF. No retroactive
full fixed-grid equal-budget rebuild is claimed in this release. This limitation is stated in the manuscript
and should not be converted into a stronger comparative claim.

## Validation boundary

The package does not claim:

- physical-robot trials;
- ROS/Gazebo validation;
- a full warehouse-style execution study;
- a safety guarantee.

The held-out high-fidelity block (scenarios 204–211, N=8) is a simulation/interface stress test using
bounded unicycle dynamics, noisy CV-Kalman state estimation, five-tick replanning and continuous
swept-segment collision checks. The warehouse scenario generator is provided for future deployment-
style evaluation but no warehouse result is reported.

## Verification and integrity

- `docs/C6_SHA256_MANIFEST.json` is the authoritative package manifest, excluding itself.
- `docs/DLITE_SOURCE_MANIFEST.json` records the D* Lite provenance and compatibility result.
- `docs/ORCA_MPC_SHA256_MANIFEST.json` records the ORCA/MPC subset hashes.
- Python caches and bytecode are excluded from the release.
- `python -m compileall -q .` passes for the packaged Python sources.

## Reproduction entry points

See `README.md` for installation and lightweight stored-result checks. The main protocol and evidence
boundaries are documented in:

- `docs/EVAL_PROTOCOL_v2.md`
- `docs/RUN_ORDER.md`
- `docs/FLOOR_EVIDENCE_BOUNDARY.md`
- `docs/HIGH_FIDELITY_VALIDATION.md`
- `docs/DSTAR_LITE_REPRODUCIBILITY.md`
- `docs/PAPER_POSITIONING.md`
