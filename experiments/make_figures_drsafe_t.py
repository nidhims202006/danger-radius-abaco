"""Figure 12 (paper): DR-SAFE vs baselines. (a,b) main environment N=300, (c,d) 36-scenario suite (scenario-level means).
Error bars = 95% bootstrap CI of the mean."""
import json, os
import numpy as np
import drsafe_lib as L
import matplotlib.pyplot as plt

rng = np.random.default_rng(0)
def ci(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    b = rng.choice(x, size=(3000, len(x))).mean(1)
    return x.mean(), np.percentile(b, [2.5, 97.5])

old = json.load(open(os.path.join(L.RESULTS_DIR, "confirmatory_perrun.json")))["runs"]
new = json.load(open(os.path.join(L.RESULTS_DIR, "main_new_arms.json")))["runs"]
src = {"HB": old, "HBP": new, "DR": old, "DRS": old, "TA": new, "TB": new}
seeds = sorted(new, key=int)
main = {a: {m: [src[a][s][a][m] for s in seeds] for m in ("coll", "turns")} for a in src}
labels_main = {"HB": "HB", "HBP": "HB+pred", "DR": "DR", "DRS": "Snapshot\nfloor", "TA": "DR-SAFE\nD=1.0", "TB": "DR-SAFE\nD=1.5"}

sk = json.load(open(os.path.join(L.RESULTS_DIR, "suite_results.json")))
runs, ns = sk["runs"], sk["meta"]["n_seeds"]
sids = range(36)
suite_arms = ["HB", "HBP", "DR", "TA", "TB", "TA_n", "TB_n"]
suite = {a: {m: [np.mean([runs[f"{s}|{j}"][a][m] for j in range(ns) if runs[f"{s}|{j}"][a]["ok"]]) for s in sids] for m in ("coll", "turns")} for a in suite_arms}
labels_suite = {"HB": "HB", "HBP": "HB+pred", "DR": "DR", "TA": "DR-SAFE\nD=1.0", "TB": "DR-SAFE\nD=1.5", "TA_n": "DR-SAFE D=1.0\nnoisy est.", "TB_n": "DR-SAFE D=1.5\nnoisy est."}

fig, axes = plt.subplots(2, 2, figsize=(11, 7))
for col, m, t in ((0, "coll", "Collisions per run"), (1, "turns", "Sharp turns per run")):
    for row, (data, labels, title) in enumerate(((main, labels_main, "Main environment (N=300 seeds)"), (suite, labels_suite, "36 randomized scenarios (scenario means)"))):
        ax = axes[row, col]
        arms = list(labels)
        means, los, his = [], [], []
        for a in arms:
            mu, (lo, hi) = ci(data[a][m]); means.append(mu); los.append(mu - lo); his.append(hi - mu)
        colors = ["#888", "#aaa", "#6b8fd6", "#c9503c", "#e28a2f", "#d97a6a", "#eeb46a"][:len(arms)] if row == 1 else ["#888", "#aaa", "#6b8fd6", "#b7a3d9", "#c9503c", "#e28a2f"]
        ax.bar(range(len(arms)), means, yerr=[los, his], color=colors, capsize=3)
        ax.set_xticks(range(len(arms))); ax.set_xticklabels([labels[a] for a in arms], fontsize=7)
        ax.set_title(f"{title}: {t}", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(L.FIG_DIR, "Figure12_drsafe_results.png"), dpi=150)
print("saved")

# ---------------------------------------------------------------- Figure 13: ablation + APF (main environment, N=300)
ab = json.load(open(os.path.join(L.RESULTS_DIR, "ablation_main.json")))["runs"]
ap = json.load(open(os.path.join(L.RESULTS_DIR, "apf_main.json")))["runs"]
S = sorted(new, key=int)
arms2 = {"HB": lambda s: old[s]["HB"], "HB+pred": lambda s: new[s]["HBP"], "Soft only": lambda s: ab[s]["SOFT"],
         "Floor only\nD=1.0": lambda s: ab[s]["F10"], "Floor only\nD=1.5": lambda s: ab[s]["F15"],
         "DR-SAFE\nD=1.0": lambda s: new[s]["TA"], "DR-SAFE\nD=1.5": lambda s: new[s]["TB"],
         "APF\nsnapshot": lambda s: ap[s]["APFS"], "APF\npredicted": lambda s: ap[s]["APFP"]}
groups = {"Ablation (a, b)": ["HB", "HB+pred", "Soft only", "Floor only\nD=1.0", "Floor only\nD=1.5", "DR-SAFE\nD=1.0", "DR-SAFE\nD=1.5"],
          "APF-ACO comparison (c, d)": ["HB", "HB+pred", "APF\nsnapshot", "APF\npredicted", "DR-SAFE\nD=1.0", "DR-SAFE\nD=1.5"]}
palette = {"HB": "#888", "HB+pred": "#aaa", "Soft only": "#6b8fd6", "Floor only\nD=1.0": "#b7a3d9", "Floor only\nD=1.5": "#9a86c4",
           "DR-SAFE\nD=1.0": "#c9503c", "DR-SAFE\nD=1.5": "#e28a2f", "APF\nsnapshot": "#5aa37a", "APF\npredicted": "#8cc7a1"}
fig, axes = plt.subplots(2, 2, figsize=(11, 7))
for row, (gname, arms) in enumerate(groups.items()):
    for col, (m, t) in enumerate((("coll", "Collisions per run"), ("turns", "Sharp turns per run"))):
        ax = axes[row, col]
        means, los, his = [], [], []
        for a in arms:
            mu, (lo, hi) = ci([arms2[a](s)[m] for s in S]); means.append(mu); los.append(mu - lo); his.append(hi - mu)
        ax.bar(range(len(arms)), means, yerr=[los, his], color=[palette[a] for a in arms], capsize=3)
        ax.set_xticks(range(len(arms))); ax.set_xticklabels(arms, fontsize=7)
        ax.set_title(f"{gname}: {t}", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(L.FIG_DIR, "Figure13_ablation_apf.png"), dpi=150)
print("saved figure 13")
