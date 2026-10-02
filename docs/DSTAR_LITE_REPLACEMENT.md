# D* Lite replacement

The historical standalone `FastDStarLite` source was not available in the recovered submission archives. A new runner-compatible implementation is therefore supplied in `experiments/fast_dstar_lite.py`.

This is explicitly a replacement implementation, not a claim that the historical source has been recovered. It preserves the runner API used by the closed-loop experiments and applies the same per-call `max_expansions` behaviour used by the validated compatibility implementation.

## Full compatibility check

The replacement was executed on all 200 stored closed-loop scenarios (IDs 4–203).

- Exact matches: 199/200
- Mismatches: 1
- Timeouts: 0
- Stored success: 100.0%
- Replacement success: 100.0%
- Stored any-collision: 22.5%
- Replacement any-collision: 22.0%

The sole mismatch is scenario 189. Both runs succeed; the stored run records a collision while the replacement does not. Because the historical source is unavailable, the implementation does not hard-code the stored outcome for that scenario.

The stored per-run data remain the reference values for the manuscript's D* Lite + DWA rows.
