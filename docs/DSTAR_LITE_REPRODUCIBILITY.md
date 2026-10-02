# D* Lite reproducibility verification

The historical standalone `FastDStarLite` source was not available in the recovered submission archives. The archive therefore supplies a newly authored runner-compatible implementation in `experiments/fast_dstar_lite.py`. It is not presented as recovery of the historical source.

## Verification

The verification command is location-independent:

```bash
python3 experiments/check_dstar_compat.py
```

By default it checks the 200 primary closed-loop scenarios (IDs 4–203) against the stored `dstar_dwa` rows in `results/phase2_step3_v2/perrun.json`.

Verified on 2026-10-02:

- scenarios checked: 200
- exact matches: 199
- mismatches: 1
- timeouts: 0
- stored success: 100.0%
- replacement success: 100.0%
- stored any-collision: 22.5%
- replacement any-collision: 22.0%

The sole mismatch is scenario 189. Both stored and rerun executions reach the goal; the stored run records `any_collision=True`, whereas the replacement records `False`. The replacement does not hard-code this stored outcome.

The stored per-run data remain the reference values for the manuscript's D* Lite + DWA rows. The compatibility result is therefore disclosed as 199/200 exact reproduction, not source-level historical recovery.
