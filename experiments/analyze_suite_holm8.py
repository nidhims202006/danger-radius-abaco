"""analyze_suite_holm8.py -- randomized suite with HBP added to the Holm family: {collisions, sharp turns} x {DR-SAFE 1.0, 1.5} x {HB, HBP},
scenario means (36 scenarios), Wilcoxon signed-rank, Holm over 8. Also exact McNemar on any-collision for the development block.
Usage: python analyze_suite_holm8.py [n_seeds_per_scenario=10]
  Paper (v22 freeze): exact-estimate arms use 10 seeds per scenario (Tables 5-6); the noisy-estimate sub-study (Tables 7-8) stays at
  its protocol-fixed 5 seeds. Pass 5 to reproduce the earlier 5-seed version of Table 6 (kept as a sensitivity check).
Writes results/suite_holm8.json (10 seeds) or results/suite_holm8_5seeds.json (any other value)."""
import json, os, sys
import numpy as np
import drsafe_lib as L
from analyze_confirmatory import paired_stats, holm, mcnemar_exact
R = L.RESULTS_DIR
NS = int(sys.argv[1]) if len(sys.argv) > 1 else 10
old = json.load(open(R + "/suite_results.json"))["runs"]
def sm(a, m):
    return np.array([np.mean([old[f"{s}|{j}"][a][m] for j in range(NS) if old[f"{s}|{j}"][a]["ok"]]) for s in range(36)])
out = {"suite": {}, "mcnemar_dev": {}}
rows = []
for t in ("TA", "TB"):
    for ref in ("HB", "HBP"):
        for m in ("coll", "turns"):
            rows.append((m, t, ref, paired_stats(sm(ref, m), sm(t, m))))
h = holm([r[3]["p_wilcoxon"] for r in rows])
for (m, t, ref, s), hp in zip(rows, h):
    s["p_holm"] = float(hp); out["suite"][f"{m}|{t}-{ref}"] = s
    print(f"{m:5} {t}-{ref:3}: {s['diff']:+.3f} [{s['diff_ci'][0]:+.3f},{s['diff_ci'][1]:+.3f}] dz {s['dz']:+.2f} p_W {s['p_wilcoxon']:.4f} Holm {hp:.4f}")
dn = json.load(open(R + "/main_new_arms.json"))["runs"]; do = json.load(open(R + "/confirmatory_perrun.json"))["runs"]
seeds = sorted(dn, key=int)
get = {"HB": lambda s: do[s]["HB"]["coll"], "HBP": lambda s: dn[s]["HBP"]["coll"], "TA": lambda s: dn[s]["TA"]["coll"], "TB": lambda s: dn[s]["TB"]["coll"]}
for t in ("TA", "TB"):
    for ref in ("HB", "HBP"):
        n10, n01, p = mcnemar_exact([get[ref](s) for s in seeds], [get[t](s) for s in seeds])
        out["mcnemar_dev"][f"{t}-{ref}"] = dict(only_ref=n10, only_target=n01, p=p); print("McNemar dev", t, ref, n10, n01, round(p, 5))
out["n_seeds_per_scenario"] = NS
json.dump(out, open(R + ("/suite_holm8.json" if NS == 10 else f"/suite_holm8_{NS}seeds.json"), "w"), indent=1, default=float)
