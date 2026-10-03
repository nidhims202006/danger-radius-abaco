# Repository contents — ESWA reproducibility release

The manuscript is a separate deliverable and is intentionally absent from this repository archive.

| Directory | Contents |
|---|---|
| `abaco/` | ABACO core planner and execution-aligned metrics |
| `danger_radius/` | DR-T / DR-SAFE prediction-based and continuous implementations |
| `baselines/` | Baseline implementations, including the runner-compatible D* Lite + DWA source |
| `experiments/` | Experiment runners, analysis, verification, high-fidelity validation and reproduction checks |
| `results/` | Stored result files used by the manuscript |
| `figures/` | Source experiment figures |
| `figures_eswa/` | ESWA-oriented figure exports |
| `docs/` | Protocols, evidence boundaries, manifests, package status and reproducibility records |

## Top-level metadata

- `README.md` — installation, evidence scope and stored-result checks.
- `VERSION` — current repository release identifier.
- `CITATION.cff` — citation metadata and repository/DOI identifiers.
- `.zenodo.json` — Zenodo metadata for the archived software release.
- `.gitignore` — repository hygiene rules.
- `docs/PHASE5_POST_HOC.md` — post hoc legacy-pheromone and ACO+DWA analyses (`experiments/phase5_*.py`, `results/phase5/`).
- `docs/DATA_AVAILABILITY.md` — public GitHub and Zenodo availability statement.
- `docs/C6_SHA256_MANIFEST.json` — authoritative SHA-256 integrity manifest for package contents other than the manifest itself.
- `docs/DLITE_SOURCE_MANIFEST.json` — D* Lite implementation/source-package manifest.

## Evidence boundary

DR-T is the primary contribution. DR-SAFE is retained as a secondary hard-floor extension; the exact-estimate ablation did not detect an incremental floor benefit, and the floor is not presented as a safety guarantee. See `docs/FLOOR_EVIDENCE_BOUNDARY.md` and `docs/PAPER_POSITIONING.md`.

A held-out N=8 continuous-kinematic validation is included as simulation/interface evidence. It is not physical-robot or ROS/Gazebo validation. The warehouse scenario generator is included, but no full warehouse validation result is claimed.

## Public identifiers

- GitHub: https://github.com/nidhims202006/danger-radius-abaco.git
- Zenodo DOI: https://doi.org/10.5281/zenodo.23106834
