"""
ABACO_safety_pred_continuous.py  --  EXPLORATORY: time-aligned continuous danger-radius cost (Phase 1)

Diagnosis this responds to
    ABACO_safety_radius.py applies the hard floor and the soft cost to the
    obstacle's position AT THE PLANNING SNAPSHOT for every step of the path.
    The execution-aligned metric (exec_aligned_metrics.py) scores waypoint i
    against the obstacle where it will be i iterations later. The floor
    therefore guards where the obstacle IS, while collisions happen where it
    WILL BE, so the floor cannot structurally prevent the collisions the
    metric counts (and it fires as a fallback thousands of times because the
    whole path is tested against one frozen position).

Variant tested here
    When an ant is choosing waypoint index s (s = current path length), the
    floor and the continuous soft cost use each obstacle's predicted position s steps
    ahead of the snapshot, from the same constant-velocity (+ wall-bounce)
    model the paper already defines in Section 2.3.

    THIS ADDS AN ASSUMPTION: the planner knows (or can estimate) each dynamic
    obstacle's speed and heading. It must be stated in the paper if adopted.

No existing file is modified; ABACO_baseline hooks are patched for the
duration of a run and restored.
"""
import copy
import ABACO_baseline as base
import numpy as np

D_SAFE = 1.5
SAFE_R = 3.5
FALLBACK = 0
NOISE = (0.0, 0.0)     # (sigma_heading_deg, sigma_speed_fraction) of the planner's estimate error
_est = []              # per-obstacle (dtheta_rad, speed_scale) drawn once per run
MODE = 'safe'          # 'safe' = DR-SAFE-T ; 'hb' = hard block with prediction (ablation)

_dyn_ref = []          # obstacle objects of the current run (captured)
_pred_cache = {}       # iteration index -> list (per obstacle) of predicted positions


def _predicted(t_iter):
    """Predicted position lists for every obstacle: index s = s steps after the
    current snapshot. Constant-velocity extrapolation (with the same wall
    reflection as the simulator) from the obstacle's CURRENT speed and heading,
    optionally corrupted by a fixed per-run estimation error (NOISE). The
    planner never sees a future heading change: it re-predicts every iteration
    from whatever the obstacle's heading is at that moment."""
    if t_iter in _pred_cache:
        return _pred_cache[t_iter]
    out = []
    for i, o in enumerate(_dyn_ref):
        dth, vs = _est[i]
        c = base.DynObs(0, 0, o.v * vs, 0.0)      # plain constant-velocity obstacle
        c.x, c.y, c.theta = o.x, o.y, o.theta + dth
        c.traj = [o.pos]
        for _ in range(base.MAX_STEPS + 1):
            c.step()
        out.append(c.traj)
    _pred_cache.clear()
    _pred_cache[t_iter] = out
    return out


