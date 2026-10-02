"""
scenario_suite.py -- randomized multi-environment suite (addresses "single environment"
and "constant-velocity only" reviewer points).

Each scenario randomizes: grid size (12/18/25), static-obstacle density (sparse/dense),
number of dynamic obstacles (1/3/5), their start cells, speeds (0.30-0.50 cells/step) and
headings; 12 of 36 scenarios (fixed random subset) contain a dynamic obstacle that changes heading mid-run
(unknown to the planner). Start = (0,0), goal = (n-1, n-1).

FROZEN design: 18 cells (3 sizes x 2 densities x 3 obstacle counts) x 2 replicates = 36
scenarios, scenario ids 0..35, scenario RNG seeds 70000+id. Every scenario is reachable in
the static map (checked by BFS). ACO seeds per scenario: 500000+id*10+j, j=0..n-1.
"""
import math, random, itertools
from collections import deque
import numpy as np
import drsafe_lib as L

base, novelty = L.base, L.novelty
SIZES, DENSITIES, NDYN = [12, 18, 25], {"sparse": 0.04, "dense": 0.08}, [1, 3, 5]
COMBOS = list(itertools.product(SIZES, DENSITIES, NDYN))          # 18
N_SCENARIOS = 2 * len(COMBOS)                                      # 36
HC_SET = set(random.Random(99).sample(range(N_SCENARIOS), 12))     # fixed 12/36 scenarios contain a heading-change obstacle


def _gen_clusters(n, n_cells, rng, avoid):
    cells, tries = set(), 0
    while len(cells) < n_cells and tries < 4000:
        tries += 1
        shape = rng.choice(["single", "pair_h", "pair_v", "row3", "row4"])
        r0, c0 = rng.randint(1, n - 3), rng.randint(1, n - 3)
        block = {"single": [(r0, c0)], "pair_h": [(r0, c0), (r0, c0 + 1)], "pair_v": [(r0, c0), (r0 + 1, c0)],
                 "row3": [(r0, c0 + i) for i in range(3)], "row4": [(r0, c0 + i) for i in range(4)]}[shape]
        if any(not (0 <= r < n and 0 <= c < n) for r, c in block):
            continue
        if any(abs(r - a[0]) + abs(c - a[1]) < 3 for r, c in block for a in avoid):
            continue
        if cells & set(block):
            continue
        cells.update(block)
    return cells


def _reachable(n, cells):
    g = np.zeros((n, n), int)
    for r, c in cells:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = r + dr, c + dc
                if 0 <= rr < n and 0 <= cc < n and (rr, cc) not in ((0, 0), (n - 1, n - 1)):
                    g[rr, cc] = 1
        g[r, c] = 2
    seen, dq = {(0, 0)}, deque([(0, 0)])
    while dq:
        r, c = dq.popleft()
        if (r, c) == (n - 1, n - 1):
            return True
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = r + dr, c + dc
                if (dr or dc) and 0 <= rr < n and 0 <= cc < n and g[rr, cc] == 0 and (rr, cc) not in seen:
                    seen.add((rr, cc)); dq.append((rr, cc))
    return False


def make_scenario(sid):
    n, dens, nd = COMBOS[sid % len(COMBOS)]
    rng = random.Random(70000 + sid)
    for _ in range(50):
        cells = _gen_clusters(n, max(2, int(round(n * n * DENSITIES[dens]))),
                              rng, [(0, 0), (n - 1, n - 1)])
        if _reachable(n, cells):
            break
    dyn = []
    hc_idx = rng.randrange(nd) if sid in HC_SET else None       # 12 of 36 scenarios (fixed random subset)
    for i in range(nd):
        while True:
            r, c = rng.randint(0, n - 1), rng.randint(0, n - 1)
            if (r, c) in cells:
                continue
            if math.hypot(r, c) < 4 or math.hypot(r - (n - 1), c - (n - 1)) < 4:
                continue
            break
        spec = dict(r=r, c=c, v=round(rng.uniform(0.30, 0.50), 3), ang=round(rng.uniform(0, 360), 1))
        if i == hc_idx:
            spec.update(change_step=rng.randint(20, 60), new_ang=round(rng.uniform(0, 360), 1))
        dyn.append(spec)
    return dict(sid=sid, n=n, density=dens, n_dyn=nd, cells=cells, dyn=dyn, heading_change=hc_idx is not None)


def _factory(module, specs):
    import math as _m

    class HC(module.DynObs):
        def __init__(self, r, c, v, ang, change_step, new_ang):
            super().__init__(r, c, v, ang)
            self.cs, self.na, self._n = change_step, _m.radians(new_ang), 0

        def step(self):
            self._n += 1
            if self._n == self.cs:
                self.theta = self.na
            return super().step()

    def make():
        out = []
        for s in specs:
            if "change_step" in s:
                out.append(HC(s["r"], s["c"], s["v"], s["ang"], s["change_step"], s["new_ang"]))
            else:
                out.append(module.DynObs(s["r"], s["c"], s["v"], s["ang"]))
        return out
    return make


class apply_scenario:
    """Context manager: patch both modules' environment globals, restore on exit."""
    def __init__(self, scn):
        self.scn = scn

    def __enter__(self):
        s = self.scn
        self.saved = {}
        for m in (base, novelty):
            self.saved[m] = {k: getattr(m, k) for k in ("GRID_SIZE", "START", "GOAL", "RAW_OBS_CELLS", "make_dyn_obs")}
            m.GRID_SIZE, m.START, m.GOAL = s["n"], (0, 0), (s["n"] - 1, s["n"] - 1)
            m.RAW_OBS_CELLS = s["cells"]
            m.make_dyn_obs = _factory(m, s["dyn"])
        self.grid = base.create_grid()
        return self.grid

    def __exit__(self, *a):
        for m, d in self.saved.items():
            for k, v in d.items():
                setattr(m, k, v)


if __name__ == "__main__":
    for sid in range(N_SCENARIOS):
        s = make_scenario(sid)
        print(sid, s["n"], s["density"], s["n_dyn"], "HC" if s["heading_change"] else "  ", len(s["cells"]))
