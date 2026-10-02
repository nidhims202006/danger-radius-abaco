"""Post hoc matched-interface ORCA and MPC baselines for the closed-loop study.

Both planners use the same world interface as the other closed-loop planners:
8-connected grid cells, one displacement per tick, Kalman-estimated obstacle
positions/velocities (NOT ground truth), robot radius 0.35 and obstacle radius
0.35 cell.  They are matched-interface re-implementations of the *methods*,
not source-level reproductions of any published code.

ORCA (van den Berg et al., 2011)
    Preferred velocity follows a static-obstacle distance field to the goal.
    For every estimated obstacle an ORCA half-plane is built with the standard
    construction (cut-off circle / tangent legs).  Obstacles do not react, so
    the robot takes full responsibility (the half-plane passes through
    v + u, not v + u/2).  The continuous velocity LP is replaced by exact
    selection over the robot's admissible displacement set (the 8 neighbours
    plus 'stay'): the displacement closest to the preferred velocity that lies
    in every half-plane; if none does, the displacement with the smallest
    maximum half-plane violation.  Static obstacles are handled by excluding
    blocked cells from the admissible set.

MPC
    Finite-horizon receding-horizon controller over the same discrete
    displacement set.  Stage cost = 1 (time) + 0.25 x step length + collision penalty (staying on the goal
    cell is free, otherwise 'wait now, move later' ties with 'move now' and the
    controller procrastinates) against the
    Kalman-predicted obstacle positions at that step; terminal cost = static
    distance-to-goal.  The finite-horizon problem is solved exactly by dynamic
    programming over (step, cell); only the first displacement is executed and
    the problem is re-solved at the next tick.
"""
from __future__ import annotations
import heapq
import math
import time

_MOVES = [(0, 0)] + [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]
_DMAP_CACHE: dict = {}


def distance_map(rows, cols, goal, static_blocked, key=None):
    """Dijkstra distance-to-goal over static-free 8-connected cells."""
    if key is not None and key in _DMAP_CACHE:
        return _DMAP_CACHE[key]
    INF = float("inf")
    d = {goal: 0.0}
    pq = [(0.0, goal)]
    while pq:
        dist, (r, c) = heapq.heappop(pq)
        if dist > d.get((r, c), INF):
            continue
        for dr, dc in _MOVES[1:]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in static_blocked:
                nd = dist + math.hypot(dr, dc)
                if nd < d.get((nr, nc), INF):
                    d[(nr, nc)] = nd
                    heapq.heappush(pq, (nd, (nr, nc)))
    if key is not None:
        _DMAP_CACHE[key] = d
    return d


def _predict(est, k, rows, cols):
    """Kalman-extrapolated obstacle positions k ticks ahead (clipped)."""
    out = []
    for kf in est:
        r, c = kf.position
        vr, vc = kf.velocity
        out.append((min(max(r + vr * k, 0.0), rows - 1), min(max(c + vc * k, 0.0), cols - 1)))
    return out


# ----------------------------------------------------------------- ORCA ---
def _det(a, b):
    return a[0] * b[1] - a[1] * b[0]


def _orca_halfplane(p_rel, v_rel, radius, tau):
    """Return (u, direction) of the ORCA line for one obstacle, full
    responsibility; the admissible set is det(direction, v_robot + u - v) <= 0.  Vectors are (x=col, y=row).  Port of the RVO2 agent
    construction with dt = 1 tick."""
    dist_sq = p_rel[0] ** 2 + p_rel[1] ** 2
    r_sq = radius ** 2
    if dist_sq > r_sq:
        w = (v_rel[0] - p_rel[0] / tau, v_rel[1] - p_rel[1] / tau)
        w_sq = w[0] ** 2 + w[1] ** 2
        dot1 = w[0] * p_rel[0] + w[1] * p_rel[1]
        if dot1 < 0.0 and dot1 ** 2 > r_sq * w_sq:
            w_len = math.sqrt(w_sq) or 1e-9
            uw = (w[0] / w_len, w[1] / w_len)
            direction = (uw[1], -uw[0])
            u = ((radius / tau - w_len) * uw[0], (radius / tau - w_len) * uw[1])
        else:
            leg = math.sqrt(max(dist_sq - r_sq, 0.0))
            if _det(p_rel, w) > 0.0:
                direction = ((p_rel[0] * leg - p_rel[1] * radius) / dist_sq,
                             (p_rel[0] * radius + p_rel[1] * leg) / dist_sq)
            else:
                direction = (-(p_rel[0] * leg + p_rel[1] * radius) / dist_sq,
                             -(-p_rel[0] * radius + p_rel[1] * leg) / dist_sq)
            dot2 = v_rel[0] * direction[0] + v_rel[1] * direction[1]
            u = (dot2 * direction[0] - v_rel[0], dot2 * direction[1] - v_rel[1])
    else:  # already overlapping: resolve within one tick
        w = (v_rel[0] - p_rel[0], v_rel[1] - p_rel[1])
        w_len = math.hypot(*w) or 1e-9
        uw = (w[0] / w_len, w[1] / w_len)
        direction = (uw[1], -uw[0])
        u = ((radius - w_len) * uw[0], (radius - w_len) * uw[1])
    return u, direction  # full responsibility: line passes through v_robot + u


