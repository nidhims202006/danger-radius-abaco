"""make_figures_pilot.py -- Figure 3 (results/safety_experiment_results_execution_aligned_v2.json; file Figure11_safety_floor.png) and
Figure S8 (that file + results/apf_methodb_results_execution_aligned_v2.json; file Figure10_apf_comparison.png). Pilot, N = 50, seeds 42-91.
Asserts that the plotted means equal the values printed in Tables 3 and S5 of the paper."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import drsafe_lib as L
R, F = L.RESULTS_DIR, L.FIG_DIR
a = json.load(open(os.path.join(R, "safety_experiment_results_execution_aligned_v2.json"))); ap = json.load(open(os.path.join(R, "apf_methodb_results_execution_aligned_v2.json")))
m = lambda d, k: float(np.mean(d[k]))
T3 = {"HB": (13.80, 35.98, 1.589, 16), "DR": (12.16, 34.87, 1.511, 14), "DR_SAFE": (12.18, 35.12, 1.810, 8)}
for k, (t, l, c, n) in T3.items():
    assert (round(m(a[k], "turns"), 2), round(m(a[k], "len"), 2), round(m(a[k], "clear"), 3), int(np.sum(a[k]["coll"]))) == (t, l, c, n), k
assert (round(m(ap, "len"), 2), round(m(ap, "turns"), 2), round(m(ap, "clear"), 3), int(ap["coll"])) == (35.50, 12.88, 1.852, 8)
fig, axs = plt.subplots(2, 2, figsize=(8, 8)); names = ["HB", "DR", "DR + safety floor"]
for ax, (ttl, f) in zip(axs.ravel(), [("Sharp turns", lambda d: m(d, "turns")), ("Path length (m)", lambda d: m(d, "len")),
                                       ("Min clearance (cells)", lambda d: m(d, "clear")), ("Collisions (total)", lambda d: float(np.sum(d["coll"])))]):
    ax.bar(names, [f(a["HB"]), f(a["DR"]), f(a["DR_SAFE"])]); ax.set_title(ttl); ax.tick_params(axis="x", rotation=15)
fig.suptitle("Safety-floor comparison using execution-aligned metrics"); plt.tight_layout(); plt.savefig(os.path.join(F, "Figure11_safety_floor.png"), dpi=170); plt.close()
fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.2)); names = ["Hard block", "APF baseline", "Danger-radius (DR)"]
for ax, (ttl, k) in zip(axs, [("Sharp turns", "turns"), ("Path length (m)", "len"), ("Min clearance (cells)", "clear")]):
    ax.bar(names, [m(a["HB"], k), m(ap, k), m(a["DR"], k)]); ax.set_title(ttl); ax.tick_params(axis="x", rotation=15)
plt.tight_layout(); plt.savefig(os.path.join(F, "Figure10_apf_comparison.png"), dpi=200); plt.close()
print("pilot figures written; means match Tables 3 and S5")

# ---- Figure S4: per-seed pilot metrics, HB vs DR (results/pilot_n50_perrun.json; execution-aligned clearance)
from scipy import stats
pj = json.load(open(os.path.join(R, "pilot_n50_perrun.json")))["runs"]; ks = sorted(pj, key=int)
hb = {m: np.array([pj[k]["HB"][m] for k in ks], float) for m in ("len", "turns", "clear")}; dr = {m: np.array([pj[k]["DR"][m] for k in ks], float) for m in ("len", "turns", "clear")}
pw = {m: float(stats.wilcoxon(hb[m], dr[m], zero_method="wilcox").pvalue) for m in hb}
assert (round(pw["len"], 4), round(pw["turns"], 4), round(pw["clear"], 3)) == (0.0028, 0.0302, 0.707), pw    # Table S2
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2)); fig.suptitle("Hard block vs. danger-radius over 50 paired runs", y=1.03)
idx, w = np.arange(len(ks)), 0.35
for ax, (m, ttl, yl) in zip(axes, [("len", "Path length per seed", "m"), ("turns", "Sharp turns (>45°) per seed", "count"), ("clear", "Minimum clearance per seed", "cells")]):
    ax.bar(idx - w / 2, hb[m], w, color="red", label="Hard block (HB)"); ax.bar(idx + w / 2, dr[m], w, color="blue", label="Danger-radius (DR)")
    ax.set_title(f"{ttl}\nWilcoxon p={pw[m]:.4f}", fontsize=10); ax.set_xlabel("Run (seed index)"); ax.set_ylabel(yl)
axes[0].legend(fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(F, "Figure6_per_run_metrics.png"), dpi=150, bbox_inches="tight"); plt.close(fig)
print("Figure S4 written; Wilcoxon p-values match Table S2")
