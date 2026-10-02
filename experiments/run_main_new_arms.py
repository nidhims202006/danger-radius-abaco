"""
run_main_new_arms.py -- N=300 confirmatory run of the NEW arms on the main 18x18 environment,
seeds 10000-10299 (same seeds as results/confirmatory_perrun.json, which already holds HB, DR,
DR-SAFE-old). Arms: HBP (hard block with prediction), TA (DR-SAFE-T, D_SAFE=1.0), TB (D_SAFE=1.5),
each at the (R,K) chosen by select_drsafe_t.py on the separate tuning seeds 6000-6029.
"""
import json, os, time, sys
import drsafe_lib as L
import ABACO_safety_pred as P

sel = json.load(open(os.path.join(L.RESULTS_DIR, "drsafe_t_selected.json")))["selected"]
OUT = os.path.join(L.RESULTS_DIR, "main_new_arms.json")
ck = L.load_ckpt(OUT, {"meta": dict(selected=sel, seeds="10000-10299"), "runs": {}})
runs = ck["runs"]
t0 = time.time()
n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
for i in range(n):
    s = 10000 + i
    rec = runs.setdefault(str(s), {})
    if "HBP" not in rec: rec["HBP"] = L._flat(P.run_abaco_safety_pred(L.GRID, s, mode="hb"), L.base)
    for name, d in (("TA", "1.0"), ("TB", "1.5")):
        if name not in rec:
            p = sel[d]
            rec[name] = L._flat(P.run_abaco_safety_pred(L.GRID, s, d_safe=p["d_safe"], R=p["R"], K=p["K"]), L.base)
    L.save_ckpt(OUT, ck)
    if (i + 1) % 10 == 0:
        print(s, f"{i+1}/{n} {time.time()-t0:.0f}s", flush=True)
print("complete")
