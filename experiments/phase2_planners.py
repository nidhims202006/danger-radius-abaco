"""Phase-2 independent planners on a common grid/world interface.

This file contains new comparison planners only; frozen ABACO files are untouched.
"""
from __future__ import annotations
import heapq
import math
import time
from typing import Iterable

Cell = tuple[int, int]


def neighbors(cell: Cell, rows: int, cols: int):
    r, c = cell
    for dr, dc in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < rows and 0 <= cc < cols:
            yield (rr, cc), math.hypot(dr, dc)


def _reconstruct(parent, state):
    path = []
    while state is not None:
        path.append(state)
        state = parent.get(state)
    return list(reversed(path))


def space_time_astar(rows: int, cols: int, start: Cell, goal: Cell,
                     static_blocked: set[Cell], predicted: list[set[Cell]],
                     max_time: int = 200):
    """A* over (cell,time), avoiding predicted dynamic occupancy."""
    t0 = time.perf_counter()
    start_state = (start[0], start[1], 0)
    pq = [(math.dist(start, goal), 0.0, start_state)]
    g = {start_state: 0.0}
    parent = {start_state: None}
    while pq:
        _, cost, (r, c, t) = heapq.heappop(pq)
        if cost != g.get((r, c, t)):
            continue
        if (r, c) == goal:
            states = _reconstruct(parent, (r, c, t))
            return [(a, b) for a, b, _ in states], time.perf_counter() - t0
        if t >= max_time:
            continue
        for (nr, nc), step_cost in neighbors((r, c), rows, cols):
            nt = t + 1
            if (nr, nc) in static_blocked:
                continue
            if nt < len(predicted) and (nr, nc) in predicted[nt]:
                continue
            ns = (nr, nc, nt)
            ng = cost + step_cost
            if ng < g.get(ns, float("inf")):
                g[ns] = ng
                parent[ns] = (r, c, t)
                h = math.dist((nr, nc), goal)
                heapq.heappush(pq, (ng + h, ng, ns))
    return [], time.perf_counter() - t0


class DStarLite:
    """Compact D* Lite implementation for a grid with mutable blocked cells."""
    INF = float("inf")

    def __init__(self, rows, cols, start, goal, blocked: set[Cell]):
        self.rows, self.cols, self.start, self.goal = rows, cols, start, goal
        self.blocked = set(blocked)
        self.g, self.rhs = {}, {}
        self.rhs[goal] = 0.0
        self.U = []
        self.km = 0.0
        self.last = start
        self._push(goal)

    def _h(self, a, b): return math.dist(a, b)
    def _key(self, s):
        m = min(self.g.get(s, self.INF), self.rhs.get(s, self.INF))
        return (m + self._h(self.start, s) + self.km, m)
    def _push(self, s): heapq.heappush(self.U, (*self._key(s), s))
    def _succ(self, s): return [n for n,_ in neighbors(s,self.rows,self.cols) if n not in self.blocked]
    def _pred(self, s): return self._succ(s)
    def _cost(self, a, b): return math.dist(a,b)

    def _update(self, u):
        if u != self.goal:
            vals = [self._cost(u,s) + self.g.get(s,self.INF) for s in self._succ(u)]
            self.rhs[u] = min(vals) if vals else self.INF
        if self.g.get(u,self.INF) != self.rhs.get(u,self.INF):
            self._push(u)

    def compute_shortest_path(self, max_expansions=100000):
        expansions = 0
        while self.U and expansions < max_expansions:
            k1,k2,u = heapq.heappop(self.U)
            if (k1,k2) > self._key(self.start):
                heapq.heappush(self.U,(k1,k2,u)); break
            if self.g.get(u,self.INF) > self.rhs.get(u,self.INF):
                self.g[u] = self.rhs[u]
                for p in self._pred(u): self._update(p)
            else:
                self.g[u] = self.INF
                for p in self._pred(u) + [u]: self._update(p)
            expansions += 1
        return expansions

    def move_start(self, start: Cell):
        """Advance the D* Lite start state after the robot moves."""
        self.km += self._h(self.last, start)
        self.start = start
        self.last = start

    def update_blocked(self, blocked: set[Cell]):
        old = self.blocked
        changed = old ^ set(blocked)
        self.blocked = set(blocked)
        for cell in changed:
            self._update(cell)
            for p in self._pred(cell): self._update(p)
        self.compute_shortest_path()

    def path(self, max_steps=500):
        self.compute_shortest_path()
        if self.g.get(self.start,self.INF) == self.INF:
            return []
        cur = self.start; out = [cur]
        for _ in range(max_steps):
            if cur == self.goal: return out
            candidates = [(self._cost(cur,n)+self.g.get(n,self.INF), n) for n,_ in neighbors(cur,self.rows,self.cols)
                          if n not in self.blocked]
            if not candidates: return []
            val, nxt = min(candidates)
            if not math.isfinite(val): return []
            if nxt in out[-3:]:
                candidates = sorted(candidates, key=lambda x:x[0])
                candidates = [x for x in candidates if x[1] not in out[-3:]] or candidates
                nxt = candidates[0][1]
            cur = nxt; out.append(cur)
        return []


def dwa_local_step(position: tuple[float,float], goal: Cell, blocked: set[Cell],
                   candidates: Iterable[Cell] | None = None) -> Cell:
    """Discrete DWA-style local selector: score short reachable motions by goal
    progress, clearance, and heading change. The world interface remains grid based."""
    r,c = position
    opts = list(candidates) if candidates is not None else [x for x,_ in neighbors((round(r),round(c)), 9999,9999)]
    best = None; best_score = float("-inf")
    for cell in opts:
        if cell in blocked: continue
        progress = -math.dist(cell, goal)
        clearance = min((math.dist(cell,b) for b in blocked), default=5.0)
        score = progress + 0.25 * min(clearance, 5.0)
        if score > best_score:
            best_score, best = score, cell
    return best if best is not None else (round(r), round(c))
