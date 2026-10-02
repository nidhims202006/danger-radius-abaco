import numpy as np, matplotlib, json, os, sys, time
matplotlib.use('Agg')
from scipy import stats
import ABACO_baseline as base
import ABACO_novelty as novelty
from broaden_validation import (env_A_factories, env_B_factories, env_C_factories,
                                 set_environment, snapshot_module, restore_module)
from exec_aligned_metrics import execution_aligned_metrics

ENVS = {'A': env_A_factories(), 'B': env_B_factories(), 'C': env_C_factories()}
N_RUNS = 20
SEED_BASE = 42

CKPT = os.path.join('..', 'results', 'generalization_methodb_results_execution_aligned_v2.json')
if os.path.exists(CKPT):
    with open(CKPT) as f:
        state = json.load(f)
else:
    state = {env_key: {'b': {'len':[],'turns':[],'clear':[],'coll':0},
                        'n': {'len':[],'turns':[],'clear':[],'coll':0},
                        '_next_i': 0}
              for env_key in ENVS}

env_key = sys.argv[1]
batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 10

env = ENVS[env_key]
st = state[env_key]
start = st['_next_i']
end = min(start + batch_size, N_RUNS)

base_snap = snapshot_module(base)
novelty_snap = snapshot_module(novelty)
t0 = time.time()
try:
    set_environment(base, env["grid_size"], env["start"], env["goal"], env["obstacles"], env["base_dyn"])
    set_environment(novelty, env["grid_size"], env["start"], env["goal"], env["obstacles"], env["novelty_dyn"])
    grid = base.create_grid()

    for i in range(start, end):
        seed = SEED_BASE + i
        br = base.run_abaco(grid, use_novelty=False, seed=seed)
        nr = novelty.run_abaco(grid, use_novelty=True, seed=seed)
        bc, bmc = execution_aligned_metrics(br, base)
        nc, nmc = execution_aligned_metrics(nr, novelty)
        st['b']['len'].append(br['best_distance']); st['b']['turns'].append(br['sharp_turns'])
        st['b']['clear'].append(bmc); st['b']['coll'] += bc
        st['n']['len'].append(nr['best_distance']); st['n']['turns'].append(nr['sharp_turns'])
        st['n']['clear'].append(nmc); st['n']['coll'] += nc
        print(f"env {env_key} run {i+1}/{N_RUNS} done, elapsed {time.time()-t0:.1f}s")
finally:
    restore_module(base, base_snap)
    restore_module(novelty, novelty_snap)

st['_next_i'] = end
os.makedirs(os.path.dirname(CKPT), exist_ok=True)
with open(CKPT, 'w') as f:
    json.dump(state, f)
print(f"env {env_key} batch done: {start} to {end}")
