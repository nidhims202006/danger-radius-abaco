"""
sweep_drsafe_t.py -- tuning sweep for the time-aligned DR-SAFE (DR-SAFE-T).

FROZEN BEFORE RUNNING
  Tuning seeds : 6000-6029 (fresh; 5000-5029 were already looked at during the exploratory prototype)
  Grid         : R in {2.5, 3.5, 4.5} x K in {1, 2, 4} x D_SAFE in {1.0, 1.5}  (18 cells)
  Also per seed: HB, HB-with-prediction (HBP), DR at (3.5, 2.0)
  Selection    : for EACH D_SAFE value separately, z-score turns and collisions/run across
                 the 9 (R x K) cells of that D_SAFE, score = z(turns) + z(coll); lowest wins; ties -> shorter length.
                 The two winners (one per D_SAFE) go into the confirmatory run unchanged.
Checkpointed / resumable; seed-major loop.
"""
import os, time
import drsafe_lib as L
import ABACO_safety_pred as P

R_GRID, K_GRID, D_GRID = [2.5, 3.5, 4.5], [1.0, 2.0, 4.0], [1.0, 1.5]
OUT = os.path.join(L.RESULTS_DIR, "sweep_drsafe_t.json")
ck = L.load_ckpt(OUT, {"meta": dict(r=R_GRID, k=K_GRID, d=D_GRID, seeds="6000-6029"), "runs": {}})
runs = ck["runs"]
t0 = time.time()
for s in range(6000, 6030):
    todo = []
    if f"HB|{s}" not in runs: runs[f"HB|{s}"] = L.run_hb(s)
    if f"DR|{s}" not in runs: runs[f"DR|{s}"] = L.run_dr(s)
    if f"HBP|{s}" not in runs: runs[f"HBP|{s}"] = L._flat(P.run_abaco_safety_pred(L.GRID, s, mode="hb"), L.base)
    for d in D_GRID:
        for R in R_GRID:
            for K in K_GRID:
                k = f"T|{R}|{K}|{d}|{s}"
                if k not in runs:
                    runs[k] = L._flat(P.run_abaco_safety_pred(L.GRID, s, d_safe=d, R=R, K=K), L.base)
    L.save_ckpt(OUT, ck)
    print(s, f"{time.time()-t0:.0f}s", flush=True)
print("complete")