def orca_step(rows, cols, pos, goal, static_blocked, est, v_robot,
              tau=3.0, buffer=0.15, pref_speed=1.0, neighbor_dist=7.0,
              dmap_key=None):
    """One ORCA decision; returns the next cell (may equal the current one)."""
    t0 = time.perf_counter()
    cur = (int(round(pos[0])), int(round(pos[1])))
    dmap = distance_map(rows, cols, goal, static_blocked, dmap_key)
    inf = float("inf")
    # preferred velocity: towards the best static-free neighbour
    best, best_d = cur, dmap.get(cur, inf)
    for dr, dc in _MOVES[1:]:
        n = (cur[0] + dr, cur[1] + dc)
        if n in dmap and dmap[n] < best_d:
            best, best_d = n, dmap[n]
    vec = (best[0] - cur[0], best[1] - cur[1])
    ln = math.hypot(*vec)
    pref = (0.0, 0.0) if ln == 0 else (vec[1] / ln * pref_speed, vec[0] / ln * pref_speed)  # (x=col, y=row)
    # ORCA lines from Kalman estimates
    active = []
    radius = 0.70 + buffer
    vx_r, vy_r = v_robot[1], v_robot[0]
    for kf in est:
        o_r, o_c = kf.position
        vr, vc = kf.velocity
        p_rel = (o_c - pos[1], o_r - pos[0])
        if math.hypot(*p_rel) > neighbor_dist:
            continue
        u, direction = _orca_halfplane(p_rel, (vx_r - vc, vy_r - vr), radius, tau)
        active.append(((vx_r + u[0], vy_r + u[1]), direction))
    # exact selection over the admissible displacement set
    best_move, best_key = cur, None
    for dr, dc in _MOVES:
        nxt = (cur[0] + dr, cur[1] + dc)
        if not (0 <= nxt[0] < rows and 0 <= nxt[1] < cols) or nxt in static_blocked:
            continue
        v = (float(dc), float(dr))  # (x=col, y=row)
        worst = 0.0
        for point, direction in active:
            viol = _det(direction, (point[0] - v[0], point[1] - v[1]))
            worst = max(worst, viol)
        dist_pref = (v[0] - pref[0]) ** 2 + (v[1] - pref[1]) ** 2
        key = (0, dist_pref, dmap.get(nxt, inf)) if worst <= 1e-9 else (1, worst, dmap.get(nxt, inf))
        if best_key is None or key < best_key:
            best_key, best_move = key, nxt
    return best_move, time.perf_counter() - t0


# ------------------------------------------------------------------ MPC ---
def mpc_step(rows, cols, pos, goal, static_blocked, est,
             horizon=6, r_safe=1.5, w_coll=5.0, dmap_key=None):
    """Exact finite-horizon discrete MPC by DP over (step, cell)."""
    t0 = time.perf_counter()
    cur = (int(round(pos[0])), int(round(pos[1])))
    dmap = distance_map(rows, cols, goal, static_blocked, dmap_key)
    inf = float("inf")
    preds = [_predict(est, k, rows, cols) for k in range(horizon + 1)]
    span = max(r_safe - 0.70, 1e-6)

    def pen(cell, k):
        total = 0.0
        for (orr, occ) in preds[k]:
            d = math.hypot(cell[0] - orr, cell[1] - occ)
            if d < 0.70:
                total += 100.0
            elif d < r_safe:
                total += w_coll * ((r_safe - d) / span) ** 2
        return total

    layer = {cur: (0.0, None)}  # cell -> (cost, first move)
    for k in range(1, horizon + 1):
        nxt_layer = {}
        for cell, (cost, first) in layer.items():
            for dr, dc in _MOVES:
                n = (cell[0] + dr, cell[1] + dc)
                if not (0 <= n[0] < rows and 0 <= n[1] < cols) or n in static_blocked:
                    continue
                if cell == goal and (dr, dc) == (0, 0):
                    nc = cost + pen(n, k)  # goal is absorbing: staying there is free
                else:
                    nc = cost + 1.0 + 0.25 * math.hypot(dr, dc) + pen(n, k)
                f = first if first is not None else n
                old = nxt_layer.get(n)
                if old is None or nc < old[0]:
                    nxt_layer[n] = (nc, f)
        layer = nxt_layer
    best, best_cost = cur, inf
    for cell, (cost, first) in layer.items():
        total = cost + dmap.get(cell, inf)
        if total < best_cost:
            best_cost, best = total, first
    return (best if best is not None else cur), time.perf_counter() - t0
