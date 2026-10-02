"""
select_drsafe_t.py -- apply the FROZEN selection rule to results/sweep_drsafe_t.json.

Rule (declared in sweep_drsafe_t.py before the sweep ran): for EACH D_SAFE value separately,
z-score mean sharp turns and mean collisions/run across the 9 (R x K) cells of that D_SAFE, score = z(turns) + z(coll),
lowest score wins, ties -> shorter mean length. Writes results/drsafe_t_selected.json.
"""
import json, os
import numpy as np
import drsafe_lib as L

ck = json.load(open(os.path.join(L.RESULTS_DIR, "sweep_drsafe_t.json")))
runs, meta = ck["runs"], ck["meta"]
seeds = [s for s in range(6000, 6030) if all(f"{a}|{s}" in runs for a in ("HB", "DR", "HBP"))
         and all(f"T|{R}|{K}|{d}|{s}" in runs for R in meta["r"] for K in meta["k"] for d in meta["d"])]
print("complete tuning seeds:", len(seeds))
mean = lambda key, m: float(np.mean([runs[f"{key}|{s}"][m] for s in seeds]))
print(f"{'arm':10} {'len':>6} {'turns':>6} {'coll/run':>9} {'clear':>6}")
for a in ("HB", "HBP", "DR"):
    print(f"{a:10} {mean(a,'len'):6.2f} {mean(a,'turns'):6.2f} {mean(a,'coll'):9.3f} {mean(a,'clear'):6.2f}")
sel = {}
for d in meta["d"]:
    cells = [(R, K) for R in meta["r"] for K in meta["k"]]
    st = {c: {m: float(np.mean([runs[f"T|{c[0]}|{c[1]}|{d}|{s}"][m] for s in seeds])) for m in ("len", "turns", "coll", "clear", "fb")} for c in cells}
    T = np.array([st[c]["turns"] for c in cells]); C = np.array([st[c]["coll"] for c in cells])
    z = lambda x: (x - x.mean()) / (x.std() if x.std() > 0 else 1)
    score = z(T) + z(C)
    order = sorted(range(len(cells)), key=lambda i: (round(score[i], 9), st[cells[i]]["len"]))
    best = cells[order[0]]
    print(f"\nD_SAFE={d}")
    print(f"{'R':>4} {'K':>4} {'len':>6} {'turns':>6} {'coll/run':>9} {'clear':>6} {'fb':>6} {'score':>6}")
    for i, c in enumerate(cells):
        print(f"{c[0]:4.1f} {c[1]:4.1f} {st[c]['len']:6.2f} {st[c]['turns']:6.2f} {st[c]['coll']:9.3f} {st[c]['clear']:6.2f} {st[c]['fb']:6.0f} {score[i]:6.2f}" + ("  <- selected" if c == best else ""))
    sel[str(d)] = dict(R=best[0], K=best[1], d_safe=d, tuning=st[best])
json.dump(dict(n_tuning_seeds=len(seeds), selected=sel), open(os.path.join(L.RESULTS_DIR, "drsafe_t_selected.json"), "w"), indent=2)
print("\nselected:", {d: (v["R"], v["K"]) for d, v in sel.items()})
