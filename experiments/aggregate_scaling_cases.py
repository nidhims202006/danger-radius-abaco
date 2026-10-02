from __future__ import annotations
import json, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
rows=json.loads((ROOT/"results/scaling_memory_direct.json").read_text())
METHODS=["HB","HBP","DR-T","DR-SAFE","space_time_astar","dstar_dwa"]
SIZES=[12,18,25,30,40]
DYN=[1,3,5]
def med_iqr(values):
    v=sorted(values); n=len(v); med=statistics.median(v); q1=statistics.median(v[:n//2]); q3=statistics.median(v[(n+1)//2:]); return med,q3-q1
out=[]
for g in SIZES:
    for m in METHODS:
        rs=[r for r in rows if r["grid"]==g and r["method"]==m and r["dynamic_obstacles"] in DYN]
        assert len(rs)==3,(g,m,len(rs))
        rt=med_iqr([r["planning_time_s"]*1000 for r in rs])
        mem=med_iqr([r["peak_tracemalloc_MB"] for r in rs])
        out.append({"grid":g,"method":m,"n_cases":3,"dynamic_obstacles":DYN,"runtime_ms_median":rt[0],"runtime_ms_iqr":rt[1],"tracemalloc_mb_median":mem[0],"tracemalloc_mb_iqr":mem[1]})
path=ROOT/"results/scaling_memory_median_iqr.json"
path.write_text(json.dumps(out,indent=2))
print(f"wrote {path}; {len(out)} method-grid summaries")
