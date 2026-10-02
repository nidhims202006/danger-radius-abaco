"""analyze_apf_main.py -- APF-style baseline vs DR-SAFE on the main environment (N=300, seeds 10000-10299)."""
import json, os
import numpy as np
import drsafe_lib as L
from analyze_confirmatory import paired_stats, holm
R = L.RESULTS_DIR
ap = json.load(open(os.path.join(R, "apf_main.json")))["runs"]
new = json.load(open(os.path.join(R, "main_new_arms.json")))["runs"]; old = json.load(open(os.path.join(R, "confirmatory_perrun.json")))["runs"]
src = {"HB": lambda s: old[s]["HB"], "HBP": lambda s: new[s]["HBP"], "DR": lambda s: old[s]["DR"], "APFS": lambda s: ap[s]["APFS"],
       "APFP": lambda s: ap[s]["APFP"], "DRS1.0": lambda s: new[s]["TA"], "DRS1.5": lambda s: new[s]["TB"]}
seeds = [s for s in sorted(ap, key=int) if all(a in ap[s] for a in ("APFS", "APFP"))]
ok = [s for s in seeds if all(src[a](s)["ok"] for a in src)]
print(f"seeds {len(seeds)}, all-arms-successful {len(ok)}; per-arm success:", {a: round(np.mean([src[a](s)['ok'] for s in seeds]), 3) for a in ('APFS', 'APFP')})
g = lambda a, k: np.array([src[a](s)[k] for s in ok], float)
print(f"\n{'arm':7} {'len':>7} {'turns':>7} {'clear':>7} {'coll/run':>9} {'runs>=1':>8}")
for a in src:
    c = g(a, 'coll'); print(f"{a:7} {g(a,'len').mean():7.2f} {g(a,'turns').mean():7.2f} {g(a,'clear').mean():7.3f} {c.mean():9.3f} {int((c>0).sum()):8d}")
fam = [(m, d, a) for d in ("DRS1.0", "DRS1.5") for a in ("APFS", "APFP") for m in ("coll", "turns")]
st = [paired_stats(g(a, m), g(d, m)) for m, d, a in fam]
adj = holm(np.array([s['p_wilcoxon'] for s in st]))
out = {"n": len(ok), "primary": {}, "secondary": {}}
print("\nPRIMARY (DR-SAFE - APF; negative favours DR-SAFE; Holm over 8):")
for (m, d, a), s, h in zip(fam, st, adj):
    out['primary'][f"{m}|{d}|{a}"] = dict(s, p_holm=float(h))
    print(f"  {m:5} {d}-{a}: {s['diff']:+.3f} [{s['diff_ci'][0]:+.3f},{s['diff_ci'][1]:+.3f}] d_z {s['dz']:.2f} p_W {s['p_wilcoxon']:.4f} p_Holm {h:.4f}")
print("\nSECONDARY (unadjusted): length, clearance")
for d in ("DRS1.0", "DRS1.5"):
    for a in ("APFS", "APFP"):
        row = []
        for m in ("len", "clear"):
            s = paired_stats(g(a, m), g(d, m)); out['secondary'][f"{m}|{d}|{a}"] = s
            row.append(f"{m} {s['diff']:+.2f} (p {s['p_wilcoxon']:.4f})")
        print(f"  {d}-{a}: " + " | ".join(row))
json.dump(out, open(os.path.join(R, "apf_main_summary.json"), "w"), indent=2)
