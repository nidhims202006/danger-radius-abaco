from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = json.loads((ROOT/'results/scaling_memory_direct.json').read_text())
rss = [json.loads(x) for x in (ROOT/'results/scaling_memory_rss.jsonl').read_text().splitlines() if x.strip()]
methods = ['HB','HBP','DR-T','DR-SAFE','space_time_astar','dstar_dwa']
sizes = [12,18,25,30,40]

# Priority-8 manuscript block: 5 grid sizes x 6 methods at 3 dynamic obstacles.
sub = {(r['grid'], r['method']): r for r in rows if r['dynamic_obstacles'] == 3}
assert len(sub) == 30, len(sub)
assert set(sub) == {(g,m) for g in sizes for m in methods}

rss_sub = {(r['grid'], r['method']): r for r in rss}
assert len(rss_sub) == 30, len(rss_sub)
assert set(rss_sub) == set(sub)

# Values printed in manuscript Tables 20/21 (rounded to 2/1 decimal places).
expected_ms = {
  12:[22.70,92.09,74.11,107.12,0.09,2.81],
  18:[27.41,117.05,89.48,149.36,0.30,0.67],
  25:[36.38,135.33,106.20,209.94,0.55,3.15],
  30:[28.77,141.27,123.90,205.51,0.41,1.29],
  40:[43.50,167.22,121.50,215.13,58.65,1.80],
}
expected_rss = {
  12:[90.4,90.4,90.4,90.4,90.4,90.4],
  18:[90.4,90.4,90.4,90.4,90.4,90.4],
  25:[90.4,90.4,90.4,90.4,90.4,90.4],
  30:[90.3,90.4,90.4,90.3,90.4,90.4],
  40:[90.3,90.4,90.4,90.4,92.5,90.4],
}

def close(a,b,tol):
    return abs(a-b) <= tol

for g in sizes:
    for i,m in enumerate(methods):
        got_ms = rss_sub[(g,m)]['planning_time_s']*1000
        assert close(got_ms, expected_ms[g][i], 0.03), (g,m,got_ms,expected_ms[g][i])
        got_rss = rss_sub[(g,m)]['peak_rss_kb']/1024
        assert close(got_rss, expected_rss[g][i], 0.12), (g,m,got_rss,expected_rss[g][i])

print('Priority-8 scaling check: PASS')
print('  Table 20: 30/30 manuscript runtime cells match stored direct-planning measurements.')
print('  Table 21: 30/30 manuscript RSS cells match stored isolated measurements.')
print('  Protocol: 5 grid sizes, 3 dynamic obstacles, 6 methods; no new tuning.')
