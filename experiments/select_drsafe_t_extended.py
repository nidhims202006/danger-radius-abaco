"""select_drsafe_t_extended.py -- the frozen rule of select_drsafe_t.py applied to the extended grid (see sweep_drsafe_t_extend.py)."""
import json, os
import numpy as np
import drsafe_lib as L
R0 = json.load(open(os.path.join(L.RESULTS_DIR, "sweep_drsafe_t.json")))["runs"]
R1 = json.load(open(os.path.join(L.RESULTS_DIR, "sweep_drsafe_t_ext.json")))["runs"]
runs = {**R0, **R1}
seeds = [s for s in range(6000, 6030) if all(f"T|{R}|{K}|{d}|{s}" in runs for R in (2.5, 3.5, 4.5, 5.5, 6.5) for K in (1.0, 2.0, 4.0) for d in (1.0, 1.5))]
print("complete tuning seeds:", len(seeds)); sel = {}
for d in (1.0, 1.5):
    cells = [(R, K) for R in (2.5, 3.5, 4.5, 5.5, 6.5) for K in (1.0, 2.0, 4.0)]
    st = {c: {m: float(np.mean([runs[f"T|{c[0]}|{c[1]}|{d}|{s}"][m] for s in seeds])) for m in ("len", "turns", "coll", "clear", "fb")} for c in cells}
    T = np.array([st[c]["turns"] for c in cells]); C = np.array([st[c]["coll"] for c in cells])
    z = lambda x: (x - x.mean()) / (x.std() if x.std() > 0 else 1)
    score = z(T) + z(C)
    order = sorted(range(len(cells)), key=lambda i: (round(score[i], 9), st[cells[i]]["len"])); best = cells[order[0]]
    print(f"\nD_SAFE={d}\n{'R':>4} {'K':>4} {'len':>6} {'turns':>6} {'coll/run':>9} {'clear':>6} {'fb':>6} {'score':>6}")
    for i, c in enumerate(cells):
        print(f"{c[0]:4.1f} {c[1]:4.1f} {st[c]['len']:6.2f} {st[c]['turns']:6.2f} {st[c]['coll']:9.3f} {st[c]['clear']:6.2f} {st[c]['fb']:6.0f} {score[i]:6.2f}" + ("  <- selected" if c == best else ""))
    print("top 3 by score:", [(cells[i], round(float(score[i]), 2)) for i in order[:3]])
    sel[str(d)] = dict(R=best[0], K=best[1], d_safe=d, tuning=st[best], top3=[(cells[i], float(score[i])) for i in order[:3]])
frozen = json.load(open(os.path.join(L.RESULTS_DIR, "drsafe_t_selected.json")))["selected"]
print("\nfrozen selection:", {d: (v["R"], v["K"]) for d, v in frozen.items()}, "| extended-grid selection:", {d: (v["R"], v["K"]) for d, v in sel.items()})
json.dump(dict(n_tuning_seeds=len(seeds), selected=sel, frozen=frozen), open(os.path.join(L.RESULTS_DIR, "drsafe_t_selected_extended.json"), "w"), indent=2)
