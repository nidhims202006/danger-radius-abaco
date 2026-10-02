# Priority 8 — Computational scaling and memory

Date: 2026-10-02
Package checkpoint: v65.6-c6-item8
Manuscript checked: `Danger-Radius_Paper_v87_refs_1-3_fixed.docx`

## Completed

1. The manuscript already contains Section 5.12, **Computational Scaling and Memory**, with Tables 20 and 21.
2. The repository contains the direct-planning scaling benchmark and stored outputs:
   - `experiments/benchmark_scaling_memory_direct.py`
   - `experiments/benchmark_scaling_memory.py`
   - `results/scaling_memory_direct.json`
   - `results/scaling_memory_rss.jsonl`
   - `results/SCALING_MEMORY_REPORT.md`
3. The stored direct benchmark contains the full 5 × 6 × 3 matrix: grid sizes 12, 18, 25, 30, 40; six methods; and 1, 3, 5 dynamic obstacles (90 cases).
4. The manuscript Tables 20 and 21 use the 3-dynamic-obstacle slice: 5 grid sizes × 6 methods = 30 runtime cells and 30 RSS cells.
5. `experiments/check_scaling_benchmark.py` passes: 90/90 stored grid-method-obstacle cases are present.
6. `experiments/check_priority8_scaling.py` passes: all 30 Table-20 runtime values and all 30 Table-21 RSS values match the stored isolated measurements within the manuscript rounding tolerance.
7. The manuscript numerical checker remains clean: `415 cells/values agree; 0 disagree`.

## Interpretation retained in the manuscript

The scaling block is an engineering probe, not a statistical comparison. Runtime is environment-specific. Peak RSS includes the Python interpreter/library baseline and is not an algorithm-only memory requirement. The observed RSS range is approximately 90.3–92.5 MB in the reported benchmark. The 40×40 space-time A* runtime is substantially larger than its smaller-grid values in this tested configuration.

No manuscript numerical values were changed for Priority 8.
