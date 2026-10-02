from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
rows=json.loads((ROOT/"results/scaling_memory_median_iqr.json").read_text())
assert len(rows)==30
for r in rows:
    assert r["n_cases"]==3 and r["dynamic_obstacles"]==[1,3,5]
    assert r["runtime_ms_median"]>=0 and r["runtime_ms_iqr"]>=0
    assert r["tracemalloc_mb_median"]>=0 and r["tracemalloc_mb_iqr"]>=0
print("Priority-14 scaling check: PASS")
print("  Table 20 basis: 30 method-grid summaries, each aggregated over 3 cases (1/3/5 dynamic obstacles).")
print("  Table 21 basis: peak traced Python allocations, excluding process RSS baseline and native/C allocations.")
