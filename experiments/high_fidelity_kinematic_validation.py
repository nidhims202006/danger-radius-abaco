"""High-fidelity continuous-kinematic validation for the ESWA review closure.

This is not a Gazebo/ROS result and must not be described as physical-robot
validation. It adds a continuous unicycle-style robot model, bounded speed and
acceleration, heading-rate limits, noisy observations, CV-Kalman estimation,
5-tick replanning, dynamic obstacle motion, and swept-segment collision checks
on held-out generated scenarios.

The grid planners are used only to select a short-horizon waypoint; execution
is continuous between grid cells, so the reported collision test is not the
same discrete-cell test used by the main paper tables.
"""
from __future__ import annotations
import argparse, csv, json, math, random, time
from pathlib import Path

from phase2_estimator import CVKalman
from phase2_scenario_generator import generate_scenarios, Scenario
from phase3_abaco_v3 import abaco_plan
from phase2_closed_loop import _predicted_obstacles_from_estimates, SimObstacle
from phase2_planners import space_time_astar, DStarLite, dwa_local_step

ROBOT_RADIUS = 0.35
OBSTACLE_RADIUS = 0.35
DT = 0.20
V_MAX = 0.85          # cells / tick-equivalent execution speed
A_MAX = 0.18          # cells / tick^2
OMEGA_MAX = math.radians(30.0)
REPLAN_EVERY = 5
MAX_TICKS = 180
GOAL_TOL = 0.75


def wrap_pi(a):
    while a > math.pi: a -= 2*math.pi
    while a < -math.pi: a += 2*math.pi
    return a


def advance_robot(state, target, blocked, rows, cols):
    x, y, th, v = state
    tx, ty = float(target[0]), float(target[1])
    dx, dy = tx-x, ty-y
    desired = math.atan2(dy, dx)
    err = wrap_pi(desired-th)
    omega = max(-OMEGA_MAX, min(OMEGA_MAX, err))
    desired_v = V_MAX * max(0.0, math.cos(err))
    # Slow near the target waypoint and when turning sharply.
    desired_v = min(desired_v, max(0.15, math.hypot(dx,dy)))
    dv = max(-A_MAX, min(A_MAX, desired_v-v))
    v2 = max(0.0, min(V_MAX, v+dv))
    th2 = wrap_pi(th+omega)
    x2 = x + v2*math.cos(th2)
    y2 = y + v2*math.sin(th2)
    x2 = min(max(x2, 0.0), cols-1.0)
    y2 = min(max(y2, 0.0), rows-1.0)
    return (x2,y2,th2,v2)


def point_seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx-ax, by-ay
    wx, wy = px-ax, py-ay
    den = vx*vx+vy*vy
    t = 0.0 if den == 0 else max(0.0, min(1.0, (wx*vx+wy*vy)/den))
    qx, qy = ax+t*vx, ay+t*vy
    return math.hypot(px-qx, py-qy)


