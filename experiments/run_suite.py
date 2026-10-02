"""
run_suite.py -- randomized multi-environment evaluation (36 scenarios x n seeds).

Arms (same ACO seed per (scenario, j)):
  HB, HBP (hard block + prediction), DR (3.5, 2.0), TA / TB (DR-SAFE-T, D_SAFE 1.0 / 1.5, tuned R,K
  from drsafe_t_selected.json), and noisy-prediction variants TA_n / TB_n (planner's heading estimate
  error sigma = 15 deg and speed estimate error sigma = 20%, drawn once per run per obstacle).
Usage: python experiments/run_suite.py [n_seeds_per_scenario=5] [first_scenario] [last_scenario_exclusive]
"""
import json, os, sys, time
import drsafe_lib as L
import ABACO_safety_pred as P
import scenario_suite as S

NOISE = (15.0, 0.20)
sel = json.load(open(os.path.join(L.RESULTS_DIR, "drsafe_t_selected.json")))["selected"]
OUT = os.path.join(L.RESULTS_DIR, "suite_results.json")
nseed = int(sys.argv[1]) if len(sys.argv) > 1 else 5
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
hi = int(sys.argv[3]) if len(sys.argv) > 3 else S.N_SCENARIOS
ck = L.load_ckpt(OUT, {"meta": dict(noise=NOISE, selected=sel, n_seeds=nseed), "runs": {}, "scn": {}})
runs = ck["runs"]
t0 = time.time()
for sid in range(lo, hi):
    scn = S.make_scenario(sid)
    ck["scn"][str(sid)] = dict(n=scn["n"], density=scn["density"], n_dyn=scn["n_dyn"], hc=scn["heading_change"])
    with S.apply_scenario(scn) as grid:
        for j in range(nseed):
            seed = 500000 + sid * 10 + j
            rec = runs.setdefault(f"{sid}|{j}", {})
            if "HB" not in rec:  rec["HB"] = L.run_hb(seed, grid)
            if "HBP" not in rec: rec["HBP"] = L._flat(P.run_abaco_safety_pred(grid, seed, mode="hb"), L.base)
            if "DR" not in rec:  rec["DR"] = L.run_dr(seed, grid=grid)
            for name, d in (("TA", "1.0"), ("TB", "1.5")):
                p = sel[d]
                if name not in rec:
                    rec[name] = L._flat(P.run_abaco_safety_pred(grid, seed, d_safe=p["d_safe"], R=p["R"], K=p["K"]), L.base)
                if name + "_n" not in rec:
                    rec[name + "_n"] = L._flat(P.run_abaco_safety_pred(grid, seed, d_safe=p["d_safe"], R=p["R"], K=p["K"], noise=NOISE), L.base)
    L.save_ckpt(OUT, ck)
    print(f"scenario {sid} done ({scn['n']}x{scn['n']} {scn['density']} nd={scn['n_dyn']} hc={scn['heading_change']}) {time.time()-t0:.0f}s", flush=True)
print("complete")
