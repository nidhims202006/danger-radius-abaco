"""
analyze_rk_sweep.py -- turn results/rk_sweep_drsafe.json into the tuning table,
heatmaps and the (pre-declared) parameter selection.

SELECTION RULE (declared in sweep_rk_drsafe.py before any data existed):
    For each method, compute per-cell means over the tuning seeds of
    turns, length, collisions/run, clearance. Z-score each across the grid
    cells; score = z(turns) + z(length) + z(coll/run) - z(clearance);
    the lowest score wins. Equal weights, no post-hoc changes.

Also reported, because a winner picked from 24 noisy cells is optimistic:
    * Friedman omnibus test per metric (is there ANY detectable R/K effect?)
    * paired difference of every cell vs the paper's default (3.5, 2.0) with
      bootstrap 95% CI, and how many cells beat the default on the composite.
The chosen parameters are then evaluated on fresh seeds in confirmatory_run.py.
"""
import json, os, sys
import numpy as np
from scipy import stats
import drsafe_lib as L
import matplotlib.pyplot as plt

IN = os.path.join(L.RESULTS_DIR, "rk_sweep_drsafe.json")
OUT = os.path.join(L.RESULTS_DIR, "rk_sweep_summary.json")
METRICS = ["turns", "len", "coll", "clear"]


def load():
    ck = json.load(open(IN))
    meta, runs = ck["meta"], ck["runs"]
    R_GRID, K_GRID = meta["r_grid"], meta["k_grid"]
    seeds = sorted({int(k.split("|")[3]) for k in runs})
    # keep only seeds complete for every cell of every method present
    methods = sorted({k.split("|")[0] for k in runs if not k.startswith("HB")})
    full = []
    for s in seeds:
        if all(f"{m}|{R}|{K}|{s}" in runs for m in methods for R in R_GRID for K in K_GRID):
            full.append(s)
    return meta, runs, R_GRID, K_GRID, methods, full


def cell_arrays(runs, m, R, K, seeds):
    rows = [runs[f"{m}|{R}|{K}|{s}"] for s in seeds]
    out = {k: np.array([np.nan if r[k] is None else r[k] for r in rows], float)
           for k in METRICS + ["fb"]}
    out["ok"] = np.array([r["ok"] for r in rows], bool)
    return out


def boot_ci(x, n=4000, seed=0):
    rng = np.random.default_rng(seed)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return (np.nan, np.nan)
    bs = rng.choice(x, size=(n, len(x))).mean(axis=1)
    return tuple(np.percentile(bs, [2.5, 97.5]))


