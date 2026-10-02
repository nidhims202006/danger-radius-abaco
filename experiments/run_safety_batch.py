import numpy as np, matplotlib, json, os, sys, time
matplotlib.use('Agg')
import ABACO_baseline as base
import ABACO_novelty as novelty
import ABACO_safety_radius as safety
from exec_aligned_metrics import execution_aligned_metrics

safety.D_SAFE = 1.5
grid = base.create_grid()

CKPT = os.path.join('..', 'results', 'safety_experiment_results_execution_aligned_v2.json')
if os.path.exists(CKPT):
    with open(CKPT) as f:
        rows = json.load(f)
    start = rows['_next_i']
else:
    rows = {k: {'len':[], 'turns':[], 'clear':[], 'coll':0, 'fallbacks':[]} for k in ['HB','DR','DR_SAFE']}
    rows['_next_i'] = 0
    start = 0

batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 15
end = min(start + batch_size, 50)
t0 = time.time()
for i in range(start, end):
    seed = 42 + i
    br = base.run_abaco(grid, use_novelty=False, seed=seed)
    nr = novelty.run_abaco(grid, use_novelty=True, seed=seed)
    sr = safety.run_abaco_safety(grid, seed=seed)
    for key, r, mod in [('HB', br, base), ('DR', nr, novelty), ('DR_SAFE', sr, base)]:
        c, mc = execution_aligned_metrics(r, mod)
        rows[key]['len'].append(r['best_distance'])
        rows[key]['turns'].append(r['sharp_turns'])
        rows[key]['clear'].append(mc)
        rows[key]['coll'] += c
        rows[key]['fallbacks'].append(r.get('safety_fallback_count', 0) if key == 'DR_SAFE' else 0)
    print(f"run {i+1}/50 done, elapsed {time.time()-t0:.1f}s")

rows['_next_i'] = end
os.makedirs(os.path.dirname(CKPT), exist_ok=True)
with open(CKPT, 'w') as f:
    json.dump(rows, f)
print(f"Batch done: {start} to {end}. Next start: {end}")
