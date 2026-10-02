"""analyze_start_cell_adjusted.py -- sensitivity analysis: collisions EXCLUDING the start waypoint.
An obstacle occupying the start cell at the planning moment is an unavoidable 'collision' for any planner
(waypoint 0 is where the robot already is). Adjusted count = counted events - obstacles on the start cell at conv."""
import json, os
import numpy as np
import drsafe_lib as L
from analyze_confirmatory import paired_stats, holm
base = L.base; R = L.RESULTS_DIR
new = json.load(open(os.path.join(R, "main_new_arms.json")))["runs"]; old = json.load(open(os.path.join(R, "confirmatory_perrun.json")))["runs"]
ab = json.load(open(os.path.join(R, "ablation_main.json")))["runs"]
arms = {"HB": lambda s: old[s]["HB"], "HBP": lambda s: new[s]["HBP"], "DR": lambda s: old[s]["DR"], "Snapshot floor": lambda s: old[s]["DRS"],
        "DR-SAFE 1.0": lambda s: new[s]["TA"], "DR-SAFE 1.5": lambda s: new[s]["TB"], "Soft only": lambda s: ab[s]["SOFT"]}
seeds = sorted(new, key=int)
def n_start(seed, conv):
    real = L.real_obstacles_at(conv)
    return sum(base.dist((0, 0), o.traj[min(conv, len(o.traj) - 1)]) < 0.5 for o in real)
adj = {}
for n, g in arms.items():
    adj[n] = np.array([g(s)["coll"] - n_start(s, g(s)["conv"]) for s in seeds], float)
    assert adj[n].min() >= 0
print(f"{'arm':15} {'raw coll/run':>13} {'adj coll/run':>13} {'runs>=1 adj':>12}")
res = {}
for n, g in arms.items():
    raw = np.mean([g(s)["coll"] for s in seeds])
    res[n] = dict(raw=float(raw), adjusted=float(adj[n].mean()), runs_ge1=int((adj[n] > 0).sum()))
    print(f"{n:15} {raw:13.3f} {adj[n].mean():13.3f} {int((adj[n]>0).sum()):12d}")
print("\nAdjusted paired comparisons (Wilcoxon):")
for a, b in (("HB", "DR-SAFE 1.0"), ("HB", "DR-SAFE 1.5"), ("HBP", "DR-SAFE 1.0"), ("HBP", "DR-SAFE 1.5"), ("Snapshot floor", "DR-SAFE 1.0"), ("HB", "HBP")):
    s = paired_stats(adj[a], adj[b]); res[f"{b}-{a}"] = s
    print(f"  {b} - {a}: {s['diff']:+.3f} [{s['diff_ci'][0]:+.3f},{s['diff_ci'][1]:+.3f}] p_W {s['p_wilcoxon']:.4f}")
json.dump(res, open(os.path.join(R, "start_cell_adjusted.json"), "w"), indent=2)
