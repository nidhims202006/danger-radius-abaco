"""analyze_ablation.py -- component ablation of DR-SAFE (main environment, N=300, seeds 10000-10299).
Full DR-SAFE (TA/TB) vs soft-cost-only (SOFT) and floor-only (F10/F15); all with time-aligned prediction, R=4.5, K=2.0.
Primary family (Holm over 8): {collisions, turns} x {full(1.0) vs SOFT, full(1.0) vs F10, full(1.5) vs SOFT, full(1.5) vs F15}."""
import json, os
import numpy as np
import drsafe_lib as L
from analyze_confirmatory import paired_stats, holm

R = L.RESULTS_DIR
ab = json.load(open(os.path.join(R, "ablation_main.json")))["runs"]
new = json.load(open(os.path.join(R, "main_new_arms.json")))["runs"]
old = json.load(open(os.path.join(R, "confirmatory_perrun.json")))["runs"]
src = {"HB": lambda s: old[s]["HB"], "HBP": lambda s: new[s]["HBP"], "SOFT": lambda s: ab[s]["SOFT"], "F10": lambda s: ab[s]["F10"],
       "F15": lambda s: ab[s]["F15"], "FULL1.0": lambda s: new[s]["TA"], "FULL1.5": lambda s: new[s]["TB"]}
seeds = sorted(ab, key=int)
ok = [s for s in seeds if all(src[a](s)["ok"] for a in src)]
print(f"seeds {len(seeds)}, all-arms-successful {len(ok)}")
g = lambda a, k: np.array([src[a](s)[k] for s in ok], float)
print(f"\n{'arm':8} {'len':>7} {'turns':>7} {'clear':>7} {'coll/run':>9} {'runs>=1':>8} {'fb/run':>8}")
for a in src:
    c = g(a, "coll")
    print(f"{a:8} {g(a,'len').mean():7.2f} {g(a,'turns').mean():7.2f} {g(a,'clear').mean():7.3f} {c.mean():9.3f} {int((c>0).sum()):8d} {g(a,'fb').mean():8.0f}")
fam = [(m, f, r) for f, r in (("FULL1.0", "SOFT"), ("FULL1.0", "F10"), ("FULL1.5", "SOFT"), ("FULL1.5", "F15")) for m in ("coll", "turns")]
st = [paired_stats(g(r, m), g(f, m)) for m, f, r in fam]
adj = holm(np.array([s["p_wilcoxon"] for s in st]))
out = {"n": len(ok), "primary": {}, "secondary": {}}
print("\nPRIMARY (full - ablated; negative favours full DR-SAFE; Holm over 8):")
for (m, f, r), s, a in zip(fam, st, adj):
    out["primary"][f"{m}|{f}|{r}"] = dict(s, p_holm=float(a))
    print(f"  {m:5} {f} - {r:5}: {s['diff']:+.3f} [{s['diff_ci'][0]:+.3f},{s['diff_ci'][1]:+.3f}] d_z {s['dz']:.2f} p_W {s['p_wilcoxon']:.4f} p_Holm {a:.4f}")
print("\nSECONDARY (unadjusted): length / clearance, ablated arms vs HBP and full vs ablated")
for f, r in (("FULL1.0", "SOFT"), ("FULL1.0", "F10"), ("FULL1.5", "SOFT"), ("FULL1.5", "F15"), ("SOFT", "HBP"), ("F10", "HBP"), ("F15", "HBP")):
    for m in ("len", "clear", "turns", "coll"):
        s = paired_stats(g(r, m), g(f, m)); out["secondary"][f"{m}|{f}|{r}"] = s
    print(f"  {f:8} - {r:5}: len {out['secondary'][f'len|{f}|{r}']['diff']:+.2f} (p {out['secondary'][f'len|{f}|{r}']['p_wilcoxon']:.3f}) | clear {out['secondary'][f'clear|{f}|{r}']['diff']:+.2f} | turns {out['secondary'][f'turns|{f}|{r}']['diff']:+.2f} (p {out['secondary'][f'turns|{f}|{r}']['p_wilcoxon']:.3f}) | coll {out['secondary'][f'coll|{f}|{r}']['diff']:+.3f} (p {out['secondary'][f'coll|{f}|{r}']['p_wilcoxon']:.3f})")
json.dump(out, open(os.path.join(R, "ablation_summary.json"), "w"), indent=2)
