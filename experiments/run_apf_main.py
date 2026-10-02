"""
run_apf_main.py -- APF-style baseline against DR-SAFE on the main environment, seeds 10000-10299.
  APFS : APF cost at the planning-time snapshot (as in the pilot, Section 5.6), D0=3.5, ETA=2.0
  APFP : APF cost at the PREDICTED position (same information as DR-SAFE), D0=4.5, ETA=2.0 (matched to DR-SAFE's R, K)
"""
import os, sys, time
import drsafe_lib as L
import ABACO_safety_pred as P
sys.path.insert(0, os.path.join(L.ROOT, "baselines"))
import ABACO_apf_baseline as apf

OUT = os.path.join(L.RESULTS_DIR, "apf_main.json")
ck = L.load_ckpt(OUT, {"meta": dict(apfs=(3.5, 2.0), apfp=(4.5, 2.0), seeds="10000-10299"), "runs": {}})
runs = ck["runs"]
t0 = time.time()
for i in range(300):
    s = 10000 + i
    rec = runs.setdefault(str(s), {})
    if "APFS" not in rec: rec["APFS"] = L._flat(apf.run_abaco_apf(L.GRID, seed=s), L.base)
    if "APFP" not in rec: rec["APFP"] = L._flat(P.run_abaco_safety_pred(L.GRID, s, R=4.5, K=2.0, mode="apf"), L.base)
    L.save_ckpt(OUT, ck)
    if (i + 1) % 10 == 0:
        print(s, f"{i+1}/300 {time.time()-t0:.0f}s", flush=True)
print("complete")
