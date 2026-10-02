"""
drsafe_lib.py

Shared helpers for the tuning / power / confirmatory scripts added to answer
the two methodological gaps flagged for the journal submission:

  (1) N = 50 on a single environment is under-powered for the headline
      DR-SAFE collision claim  ->  power_analysis.py + confirmatory_run.py
  (2) R = 3.5 / K = 2.0 were tuned on plain DR, never re-swept for DR-SAFE
      ->  sweep_rk_drsafe.py

This module only wraps the existing planners; it does not change them.
Every run returns one flat dict of execution-aligned metrics (the single
canonical definition in abaco/exec_aligned_metrics.py) so downstream scripts
never touch run_abaco()'s own legacy 'collisions'/'min_clearance' fields.
Historical stored results retain their original total-event values; the v29
review-closure checker additionally computes the start-waypoint-excluded
primary metric for Tables 18–21.

Parameter handling
------------------
* DR      : ABACO_novelty.trans_prob reads novelty.DANGER_RADIUS and
            novelty.K_PENALTY at call time.
* DR-SAFE : ABACO_safety_radius.trans_prob_safety reads safety.SAFE_R (bound
            to base.DANGER_RADIUS *once at import time*) and base.K_PENALTY /
            base.EPSILON at call time. So sweeping R for DR-SAFE requires
            setting safety.SAFE_R, NOT base.DANGER_RADIUS, and sweeping K
            requires base.K_PENALTY. (Setting only base.DANGER_RADIUS would
            silently leave DR-SAFE at R = 3.5.)
All parameters are restored in `finally` blocks.
"""
import os, sys, json, time, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _sub in ("experiments", "baselines", "danger_radius", "abaco"):
    _p = os.path.join(ROOT, _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import matplotlib
matplotlib.use("Agg")
import numpy as np

import ABACO_baseline as base
import ABACO_novelty as novelty
import ABACO_safety_radius as safety
from exec_aligned_metrics import execution_aligned_metrics

RESULTS_DIR = os.path.join(ROOT, "results")
FIG_DIR = os.path.join(ROOT, "figures")

# Values used throughout the current paper.
DEFAULT_R = 3.5
DEFAULT_K = 2.0
DEFAULT_D_SAFE = 1.5

GRID = base.create_grid()


@contextlib.contextmanager
def _patched(obj, **attrs):
    old = {k: getattr(obj, k) for k in attrs}
    try:
        for k, v in attrs.items():
            setattr(obj, k, v)
        yield
    finally:
        for k, v in old.items():
            setattr(obj, k, v)


def _flat(result, module):
    ok = bool(result["best_path"])
    out = dict(ok=ok, conv=int(result["convergence"]),
               fb=int(result.get("safety_fallback_count", 0)))
    if ok:
        c, mc = execution_aligned_metrics(result, module)
        out.update(len=float(result["best_distance"]),
                   turns=int(result["sharp_turns"]),
                   clear=float(mc), coll=int(c))
    else:
        out.update(len=None, turns=None, clear=None, coll=None)
    return out


def run_hb(seed, grid=None):
    return _flat(base.run_abaco(GRID if grid is None else grid, use_novelty=False, seed=seed), base)


def run_dr(seed, R=DEFAULT_R, K=DEFAULT_K, grid=None):
    with _patched(novelty, DANGER_RADIUS=R, K_PENALTY=K):
        return _flat(novelty.run_abaco(GRID if grid is None else grid, use_novelty=True, seed=seed), novelty)


def run_drs(seed, R=DEFAULT_R, K=DEFAULT_K, d_safe=DEFAULT_D_SAFE):
    with _patched(safety, SAFE_R=R, D_SAFE=d_safe), _patched(base, K_PENALTY=K):
        return _flat(safety.run_abaco_safety(GRID, seed=seed), base)


# ------------------------------------------------------- obstacle replay helper
def real_obstacles_at(t0, extra=205):
    """Main-environment dynamic obstacles stepped t0 iterations (the planning snapshot), then `extra`
    further iterations so .traj covers the whole scored path. Used by analyze_start_cell_adjusted.py
    to find obstacles sitting on the start cell at the convergence iteration. (Moved here from the
    former space_time_astar._obstacle_states; obstacle motion is deterministic, so no seed is needed.)"""
    real = base.make_dyn_obs()
    for _ in range(t0 + extra):
        for o in real:
            o.step()
    return real


# ---------------------------------------------------------------- checkpoints
def load_ckpt(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save_ckpt(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f)
    os.replace(tmp, path)
