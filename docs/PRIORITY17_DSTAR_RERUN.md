# Priority 17 — D* Lite rerun

Date: 2026-10-02
Package checkpoint: v66.3-c6-item17-dstar-rerun

## Rerun
The runner-compatible FastDStarLite implementation was rerun against the 200 primary closed-loop scenarios (scenario IDs 4–203), using the packaged scenario generator and the stored D* Lite + DWA configuration.

Result: 199/200 exact matches, 0 timeouts, 1 difference.

The sole difference is scenario 189: the stored run reports `any_collision=true`, while the rerun reports `any_collision=false`. Both stored and rerun runs report success.

## Interpretation
The historical standalone FastDStarLite source was not recovered. The archive therefore contains a newly authored runner-compatible replacement. The 199/200 match rate provides a reproducibility check for that replacement but does not establish source-level recovery of the historical implementation.

The stored per-run results remain the manuscript reference for the D* Lite + DWA rows. No stored numerical result was overwritten.

## Action
Priority 17 is treated as a completed rerun and documented residual mismatch, rather than claiming exact reproduction of all 200 historical runs.
