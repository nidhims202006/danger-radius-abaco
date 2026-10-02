# Priority 19 — Archive tidy-up

Date: 2026-10-02
Package checkpoint: v66.5-c6-item19-archive-tidy

## Actions

- Moved two superseded planning/freeze documents out of the active `docs/` namespace into `docs/archive/legacy/`:
  - `NEXT_STEPS.md` — historical v22-era planning checklist whose completed items and terminology no longer describe the current submission checkpoint.
  - `SUBMISSION_PACKAGE_FREEZE.md` — historical v65 freeze note retained for provenance but superseded by the current v66.x package checkpoints.
- Removed no accepted numerical result, source module, figure, protocol, or verification audit.
- Confirmed Python caches and bytecode are absent from the archive.
- Retained historical result files that are still referenced by audit/provenance documents, including the older RSS benchmark outputs.
- Updated active package metadata (`VERSION`, `README.md`, `REPOSITORY_CONTENTS.md`, `CITATION.cff`, and `docs/PACKAGE_STATUS.md`) to the v66.5 checkpoint.
- Regenerated the authoritative package SHA-256 manifest after the cleanup.

## Scope

This is an archive-organization change only. No experimental result, manuscript number, algorithm, parameter, or baseline result was changed.
