"""verify_reproduction.py -- spot-check that the CURRENT code reproduces the STORED per-run results exactly.

Every planner arm is deterministic given its seed, so a re-run must match the stored record field for field
(ok, conv, fb, len, turns, clear, coll). This samples N stored runs at random (fixed sampling seed) across all result files and re-runs them:
  main environment, development block (10000-10299): main_new_arms (HBP, TA, TB), ablation_main (SOFT, F10, F15), apf_main (APFS, APFP)
  main environment, confirmation block (20000-20299): fresh_main (HB, HBP, DR, TA, TB, SOFT, APFP); fresh_noise (TA_n, TB_n, HBP_n, SOFT_n, APFP_n)
  randomized suite: suite_results (HB, HBP, DR, TA, TB, TA_n, TB_n) and suite_added (SOFT, SOFT_n, HBP_n, APFP, APFP_n)
Usage: python experiments/verify_reproduction.py [N=12] [sampling_seed=0]   (about 4 s per run; exit code 1 on any mismatch)
It re-runs planners, so it is not part of run_all.sh --analysis-only. Use it after ANY change to abaco/, danger_radius/, baselines/ or drsafe_lib.py.
"""
import json, os, random, sys, time
import drsafe_lib as L, fresh_run as F, scenario_suite as S

R = L.RESULTS_DIR; FIELDS = ["ok", "conv", "fb", "len", "turns", "clear", "coll"]
n = int(sys.argv[1]) if len(sys.argv) > 1 else 12; rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
J = lambda f: json.load(open(os.path.join(R, f)))["runs"]
pool = []                                                       # (kind, record key, arm, stored record)
for f, arms in (("main_new_arms.json", ("HBP", "TA", "TB")), ("ablation_main.json", ("SOFT", "F10", "F15")), ("apf_main.json", ("APFS", "APFP")),
                ("confirmatory_perrun.json", ("HB", "DR")), ("fresh_main.json", ("HB", "HBP", "DR", "TA", "TB", "SOFT", "APFP")),
                ("fresh_noise.json", ("TA_n", "TB_n", "HBP_n", "SOFT_n", "APFP_n")), ("suite_results.json", ("HB", "HBP", "DR", "TA", "TB", "TA_n", "TB_n")),
                ("suite_added.json", ("SOFT", "SOFT_n", "HBP_n", "APFP", "APFP_n"))):
    runs = J(f); kind = "suite" if f.startswith("suite") else "main"
    pool += [(kind, k, a, runs[k][a], f) for k in runs for a in arms if a in runs[k]]
sample = rng.sample(pool, min(n, len(pool))); bad = 0; t0 = time.time()
for kind, key, arm, want, f in sample:
    if kind == "main": got = F.run_arm(arm, L.GRID, int(key))
    else:
        sid, j = map(int, key.split("|")); scn = S.make_scenario(sid)
        with S.apply_scenario(scn) as grid: got = F.run_arm(arm, grid, 500000 + sid * 10 + j)
    ok = all(got[k] == want[k] for k in FIELDS); bad += not ok
    print(f"{'MATCH' if ok else 'DIFF ':5} {f:26} key {key:8} arm {arm:6}" + ("" if ok else f"  got {[got[k] for k in FIELDS]} stored {[want[k] for k in FIELDS]}"), flush=True)
print(f"{len(sample)} stored runs re-run in {time.time()-t0:.0f}s; {bad} mismatches")
sys.exit(1 if bad else 0)
