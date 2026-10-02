"""analyze_soft_primary.py -- evidence for the v22 positioning of the paper around the time-aligned SOFT cost (DR-T).

Background: the component ablation (Tables 9-10, 13) shows the hard floor adds nothing detectable with exact estimates, so the paper
presents the soft time-aligned cost alone ("soft cost only (no floor)", arm SOFT) as the proposed method (DR-T) and DR-SAFE (= DR-T +
floor) as an extension. The pre-specified primary families in Tables 4 and 14 were about DR-SAFE, not SOFT. This script therefore gives
the corresponding comparisons for SOFT and they are POST HOC (SOFT was a declared arm of the confirmation protocol, but SOFT-vs-HB and
SOFT-vs-HBP were not among the declared comparisons; on the development block SOFT was added after the design was informed by those seeds).

Family (Holm over 8): {collisions/run, sharp turns} x {SOFT - HB, SOFT - HBP} x {development block 10000-10299, confirmation block 20000-20299}.
Secondary, unadjusted: path length and minimum clearance for the same four contrasts.
Writes results/soft_primary_summary.json (used for Table C.1 / Appendix C of the paper).
"""
import json, os
import numpy as np
import drsafe_lib as L
from analyze_confirmatory import paired_stats, holm

R = L.RESULTS_DIR
J = lambda f: json.load(open(os.path.join(R, f)))["runs"]
ab, new, old, fr = J("ablation_main.json"), J("main_new_arms.json"), J("confirmatory_perrun.json"), J("fresh_main.json")
BLOCKS = {
    "development": dict(seeds=sorted(ab, key=int),
                        get={"HB": lambda s: old[s]["HB"], "HBP": lambda s: new[s]["HBP"], "SOFT": lambda s: ab[s]["SOFT"]}),
    "confirmation": dict(seeds=sorted(fr, key=int),
                         get={a: (lambda s, a=a: fr[s][a]) for a in ("HB", "HBP", "SOFT")}),
}
out = {"family": {}, "secondary": {}, "means": {}, "n": {}}
rows = []
for blk, B in BLOCKS.items():
    ok = [s for s in B["seeds"] if all(B["get"][a](s)["ok"] for a in B["get"])]
    out["n"][blk] = len(ok)
    g = lambda a, k: np.array([B["get"][a](s)[k] for s in ok], float)
    out["means"][blk] = {a: {k: float(g(a, k).mean()) for k in ("len", "turns", "clear", "coll")} for a in B["get"]}
    for ref in ("HB", "HBP"):
        for m in ("coll", "turns"):
            rows.append((blk, ref, m, paired_stats(g(ref, m), g("SOFT", m))))
        for m in ("len", "clear"):
            out["secondary"][f"{blk}|SOFT-{ref}|{m}"] = paired_stats(g(ref, m), g("SOFT", m))
h = holm([r[3]["p_wilcoxon"] for r in rows])
print(f"n per block: {out['n']}")
for blk, m_ in out["means"].items():
    print(blk, {a: {k: round(v, 3) for k, v in d.items()} for a, d in m_.items()})
print("\nPOST HOC family (SOFT minus reference; negative favours SOFT; Holm over 8)")
for (blk, ref, m, s), hp in zip(rows, h):
    s["p_holm"] = float(hp)
    out["family"][f"{blk}|{m}|SOFT-{ref}"] = s
    print(f"  {blk:12} {m:5} SOFT-{ref:3}: {s['diff']:+.3f} [{s['diff_ci'][0]:+.3f},{s['diff_ci'][1]:+.3f}] d_z {s['dz']:+.2f} p_W {s['p_wilcoxon']:.4f} Holm {hp:.4f}")
print("\nSecondary (unadjusted)")
for k, s in out["secondary"].items():
    print(f"  {k:32} {s['diff']:+.3f} [{s['diff_ci'][0]:+.3f},{s['diff_ci'][1]:+.3f}] p_W {s['p_wilcoxon']:.4f}")
json.dump(out, open(os.path.join(R, "soft_primary_summary.json"), "w"), indent=1, default=float)
print("\nsaved results/soft_primary_summary.json")
