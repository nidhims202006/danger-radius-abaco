"""Phase-5 additions (post hoc, frozen parameters, no retuning).

(1) abaco_plan_legacy: the closed-loop v2 adapter with the two construction/pheromone rules of
    the fixed-grid ABACO restored (manuscript Section 5.3, item iii): age-based Q deposition
    (Q ~ Uniform(10,100), sorted descending, paired with routes sorted shortest-first, deposit Q/L)
    and a 500-step construction limit (v2 uses 100 and a flat 1/L deposit).  Everything else
    (goal-directed heuristic, boundary-continuous DR cost, prediction index, evaporation 0.3,
    directed pheromone edges, alpha=1, beta=5) is identical to phase3_abaco_v2.abaco_plan.
(2) aco_dwa_hybrid_plan: ACO+DWA (strong_baselines.aco_dwa_plan) whose ACO stage uses
    prediction-aware transition costs ('HBP' or 'DR-T') on Kalman-predicted obstacle positions
    instead of the current-occupancy hard block. The DWA-style local step is unchanged.
"""
from __future__ import annotations
import math, random, time, os
from phase2_planners import neighbors
from phase3_abaco_v2 import _score_candidates, _dist
import phase3_abaco_v2 as v2

MIN_Q, MAX_Q = 10.0, 100.0


def abaco_plan_legacy(rows, cols, start, goal, static_blocked, predicted, mode='DR-T',
                      R=4.5, K=2.0, D_SAFE=1.0, ants=20, iterations=30, seed=0,
                      step_cap=None, age_q=None):
    step_cap = int(os.environ.get('P5_CAP', 500)) if step_cap is None else step_cap
    age_q = (os.environ.get('P5_AGEQ', '1') == '1') if age_q is None else age_q
    t0 = time.perf_counter()
    rng = random.Random(seed)
    pher = {}
    best, best_len, floor_relaxations = [], float('inf'), 0
    for _it in range(iterations):
        paths = []
        for _a in range(ants):
            cur = start; path = [cur]; seen = {cur}; length = 0.0
            for step in range(step_cap):
                if cur == goal:
                    break
                cands = [n for n, _ in neighbors(cur, rows, cols)
                         if n not in static_blocked and n not in seen]
                if not cands:
                    break
                obs = predicted[min(step, len(predicted)-1)] if predicted else []   # v2 index
                if mode == 'DR-SAFE' and obs:
                    filtered = [n for n in cands if all(_dist(n, o) >= D_SAFE for o in obs)]
                    if filtered:
                        cands = filtered
                    else:
                        floor_relaxations += 1
                scored = _score_candidates(cur, cands, goal, pher, obs, mode, R, K)
                if not scored:
                    break
                ns = [x[0] for x in scored]
                ws = [max(x[1], 1e-15) for x in scored]
                nxt = rng.choices(ns, weights=ws, k=1)[0]
                length += _dist(cur, nxt); cur = nxt; path.append(cur); seen.add(cur)
            if cur == goal:
                paths.append((length, path))
        if paths:
            bl, bp = min(paths, key=lambda x: x[0])
            if bl < best_len:
                best_len, best = bl, bp
            pher = {e: v * 0.7 for e, v in pher.items()}
            if age_q:
                qs = sorted((rng.uniform(MIN_Q, MAX_Q) for _ in paths), reverse=True)
                order = sorted(range(len(paths)), key=lambda i: paths[i][0])
                qmap = {idx: q for idx, q in zip(order, qs)}
            for i, (length, path) in enumerate(paths):
                dep = (qmap[i] / (length + 1e-9)) if age_q else 1.0 / (length + 1e-9)
                for a, b in zip(path, path[1:]):
                    pher[(a, b)] = pher.get((a, b), 1.0) + dep
    return best, time.perf_counter()-t0, floor_relaxations


def aco_dwa_hybrid_plan(rows, cols, start, goal, static_blocked, current_obs, predicted, mode,
                        R=3.5, K=0.5, ants=8, iterations=10, clearance_weight=0.1,
                        goal_weight=1.0, seed=0):
    t0 = time.perf_counter()
    plan = abaco_plan_legacy if os.environ.get('ADAPTER') == 'legacy' else v2.abaco_plan
    path, _, _ = plan(rows, cols, start, goal, set(static_blocked), predicted,
                      mode=mode, R=R, K=K, ants=ants, iterations=iterations, seed=seed)
    if len(path) < 2:
        return start, time.perf_counter()-t0
    blocked = set(static_blocked) | set(current_obs)
    target = path[min(3, len(path)-1)]
    best, best_score = None, -1e18
    for cell, _ in neighbors(start, rows, cols):
        if cell in blocked:
            continue
        progress = -goal_weight*math.dist(cell, target)
        clearance = min((math.dist(cell, b) for b in blocked), default=5.0)
        score = progress + clearance_weight*min(clearance, 5.0)
        if score > best_score:
            best_score, best = score, cell
    return (best if best is not None else start), time.perf_counter()-t0
