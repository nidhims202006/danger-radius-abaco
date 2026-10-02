"""Exploratory: time-aligned floor (DR-SAFE-T) on the TUNING seeds (5000-5029) only.
Reuses HB / DR / DR-SAFE(3.5,2.0) results for the same seeds from rk_sweep_drsafe.json."""
import json, os, sys, time
import numpy as np
import drsafe_lib as L
import ABACO_safety_pred as P

OUT = os.path.join(L.RESULTS_DIR, "explore_time_aligned_floor.json")
ck = L.load_ckpt(OUT, {"runs": {}})
runs = ck["runs"]
t0 = time.time()
for s in range(5000, 5030):
    for ds in (1.0, 1.5):
        k = f"DRST_T|{ds}|{s}"
        if k not in runs:
            r = P.run_abaco_safety_pred(L.GRID, s, d_safe=ds)
            runs[k] = L._flat(r, L.base)
    L.save_ckpt(OUT, ck)
    print(s, f"{time.time()-t0:.0f}s", flush=True)
print("complete")
