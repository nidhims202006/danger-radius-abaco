"""
fresh_run.py -- runner for the fresh-seed confirmation and the fair noisy-prediction experiments.
All code paths are the existing planners; nothing in abaco/, danger_radius/ or baselines/ is modified.
Parameters (R, K, D_SAFE) come from results/drsafe_t_selected.json (tuning seeds 6000-6029) and are NOT changed.

Arms (suffix _n = planner's heading/speed estimates perturbed, sigma 15 deg / 20%, drawn once per obstacle per run;
      _n1 = 5 deg / 10%; _n3 = 30 deg / 40%):
  HB, HBP (hard block + prediction), DR (3.5,2.0 snapshot), DRS (snapshot floor, 3.5,2.0,1.5), TA / TB (DR-SAFE 1.0 / 1.5),
  SOFT (time-aligned soft cost only, D_SAFE=0), F10 / F15 (floor only), APFS (APF at snapshot), APFP (APF at predicted, D0=4.5, eta=2.0)

Usage:
  python experiments/fresh_run.py main  OUT.json ARM,ARM,... FIRST_SEED LAST_SEED_EXCL
  python experiments/fresh_run.py suite OUT.json ARM,ARM,... N_SEEDS_PER_SCENARIO [FIRST_SCN LAST_SCN_EXCL]
Every run is checkpointed per seed / per scenario and resumes.
"""
import json, os, re, sys, time
import drsafe_lib as L
import ABACO_safety_pred as P
sys.path.insert(0, os.path.join(L.ROOT, "baselines"))
import ABACO_apf_baseline as apf

sel = json.load(open(os.path.join(L.RESULTS_DIR, "drsafe_t_selected.json")))["selected"]
NOISE_LEVELS = {"_n": (15.0, 0.20), "_n1": (5.0, 0.10), "_n3": (30.0, 0.40)}


def run_arm(name, grid, seed):
    m = re.match(r"^(.*?)(_n\d?)$", name)
    base_name, nz = (m.group(1), NOISE_LEVELS[m.group(2)]) if m else (name, (0.0, 0.0))
    f = lambda **kw: L._flat(P.run_abaco_safety_pred(grid, seed, noise=nz, **kw), L.base)
    if base_name == "HB":   return L.run_hb(seed, grid)
    if base_name == "DR":   return L.run_dr(seed, grid=grid)
    if base_name == "DRS":  return L.run_drs(seed, R=3.5, K=2.0, d_safe=1.5)
    if base_name == "APFS": return L._flat(apf.run_abaco_apf(grid, seed=seed), L.base)
    if base_name == "HBP":  return f(mode="hb")
    if base_name == "TA":   return f(d_safe=1.0, R=sel["1.0"]["R"], K=sel["1.0"]["K"])
    if base_name == "TB":   return f(d_safe=1.5, R=sel["1.5"]["R"], K=sel["1.5"]["K"])
    if base_name == "SOFT": return f(d_safe=0.0, R=4.5, K=2.0)
    if base_name == "F10":  return f(d_safe=1.0, R=4.5, K=0.0)
    if base_name == "F15":  return f(d_safe=1.5, R=4.5, K=0.0)
    if base_name == "APFP": return f(R=4.5, K=2.0, mode="apf")
    raise ValueError(name)


if __name__ == "__main__":
    kind, out = sys.argv[1], os.path.join(L.RESULTS_DIR, sys.argv[2])
    arms = sys.argv[3].split(",")
    t0 = time.time()
    if kind == "main":
        lo, hi = int(sys.argv[4]), int(sys.argv[5])
        ck = L.load_ckpt(out, {"meta": dict(selected=sel, noise=NOISE_LEVELS), "runs": {}})
        for i, s in enumerate(range(lo, hi)):
            rec = ck["runs"].setdefault(str(s), {})
            for a in arms:
                if a not in rec:
                    rec[a] = run_arm(a, L.GRID, s)
            L.save_ckpt(out, ck)
            if (i + 1) % 10 == 0:
                print(s, f"{i+1}/{hi-lo} {time.time()-t0:.0f}s", flush=True)
    else:
        import scenario_suite as S
        nseed = int(sys.argv[4]); lo = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        hi = int(sys.argv[6]) if len(sys.argv) > 6 else S.N_SCENARIOS
        ck = L.load_ckpt(out, {"meta": dict(selected=sel, noise=NOISE_LEVELS, n_seeds=nseed), "runs": {}})
        for sid in range(lo, hi):
            scn = S.make_scenario(sid)
            with S.apply_scenario(scn) as grid:
                for j in range(nseed):
                    seed = 500000 + sid * 10 + j
                    rec = ck["runs"].setdefault(f"{sid}|{j}", {})
                    for a in arms:
                        if a not in rec:
                            rec[a] = run_arm(a, grid, seed)
            L.save_ckpt(out, ck)
            print(f"scenario {sid} done {time.time()-t0:.0f}s", flush=True)
    print("complete")
