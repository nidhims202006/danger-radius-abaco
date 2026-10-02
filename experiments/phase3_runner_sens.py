"""Phase-3 closed-loop runner using the corrected v2 ABACO adapter."""
from __future__ import annotations
import math, random, time
from phase2_estimator import CVKalman
from phase2_planners import space_time_astar, neighbors
import importlib, os
abaco_plan = importlib.import_module(os.environ.get('ADAPTER','phase3_abaco_v2')).abaco_plan


def _predicted(estimates, horizon, rows, cols):
    out = [set() for _ in range(horizon+1)]
    for k in range(horizon+1):
        for kf in estimates:
            r, c = kf.position
            vr, vc = kf.velocity
            rr = min(max(r + vr*k, 0), rows-1)
            cc = min(max(c + vc*k, 0), cols-1)
            out[k].add((round(rr), round(cc)))
    return out


def _current_obstacles(obs):
    return {(round(o['row']), round(o['col'])) for o in obs}


def run_scenario(s, method, params, max_ticks=45, seed_offset=0):
    rng = random.Random(s.seed + seed_offset)
    obs = [dict(row=o.row, col=o.col, heading=o.heading_deg,
                speed=o.speed, spec=o) for o in s.dynamic_obstacles]
    kfs = [CVKalman(o['row'], o['col'], s.observation_sigma) for o in obs]
    pos = (float(s.start[0]), float(s.start[1]))
    traj = [pos]
    planned = []
    dstar = None
    collision = False
    min_clear = float('inf')
    total_plan = 0.0
    replans = 0
    goal_tick = None
    turns = 0
    prev_vec = None
    floor_relaxations = 0

    for tick in range(max_ticks):
        for o in obs:
            motion = o['spec'].motion
            if motion == 'stop_go' and ((tick//12) % 2 == 1):
                continue
            if motion == 'random_walk':
                o['heading'] += rng.uniform(-35, 35)
            if motion == 'curved':
                o['heading'] += 2.5
            th = math.radians(o['heading'])
            o['col'] += o['speed'] * math.cos(th)
            o['row'] += o['speed'] * math.sin(th)
            if o['col'] < 0 or o['col'] >= s.cols:
                o['heading'] = 180 - o['heading']
                o['col'] = min(max(o['col'], 0), s.cols-1)
            if o['row'] < 0 or o['row'] >= s.rows:
                o['heading'] = -o['heading']
                o['row'] = min(max(o['row'], 0), s.rows-1)

        for o, kf in zip(obs, kfs):
            nr = rng.gauss(o['row'], s.observation_sigma) if s.observation_sigma else o['row']
            nc = rng.gauss(o['col'], s.observation_sigma) if s.observation_sigma else o['col']
            kf.predict(); kf.update(nr, nc)

        for o in obs:
            clr = math.hypot(pos[0]-o['row'], pos[1]-o['col']) - 0.7
            min_clear = min(min_clear, clr)
            if clr < 0:
                collision = True

        if math.dist(pos, s.goal) <= 0.75:
            goal_tick = tick
            break

        if tick % 5 == 0 or not planned:
            replans += 1
            t0 = time.perf_counter()
            current = tuple(map(round, pos))
            if method in ('HB', 'HBP', 'DR-T', 'DR-SAFE'):
                pred = _predicted(kfs, 50, s.rows, s.cols)
                if method == 'HB':
                    # HB uses current occupancy; it does not use prediction.
                    predicted = [list(_current_obstacles(obs)) for _ in pred]
                else:
                    predicted = [list(x) for x in pred]
                path, _, floor_rel = abaco_plan(
                    s.rows, s.cols, current, s.goal, set(s.static_obstacles), predicted,
                    mode=method, R=params.get('R', 4.5), K=params.get('K', 2.0),
                    D_SAFE=params.get('D_SAFE', 1.0), ants=params.get('ants', 20),
                    iterations=params.get('iterations', 30), seed=s.seed+tick)
                floor_relaxations += floor_rel
                planned = path[1:]
            elif method == 'space_time_astar':
                pred = _predicted(kfs, 50, s.rows, s.cols)
                path, _ = space_time_astar(
                    s.rows, s.cols, current, s.goal, set(s.static_obstacles), pred,
                    max_time=int(params.get('horizon', 50)))
                planned = path[1:]
            elif method == 'dstar_dwa':
                blocked = set(s.static_obstacles) | _current_obstacles(obs)
                if dstar is None:
                    dstar = FastDStarLite(
                        s.rows, s.cols, current, s.goal, blocked,
                        max_expansions=int(params.get('max_expansions', 1000)))
                else:
                    dstar.move_start(current); dstar.update_blocked(blocked)
                gp = dstar.path()
                target = gp[1] if len(gp) > 1 else s.goal
                cand = [x for x, _ in neighbors(current, s.rows, s.cols)]
                pw = float(params.get('progress_weight', 1.0))
                cw = float(params.get('clearance_weight', 0.25))
                best = None; best_score = -1e18
                for cell in cand:
                    if cell in blocked:
                        continue
                    progress = -math.dist(cell, target)
                    clearance = min((math.dist(cell, b) for b in blocked), default=5.0)
                    score = pw*progress + cw*min(clearance, 5.0)
                    if score > best_score:
                        best_score = score; best = cell
                step = best if best is not None else current
                planned = [step]
            else:
                raise ValueError(method)
            total_plan += time.perf_counter() - t0

        if planned:
            nxt = planned.pop(0)
            vec = (nxt[0]-pos[0], nxt[1]-pos[1])
            if prev_vec is not None and math.hypot(*prev_vec) > 0 and math.hypot(*vec) > 0:
                dot = prev_vec[0]*vec[0] + prev_vec[1]*vec[1]
                den = math.hypot(*prev_vec)*math.hypot(*vec)
                ang = math.degrees(math.acos(max(-1, min(1, dot/den))))
                if ang > 45:
                    turns += 1
            prev_vec = vec
            pos = (float(nxt[0]), float(nxt[1]))
            traj.append(pos)
        else:
            break

    if goal_tick is None and math.dist(pos, s.goal) <= 0.75:
        goal_tick = max_ticks-1

    return {
        'scenario_id': s.scenario_id, 'seed': s.seed, 'method': method,
        'params': params, 'any_collision': collision,
        'time_to_goal': goal_tick, 'success': goal_tick is not None,
        'distance': sum(math.dist(a,b) for a,b in zip(traj, traj[1:])),
        'min_clearance': min_clear, 'turns': turns,
        'planning_time_s': total_plan, 'replans': replans,
        'floor_relaxations': floor_relaxations,
    }
