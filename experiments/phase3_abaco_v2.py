"""Closed-loop ABACO-family adapter v2.

This is a new adapter; frozen planner files are untouched. Two implementation
corrections are isolated here for the closed-loop study:
1. the transition heuristic is goal-directed (distance-to-goal), rather than
   using only the constant local edge length of an 8-neighbour grid;
2. the hard-block (HB) condition receives the current dynamic-obstacle cells.

The pheromone update, no-revisit construction, eight-neighbourhood and
DR-T/DR-SAFE cost terms remain in the adapter. DR-SAFE floor relaxation is
returned as a diagnostic rather than being silently lost.
"""
from __future__ import annotations
import math, random, time
from phase2_planners import neighbors


def _dist(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])


def _score_candidates(cur, cands, goal, pher, obstacles, mode, R, K):
    vals = []
    for nb in cands:
        tau = pher.get((cur, nb), 1.0)
        # Goal-directed heuristic is necessary in the closed-loop adapter:
        # all 8-neighbour edge lengths are otherwise only 1 or sqrt(2).
        eta = 1.0 / (_dist(nb, goal) + 1e-6)
        if obstacles:
            if mode in ('HB', 'HBP'):
                pen = sum(10.0 for op in obstacles if _dist(nb, op) < 0.5)
                eta /= 1.0 + pen
            elif mode in ('DR-T', 'DR-SAFE'):
                pen = sum(
                    K * max(0.0, 1.0/(_dist(nb, op)+0.1) - 1.0/(R+0.1))
                    for op in obstacles if _dist(nb, op) < R
                )
                eta /= 1.0 + pen
        vals.append((nb, (tau**1.0) * (eta**5.0)))
    return vals


def abaco_plan(rows, cols, start, goal, static_blocked, predicted, mode='DR-T',
               R=4.5, K=2.0, D_SAFE=1.0, ants=20, iterations=30, seed=0):
    t0 = time.perf_counter()
    rng = random.Random(seed)
    pher = {}
    best = []
    best_len = float('inf')
    floor_relaxations = 0

    for _it in range(iterations):
        paths = []
        for _a in range(ants):
            cur = start
            path = [cur]
            seen = {cur}
            length = 0.0
            for step in range(min(max(rows*cols*2, 100), 100)):
                if cur == goal:
                    break
                cands = [n for n, _ in neighbors(cur, rows, cols)
                         if n not in static_blocked and n not in seen]
                if not cands:
                    break
                obs = predicted[min(step, len(predicted)-1)] if predicted else []
                if mode == 'DR-SAFE' and obs:
                    filtered = [n for n in cands
                                if all(_dist(n, o) >= D_SAFE for o in obs)]
                    if filtered:
                        cands = filtered
                    else:
                        # Preserve the existing fallback semantics, but log it.
                        floor_relaxations += 1
                scored = _score_candidates(cur, cands, goal, pher, obs, mode, R, K)
                if not scored:
                    break
                ns = [x[0] for x in scored]
                ws = [max(x[1], 1e-15) for x in scored]
                nxt = rng.choices(ns, weights=ws, k=1)[0]
                length += _dist(cur, nxt)
                cur = nxt
                path.append(cur)
                seen.add(cur)
            if cur == goal:
                paths.append((length, path))

        if paths:
            best_iter_len, best_iter_path = min(paths, key=lambda x: x[0])
            if best_iter_len < best_len:
                best_len = best_iter_len
                best = best_iter_path
            pher = {e: v * 0.7 for e, v in pher.items()}
            for length, path in paths:
                dep = 1.0 / (length + 1e-9)
                for a, b in zip(path, path[1:]):
                    e = (a, b)
                    pher[e] = pher.get(e, 1.0) + dep

    return best, time.perf_counter()-t0, floor_relaxations
