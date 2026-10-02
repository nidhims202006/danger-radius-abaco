# D* Lite + DWA source-level reproducibility

This directory contains the complete source implementation used for the D* Lite + DWA
reproducibility audit.

## Scope
- D* Lite search/planning implementation
- Dynamic replanning interface
- DWA local-control implementation/interface
- Collision and clearance evaluation
- Scenario loading and fixed configuration
- Per-scenario runner
- Output analysis

## Provenance
The original historical standalone D* Lite + DWA source was not recovered. Therefore this
directory does **not** claim to be the historical source. It is the complete source of the
replacement compatibility implementation used for the audit.

## Validation
The implementation was rerun on all 200 stored closed-loop scenarios:
- 199/200 stored runs reproduced exactly.
- Scenario 189 is the sole discrepancy.
- The discrepancy is only the collision flag.
- Rerun any-collision: 22.0%.
- Stored any-collision: 22.5%.
- Success: 100.0% in both.

## Reproduction
Use the project environment requirements and run the D* Lite + DWA batch runner supplied
with this archive. The exact source/configuration file hashes are recorded in
`docs/DLITE_SOURCE_MANIFEST.json`.