def _trans_prob_pred(cur, nbs, goal, ph, pred_pos):
    global FALLBACK
    if MODE == 'hb':
        # Same hard-block rule as ABACO_baseline.trans_prob (heavy penalty inside 0.5),
        # but evaluated at the PREDICTED position for this step. Ablation that isolates
        # what prediction alone buys, without the danger-radius cost or the floor.
        ds = []
        for nb in nbs:
            tau = ph.get(cur, nb)
            eta = 1.0 / (base.dist(cur, nb) + base.FITNESS_EPSILON)
            if pred_pos:
                eta /= (1.0 + sum(10.0 for op in pred_pos if base.dist(nb, op) < 0.5))
            ds.append((tau ** base.ALPHA) * (eta ** base.BETA))
        t = sum(ds)
        return [d / t for d in ds] if t > 0 else [1 / len(nbs)] * len(nbs)
    if MODE == 'apf':
        # APF-style repulsive-potential cost (same formula as baselines/ABACO_apf_baseline.py)
        # evaluated at the PREDICTED position: D0 = SAFE_R, ETA = K_PENALTY. No floor.
        ds = []
        for nb in nbs:
            tau = ph.get(cur, nb)
            eta = 1.0 / (base.dist(cur, nb) + base.FITNESS_EPSILON)
            if pred_pos:
                U = 0.0
                for op in pred_pos:
                    dd = base.dist(nb, op)
                    if dd < SAFE_R:
                        U += 0.5 * base.K_PENALTY * (1.0 / max(dd, base.EPSILON) - 1.0 / SAFE_R) ** 2
                eta /= (1.0 + U)
            ds.append((tau ** base.ALPHA) * (eta ** base.BETA))
        t = sum(ds)
        return [d / t for d in ds] if t > 0 else [1 / len(nbs)] * len(nbs)
    # DR-T: continuous time-aligned soft cost only; no hard inner floor.
    # DR-SAFE-T: apply the same soft cost plus the hard D_SAFE feasibility floor.
    filtered = nbs
    if MODE == 'safe' and pred_pos:
        ok = [nb for nb in nbs if all(base.dist(nb, op) >= D_SAFE for op in pred_pos)]
        if ok:
            filtered = ok
        else:
            FALLBACK += 1
    ds = []
    for nb in filtered:
        tau = ph.get(cur, nb)
        eta = 1.0 / (base.dist(cur, nb) + base.FITNESS_EPSILON)
        if pred_pos:
            # Phase-1 continuous soft cost: K * [1/(d+eps) - 1/(R+eps)]_+ .
            # This reaches exactly zero at d = R instead of discontinuously
            # dropping from a positive value to zero at the radius.
            pen = sum(max(0.0, base.K_PENALTY * (
                          1.0 / (base.dist(nb, op) + base.EPSILON)
                          - 1.0 / (SAFE_R + base.EPSILON)))
                      for op in pred_pos if base.dist(nb, op) < SAFE_R)
            eta /= (1.0 + pen)
        ds.append((tau ** base.ALPHA) * (eta ** base.BETA))
    t = sum(ds)
    pf = [d / t for d in ds] if t > 0 else [1 / len(filtered)] * len(filtered)
    if len(filtered) == len(nbs):
        return pf
    probs, fi = [], 0
    for nb in nbs:
        if nb in filtered:
            probs.append(pf[fi]); fi += 1
        else:
            probs.append(0.0)
    s = sum(probs)
    return [p / s for p in probs] if s > 0 else [1 / len(nbs)] * len(nbs)


def _construct(grid, pheromone, dyn_pos, use_novelty, rng):
    current = base.START
    path = [current]
    path_length = 0.0
    tabu = np.zeros((base.GRID_SIZE, base.GRID_SIZE), dtype=bool)
    tabu[current] = True
    t_iter = len(_dyn_ref[0].traj)          # iterations stepped so far
    pred = _predicted(t_iter)
    for _layer in range(base.MAX_STEPS):
        if current == base.GOAL:
            return path, path_length, tabu
        feasible = [n for n in base.neighbors(grid, current) if not tabu[n]]
        if not feasible:
            break
        s = len(path)                        # index the chosen node will take
        pred_pos = [p[min(s, len(p) - 1)] for p in pred]
        probs = _trans_prob_pred(current, feasible, base.GOAL, pheromone, pred_pos)
        nxt = rng.choices(feasible, weights=probs, k=1)[0]
        path_length += base.dist(current, nxt)
        current = nxt
        path.append(current)
        tabu[current] = True
    return None, float('inf'), tabu


def run_abaco_safety_pred(grid, seed, d_safe=1.5, R=3.5, K=2.0, mode='safe', noise=(0.0, 0.0)):
    global D_SAFE, SAFE_R, FALLBACK, _dyn_ref, MODE, NOISE, _est
    D_SAFE, SAFE_R, FALLBACK, MODE, NOISE = d_safe, R, 0, mode, noise
    _pred_cache.clear()
    orig_c, orig_m, orig_K = base.construct_abaco_solution, base.make_dyn_obs, base.K_PENALTY

    def make_and_capture():
        global _dyn_ref, _est
        _dyn_ref = orig_m()
        rng_n = np.random.default_rng(seed * 7 + 13)      # separate stream: does not touch the ACO RNG
        _est = [(float(np.radians(rng_n.normal(0, NOISE[0]))) if NOISE[0] > 0 else 0.0,
                 float(1.0 + rng_n.normal(0, NOISE[1])) if NOISE[1] > 0 else 1.0) for _ in _dyn_ref]
        return _dyn_ref
    base.construct_abaco_solution = _construct
    base.make_dyn_obs = make_and_capture
    base.K_PENALTY = K
    try:
        res = base.run_abaco(grid, use_novelty=True, seed=seed)
        res["safety_fallback_count"] = FALLBACK
        return res
    finally:
        base.construct_abaco_solution, base.make_dyn_obs, base.K_PENALTY = orig_c, orig_m, orig_K
