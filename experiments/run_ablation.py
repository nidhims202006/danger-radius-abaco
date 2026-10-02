"""
run_ablation.py -- component ablation of DR-SAFE on the main environment, seeds 10000-10299
(paired with the HB, HBP and full DR-SAFE runs already stored).

Arms (all with time-aligned prediction, R=4.5, K=2.0 as selected in tuning; NOT re-tuned):
  SOFT  : soft danger-radius cost only, no hard floor          (D_SAFE = 0)
  F10   : hard floor only (D_SAFE = 1.0), no soft cost          (K = 0)
  F15   : hard floor only (D_SAFE = 1.5), no soft cost          (K = 0)
Full DR-SAFE (both parts) is TA (D=1.0) / TB (D=1.5) in main_new_arms.json.
"""
import os, sys, time
import drsafe_lib as L
import ABACO_safety_pred as P

OUT = os.path.join(L.RESULTS_DIR, "ablation_main.json")
ck = L.load_ckpt(OUT, {"meta": dict(R=4.5, K=2.0, seeds="10000-10299"), "runs": {}})
runs = ck["runs"]
t0 = time.time()
for i in range(300):
    s = 10000 + i
    rec = runs.setdefault(str(s), {})
    if "SOFT" not in rec: rec["SOFT"] = L._flat(P.run_abaco_safety_pred(L.GRID, s, d_safe=0.0, R=4.5, K=2.0), L.base)
    if "F10" not in rec:  rec["F10"]  = L._flat(P.run_abaco_safety_pred(L.GRID, s, d_safe=1.0, R=4.5, K=0.0), L.base)
    if "F15" not in rec:  rec["F15"]  = L._flat(P.run_abaco_safety_pred(L.GRID, s, d_safe=1.5, R=4.5, K=0.0), L.base)
    L.save_ckpt(OUT, ck)
    if (i + 1) % 10 == 0:
        print(s, f"{i+1}/300 {time.time()-t0:.0f}s", flush=True)
print("complete")
