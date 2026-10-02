# Changes v22 -> Phase 0 update

**Date:** 2026-09-30

## Changed

- Added `docs/PHASE0_AUDIT.md` documenting the three undocumented hash mismatches and the limitation that the original-release files are absent from the supplied archive.
- Added `docs/PHASE0_MEETING_NOTES.md` recording the DR-T / DR-SAFE framing and ESWA submission target information available from the project materials.
- Added the Phase 0 provenance-audit update to `docs/FRESH_SEED_PROTOCOL.md`.
- Updated Section 5.10 of `paper/Danger-Radius_Paper_v22.docx` so its SHA-256 provenance statement matches the actual audit status rather than claiming that all current files still match the recorded hashes.
- Archived the supplied original v22 manuscript as `paper/archive/Danger-Radius_Paper_v22_freeze_original.docx`.
- Added `docs/SHA256_PHASE0.txt` for the changed Phase 0 artifacts.

## Not changed

No frozen planner files, result files, or experiment implementations were edited.

## Verification

`python experiments/check_paper_numbers.py` reports:

`348 cells/values agree; 0 disagree`

The three source-level diffs requested in checklist item 0.1 remain unavailable because the original release/Git history is not present in the supplied archive. The existing 69-run behavioral reproduction evidence is recorded rather than overstated as a source diff.

## 2026-09-30 — 0.3 owner/deadline completion

- Recorded submission deadline: Friday, 2 October 2026.
- Recorded authors/owners: M S Nidhi and Kolluri Sri Sasanka RushiMithra, jointly for checklist ownership.
- Added `docs/PHASE0_OWNER_MATRIX.md`.
