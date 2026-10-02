"""
ABACO_apf_baseline.py

Comparison baseline: an artificial-potential-field (APF) repulsive-cost term added to the same ABACO transition rule used throughout this paper.

It is NOT a reproduction of Gong, Yang, Yuan, & Wang (2022) (Mathematical Biosciences and Engineering, 19(12), 12405-12426): that paper combines an improved
ACO global planner with rule-based local avoidance strategies (wait-and-avoid / re-planning chosen by obstacle size, speed and approach direction) and does not use a
potential field. This module is a minimal, clearly described potential-field cost (ACO with potential-field terms has been explored elsewhere), used so the shape of a
repulsive cost can be compared with the hard-block and danger-radius conditions under identical conditions: same grid, same static/dynamic obstacles, same colony
parameters, same seeds.

Repulsive potential (classic Khatib-style formulation):

    U_rep(d) = 0.5 * ETA * (1/d - 1/D0)^2     for d < D0
             = 0                               otherwise

where d is distance to the obstacle, D0 is the influence radius, and ETA is a repulsive gain. This differs structurally from this paper's danger-radius cost,
sum_i K/(d_i + eps) for d_i < R, in that the APF penalty grows with 1/d^2 close to the obstacle (a much harder,
more sharply-peaked repulsion near contact) and is exactly zero beyond
D0, whereas danger-radius grows more gently as ~1/d and is smoothly
bounded by the same K/EPSILON cap at d -> 0. D0 is set equal to this
paper's DANGER_RADIUS so both methods sense obstacles at the same range,
isolating the *shape* of the repulsive cost as the only difference
between the two conditions.

No changes are made to ABACO_baseline.py: this script monkey-patches its
`trans_prob` function for the duration of each run and restores the
original afterwards, exactly as ABACO_novelty.py's DANGER_RADIUS/R sweep
and broaden_validation.py's environment swaps already do.
"""

import math
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

import ABACO_baseline as base

# Influence radius: identical to this paper's danger radius R, so both
# conditions sense obstacles at the same range.
APF_D0 = base.DANGER_RADIUS
# Repulsive gain. Set equal to this paper's K_PENALTY (2.0) so the two
# conditions share the same gain magnitude and influence radius -- the
# only remaining difference is the functional shape of the repulsive
# cost. A probe sweep (see tune_eta() below) confirmed ETA=2.0 gives a
# 100% path-success rate and path lengths/turn counts in the same range
# as the hard-block and danger-radius conditions, i.e. this is not a
# value chosen to make the baseline look artificially weak or strong.
APF_ETA = 2.0


def trans_prob_apf(cur, nbs, goal, ph, dyn_pos=None, use_novelty=None):
    """Drop-in replacement for ABACO_baseline.trans_prob. Same signature
    (so it can be monkey-patched into the existing construct_abaco_solution
    / run_abaco pipeline unmodified); use_novelty is accepted but ignored
    -- this is a third, distinct condition, not a toggle on the other two."""
    ds = []
    for nb in nbs:
        tau = ph.get(cur, nb)
        eta = 1.0 / (base.dist(cur, nb) + base.FITNESS_EPSILON)
        if dyn_pos:
            U = 0.0
            for op in dyn_pos:
                d = base.dist(nb, op)
                if d < APF_D0:
                    d_safe = max(d, base.EPSILON)
                    U += 0.5 * APF_ETA * (1.0 / d_safe - 1.0 / APF_D0) ** 2
            eta /= (1.0 + U)
        ds.append((tau ** base.ALPHA) * (eta ** base.BETA))
    t = sum(ds)
    return [d / t for d in ds] if t > 0 else [1 / len(nbs)] * len(nbs)


def run_abaco_apf(grid, seed=base.SEED):
    """Run one APF-baseline trial by monkey-patching base.trans_prob for
    the duration of the call, then restoring it -- reuses run_abaco,
    construct_abaco_solution, Pher, DynObs, age_based_q_values, and the
    sharp-turn/clearance/collision metrics unchanged."""
    original_trans_prob = base.trans_prob
    base.trans_prob = trans_prob_apf
    try:
        return base.run_abaco(grid, use_novelty=True, seed=seed)
    finally:
        base.trans_prob = original_trans_prob


def run_apf_experiment(grid, runs, seed_base=base.SEED):
    results = [run_abaco_apf(grid, seed=seed_base + i) for i in range(runs)]
    successful = [r for r in results if r["best_path"]]
    if not successful:
        raise RuntimeError("APF baseline found no feasible path in any execution.")
    return results


def tune_eta(grid, candidate_etas, n_probe_runs=5, seed_base=200,
             output_path="../results/apf_eta_tuning_results.json"):
    """Run a small pre-comparison tuning sweep and persist its results.

    The sweep is a coarse sensitivity check, not a statistically powered
    parameter optimization. The saved JSON records the exact probe settings
    and metrics used to justify the selected APF_ETA.
    """
    print(f"{'ETA':>6}  {'success':>8}  {'mean_len':>10}  {'mean_turns':>10}  "
          f"{'mean_clear':>10}")
    global APF_ETA
    rows = []

    for eta in candidate_etas:
        APF_ETA = eta
        lens, turns, clears, ok = [], [], [], 0

        for i in range(n_probe_runs):
            r = run_abaco_apf(grid, seed=seed_base + i)
            if r["best_path"]:
                ok += 1
                lens.append(r["best_distance"])
                turns.append(r["sharp_turns"])
                # ABACO_baseline.run_abaco now returns the shared
                # execution-aligned safety metrics.
                clears.append(r["min_clearance"])

        row = {
            "eta": eta,
            "probe_runs": n_probe_runs,
            "successes": ok,
            "mean_length": float(np.mean(lens)) if lens else None,
            "mean_sharp_turns": float(np.mean(turns)) if turns else None,
            "mean_min_clearance": float(np.mean(clears)) if clears else None,
        }
        rows.append(row)

        print(f"{eta:6.2f}  {ok:8d}/{n_probe_runs}  "
              f"{row['mean_length'] if row['mean_length'] is not None else float('nan'):10.3f}  "
              f"{row['mean_sharp_turns'] if row['mean_sharp_turns'] is not None else float('nan'):10.3f}  "
              f"{row['mean_min_clearance'] if row['mean_min_clearance'] is not None else float('nan'):10.3f}")

    out = os.path.abspath(os.path.join(os.path.dirname(__file__), output_path))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    print(f"Saved APF ETA tuning results to: {out}")
    return rows


if __name__ == "__main__":
    grid = base.create_grid()
    print("Tuning ETA on a few probe runs...")
    tune_eta(grid, [1.0, 2.0, 4.0, 6.0, 8.0, 12.0])
