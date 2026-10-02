"""
analyze_suite.py -- analysis of the randomized multi-environment suite (results/suite_results.json).

Unit of analysis = SCENARIO (mean over its seeds), because runs within a scenario share the same
map and obstacle setup and are not independent. Paired Wilcoxon across scenarios; effect sizes and
bootstrap CIs on scenario-level differences. Primary (Holm over 4): {collisions, turns} x {TA, TB} vs HB.
Also reported: vs HBP and DR, noisy-prediction arms, heading-change vs constant-velocity scenarios,
and breakdowns by grid size / obstacle count.
"""
import json, os
import numpy as np
from scipy import stats
import drsafe_lib as L
from analyze_confirmatory import paired_stats, holm

ck = json.load(open(os.path.join(L.RESULTS_DIR, "suite_results.json")))
runs, scn = ck["runs"], ck["scn"]
ARMS = ["HB", "HBP", "DR", "TA", "TB", "TA_n", "TB_n"]
sids = sorted({int(k.split("|")[0]) for k in runs if all(a in runs[k] for a in ARMS)})
sids = [s for s in sids if all(all(a in runs[f"{s}|{j}"] for a in ARMS) for j in range(ck["meta"]["n_seeds"]) if f"{s}|{j}" in runs)]
print("scenarios complete:", len(sids), "of 36")

def agg(a, m, subset=None):
    out = []
    for s in (subset or sids):
        v = [runs[f"{s}|{j}"][a][m] for j in range(ck["meta"]["n_seeds"]) if f"{s}|{j}" in runs and runs[f"{s}|{j}"][a]["ok"]]
        out.append(np.mean(v) if v else np.nan)
    return np.array(out, float)

succ = {a: np.mean([runs[f"{s}|{j}"][a]["ok"] for s in sids for j in range(ck["meta"]["n_seeds"]) if f"{s}|{j}" in runs]) for a in ARMS}
print("success rate per arm:", {a: round(v, 3) for a, v in succ.items()})
print(f"\n{'arm':6} {'len':>7} {'turns':>7} {'clear':>7} {'coll/run':>9} {'fb/run':>8}")
for a in ARMS:
    print(f"{a:6} {np.nanmean(agg(a,'len')):7.2f} {np.nanmean(agg(a,'turns')):7.2f} {np.nanmean(agg(a,'clear')):7.3f} {np.nanmean(agg(a,'coll')):9.3f} {np.nanmean(agg(a,'fb')):8.0f}")

def ps(ref, t, m, subset=None):
    x, y = agg(ref, m, subset), agg(t, m, subset)
    k = ~(np.isnan(x) | np.isnan(y))
    return paired_stats(x[k], y[k]) if k.sum() >= 5 else None

res = {"n_scenarios": len(sids), "primary": {}, "other": {}}
fam = [(m, t) for t in ("TA", "TB") for m in ("coll", "turns")]
st = [ps("HB", t, m) for m, t in fam]
adj = holm(np.array([s["p_wilcoxon"] for s in st]))
print("\nPRIMARY (scenario-level, vs HB, Holm over 4):")
for (m, t), s, a in zip(fam, st, adj):
    res["primary"][f"{m}|{t}|HB"] = dict(s, p_holm=float(a))
    print(f"  {m:5} {t} vs HB  ref {s['mean_x']:.3f} T {s['mean_y']:.3f} diff {s['diff']:+.3f} [{s['diff_ci'][0]:+.3f},{s['diff_ci'][1]:+.3f}] d_z {s['dz']:.2f} p_W {s['p_wilcoxon']:.4f} p_Holm {a:.4f}")

print("\nOTHER contrasts (uncorrected):")
for t in ("TA", "TB", "TA_n", "TB_n"):
    for r in ("HB", "HBP", "DR"):
        for m in ("coll", "turns", "len", "clear"):
            s = ps(r, t, m)
            if s: res["other"][f"{m}|{t}|{r}"] = s
        c, tr = res["other"][f"coll|{t}|{r}"], res["other"][f"turns|{t}|{r}"]
        print(f"  {t:5} vs {r:3}: coll {c['diff']:+.3f} (p {c['p_wilcoxon']:.3f}) | turns {tr['diff']:+.2f} (p {tr['p_wilcoxon']:.3f}) | len {res['other'][f'len|{t}|{r}']['diff']:+.2f} | clear {res['other'][f'clear|{t}|{r}']['diff']:+.2f}")

print("\nBy scenario type (mean paired diff T - HB; collisions / turns):")
groups = {"constant-velocity only": [s for s in sids if not scn[str(s)]["hc"]], "heading-change": [s for s in sids if scn[str(s)]["hc"]]}
for n in (12, 18, 25): groups[f"grid {n}"] = [s for s in sids if scn[str(s)]["n"] == n]
for k in (1, 3, 5): groups[f"{k} dyn obs"] = [s for s in sids if scn[str(s)]["n_dyn"] == k]
for gname, sub in groups.items():
    if len(sub) < 3: continue
    row = []
    for t in ("TA", "TB", "TA_n", "TB_n"):
        c = np.nanmean(agg(t, "coll", sub) - agg("HB", "coll", sub)); tr = np.nanmean(agg(t, "turns", sub) - agg("HB", "turns", sub))
        row.append(f"{t}: {c:+.3f}/{tr:+.2f}")
    print(f"  {gname:24} (n={len(sub):2}) HB coll {np.nanmean(agg('HB','coll',sub)):.3f} | " + " | ".join(row))
json.dump(res, open(os.path.join(L.RESULTS_DIR, "suite_summary.json"), "w"), indent=2)
print("\nsaved results/suite_summary.json")
