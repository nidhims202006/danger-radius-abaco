"""
make_figures_progression.py -- Figures 3 and 7: path progression of DR-SAFE and the APF-style baseline in the main environment.
Same run layout as the original DR progression figure (iterations 25/50/75/100; best path so far in blue, obstacles in magenta).
Time alignment is drawn explicitly: for the best path shown, each obstacle is drawn where it will be when the path reaches its closest waypoint
(step i*: obstacle position traj[conv + i*], the position the DR-SAFE cost is evaluated at); gold = soft-cost zone (d < R), red outline = hard floor (d < D_SAFE),
dotted black line = link from the path waypoint to the obstacle position at that step.
Run selection rule (declared here, before looking at the pictures): the first seed >= 20000 for which the DR-SAFE (D_SAFE = 1.5) winning path
passes within R = 4.5 of an obstacle at its aligned time; the APF-style baseline is run on the same seed. Illustration only; not a representative sample.
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import drsafe_lib as L
import ABACO_safety_pred as P
sys.path.insert(0, os.path.join(L.ROOT, "experiments"))
import generate_paper_figures as G

base = L.base; R_ZONE, D_SAFE = 4.5, 1.5
def conv_of(snaps, t):
    best = snaps[t - 1]["best"]
    for k, s in enumerate(snaps):
        if s["best"] == best: return k + 1
    return t
def closest(path, trajs, c):
    out = []
    for tj in trajs:
        dmin, imin = 1e9, 0
        for i, cell in enumerate(path):
            pos = tj[min(c + i, len(tj) - 1)]; dd = base.dist(cell, pos)
            if dd < dmin: dmin, imin = dd, i
        out.append((dmin, imin, tj[min(c + imin, len(tj) - 1)]))
    return out
def panel(ax, grid, snaps, trajs, t, floor):
    snap = snaps[t - 1]; path = snap["best"]; c = conv_of(snaps, t)
    G.draw_grid(ax, grid)
    for tj, (dm, im, pos) in zip(trajs, closest(path, trajs, c)):
        for br in range(G.GRID_SIZE):
            for bc in range(G.GRID_SIZE):
                d = base.dist((br, bc), pos)
                if d < R_ZONE: ax.add_patch(mpatches.Rectangle((bc, br), 1, 1, color="gold", alpha=0.25, ec="none"))
                if floor and d < D_SAFE: ax.add_patch(mpatches.Rectangle((bc, br), 1, 1, fill=False, ec="red", lw=1.1, zorder=6))
        ax.scatter(pos[1] + 0.5, pos[0] + 0.5, c="magenta", s=90, marker="D", edgecolors="black", linewidths=0.8, zorder=8)
        cell = path[im]; ax.plot([cell[1] + 0.5, pos[1] + 0.5], [cell[0] + 0.5, pos[0] + 0.5], color="black", lw=0.8, ls=":", zorder=7)
        ax.text(pos[1] + 0.9, pos[0] - 0.1, f"step {im}", fontsize=7, zorder=9)
    for dp in snap["dyn"]:
        ax.scatter(dp[1] + 0.5, dp[0] + 0.5, c="magenta", s=45, marker="s", edgecolors="black", linewidths=0.6, alpha=0.55, zorder=7)
    G.draw_path(ax, path, "#1f77b4", lw=2.2); G.draw_start_goal(ax)
    ax.set_title(f"Iteration {t}/100", fontsize=11)
def figure(res, title, fname, floor):
    fig, axes = plt.subplots(2, 2, figsize=(11, 11))
    trajs = [o.traj for o in res["dyn_obs"]]
    for ax, t in zip(axes.ravel(), (25, 50, 75, 100)): panel(ax, L.GRID, res["snapshots"], trajs, t, floor)
    fig.suptitle(title, y=0.995); fig.tight_layout(rect=[0, 0, 1, 0.97]); fig.savefig(os.path.join(L.FIG_DIR, fname), dpi=150); plt.close(fig)

seed = None
for s in range(20000, 20100):
    r = P.run_abaco_safety_pred(L.GRID, s, d_safe=1.5, R=4.5, K=2.0)
    c = conv_of(r["snapshots"], 100)
    if min(x[0] for x in closest(r["best_path"], [o.traj for o in r["dyn_obs"]], c)) < R_ZONE: seed, res_t = s, r; break
print("seed", seed, "collisions", res_t["collisions"], "clearance", round(res_t["min_clearance"], 2), "fallbacks", res_t["safety_fallback_count"])
figure(res_t, "DR-SAFE (D_SAFE = 1.5) path progression: time-aligned soft zone (gold) and hard floor (red) around each obstacle", "Figure16_drsafe_progression.png", True)
res_a = P.run_abaco_safety_pred(L.GRID, seed, R=4.5, K=2.0, mode="apf")
print("APF-style: collisions", res_a["collisions"], "clearance", round(res_a["min_clearance"], 2))
fig, axes = plt.subplots(1, 2, figsize=(15, 7.6))
for ax, res, ttl, floor in ((axes[0], res_a, "APF-style baseline (repulsive cost, predicted positions)", False), (axes[1], res_t, "DR-SAFE (D_SAFE = 1.5)", True)):
    panel(ax, L.GRID, res["snapshots"], [o.traj for o in res["dyn_obs"]], 100, floor); ax.set_title(f"{ttl}, iteration 100/100", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(L.FIG_DIR, "Figure17_apf_vs_drsafe.png"), dpi=150); plt.close(fig)
import os as _os
_p = _os.path.join(L.FIG_DIR, "Figure17_apf_progression.png")
if _os.path.exists(_p): _os.remove(_p)
json.dump(dict(seed=seed, drsafe=dict(collisions=res_t["collisions"], clearance=res_t["min_clearance"], turns=res_t["sharp_turns"], length=res_t["best_distance"], fallbacks=res_t["safety_fallback_count"]),
               apf=dict(collisions=res_a["collisions"], clearance=res_a["min_clearance"], turns=res_a["sharp_turns"], length=res_a["best_distance"])), open(os.path.join(L.RESULTS_DIR, "progression_run.json"), "w"), indent=1, default=float)
