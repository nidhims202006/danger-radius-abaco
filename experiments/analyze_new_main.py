"""
analyze_new_main.py -- FROZEN analysis of the N=300 main-environment confirmatory run.

Merges results/confirmatory_perrun.json (HB, DR, DRS-old; seeds 10000-10299) with
results/main_new_arms.json (HBP, TA=DR-SAFE-T D_SAFE 1.0, TB=DR-SAFE-T D_SAFE 1.5).
Primary family (Holm over 8): {collisions, sharp turns} x {TA, TB} x {vs HB, vs HBP}, Wilcoxon signed-rank.
Success rule per variant: collisions reduced vs BOTH HB and HBP (Holm p < 0.05, negative diff) AND the
95% CI upper bound of (turns_T - turns_DR) <= 0.5 turns.
"""
import json, os
import numpy as np
import drsafe_lib as L
from analyze_confirmatory import paired_stats, holm, mcnemar_exact

old = json.load(open(os.path.join(L.RESULTS_DIR, "confirmatory_perrun.json")))["runs"]
new = json.load(open(os.path.join(L.RESULTS_DIR, "main_new_arms.json")))["runs"]
seeds = [s for s in sorted(new, key=int) if s in old and all(a in new[s] for a in ("HBP", "TA", "TB"))]
arms = {"HB": old, "DR": old, "DRS": old, "HBP": new, "TA": new, "TB": new}
ok = [s for s in seeds if all(arms[a][s][a]["ok"] for a in arms)]
print(f"seeds available {len(seeds)}, all-arms-successful {len(ok)}")
g = lambda a, k: np.array([arms[a][s][a][k] for s in ok], float)

print(f"\n{'arm':5} {'len':>7} {'turns':>7} {'clear':>7} {'coll/run':>9} {'events':>7} {'runs>=1':>8} {'fb/run':>8}")
for a in ("HB", "HBP", "DR", "DRS", "TA", "TB"):
    c = g(a, "coll")
    print(f"{a:5} {g(a,'len').mean():7.2f} {g(a,'turns').mean():7.2f} {g(a,'clear').mean():7.3f} {c.mean():9.3f} {int(c.sum()):7d} {int((c>0).sum()):8d} {g(a,'fb').mean():8.0f}")

res = {"n": len(ok), "primary": {}, "secondary": {}}
fam = [(m, t, r) for t in ("TA", "TB") for m in ("coll", "turns") for r in ("HB", "HBP")]
stats_ = [paired_stats(g(r, m), g(t, m)) for m, t, r in fam]
adj = holm(np.array([s["p_wilcoxon"] for s in stats_]))
print("\nPRIMARY (Wilcoxon, Holm over 8):")
print(f"{'metric':6} {'contrast':10} {'mean ref':>9} {'mean T':>8} {'diff [95% CI]':>24} {'d_z':>6} {'p_W':>8} {'p_Holm':>8}")
for (m, t, r), s, a in zip(fam, stats_, adj):
    res["primary"][f"{m}|{t}|{r}"] = dict(s, p_holm=float(a))
    print(f"{m:6} {t+' vs '+r:10} {s['mean_x']:9.3f} {s['mean_y']:8.3f} {s['diff']:7.3f} [{s['diff_ci'][0]:6.3f},{s['diff_ci'][1]:6.3f}] {s['dz']:6.2f} {s['p_wilcoxon']:8.4f} {a:8.4f}")

print("\nSUCCESS RULE:")
for t in ("TA", "TB"):
    cvs = [res["primary"][f"coll|{t}|{r}"] for r in ("HB", "HBP")]
    coll_ok = all(c["p_holm"] < 0.05 and c["diff"] < 0 for c in cvs)
    tr = paired_stats(g("DR", "turns"), g(t, "turns"))
    turn_ok = tr["diff_ci"][1] <= 0.5
    res["secondary"][f"turns_{t}_minus_DR"] = tr
    res[f"success_{t}"] = dict(collisions_reduced_vs_HB_and_HBP=bool(coll_ok), turns_within_margin_of_DR=bool(turn_ok), overall=bool(coll_ok and turn_ok))
    print(f"  {t}: collisions reduced vs HB & HBP: {coll_ok} | turns - DR = {tr['diff']:+.3f} [{tr['diff_ci'][0]:.3f},{tr['diff_ci'][1]:.3f}] within 0.5: {turn_ok} -> {'SUCCESS' if coll_ok and turn_ok else 'NOT MET'}")

print("\nSECONDARY (uncorrected):")
for t in ("TA", "TB"):
    for r in ("HB", "HBP", "DR", "DRS"):
        for m in ("len", "turns", "clear", "coll"):
            s = paired_stats(g(r, m), g(t, m)); res["secondary"][f"{m}|{t}|{r}"] = s
            print(f"  {t} vs {r:3} {m:5} diff {s['diff']:8.3f} [{s['diff_ci'][0]:7.3f},{s['diff_ci'][1]:7.3f}] d_z {s['dz']:5.2f} p_W {s['p_wilcoxon']:.4f}")
print("\nAny-collision McNemar (ref-only, T-only, p):")
for t in ("TA", "TB"):
    for r in ("HB", "HBP"):
        n10, n01, p = mcnemar_exact(g(r, "coll"), g(t, "coll")); res["secondary"][f"mcnemar|{t}|{r}"] = dict(ref_only=n10, t_only=n01, p=p)
        print(f"  {t} vs {r:3}: {r}-only={n10} {t}-only={n01} p={p:.4f}")
json.dump(res, open(os.path.join(L.RESULTS_DIR, "main_new_summary.json"), "w"), indent=2)
print("\nsaved results/main_new_summary.json")
