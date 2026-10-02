# Phase 5.4 — Reproducibility package freeze

Date: 2026-10-02

Status: **FROZEN**

Package: `v65-submission-freeze`

The manuscript is intentionally separate. This package contains the code, accepted stored results, figures, protocols, audits, and verification material required to reproduce or inspect the numerical evidence represented in the v65 manuscript.

## Integrity decisions

- Phase-2 corrected closed-loop block: accepted.
- Matched-interface ACO+DWA and SIPP-style baselines: accepted as supplementary implementations, explicitly not source-level literature reproductions.
- Clean Step-6 `priority13_drt_extension_v3_clean`: accepted.
- Step-6 `priority13_drt_extension_v2`: quarantined and excluded.
- Older `priority13_drt_extension`: superseded and excluded.
- Python caches: removed.
- Manuscript files: excluded.
- Historical manuscript-editing scripts: excluded.

## Required integrity checks

1. `python3 experiments/verify_reproduction.py 12`
2. `python3 experiments/check_scaling_benchmark.py`
3. `cd results/priority13_drt_extension_v3_clean && sha256sum -c SHA256.txt`
4. Inspect `docs/PHASE3_STEP6_CLEAN_AUDIT.md` and `docs/PHASE3_FINAL_RECONCILIATION_CHECKPOINT.md` for scope separation.

The clean Step-6 SHA-256 manifest is retained inside its result directory. A package-level SHA-256 manifest is generated at the archive root.
