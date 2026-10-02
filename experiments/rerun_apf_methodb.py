import numpy as np, matplotlib, json, os, sys, time
matplotlib.use('Agg')
import ABACO_baseline as base
import ABACO_apf_baseline as apf
from exec_aligned_metrics import execution_aligned_metrics

grid = base.create_grid()

CKPT = os.path.join('..', 'results', 'apf_methodb_results_execution_aligned_v2.json')
if os.path.exists(CKPT):
    with open(CKPT) as f:
        rows = json.load(f)
    start = rows['_next_i']
else:
    rows = {'len': [], 'turns': [], 'clear': [], 'coll': 0, '_next_i': 0}
    start = 0

batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 15
end = min(start + batch_size, 50)
t0 = time.time()
for i in range(start, end):
    seed = 42 + i
    r = apf.run_abaco_apf(grid, seed=seed)
    c, mc = execution_aligned_metrics(r, base)
    rows['len'].append(r['best_distance'])
    rows['turns'].append(r['sharp_turns'])
    rows['clear'].append(mc)
    rows['coll'] += c
    print(f"run {i+1}/50 done, elapsed {time.time()-t0:.1f}s")

rows['_next_i'] = end
os.makedirs(os.path.dirname(CKPT), exist_ok=True)
with open(CKPT, 'w') as f:
    json.dump(rows, f)
print(f"Batch done: {start} to {end}.")
