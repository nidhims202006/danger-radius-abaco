"""
analyze_confirmatory.py -- paired analysis of results/confirmatory_perrun.json

Pre-specified PRIMARY family (Holm-corrected, alpha = 0.05):
    C1  collisions/run : DR-SAFE vs HB
    C2  collisions/run : DR-SAFE vs DR
    C3  path length    : DR vs HB
    C4  sharp turns    : DR vs HB
SECONDARY (uncorrected, descriptive): every other metric x contrast.

Tests per contrast: paired Wilcoxon signed-rank (primary p), paired t-test,
paired effect size d_z with bootstrap 95% CI, mean paired difference with
bootstrap 95% CI. For collisions additionally: runs with >=1 collision per
arm and an exact McNemar test on that indicator.

Usage: python experiments/analyze_confirmatory.py [results/confirmatory_perrun.json] [DRS_ARM]
       DRS_ARM = DRS (paper params) or DRST (selected params); default DRST if present.
"""
import json, os, sys
import numpy as np
from scipy import stats
import drsafe_lib as L


def paired_stats(x, y, seed=3, reps=4000):
    x, y = np.asarray(x, float), np.asarray(y, float)
    d = y - x
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(reps, len(d)))
    bs = d[idx]
    mean_ci = np.percentile(bs.mean(1), [2.5, 97.5])
    sd = bs.std(1, ddof=1)
    dz_bs = np.where(sd > 0, bs.mean(1) / np.where(sd > 0, sd, 1), 0)
    dz_ci = np.percentile(dz_bs, [2.5, 97.5])
    try:
        pw = float(stats.wilcoxon(x, y, zero_method="wilcox").pvalue)
    except ValueError:
        pw = 1.0
    pt = float(stats.ttest_rel(x, y).pvalue) if d.std(ddof=1) > 0 else 1.0
    dz = float(d.mean() / d.std(ddof=1)) if d.std(ddof=1) > 0 else 0.0
    return dict(mean_x=float(x.mean()), mean_y=float(y.mean()), diff=float(d.mean()),
                diff_ci=[float(v) for v in mean_ci], dz=dz, dz_ci=[float(v) for v in dz_ci],
                p_wilcoxon=pw, p_t=pt)


def mcnemar_exact(x, y):
    a = np.asarray(x) > 0
    b = np.asarray(y) > 0
    n01 = int((~a & b).sum()); n10 = int((a & ~b).sum())
    n = n01 + n10
    p = 1.0 if n == 0 else float(stats.binomtest(n01, n, 0.5).pvalue)
    return n10, n01, p


