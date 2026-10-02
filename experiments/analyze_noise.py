"""
analyze_noise.py -- fair noisy-estimate comparisons.
(a) Suite (36 scenarios, scenario means): results/suite_results.json + results/suite_added.json.
(b) Main environment, seeds 20000-20099: results/fresh_main.json (clean arms) + results/fresh_noise.json (noisy arms).
Primary family for each part (Holm over 8): {collisions, turns} x {TA_n, TB_n, SOFT_n, APFP_n} vs NOISY HBP (HBP_n).
Also reported (unadjusted): each noisy arm vs its own clean arm, vs HB, vs clean HBP.
Writes results/noise_summary.json.
"""
import json, os
import numpy as np
import drsafe_lib as L
from analyze_confirmatory import paired_stats, holm

R = L.RESULTS_DIR
out = {}

def compare(name, get, units, noisy=("TA_n", "TB_n", "SOFT_n", "APFP_n")):
    arms = ["HB", "HBP", "HBP_n"] + [a for a in ("TA", "TB", "SOFT", "APFP") if a] + list(noisy)
    print(f"\n=== {name} (n = {len(units)}) ===")
    print(f"{'arm':7} {'len':>6} {'turns':>6} {'clear':>6} {'coll/run':>8} {'fb/run':>8}")
    res = {"arms": {}}
    for a in arms:
        try:
            v = {m: np.array([get(u, a, m) for u in units], float) for m in ("len", "turns", "clear", "coll", "fb")}
        except KeyError:
            continue
        res["arms"][a] = {m: float(np.nanmean(x)) for m, x in v.items()}
        r = res["arms"][a]; print(f"{a:7} {r['len']:6.2f} {r['turns']:6.2f} {r['clear']:6.3f} {r['coll']:8.3f} {r['fb']:8.1f}")
    x = lambda a, m: np.array([get(u, a, m) for u in units], float)
    def fam(refname, ref, targets, label):
        rows = []
        for t in targets:
            if t not in res["arms"] or ref not in res["arms"]:
                continue
            for m in ("coll", "turns"):
                a_, b_ = x(ref, m), x(t, m); k = ~(np.isnan(a_) | np.isnan(b_))
                rows.append((m, t, paired_stats(a_[k], b_[k])))
        if not rows:
            return
        h = holm([r[2]["p_wilcoxon"] for r in rows])
        print(f"  {label}: target - {refname} (Holm over {len(rows)})")
        for (m, t, s), hp in zip(rows, h):
            s["p_holm"] = float(hp)
            print(f"    {m:5} {t:7}-{refname}: {s['diff']:+8.3f} [{s['diff_ci'][0]:+.3f},{s['diff_ci'][1]:+.3f}] d_z {s['dz']:+.2f} p_W {s['p_wilcoxon']:.4f} Holm {hp:.4f}")
            res.setdefault(label, {})[f"{m}|{t}-{refname}"] = s
    fam("HBP_n", "HBP_n", list(noisy), "PRIMARY (noisy vs noisy HBP)")
    fam("HB", "HB", list(noisy), "vs HB")
    fam("HBP", "HBP", list(noisy), "vs clean HBP")
    for a in ("TA", "TB", "SOFT", "APFP"):
        if a + "_n" in res["arms"] and a in res["arms"]:
            fam(a, a, [a + "_n"], f"own clean arm ({a})")
    out[name] = res

# (a) suite
old = json.load(open(os.path.join(R, "suite_results.json")))["runs"]
add = json.load(open(os.path.join(R, "suite_added.json")))["runs"] if os.path.exists(os.path.join(R, "suite_added.json")) else {}
NS = 5
def suite_get(sid, a, m):
    src = old if a in ("HB", "HBP", "DR", "TA", "TB", "TA_n", "TB_n") else add
    v = [src[f"{sid}|{j}"][a][m] for j in range(NS) if src[f"{sid}|{j}"][a]["ok"]]
    return np.mean(v) if v else np.nan
sids = [s for s in range(36) if all(f"{s}|{j}" in add and all(a in add[f"{s}|{j}"] for a in ("SOFT", "SOFT_n", "HBP_n", "APFP", "APFP_n")) for j in range(NS))]
succ = {a: np.mean([(old if a in ("TA_n", "TB_n") else add)[f"{s}|{j}"][a]["ok"] for s in sids for j in range(NS)]) for a in ("TA_n", "TB_n", "SOFT_n", "HBP_n", "APFP_n")}
print("suite scenarios complete:", len(sids), "| success rates:", {k: round(float(v), 3) for k, v in succ.items()})
compare("suite", suite_get, sids)

# (b) main environment, first 100 fresh seeds
mp, npth = os.path.join(R, "fresh_main.json"), os.path.join(R, "fresh_noise.json")
if os.path.exists(npth):
    cm, cn = json.load(open(mp))["runs"], json.load(open(npth))["runs"]
    seeds = [s for s in sorted(cn, key=int) if all(a in cn[s] for a in ("TA_n", "TB_n", "HBP_n", "SOFT_n", "APFP_n"))]
    def main_get(s, a, m):
        src = cn if a.endswith("_n") else cm
        r = src[s][a]
        return r[m] if r["ok"] else np.nan
    compare("main_env_first100", main_get, seeds)
json.dump(out, open(os.path.join(R, "noise_summary.json"), "w"), indent=1, default=float)