def main():
    meta, runs, R_GRID, K_GRID, methods, seeds = load()
    print(f"complete tuning seeds: {len(seeds)}  methods: {methods}")
    summary = {"n_seeds": len(seeds), "r_grid": R_GRID, "k_grid": K_GRID,
               "d_safe": meta["d_safe"], "methods": {}}
    default = (L.DEFAULT_R, L.DEFAULT_K)
    for m in methods:
        cells, means = {}, {}
        for R in R_GRID:
            for K in K_GRID:
                a = cell_arrays(runs, m, R, K, seeds)
                cells[(R, K)] = a
                means[(R, K)] = {k: float(np.nanmean(a[k])) for k in METRICS + ["fb"]}
                means[(R, K)]["success"] = float(a["ok"].mean())
        keys = list(cells)
        M = np.array([[means[c][k] for k in METRICS] for c in keys])
        z = (M - M.mean(0)) / np.where(M.std(0) > 0, M.std(0), 1)
        score = z[:, 0] + z[:, 1] + z[:, 2] - z[:, 3]
        best_i = int(np.argmin(score))
        best = keys[best_i]
        d_i = keys.index(default)
        # Friedman omnibus per metric (blocks = seeds, treatments = cells)
        fried = {}
        for k in METRICS:
            mat = np.array([cells[c][k] for c in keys]).T
            mat = mat[~np.isnan(mat).any(axis=1)]
            try:
                fried[k] = float(stats.friedmanchisquare(*mat.T).pvalue)
            except Exception:
                fried[k] = None
        # paired diff vs default
        vs_def = {}
        for c in keys:
            vs_def[f"{c[0]}|{c[1]}"] = {
                k: dict(diff=float(np.nanmean(cells[c][k] - cells[default][k])),
                        ci=[float(v) for v in boot_ci(cells[c][k] - cells[default][k])])
                for k in METRICS}
        n_beat = int((score < score[d_i]).sum())
        summary["methods"][m] = dict(
            cells={f"{c[0]}|{c[1]}": dict(means[c], score=float(score[i])) for i, c in enumerate(keys)},
            best=dict(R=best[0], K=best[1], score=float(score[best_i])),
            default=dict(R=default[0], K=default[1], score=float(score[d_i]),
                         rank=int((score < score[d_i]).sum()) + 1, of=len(keys)),
            cells_beating_default=n_beat, friedman_p=fried, vs_default=vs_def)

        print(f"\n=== {m} (D_SAFE={meta['d_safe']}) ===")
        print(f"{'R':>4} {'K':>4} {'turns':>7} {'len':>7} {'coll/run':>9} {'clear':>6} {'fb/run':>8} {'succ':>5} {'score':>7}")
        for i, c in enumerate(keys):
            mm = means[c]
            flag = " <- best" if i == best_i else (" <- paper default" if c == default else "")
            print(f"{c[0]:4.1f} {c[1]:4.1f} {mm['turns']:7.2f} {mm['len']:7.2f} {mm['coll']:9.3f} "
                  f"{mm['clear']:6.2f} {mm['fb']:8.0f} {mm['success']:5.2f} {score[i]:7.2f}{flag}")
        print(f"best = R {best[0]}, K {best[1]};  default rank {summary['methods'][m]['default']['rank']}/{len(keys)}; "
              f"cells beating default: {n_beat}")
        print("Friedman omnibus p:", {k: (None if v is None else round(v, 4)) for k, v in fried.items()})

        # heatmaps
        panels = [("turns", "Mean sharp turns"), ("len", "Mean path length (m)"),
                  ("coll", "Collision events / run"), ("clear", "Mean min. clearance"),
                  ("fb", "Fallback activations / run"), ("score", "Composite score (lower better)")]
        fig, axes = plt.subplots(2, 3, figsize=(12, 6.6))
        for ax, (k, title) in zip(axes.ravel(), panels):
            mat = np.array([[ (score[keys.index((R, K))] if k == "score" else means[(R, K)][k])
                              for R in R_GRID] for K in K_GRID])
            im = ax.imshow(mat, origin="lower", aspect="auto", cmap="viridis")
            ax.set_xticks(range(len(R_GRID))); ax.set_xticklabels(R_GRID)
            ax.set_yticks(range(len(K_GRID))); ax.set_yticklabels(K_GRID)
            ax.set_xlabel("R"); ax.set_ylabel("K"); ax.set_title(title, fontsize=10)
            for yi in range(len(K_GRID)):
                for xi in range(len(R_GRID)):
                    ax.text(xi, yi, f"{mat[yi, xi]:.2f}" if k != "fb" else f"{mat[yi, xi]:.0f}",
                            ha="center", va="center", color="w", fontsize=7)
            ax.plot(R_GRID.index(default[0]), K_GRID.index(default[1]), "s", mfc="none", mec="red", ms=16)
            ax.plot(R_GRID.index(best[0]), K_GRID.index(best[1]), "o", mfc="none", mec="white", ms=18)
            fig.colorbar(im, ax=ax, fraction=0.046)
        fig.suptitle(f"{m}: joint R x K sweep, {len(seeds)} paired tuning seeds, D_SAFE={meta['d_safe']} "
                     f"(red square = paper default, white circle = selected)", fontsize=10)
        fig.tight_layout()
        name = "FigureS2_rk_sweep_snapshot_floor.png" if m == "DRS" else "FigureS1_rk_sweep_dr.png"
        fig.savefig(os.path.join(L.FIG_DIR, name), dpi=150)
        plt.close(fig)

    json.dump(summary, open(OUT, "w"), indent=2)
    print("\nsaved", OUT)


if __name__ == "__main__":
    main()
