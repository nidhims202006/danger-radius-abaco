# Phase 0 audit — v22 resubmission

**Date:** 2026-09-30  
**Manuscript baseline:** `paper/Danger-Radius_Paper_v22.docx`  
**Repository baseline:** v22-freeze

## 0.1 Hash-mismatch provenance audit

The v22 frozen protocol identifies three files whose current SHA-256 hashes do not match the hashes recorded before the fresh-seed confirmation runs:

- `danger_radius/ABACO_safety_pred.py`
- `experiments/run_apf_main.py`
- `experiments/analyze_apf_main.py`

The current repository does **not** contain the original-release copies of these three files, and no Git history is included in the supplied archive. Therefore a literal source diff against the original release cannot be performed from the supplied material.

The recorded and current hashes are:

| File | Hash recorded in frozen protocol | Current v22 hash | Direct diff |
|---|---|---|---|
| `danger_radius/ABACO_safety_pred.py` | `e995b0bbdd5c3aaf8659c835af77b9673f53a367b27afb7e96154ed6b42a82e1` | `e6c260a54a1007ef92cc0c7f3ab1f18aedfed6d2a460030b783a21f63345913e` | Not possible: original absent |
| `experiments/run_apf_main.py` | `8066b8b65a81432fe91a3ffb73228769358b44f0d2594f7e66a72c778d04586c` | `b6059258d1482e2da5486f223b4d5ce9d5b2dd750ee64349c55915b17cee3e3a` | Not possible: original absent |
| `experiments/analyze_apf_main.py` | `2fbc5e5ac22bb97ba2a1476b3c57a1a41733474aee7936d97f3e1ad8a6ca0af9` | `0eeb88dcc827984a0cc8677c75a6950c24206f65844eaeb2f4cd1e29d614e419` | Not possible: original absent |

The existing v22 provenance record reports that these files were behavior-checked rather than directly diffed: 69 stored runs were re-run with the current code and matched their stored records exactly. This supports the statement that no behavioral difference was detected in the sampled reproduction checks; it does **not** establish source-level identity with the unavailable original release.

Accordingly, the manuscript's Section 5.10 wording has been changed from an unconditional statement that all code hashes were fixed before the runs to an accurate statement about the **recorded confirmation protocol and its hashes**, followed by the later provenance-audit qualification.

### Status
**0.1: Partially closed from the supplied archive.** The audit outcome is recorded; a literal three-file diff remains impossible until the original release/Git history is supplied.

## 0.2 Co-author framing decision

The v22 manuscript framing is retained:

- **DR-T** = proposed time-aligned soft danger-radius cost.
- **DR-SAFE** = DR-T plus a hard clearance floor, reported as an extension.
- With exact estimates, the hard floor did not show a detectable additional benefit; the noisy-estimate floor result remains an explicitly post hoc finding.
- The paper does not claim a general safety guarantee or a general superiority of ACO over time-explicit planners.

This is consistent with `docs/PAPER_POSITIONING.md` and the v22 manuscript.

## 0.3 Target journal / abstract / ownership

- **Target journal:** Expert Systems with Applications (ESWA).
- **Abstract target:** ≤250 words based on the current ESWA author guidance available at the time of this audit. Elsevier's general guidance requires a concise, factual, stand-alone abstract; current Elsevier guidance also requires 3–5 highlights, with each highlight ≤85 characters. See the journal/publisher references recorded in the project notes.
- **Submission deadline:** Friday, 2 October 2026.
- **Authors / owners:** M S Nidhi and Kolluri Sri Sasanka RushiMithra, as listed on the manuscript. The checklist rows are assigned jointly to these two authors; no finer role split was supplied.

## Phase 0 outcome

Phase 0 documentation and the manuscript's Section 5.10 provenance sentence have been updated. No frozen planner/result files were edited.
