# Changes from v22/Phase 0 to Phase 1

## Added
- `docs/EVAL_PROTOCOL_v2.md` — frozen Phase-1 evaluation design.
- `docs/PHASE1_AUDIT.md` — Phase-1 provenance, implementation check and status.
- `docs/SHA256_PHASE1_PRE_RUN.txt` — hashes recorded for protocol/new implementation/runner.
- `danger_radius/ABACO_safety_pred_continuous.py` — new non-frozen continuous-cost implementation.
- `experiments/run_phase1_ablation.py` — paired implementation ablation runner.
- `experiments/analyze_phase1_ablation.py` — summary generator.
- `results/phase1_continuous_ablation.json` — 20 paired implementation-check seeds.
- `results/phase1_ablation_summary.json` — aggregate comparison.

## Not changed
- Frozen planner directories/files were not edited.
- No new Phase-1 results were inserted into the manuscript.

## Interpretation
The corrected cost is continuous at the danger-radius boundary. The 20-run smoke ablation shows no collision regression but a lower mean minimum clearance, so Task 1.1 is intentionally left open rather than falsely marked complete.
