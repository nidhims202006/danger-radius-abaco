from __future__ import annotations
import json
from pathlib import Path

p=Path(__file__).resolve().parent.parent/'results'/'scaling_memory_direct.json'
rows=json.loads(p.read_text())
expected_methods={'HB','HBP','DR-T','DR-SAFE','space_time_astar','dstar_dwa'}
expected_sizes={12,18,25,30,40}; expected_dyn={1,3,5}
assert len(rows)==90, len(rows)
assert {(r['grid'],r['method'],r['dynamic_obstacles']) for r in rows} == {(g,m,d) for g in expected_sizes for m in expected_methods for d in expected_dyn}
assert all(r['peak_tracemalloc_MB']>=0 and r['peak_rss_MB']>0 for r in rows)
print('Scaling benchmark check: PASS (90/90 grid-method-obstacle cases present)')
