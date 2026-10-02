"""
power_analysis.py -- justify N for the confirmatory run from the paper's own
N=50 pilot (seeds 42..91, re-run with per-run collision counts).

Reports, for each pre-specified contrast (paired, same seeds):
  * observed paired effect size d_z and its 95% bootstrap CI
  * achieved power at N=50
  * N required for 80% / 90% power (two-sided alpha=0.05), both at the
    observed d_z and at a "shrunken" d_z/2 (pilot effects picked as
    interesting are optimistic -- winner's curse)
For the headline collision claim (DR-SAFE vs DR / HB) power is estimated by
paired bootstrap resampling of pilot seeds + Wilcoxon signed-rank at
increasing N, since collision counts are sparse and non-normal.

Usage: python experiments/power_analysis.py results/pilot_n50_perrun.json
"""
import json, os, sys
import numpy as np
from scipy import stats
import drsafe_lib as L

ALPHA = 0.05


def dz(x, y):
    d = np.asarray(y, float) - np.asarray(x, float)
    return d.mean() / d.std(ddof=1) if d.std(ddof=1) > 0 else 0.0


def power_t(dz_, n, alpha=ALPHA):
    """Power of two-sided paired t-test (noncentral t)."""
    if n < 3 or dz_ == 0:
        return alpha
    df = n - 1
    nc = abs(dz_) * np.sqrt(n)
    tc = stats.t.ppf(1 - alpha / 2, df)
    return float(1 - stats.nct.cdf(tc, df, nc) + stats.nct.cdf(-tc, df, nc))


def n_required(dz_, target, alpha=ALPHA):
    if dz_ == 0:
        return None
    for n in range(4, 20000):
        if power_t(dz_, n, alpha) >= target:
            return n
    return None


def boot_dz_ci(x, y, n=3000, seed=1):
    rng = np.random.default_rng(seed)
    d = np.asarray(y, float) - np.asarray(x, float)
    idx = rng.integers(0, len(d), size=(n, len(d)))
    bs = d[idx]
    sd = bs.std(axis=1, ddof=1)
    z = np.where(sd > 0, bs.mean(axis=1) / np.where(sd > 0, sd, 1), 0)
    return np.percentile(z, [2.5, 97.5])


def boot_power_wilcoxon(x, y, n, reps=1000, seed=2):
    rng = np.random.default_rng(seed)
    x, y = np.asarray(x, float), np.asarray(y, float)
    hits = 0
    for _ in range(reps):
        idx = rng.integers(0, len(x), size=n)
        a, b = x[idx], y[idx]
        if np.all(a == b):
            continue
        try:
            p = stats.wilcoxon(a, b, zero_method="wilcox").pvalue
        except ValueError:
            continue
        hits += p < ALPHA
    return hits / reps


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(L.RESULTS_DIR, "pilot_n50_perrun.json")
    ck = json.load(open(path))
    seeds = sorted(ck["runs"], key=int)
    recs = [ck["runs"][s] for s in seeds]
    ok = [all(r[a]["ok"] for a in ("HB", "DR", "DRS")) for r in recs]
    recs = [r for r, o in zip(recs, ok) if o]
    print(f"pilot seeds usable: {len(recs)}")
    get = lambda arm, k: np.array([r[arm][k] for r in recs], float)

    contrasts = [("DR vs HB", "HB", "DR"), ("DR-SAFE vs HB", "HB", "DRS"), ("DR-SAFE vs DR", "DR", "DRS")]
    metrics = [("turns", "sharp turns"), ("len", "path length"), ("clear", "min clearance"), ("coll", "collisions/run")]
    out = {"n_pilot": len(recs), "contrasts": {}}
    print(f"\n{'contrast':16} {'metric':14} {'mean diff':>10} {'d_z':>7} {'95% CI d_z':>17} {'pow@50':>7} {'N80':>6} {'N90':>6} {'N80(d/2)':>9}")
    for cname, a, b in contrasts:
        for k, kn in metrics:
            x, y = get(a, k), get(b, k)
            d = dz(x, y)
            lo, hi = boot_dz_ci(x, y)
            row = dict(mean_diff=float((y - x).mean()), dz=float(d), dz_ci=[float(lo), float(hi)],
                       power_at_50=power_t(d, 50), n80=n_required(d, .8), n90=n_required(d, .9),
                       n80_halved=n_required(d / 2, .8))
            out["contrasts"][f"{cname}|{k}"] = row
            print(f"{cname:16} {kn:14} {row['mean_diff']:10.3f} {d:7.2f} [{lo:6.2f},{hi:6.2f}] "
                  f"{row['power_at_50']:7.2f} {str(row['n80']):>6} {str(row['n90']):>6} {str(row['n80_halved']):>9}")

    print("\nCollision counts in the pilot (events / any-collision runs):")
    for arm in ("HB", "DR", "DRS"):
        c = get(arm, "coll")
        print(f"  {arm:4} events={int(c.sum()):3d}  runs with >=1 collision={int((c > 0).sum())}/{len(c)}")

    print("\nBootstrap power for the headline collision comparison (Wilcoxon signed-rank, alpha=.05):")
    Ns = [50, 100, 150, 200, 300, 400, 500]
    out["collision_power"] = {}
    print(f"{'N':>5} {'DRS vs DR':>10} {'DRS vs HB':>10}")
    for n in Ns:
        p1 = boot_power_wilcoxon(get("DR", "coll"), get("DRS", "coll"), n)
        p2 = boot_power_wilcoxon(get("HB", "coll"), get("DRS", "coll"), n)
        out["collision_power"][n] = dict(drs_vs_dr=p1, drs_vs_hb=p2)
        print(f"{n:5d} {p1:10.2f} {p2:10.2f}")

    json.dump(out, open(os.path.join(L.RESULTS_DIR, "power_analysis.json"), "w"), indent=2)
    print("\nsaved results/power_analysis.json")


if __name__ == "__main__":
    main()
