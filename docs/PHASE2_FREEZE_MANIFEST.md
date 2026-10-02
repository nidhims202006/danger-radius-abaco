# Phase 2 pre-run freeze manifest

**Date:** 2026-09-30

The following files are frozen before confirmation execution. Hashes are recorded in `docs/SHA256_PHASE2_PRE_RUN.txt`.

- `docs/EVAL_PROTOCOL_v2.md`
- `docs/PHASE2_IMPLEMENTATION_PLAN.md`
- `experiments/phase2_scenario_generator.py`
- `experiments/phase2_estimator.py`
- `experiments/phase2_planners.py`
- `experiments/phase2_logger.py`
- `experiments/phase2_closed_loop.py`
- `experiments/phase2_smoke_test.py`

The existing statistical analysis plan in `docs/EVAL_PROTOCOL_v2.md` is unchanged.

The Phase-2 smoke test is implementation validation only. It does not inspect, modify, or select from the existing confirmation results.

Before confirmation execution, any parameter file or run manifest added to the confirmation pipeline must be hashed and recorded here or in an amendment with a new SHA record.
