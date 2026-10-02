"""Phase-2 reproducible scenario generator.

Generates >=200 independent closed-loop scenarios spanning workspace size,
static density, dynamic-obstacle count/speed, motion model, and observation noise.
No experiment results are read or written by this module.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import math
import random
from typing import List, Tuple

Cell = Tuple[int, int]


@dataclass(frozen=True)
class DynamicSpec:
    row: float
    col: float
    speed: float
    heading_deg: float
    motion: str
    change_step: int | None = None
    new_heading_deg: float | None = None


@dataclass(frozen=True)
class Scenario:
    scenario_id: int
    seed: int
    rows: int
    cols: int
    static_density: float
    start: Cell
    goal: Cell
    static_obstacles: Tuple[Cell, ...]
    dynamic_obstacles: Tuple[DynamicSpec, ...]
    observation_sigma: float

    def to_dict(self):
        d = asdict(self)
        d["static_obstacles"] = [list(x) for x in self.static_obstacles]
        d["dynamic_obstacles"] = [asdict(x) for x in self.dynamic_obstacles]
        d["start"] = list(self.start)
        d["goal"] = list(self.goal)
        return d


WORKSPACES = [(12, 12), (18, 18), (25, 25), (30, 24)]
DENSITIES = (0.04, 0.08, 0.12)
DYN_COUNTS = (1, 3, 5, 8)
MOTIONS = ("constant", "curved", "stop_go", "random_walk")
NOISE_SIGMAS = (0.0, 0.15, 0.35, 0.70)


def _neighbors(cell: Cell, rows: int, cols: int):
    r, c = cell
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (-1, 1), (1, -1), (1, 1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < rows and 0 <= cc < cols:
            yield rr, cc


def _reachable(rows: int, cols: int, blocked: set[Cell], start: Cell, goal: Cell) -> bool:
    if start in blocked or goal in blocked:
        return False
    seen = {start}
    q = [start]
    for cur in q:
        if cur == goal:
            return True
        for nxt in _neighbors(cur, rows, cols):
            if nxt not in blocked and nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return False


def _static_obstacles(rng: random.Random, rows: int, cols: int, density: float,
                      start: Cell, goal: Cell) -> set[Cell]:
    target = max(1, int(round(rows * cols * density)))
    out: set[Cell] = set()
    while len(out) < target:
        cell = (rng.randrange(rows), rng.randrange(cols))
        if cell in (start, goal):
            continue
        # Avoid placing an immediate wall around either endpoint.
        if min(math.dist(cell, start), math.dist(cell, goal)) < 2.0:
            continue
        out.add(cell)
    return out


def _dynamic_specs(rng: random.Random, rows: int, cols: int, count: int,
                    static: set[Cell], start: Cell, goal: Cell, motion: str):
    specs: List[DynamicSpec] = []
    occupied = set(static) | {start, goal}
    for _ in range(count):
        for _attempt in range(1000):
            r, c = rng.uniform(1, rows - 2), rng.uniform(1, cols - 2)
            if all(math.dist((r, c), x) >= 3.0 for x in occupied):
                break
        occupied.add((round(r), round(c)))
        change = None
        new_heading = None
        if motion == "curved":
            change = rng.randint(8, 40)
            new_heading = rng.uniform(0, 360)
        specs.append(DynamicSpec(
            row=r, col=c,
            speed=rng.uniform(0.25, 0.75),
            heading_deg=rng.uniform(0, 360),
            motion=motion,
            change_step=change,
            new_heading_deg=new_heading,
        ))
    return tuple(specs)


def make_scenario(scenario_id: int, base_seed: int = 820000) -> Scenario:
    rng = random.Random(base_seed + scenario_id)
    rows, cols = WORKSPACES[scenario_id % len(WORKSPACES)]
    density = DENSITIES[(scenario_id // len(WORKSPACES)) % len(DENSITIES)]
    count = DYN_COUNTS[(scenario_id // (len(WORKSPACES) * len(DENSITIES))) % len(DYN_COUNTS)]
    motion = MOTIONS[(scenario_id // 12) % len(MOTIONS)]
    sigma = NOISE_SIGMAS[(scenario_id // 7) % len(NOISE_SIGMAS)]
    start, goal = (0, 0), (rows - 1, cols - 1)

    for _ in range(200):
        static = _static_obstacles(rng, rows, cols, density, start, goal)
        if _reachable(rows, cols, static, start, goal):
            break
    else:
        raise RuntimeError(f"Could not generate reachable scenario {scenario_id}")

    dyn = _dynamic_specs(rng, rows, cols, count, static, start, goal, motion)
    return Scenario(
        scenario_id=scenario_id,
        seed=base_seed + scenario_id,
        rows=rows,
        cols=cols,
        static_density=density,
        start=start,
        goal=goal,
        static_obstacles=tuple(sorted(static)),
        dynamic_obstacles=dyn,
        observation_sigma=sigma,
    )


def generate_scenarios(n: int = 240, base_seed: int = 820000) -> list[Scenario]:
    if n < 200:
        raise ValueError("Phase-2 protocol requires at least 200 scenarios")
    return [make_scenario(i, base_seed) for i in range(n)]


if __name__ == "__main__":
    scenarios = generate_scenarios(240)
    motions = sorted({s.dynamic_obstacles[0].motion for s in scenarios})
    print(f"generated={len(scenarios)}")
    print(f"workspaces={sorted({(s.rows, s.cols) for s in scenarios})}")
    print(f"densities={sorted({s.static_density for s in scenarios})}")
    print(f"dynamic_counts={sorted({len(s.dynamic_obstacles) for s in scenarios})}")
    print(f"motions={motions}")
    print(f"noise={sorted({s.observation_sigma for s in scenarios})}")
