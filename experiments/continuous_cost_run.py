"""continuous_cost_run.py -- replication of the fixed-grid exact-estimate blocks with the boundary-continuous cost
K*max(0, 1/(d+eps) - 1/(R+eps))  (danger_radius/ABACO_safety_pred_continuous_v2.py) instead of the truncated K/(d+eps)*[d<R].
Protocol (fixed before running): arms TA (DR-SAFE-T, D_SAFE=1.0), TB (D_SAFE=1.5), SOFT (= DR-T, no floor); R = 4.5, K = 2.0 exactly as in the
truncated runs (NOT re-tuned); development seeds 10000-10299 and confirmation seeds 20000-20299. HB, HBP and APF-predicted are unchanged by
the cost form and are taken from the stored per-run results (same seeds, so comparisons stay paired).
Usage: python continuous_cost_run.py dev|conf"""
import json, os, sys, time
import drsafe_lib as L
import ABACO_safety_pred_continuous_v2 as C
blk = sys.argv[1]; lo = {'dev': 10000, 'conf': 20000}[blk]
OUT = os.path.join(L.RESULTS_DIR, 'continuous_cost', f'{blk}.json')
ck = L.load_ckpt(OUT, {'meta': dict(block=blk, seeds=f'{lo}-{lo+299}', R=4.5, K=2.0, module='ABACO_safety_pred_continuous_v2'), 'runs': {}})
runs = ck['runs']; t0 = time.time()
ARMS = {'SOFT': dict(d_safe=0.0), 'TA': dict(d_safe=1.0), 'TB': dict(d_safe=1.5)}
for i in range(300):
    s = lo + i; rec = runs.setdefault(str(s), {})
    for a, kw in ARMS.items():
        if a not in rec: rec[a] = L._flat(C.run_abaco_safety_pred(L.GRID, s, R=4.5, K=2.0, **kw), L.base)
    L.save_ckpt(OUT, ck)
    if (i + 1) % 10 == 0: print(blk, f'{i+1}/300 {time.time()-t0:.0f}s', flush=True)
print('complete')
