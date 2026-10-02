"""analyze_start_cell_coprimary.py -- see docs/START_CELL_ANALYSIS_PLAN.md. Writes results/start_cell_coprimary.json."""
import json, os
import numpy as np
import drsafe_lib as L
from analyze_confirmatory import paired_stats, holm

R = L.RESULTS_DIR
dn = json.load(open(R + "/main_new_arms.json"))["runs"]; do = json.load(open(R + "/confirmatory_perrun.json"))["runs"]; fr = json.load(open(R + "/fresh_main.json"))["runs"]
blocks = {"development": ({"HB": lambda s: do[s]["HB"], "HBP": lambda s: dn[s]["HBP"], "TA": lambda s: dn[s]["TA"], "TB": lambda s: dn[s]["TB"]}, sorted(dn, key=int)),
          "confirmation": ({a: (lambda s, a=a: fr[s][a]) for a in ("HB", "HBP", "TA", "TB")}, sorted(fr, key=int))}
_c = {}
def n_start(conv):
    if conv not in _c:
        real = L.real_obstacles_at(conv)
        _c[conv] = sum(L.base.dist((0, 0), o.traj[min(conv, len(o.traj) - 1)]) < 0.5 for o in real)
    return _c[conv]
out = {"D1": {}, "C": {}, "S1": {}}
data = {}
for b, (get, seeds) in blocks.items():
    data[b] = {}
    for a in ("HB", "HBP", "TA", "TB"):
        coll = np.array([get[a](s)["coll"] for s in seeds], float); conv = np.array([get[a](s)["conv"] for s in seeds])
        st = np.array([n_start(int(c)) for c in conv])
        data[b][a] = dict(coll=coll, st=st, adj=coll - st, conv=conv)
    print(f"\n[{b}] N={len(seeds)}  arm: mean conv | runs with obstacle on start cell at conv | start events | raw coll | start-excluded coll")
    out["D1"][b] = {}
    for a in ("HB", "HBP", "TA", "TB"):
        x = data[b][a]; out["D1"][b][a] = dict(conv=float(x["conv"].mean()), runs_start=int((x["st"] > 0).sum()), start_events=int(x["st"].sum()), coll=float(x["coll"].mean()), adj=float(x["adj"].mean()))
        o = out["D1"][b][a]; print(f"  {a:4} {o['conv']:6.1f} | {o['runs_start']:3d} | {o['start_events']:3d} | {o['coll']:.3f} | {o['adj']:.3f}")
rows = []
for b in blocks:
    for t in ("TA", "TB"):
        for ref in ("HB", "HBP"):
            rows.append((b, t, ref, paired_stats(data[b][ref]["adj"], data[b][t]["adj"])))
h = holm([r[3]["p_wilcoxon"] for r in rows])
print("\nCo-primary family C: start-excluded collisions/run, Holm over 8 (target - reference)")
for (b, t, ref, s), hp in zip(rows, h):
    s["p_holm"] = float(hp); out["C"][f"{b}|{t}-{ref}"] = s
    print(f"  {b:12} {t}-{ref:3}: {s['diff']:+.3f} [{s['diff_ci'][0]:+.3f},{s['diff_ci'][1]:+.3f}] p_W {s['p_wilcoxon']:.4f} Holm {hp:.4f}")
print("\nSensitivity S1: raw collisions on seeds where no arm has an obstacle on the start cell at its own conv (unadjusted)")
for b, (get, seeds) in blocks.items():
    keep = np.ones(len(seeds), bool)
    for a in ("HB", "HBP", "TA", "TB"):
        keep &= data[b][a]["st"] == 0
    print(f"  [{b}] retained {int(keep.sum())} of {len(seeds)} seeds; mean raw coll: " + ", ".join(f"{a} {data[b][a]['coll'][keep].mean():.3f}" for a in ("HB", "HBP", "TA", "TB")))
    out["S1"][b] = dict(n=int(keep.sum()), means={a: float(data[b][a]["coll"][keep].mean()) for a in ("HB", "HBP", "TA", "TB")})
    for t in ("TA", "TB"):
        for ref in ("HB", "HBP"):
            s = paired_stats(data[b][ref]["coll"][keep], data[b][t]["coll"][keep]); out["S1"][b][f"{t}-{ref}"] = s
            print(f"     {t}-{ref:3}: {s['diff']:+.3f} [{s['diff_ci'][0]:+.3f},{s['diff_ci'][1]:+.3f}] p_W {s['p_wilcoxon']:.4f}")
json.dump(out, open(R + "/start_cell_coprimary.json", "w"), indent=1, default=float)