def holm(ps):
    order = np.argsort(ps)
    adj = np.empty(len(ps))
    running = 0
    for rank, i in enumerate(order):
        running = max(running, (len(ps) - rank) * ps[i])
        adj[i] = min(1.0, running)
    return adj


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(L.RESULTS_DIR, "confirmatory_perrun.json")
    ck = json.load(open(path))
    recs_all = [ck["runs"][s] for s in sorted(ck["runs"], key=int)]
    arms_present = set.intersection(*[set(r) for r in recs_all])
    drs_arm = sys.argv[2] if len(sys.argv) > 2 else ("DRST" if "DRST" in arms_present else "DRS")
    need = ["HB", "DR", drs_arm]
    recs = [r for r in recs_all if all(r[a]["ok"] for a in need)]
    print(f"seeds complete: {len(recs_all)}; all-arms-successful: {len(recs)}; DR-SAFE arm = {drs_arm}")
    g = lambda arm, k: np.array([r[arm][k] for r in recs], float)

    print("\nArm means (N=%d):" % len(recs))
    print(f"{'arm':6} {'len':>7} {'turns':>7} {'clear':>7} {'coll/run':>9} {'events':>7} {'runs>=1':>8} {'fb/run':>8}")
    for arm in [a for a in ("HB", "DR", "DRT", "DRS", "DRST") if a in arms_present]:
        rr = [r for r in recs_all if r[arm]["ok"]]
        c = np.array([r[arm]["coll"] for r in rr])
        print(f"{arm:6} {np.mean([r[arm]['len'] for r in rr]):7.2f} {np.mean([r[arm]['turns'] for r in rr]):7.2f} "
              f"{np.mean([r[arm]['clear'] for r in rr]):7.3f} {c.mean():9.3f} {int(c.sum()):7d} {int((c>0).sum()):8d} "
              f"{np.mean([r[arm]['fb'] for r in rr]):8.0f}   (success {len(rr)}/{len(recs_all)})")

    primary = [("C1", "coll", "HB", drs_arm), ("C2", "coll", "DR", drs_arm),
               ("C3", "len", "HB", "DR"), ("C4", "turns", "HB", "DR")]
    res = {"n": len(recs), "drs_arm": drs_arm, "primary": {}, "secondary": {}}
    pv = []
    for cid, k, a, b in primary:
        s = paired_stats(g(a, k), g(b, k))
        res["primary"][cid] = dict(metric=k, a=a, b=b, **s)
        pv.append(s["p_wilcoxon"])
    for cid, adj in zip(res["primary"], holm(np.array(pv))):
        res["primary"][cid]["p_holm"] = float(adj)

    print("\nPRIMARY family (Wilcoxon, Holm-adjusted):")
    print(f"{'id':3} {'metric':6} {'contrast':14} {'mean A':>8} {'mean B':>8} {'diff [95% CI]':>24} {'d_z [95% CI]':>22} {'p_W':>8} {'p_Holm':>8}")
    for cid, r in res["primary"].items():
        print(f"{cid:3} {r['metric']:6} {r['b']+' vs '+r['a']:14} {r['mean_x']:8.3f} {r['mean_y']:8.3f} "
              f"{r['diff']:7.3f} [{r['diff_ci'][0]:6.3f},{r['diff_ci'][1]:6.3f}] "
              f"{r['dz']:6.2f} [{r['dz_ci'][0]:5.2f},{r['dz_ci'][1]:5.2f}] {r['p_wilcoxon']:8.4f} {r['p_holm']:8.4f}")

    print("\nSECONDARY (uncorrected, descriptive):")
    contrasts = [("DR", "HB"), (drs_arm, "HB"), (drs_arm, "DR")]
    if "DRS" in arms_present and drs_arm != "DRS":
        contrasts += [("DRS", "HB"), ("DRS", "DR"), (drs_arm, "DRS")]
    for b, a in contrasts:
        for k in ("len", "turns", "clear", "coll"):
            rr = [r for r in recs_all if r[a]["ok"] and r[b]["ok"]]
            s = paired_stats([r[a][k] for r in rr], [r[b][k] for r in rr])
            res["secondary"][f"{b}|{a}|{k}"] = s
            print(f"  {b:5} vs {a:3} {k:6} diff {s['diff']:8.3f} [{s['diff_ci'][0]:7.3f},{s['diff_ci'][1]:7.3f}] "
                  f"d_z {s['dz']:5.2f}  p_W {s['p_wilcoxon']:.4f}  p_t {s['p_t']:.4f}")
    print("\nAny-collision indicator, exact McNemar (n_A-only, n_B-only, p):")
    res["mcnemar"] = {}
    for a, b in [("HB", drs_arm), ("DR", drs_arm), ("HB", "DR")]:
        n10, n01, p = mcnemar_exact(g(a, "coll"), g(b, "coll"))
        res["mcnemar"][f"{a}|{b}"] = dict(a_only=n10, b_only=n01, p=p)
        print(f"  {a:3} vs {b:5}: {a}-only={n10:3d}  {b}-only={n01:3d}  p={p:.4f}")
    json.dump(res, open(os.path.join(L.RESULTS_DIR, "confirmatory_summary.json"), "w"), indent=2)
    print("\nsaved results/confirmatory_summary.json")


if __name__ == "__main__":
    main()
