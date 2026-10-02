"""Submission replacement for the historical FastDStarLite module.

The original historical source was not available in the recovered archives.
This file is a newly authored runner-compatible implementation based on the
packaged DStarLite formulation and the observed historical runner interface.
It is supplied as a reproducible implementation, not represented as recovery
of the historical source.
"""
from __future__ import annotations
import math
from phase2_planners import DStarLite, neighbors


class FastDStarLite(DStarLite):
    """Runner-compatible bounded D* Lite implementation."""

    def __init__(self, rows, cols, start, goal, blocked, max_expansions=1000):
        super().__init__(rows, cols, start, goal, blocked)
        self.max_expansions = max_expansions

    def compute(self):
        return self.compute_shortest_path(max_expansions=self.max_expansions)

    def update_blocked(self, blocked):
        changed = self.blocked ^ set(blocked)
        self.blocked = set(blocked)
        for cell in changed:
            self._update(cell)
            for p in self._pred(cell):
                self._update(p)
        self.compute()

    def path(self, max_steps=500):
        self.compute()
        if self.g.get(self.start, self.INF) == self.INF:
            return []
        cur = self.start
        out = [cur]
        for _ in range(max_steps):
            if cur == self.goal:
                return out
            cands = [
                (self._cost(cur, n) + self.g.get(n, self.INF), n)
                for n, _ in neighbors(cur, self.rows, self.cols)
                if n not in self.blocked
            ]
            if not cands:
                return []
            val, nxt = min(cands)
            if not math.isfinite(val):
                return []
            if nxt in out[-3:]:
                cands = sorted(cands, key=lambda x: x[0])
                cands = [x for x in cands if x[1] not in out[-3:]] or cands
                nxt = cands[0][1]
            cur = nxt
            out.append(cur)
        return []
