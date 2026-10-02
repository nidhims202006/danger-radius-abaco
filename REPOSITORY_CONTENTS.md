# Repository contents — v66.5 submission checkpoint

The manuscript is a separate deliverable and is intentionally absent.

| Directory | Contents |
|---|---|
| `abaco/` | ABACO core and execution-aligned metrics |
| `danger_radius/` | danger-radius prediction and continuous/fixed-grid implementations |
| `baselines/` | APF-style baseline |
| `experiments/` | current experiment runners, analyses, figures, checks, and verification scripts |
| `results/` | accepted stored results used by the manuscript |
| `figures/` | source experiment figures |
| `figures_eswa/` | ESWA-oriented figure exports |
| `docs/` | protocols, audits, freeze/reconciliation records, package notes, and D* Lite reproducibility records |

Quarantined/superseded result blocks and manuscript editing scripts are excluded. Python caches are excluded.


## Top-level package metadata

- `VERSION` identifies the current package revision.
- `README.md` documents the current evidence blocks and reproducibility commands.
- `CITATION.cff` provides citation metadata without claiming a public DOI or repository URL.
- `docs/C6_SHA256_MANIFEST.json` is the authoritative integrity manifest.


## Priority-13 practical significance
The manuscript reports the stored randomized-suite percentage reductions and restores a practical-guidance list in the conclusion. See `docs/PRIORITY13_PRACTICAL_SIGNIFICANCE.md`.


## Priority-14 scaling revision
Tables 20–21 now aggregate three stored deterministic direct-planning cases per grid size (1, 3 and 5 dynamic obstacles) using median/IQR. Table 21 reports peak traced Python allocations rather than process RSS, with the native-allocation limitation stated explicitly. See `docs/PRIORITY14_SCALING_MEDIAN_IQR.md`.

- `docs/PRIORITY15_BASELINE_COVERAGE.md` — baseline coverage audit.


## Archive organization

Superseded planning/freeze records are retained under `docs/archive/legacy/`; the active `docs/` directory contains current protocols, audits and package-status records. Python caches and manuscript files remain excluded.

- `docs/PRIORITY19_ARCHIVE_TIDY.md` — archive cleanup audit.


## Priority-20 post hoc ORCA/MPC baselines
- `docs/PRIORITY20_ORCA_MPC_BASELINES.md` — protocol, files and caveats.
- `docs/ORCA_MPC_SHA256_MANIFEST.json` — hashes of the files added at v67 (the C6 manifest still covers the v66.5 files).