def run_one(s: Scenario, planner: str, seed_offset: int = 0):
    rng = random.Random(s.seed + seed_offset)
    obs = [SimObstacle(d, d.row, d.col, d.heading_deg) for d in s.dynamic_obstacles]
    est = [CVKalman(o.row, o.col, s.observation_sigma) for o in obs]
    state = (float(s.start[0]), float(s.start[1]), 0.0, 0.0)
    planned = []
    dstar = None
    collisions = 0
    min_clear = float('inf')
    replans = 0
    planning_time = 0.0
    distance = 0.0
    goal_tick = None
    collision_ticks = set()
    start_time = time.perf_counter()

    for tick in range(MAX_TICKS):
        for o in obs:
            o.step(tick, s.rows, s.cols, rng)
        for o,kf in zip(obs, est):
            nr = rng.gauss(o.row, s.observation_sigma) if s.observation_sigma else o.row
            nc = rng.gauss(o.col, s.observation_sigma) if s.observation_sigma else o.col
            kf.predict(); kf.update(nr,nc)

        if math.hypot(state[0]-s.goal[0], state[1]-s.goal[1]) <= GOAL_TOL:
            goal_tick = tick; break

        if tick % REPLAN_EVERY == 0 or not planned:
            replans += 1
            t0 = time.perf_counter()
            predicted = _predicted_obstacles_from_estimates(s, est, 40)
            current = (round(state[0]), round(state[1]))
            if planner in ('DR-T','DR-SAFE'):
                path, _, _ = abaco_plan(s.rows, s.cols, current, s.goal,
                    set(s.static_obstacles), predicted, mode=planner,
                    R=4.5, K=2.0, D_SAFE=1.5, ants=8, iterations=10,
                    seed=s.seed + tick)
                planned = path[1:6]
            elif planner == 'space_time_astar':
                path, _ = space_time_astar(s.rows,s.cols,current,s.goal,
                    set(s.static_obstacles),predicted)
                planned = path[1:6]
            elif planner == 'dstar_dwa':
                blocked=set(s.static_obstacles)|{(round(o.row),round(o.col)) for o in obs}
                if dstar is None:
                    dstar=DStarLite(s.rows,s.cols,current,s.goal,blocked)
                else:
                    dstar.move_start(current); dstar.update_blocked(blocked)
                gp=dstar.path(); target=gp[1] if len(gp)>1 else s.goal
                cands=[x for x,_ in __import__('phase2_planners').neighbors(current,s.rows,s.cols)]
                step=dwa_local_step((state[0],state[1]),target,blocked,cands)
                planned=[step]
            else:
                raise ValueError(planner)
            planning_time += time.perf_counter()-t0

        prev=(state[0],state[1])
        if planned:
            state=advance_robot(state,planned[0],set(s.static_obstacles),s.rows,s.cols)
            if math.hypot(state[0]-planned[0][0],state[1]-planned[0][1])<0.35:
                planned.pop(0)
        else:
            # Stop safely when planner has no action.
            state=(state[0],state[1],state[2],0.0)

        distance += math.hypot(state[0]-prev[0],state[1]-prev[1])

        # Continuous swept-segment collision check against dynamic obstacles.
        for o in obs:
            d=point_seg_dist(o.row,o.col,prev[0],prev[1],state[0],state[1])-ROBOT_RADIUS-OBSTACLE_RADIUS
            min_clear=min(min_clear,d)
            if d < 0:
                collisions += 1
                collision_ticks.add(tick)
        for r,c in s.static_obstacles:
            d=point_seg_dist(r,c,prev[0],prev[1],state[0],state[1])-ROBOT_RADIUS
            min_clear=min(min_clear,d)
            if d < 0:
                collisions += 1
                collision_ticks.add(tick)

    return {
        'scenario_id':s.scenario_id,'planner':planner,
        'success':goal_tick is not None,'goal_tick':goal_tick,
        'collision_events':collisions,'any_collision':bool(collisions),
        'collision_ticks':len(collision_ticks),'min_continuous_clearance':min_clear,
        'distance_driven':distance,'replans':replans,
        'planning_time_s':planning_time,'wall_time_s':time.perf_counter()-start_time,
        'motion_models':sorted({o.motion for o in s.dynamic_obstacles}),
        'noise_sigma':s.observation_sigma,'workspace':[s.rows,s.cols],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--n',type=int,default=20)
    ap.add_argument('--start-id',type=int,default=204)
    ap.add_argument('--out',default='results/high_fidelity_kinematic_validation')
    args=ap.parse_args()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    scenarios=generate_scenarios(max(240,args.start_id+args.n),820000)
    scenarios=scenarios[args.start_id:args.start_id+args.n]
    planners=['DR-T','DR-SAFE']
    rows=[]
    for s in scenarios:
        for p in planners:
            print(f'running scenario={s.scenario_id} planner={p}',flush=True)
            rows.append(run_one(s,p))
    with (out/'perrun.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    summary={}
    for p in planners:
        rr=[x for x in rows if x['planner']==p]
        def mean(k):
            vals=[x[k] for x in rr if isinstance(x[k],(int,float)) and math.isfinite(x[k])]
            return sum(vals)/len(vals) if vals else None
        summary[p]={
            'N':len(rr),'success_rate':sum(x['success'] for x in rr)/len(rr),
            'any_collision_rate':sum(x['any_collision'] for x in rr)/len(rr),
            'mean_collision_events':mean('collision_events'),
            'mean_min_continuous_clearance':mean('min_continuous_clearance'),
            'mean_distance_driven':mean('distance_driven'),
            'mean_replans':mean('replans'),'mean_planning_time_s':mean('planning_time_s'),
            'median_planning_time_s':sorted(x['planning_time_s'] for x in rr)[len(rr)//2],
            'mean_goal_tick':mean('goal_tick'),
        }
    (out/'summary.json').write_text(json.dumps({'protocol':{
        'name':'high-fidelity continuous-kinematic validation','N':len(scenarios),
        'scenario_ids':[s.scenario_id for s in scenarios], 'robot_radius':ROBOT_RADIUS,
        'obstacle_radius':OBSTACLE_RADIUS,'dt':DT,'v_max':V_MAX,'a_max':A_MAX,
        'omega_max_deg_per_tick':math.degrees(OMEGA_MAX),'replan_every':REPLAN_EVERY,
        'continuous_swept_collision_check':True,'estimator':'CVKalman',
        'noise_levels':sorted({s.observation_sigma for s in scenarios}),
        'motions':sorted({d.motion for s in scenarios for d in s.dynamic_obstacles}),
        'not_ros_gazebo':True},'summary':summary},indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
