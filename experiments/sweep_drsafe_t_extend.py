"""
sweep_drsafe_t_extend.py -- EXTENSION of the tuning grid past R = 4.5 (declared before running; the frozen selection of
results/drsafe_t_selected.json is NOT changed and the paper's main experiments keep R = 4.5, K = 2.0).
  Tuning seeds : 6000-6029 (same as the original sweep)
  New cells    : R in {5.5, 6.5} x K in {1, 2, 4} x D_SAFE in {1.0, 1.5}  (12 cells)
  Rule         : identical to select_drsafe_t.py, applied to the union of the original 9 (R x K) cells and these 6 per D_SAFE
                 (z-score of mean sharp turns and mean collisions/run over the 15 cells of that D_SAFE; lowest score wins; ties -> shorter length).
                 Output: results/drsafe_t_selected_extended.json (select_drsafe_t_extended.py).
"""
import os, time
import drsafe_lib as L
import ABACO_safety_pred as P

R_GRID, K_GRID, D_GRID = [5.5, 6.5], [1.0, 2.0, 4.0], [1.0, 1.5]
OUT = os.path.join(L.RESULTS_DIR, "sweep_drsafe_t_ext.json")
ck = L.load_ckpt(OUT, {"meta": dict(r=R_GRID, k=K_GRID, d=D_GRID, seeds="6000-6029"), "runs": {}})
runs = ck["runs"]; t0 = time.time()
for s in range(6000, 6030):
    for d in D_GRID:
        for R in R_GRID:
            for K in K_GRID:
                k = f"T|{R}|{K}|{d}|{s}"
                if k not in runs:
                    runs[k] = L._flat(P.run_abaco_safety_pred(L.GRID, s, d_safe=d, R=R, K=K), L.base)
    L.save_ckpt(OUT, ck)
    print(s, f"{time.time()-t0:.0f}s", flush=True)
print("complete")
