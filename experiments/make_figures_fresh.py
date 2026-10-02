"""make_figures_fresh.py -- Figure 6 (development vs fresh-seed confirmation) and Figure 7 (noisy estimates).
Reads results/*.json only; every plotted number is a mean with a 95% bootstrap CI computed here from per-run values."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import drsafe_lib as L

R, F = L.RESULTS_DIR, L.FIG_DIR
rng = np.random.default_rng(11)
def ci(v, reps=4000):
    v = np.asarray(v, float); v = v[~np.isnan(v)]
    b = v[rng.integers(0, len(v), (reps, len(v)))].mean(1)
    return v.mean(), np.percentile(b, [2.5, 97.5])
def bars(ax, labels, series, title, ylabel):
    n = len(series); w = 0.8 / n
    for k, (name, vals) in enumerate(series.items()):
        m = [ci(v)[0] for v in vals]; lo = [ci(v)[0] - ci(v)[1][0] for v in vals]; hi = [ci(v)[1][1] - ci(v)[0] for v in vals]
        ax.bar(np.arange(len(labels)) + (k - (n - 1) / 2) * w, m, w, yerr=[lo, hi], capsize=2, label=name)
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, fontsize=8); ax.set_title(title, fontsize=10); ax.set_ylabel(ylabel)

# ---- Figure 6: development (10000-10299) vs fresh (20000-20299)
dev_new = json.load(open(os.path.join(R, "main_new_arms.json")))["runs"]; dev_old = json.load(open(os.path.join(R, "confirmatory_perrun.json")))["runs"]
dev_ab = json.load(open(os.path.join(R, "ablation_main.json")))["runs"]; fr = json.load(open(os.path.join(R, "fresh_main.json")))["runs"]
dev = {"HB": lambda s: dev_old[s]["HB"], "HBP": lambda s: dev_new[s]["HBP"], "Soft only": lambda s: dev_ab[s]["SOFT"],
       "DR-SAFE 1.0": lambda s: dev_new[s]["TA"], "DR-SAFE 1.5": lambda s: dev_new[s]["TB"]}
frk = {"HB": "HB", "HBP": "HBP", "Soft only": "SOFT", "DR-SAFE 1.0": "TA", "DR-SAFE 1.5": "TB"}
ds, fs = sorted(dev_new, key=int), sorted(fr, key=int)
labels = list(dev)
fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
for ax, m, ttl in ((axs[0], "coll", "Collisions per run"), (axs[1], "turns", "Sharp turns per run")):
    bars(ax, labels, {"development (seeds 10000-10299)": [[dev[a](s)[m] for s in ds] for a in labels],
                      "confirmation (seeds 20000-20299)": [[fr[s][frk[a]][m] for s in fs] for a in labels]}, ttl, "")
axs[0].legend(fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(F, "Figure14_fresh_confirmation.png"), dpi=200); plt.close()

if __import__("sys").argv[1:] == ["fresh"]:
    print("Figure 14 written"); raise SystemExit
# ---- Figure 7: noisy estimates (suite scenario means)
old = json.load(open(os.path.join(R, "suite_results.json")))["runs"]; add = json.load(open(os.path.join(R, "suite_added.json")))["runs"]
def sm(a, m):
    src = old if a in ("HB", "HBP", "TA", "TB", "TA_n", "TB_n") else add
    return [np.nanmean([src[f"{s}|{j}"][a][m] if src[f"{s}|{j}"][a]["ok"] else np.nan for j in range(5)]) for s in range(36)]
groups = [("HB", "HB"), ("HBP", "HBP"), ("HBP_n", "HBP noisy"), ("SOFT", "Soft"), ("SOFT_n", "Soft noisy"), ("TA", "DR-SAFE 1.0"), ("TA_n", "DR-SAFE 1.0 noisy"),
          ("TB", "DR-SAFE 1.5"), ("TB_n", "DR-SAFE 1.5 noisy"), ("APFP", "APF pred."), ("APFP_n", "APF pred. noisy")]
fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
for ax, m, ttl in ((axs[0], "coll", "Collisions per run (36 scenarios)"), (axs[1], "turns", "Sharp turns per run (36 scenarios)")):
    bars(ax, [g[1] for g in groups], {"scenario means": [sm(a, m) for a, _ in groups]}, ttl, "")
    ax.tick_params(axis="x", rotation=60)
plt.tight_layout(); plt.savefig(os.path.join(F, "Figure15_noisy_estimates_suite.png"), dpi=200); plt.close()
print("figures written")
