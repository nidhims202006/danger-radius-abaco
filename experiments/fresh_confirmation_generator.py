"""Generate the fresh, fully crossed closed-loop confirmation set (IDs 1000-1199, base seed 930000).

Unlike phase2_scenario_generator (where the motion model and the number of dynamic obstacles are
assigned from the same index and are therefore perfectly confounded), every factor here is assigned
from its own independently shuffled, exactly balanced sequence, so motion model, obstacle count,
workspace size, static density and observation noise are (nearly) orthogonal.
The scenario construction functions are those of phase2_scenario_generator; no planner is run here.
"""
from __future__ import annotations
import hashlib, json, random, collections
from pathlib import Path
from phase2_scenario_generator import (WORKSPACES, DENSITIES, DYN_COUNTS, MOTIONS, NOISE_SIGMAS,
    Scenario, _static_obstacles, _dynamic_specs, _reachable)

BASE_SEED = 930000
FIRST_ID = 1000
N = 200

def _balanced(levels, n, rng):
    seq = [levels[i % len(levels)] for i in range(n)]
    rng.shuffle(seq)
    return seq

def generate_fresh(n=N, base_seed=BASE_SEED, first_id=FIRST_ID):
    frng = random.Random(base_seed)  # factor-assignment stream
    ws = _balanced(WORKSPACES, n, frng); de = _balanced(DENSITIES, n, frng)
    ct = _balanced(DYN_COUNTS, n, frng); mo = _balanced(MOTIONS, n, frng); no = _balanced(NOISE_SIGMAS, n, frng)
    out = []
    for i in range(n):
        sid = first_id + i
        rng = random.Random(base_seed + sid)
        rows, cols = ws[i]; start, goal = (0, 0), (rows - 1, cols - 1)
        for _ in range(200):
            static = _static_obstacles(rng, rows, cols, de[i], start, goal)
            if _reachable(rows, cols, static, start, goal): break
        else: raise RuntimeError(sid)
        dyn = _dynamic_specs(rng, rows, cols, ct[i], static, start, goal, mo[i])
        out.append(Scenario(scenario_id=sid, seed=base_seed + sid, rows=rows, cols=cols,
            static_density=de[i], start=start, goal=goal, static_obstacles=tuple(sorted(static)),
            dynamic_obstacles=dyn, observation_sigma=no[i]))
    return out

if __name__ == "__main__":
    S = generate_fresh()
    payload = [s.to_dict() for s in S]
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    out = Path(__file__).resolve().parents[1] / "results" / "fresh_confirmation"
    out.mkdir(parents=True, exist_ok=True)
    (out / "scenarios_1000_1199.json").write_bytes(data)
    cross = collections.Counter((s.dynamic_obstacles[0].motion, len(s.dynamic_obstacles)) for s in S)
    man = {"count": len(S), "scenario_ids": [S[0].scenario_id, S[-1].scenario_id], "base_seed": BASE_SEED,
           "generator": "experiments/fresh_confirmation_generator.py", "sha256": hashlib.sha256(data).hexdigest(),
           "motion_x_count_cell_range": [min(cross.values()), max(cross.values())], "motion_x_count_cells": len(cross),
           "marginals": {"workspace": dict(collections.Counter(f"{s.rows}x{s.cols}" for s in S)),
                         "density": dict(collections.Counter(str(s.static_density) for s in S)),
                         "dyn_count": dict(collections.Counter(len(s.dynamic_obstacles) for s in S)),
                         "motion": dict(collections.Counter(s.dynamic_obstacles[0].motion for s in S)),
                         "noise": dict(collections.Counter(str(s.observation_sigma) for s in S))},
           "status": "definitions only; no planner results"}
    (out / "MANIFEST.json").write_text(json.dumps(man, indent=2) + "\n")
    print(json.dumps(man, indent=2))
