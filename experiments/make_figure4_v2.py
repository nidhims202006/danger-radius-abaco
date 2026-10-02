"""
Regenerates Figure 4 (main environment vs. randomized-suite comparison)
using the extended 10-seed randomized suite (results/suite_results.json).

Exact-estimate arms only (HB, HBP, DR, DR-SAFE 1.0, DR-SAFE 1.5).
Noisy-estimate variants are plotted separately (see Figure 5 / analyze_noise.py).

Usage: python3 make_figure4_v2.py
Writes: ../figures/Figure4_main_vs_suite.png
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import drsafe_lib as L

ARMS = ["HB", "HBP", "DR", "TA", "TB"]
LABELS = ["HB", "HBP", "DR", "DR-SAFE\n(1.0)", "DR-SAFE\n(1.5)"]
COLORS = ["#7f8fa6", "#4a69bd", "#95a5a6", "#e67e22", "#c0392b"]

# Main environment, Table 3 numbers (N=300 development seeds, seeds 10000-10299).
# These are unaffected by the suite extension; update by hand if Table 3 changes.
MAIN_COLL = [0.203, 0.077, 0.213, 0.050, 0.033]
MAIN_TURNS = [14.10, 13.96, 13.39, 12.51, 12.00]


def load_suite(n_seeds=10):
    ck = json.load(open(os.path.join(L.RESULTS_DIR, "suite_results.json")))
    runs = ck["runs"]
    sids = sorted({int(k.split("|")[0]) for k in runs})

    def agg(a, m):
        out = []
        for s in sids:
            v = [runs[f"{s}|{j}"][a][m] for j in range(n_seeds)
                 if f"{s}|{j}" in runs and runs[f"{s}|{j}"][a]["ok"]]
            out.append(np.mean(v))
        return np.array(out, float)

    rng = np.random.default_rng(7)

    def boot_ci(x, reps=4000):
        idx = rng.integers(0, len(x), size=(reps, len(x)))
        bs = x[idx].mean(1)
        return np.percentile(bs, [2.5, 97.5])

    out = {}
    for a in ARMS:
        coll, turns = agg(a, "coll"), agg(a, "turns")
        out[a] = dict(coll_mean=coll.mean(), coll_ci=boot_ci(coll),
                      turns_mean=turns.mean(), turns_ci=boot_ci(turns))
    return out


def main():
    suite = load_suite()
    suite_coll = [suite[a]["coll_mean"] for a in ARMS]
    suite_coll_err = [[suite[a]["coll_mean"] - suite[a]["coll_ci"][0] for a in ARMS],
                       [suite[a]["coll_ci"][1] - suite[a]["coll_mean"] for a in ARMS]]
    suite_turns = [suite[a]["turns_mean"] for a in ARMS]
    suite_turns_err = [[suite[a]["turns_mean"] - suite[a]["turns_ci"][0] for a in ARMS],
                        [suite[a]["turns_ci"][1] - suite[a]["turns_mean"] for a in ARMS]]

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))

    def bar(ax, vals, err, title, ylabel):
        x = np.arange(len(LABELS))
        ax.bar(x, vals, yerr=err, color=COLORS, capsize=3, width=0.65)
        ax.set_xticks(x); ax.set_xticklabels(LABELS, fontsize=9)
        ax.set_title(title, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)

    bar(axes[0, 0], MAIN_COLL, None, "Main environment (N=300 dev. seeds)", "Collisions / run")
    bar(axes[0, 1], MAIN_TURNS, None, "Main environment (N=300 dev. seeds)", "Sharp turns / run")
    bar(axes[1, 0], suite_coll, suite_coll_err, "Randomized suite (36 scenarios, 10 seeds)", "Collisions / run")
    bar(axes[1, 1], suite_turns, suite_turns_err, "Randomized suite (36 scenarios, 10 seeds)", "Sharp turns / run")
    fig.suptitle("Collisions and sharp turns per run: main environment vs. randomized suite", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = os.path.join(L.FIG_DIR, "Figure4_main_vs_suite.png")
    fig.savefig(out_path, dpi=300)
    print("saved", out_path)


if __name__ == "__main__":
    main()
