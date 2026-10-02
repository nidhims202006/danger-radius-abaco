"""Closed-loop phase-2 simulator using a common world interface.

This is an implementation/smoke-test harness, not a confirmation runner.
It supports predicted obstacle trajectories, noisy observations with a Kalman
filter, replanning, physical collision checks, goal checks, and per-replan logs.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
import random

from phase2_estimator import CVKalman
from phase2_logger import RunLogger
from phase2_planners import space_time_astar, DStarLite, dwa_local_step
from phase2_scenario_generator import Scenario, DynamicSpec


@dataclass
class SimObstacle:
    spec: DynamicSpec
    row: float
    col: float
    heading: float
    stopped: bool = False

    def step(self, tick, rows, cols, rng):
        if self.spec.motion == "stop_go":
            self.stopped = ((tick // 12) % 2 == 1)
        if self.spec.motion == "random_walk":
            self.heading += rng.uniform(-35, 35)
        if self.spec.motion == "curved":
            self.heading += 2.5
        if self.spec.change_step is not None and tick == self.spec.change_step:
            self.heading = self.spec.new_heading_deg or self.heading
        if self.stopped:
            return
        th = math.radians(self.heading)
        self.col += self.spec.speed * math.cos(th)
        self.row += self.spec.speed * math.sin(th)
        if self.col < 0 or self.col >= cols:
            self.heading = 180 - self.heading
            self.col = min(max(self.col, 0), cols - 1)
        if self.row < 0 or self.row >= rows:
            self.heading = -self.heading
            self.row = min(max(self.row, 0), rows - 1)

    @property
    def position(self):
        return self.row, self.col


def _predicted_obstacles_from_estimates(scenario: Scenario, estimates, horizon: int):
    """Predict dynamic occupancy from Kalman state, not ground truth."""
    out = [set() for _ in range(horizon + 1)]
    for spec, kf in zip(scenario.dynamic_obstacles, estimates):
        r0, c0 = kf.position
        vr, vc = kf.velocity
        for k in range(horizon + 1):
            rr = min(max(r0 + vr * k, 0), scenario.rows - 1)
            cc = min(max(c0 + vc * k, 0), scenario.cols - 1)
            cell = (round(rr), round(cc))
            out[k].add(cell)
            # Conservative one-cell inflation under random-walk motion.
            if spec.motion == "random_walk":
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr, nc = cell[0] + dr, cell[1] + dc
                    if 0 <= nr < scenario.rows and 0 <= nc < scenario.cols:
                        out[k].add((nr, nc))
    return out


def run_closed_loop(scenario: Scenario, planner: str, max_ticks: int = 180, seed: int | None = None):
    rng = random.Random(scenario.seed if seed is None else seed)
    obstacles = [SimObstacle(s, s.row, s.col, s.heading_deg) for s in scenario.dynamic_obstacles]
    estimates = [CVKalman(o.row, o.col, scenario.observation_sigma) for o in obstacles]
    pos = (float(scenario.start[0]), float(scenario.start[1]))
    trajectory = [pos]
    logger = RunLogger()
    collisions = 0
    min_clearance = float("inf")
    replans = 0
    total_planning = 0.0
    planned = []
    goal_tick = None
    dstar = None
    robot_radius = 0.35
    obstacle_radius = 0.35

    for tick in range(max_ticks):
        for o in obstacles: o.step(tick, scenario.rows, scenario.cols, rng)
        observations = []
        for o, kf in zip(obstacles, estimates):
            nr = rng.gauss(o.row, scenario.observation_sigma) if scenario.observation_sigma else o.row
            nc = rng.gauss(o.col, scenario.observation_sigma) if scenario.observation_sigma else o.col
            kf.predict(); kf.update(nr, nc)
            observations.append(kf.position)

        physical_cells = {tuple(map(round, o.position)) for o in obstacles}
        for o in obstacles:
            clearance = math.hypot(pos[0]-o.row, pos[1]-o.col) - robot_radius - obstacle_radius
            min_clearance = min(min_clearance, clearance)
            if clearance < 0:
                collisions += 1
                logger.event(tick, "collision", clearance=clearance)

        if math.dist(pos, scenario.goal) <= 0.75:
            goal_tick = tick
            break

        if tick % 5 == 0 or not planned:
            replans += 1
            if planner == "space_time_astar":
                predicted = _predicted_obstacles_from_estimates(scenario, estimates, 40)
                path, planning_time = space_time_astar(
                    scenario.rows, scenario.cols,
                    tuple(map(round, pos)), scenario.goal,
                    set(scenario.static_obstacles), predicted)
                planned = path[1:]
            elif planner == "dstar_dwa":
                blocked = set(scenario.static_obstacles) | physical_cells
                current = tuple(map(round, pos))
                t0 = __import__('time').perf_counter()
                if dstar is None:
                    dstar = DStarLite(scenario.rows, scenario.cols, current, scenario.goal, blocked)
                else:
                    dstar.move_start(current)
                    dstar.update_blocked(blocked)
                global_path = dstar.path()
                target = global_path[1] if len(global_path) > 1 else scenario.goal
                candidates = [x for x,_ in __import__('phase2_planners').neighbors(current, scenario.rows, scenario.cols)]
                step = dwa_local_step(pos, target, blocked, candidates)
                planning_time = __import__('time').perf_counter() - t0
                planned = [step]
            else:
                raise ValueError(f"unknown planner: {planner}")
            total_planning += planning_time
            logger.replan(tick, planner, planning_time, len(planned), bool(planned))

        if planned:
            nxt = planned.pop(0)
            pos = (float(nxt[0]), float(nxt[1]))
            trajectory.append(pos)
        else:
            logger.event(tick, "planner_failure")
            break

    if goal_tick is None and math.dist(pos, scenario.goal) <= 0.75:
        goal_tick = max_ticks - 1
    return logger.finish(
        scenario_id=scenario.scenario_id,
        planner=planner,
        collision_events=collisions,
        any_collision=bool(collisions),
        min_physical_clearance=float(min_clearance),
        time_to_goal=goal_tick,
        success=goal_tick is not None,
        distance_driven=float(sum(math.dist(a,b) for a,b in zip(trajectory, trajectory[1:]))),
        replans=replans,
        total_planning_time_s=float(total_planning),
        trajectory=[list(x) for x in trajectory],
    )
