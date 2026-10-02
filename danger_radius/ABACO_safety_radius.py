"""
ABACO_safety_radius.py

Safety-constrained extension of danger-radius weighting (Priority 6 of
the review): a two-zone cost structure instead of one smooth zone.

    Zone 1 -- collision zone      (d < D_SAFE):  candidate hard-rejected
    Zone 2 -- danger zone         (D_SAFE <= d < R): soft 1/d penalty (as before)
    Zone 3 -- safe zone           (d >= R):       no additional cost

This directly answers "I want a method where it prioritises safety over
length": Zone 1 makes the closest approaches structurally impossible
(like hard-block), while Zone 2 keeps this paper's smooth anticipatory
cost further out (like plain danger-radius). It should sit strictly
between hard-block and danger-radius on the length/smoothness vs.
clearance/collision trade-off, and ideally beat plain danger-radius on
safety without regressing all the way to hard-block's length/turn cost.

As with the APF baseline, this monkey-patches ABACO_baseline.trans_prob
for the duration of each run and restores it afterwards -- no changes to
ABACO_baseline.py or ABACO_novelty.py are made.

Collision/clearance for every condition in this script use the
execution-aligned definition (Method B); see exec_aligned_metrics.py
(abaco/) for the full derivation and the single shared implementation --
every script in this repo that reports execution-aligned collisions or
clearance calls that one function instead of keeping its own copy.
"""

import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

import ABACO_baseline as base
import ABACO_novelty as novelty
from exec_aligned_metrics import execution_aligned_metrics

# Danger zone outer edge -- identical to this paper's R, so the soft-cost
# region is unchanged; only the hard floor is new.
SAFE_R = base.DANGER_RADIUS
# Hard-rejection floor. Tuned below; see tune_d_safe().
D_SAFE = 1.5
SAFETY_FALLBACK_COUNT = 0


def trans_prob_safety(cur, nbs, goal, ph, dyn_pos=None, use_novelty=None):
    """Drop-in replacement for ABACO_baseline.trans_prob (same signature).
    Candidates inside D_SAFE of any dynamic obstacle are removed from the
    feasible set entirely; the remaining candidates get the same smooth
    K/(d+eps) danger-radius penalty as ABACO_novelty.trans_prob. If every
    neighbour is inside D_SAFE (rare; only possible when an ant is nearly
    boxed in by a fast-moving obstacle), the hard filter is relaxed for
    that one step so the ant is not permanently stranded -- this fallback
    is counted per run and stored in the returned result for auditing."""
    global SAFETY_FALLBACK_COUNT
    filtered = nbs
    if dyn_pos:
        ok = [nb for nb in nbs if all(base.dist(nb, op) >= D_SAFE for op in dyn_pos)]
        if ok:
            filtered = ok
        else:
            # Fallback: no neighbour satisfies D_SAFE; relax the hard floor
            # for this step to avoid permanently stranding the ant.
            SAFETY_FALLBACK_COUNT += 1

    ds = []
    for nb in filtered:
        tau = ph.get(cur, nb)
        eta = 1.0 / (base.dist(cur, nb) + base.FITNESS_EPSILON)
        if dyn_pos:
            pen = sum(base.K_PENALTY / (base.dist(nb, op) + base.EPSILON)
                       for op in dyn_pos if base.dist(nb, op) < SAFE_R)
            eta /= (1.0 + pen)
        ds.append((tau ** base.ALPHA) * (eta ** base.BETA))
    t = sum(ds)
    probs_filtered = [d / t for d in ds] if t > 0 else [1 / len(filtered)] * len(filtered)

    if len(filtered) == len(nbs):
        return probs_filtered
    # Map back onto the original nbs order, zero-probability for rejected cells
    probs = []
    fi = 0
    for nb in nbs:
        if nb in filtered:
            probs.append(probs_filtered[fi])
            fi += 1
        else:
            probs.append(0.0)
    s = sum(probs)
    return [p / s for p in probs] if s > 0 else [1 / len(nbs)] * len(nbs)


def run_abaco_safety(grid, seed=base.SEED):
    global SAFETY_FALLBACK_COUNT
    SAFETY_FALLBACK_COUNT = 0
    original_trans_prob = base.trans_prob
    base.trans_prob = trans_prob_safety
    try:
        result = base.run_abaco(grid, use_novelty=True, seed=seed)
        result["safety_fallback_count"] = SAFETY_FALLBACK_COUNT
        return result
    finally:
        base.trans_prob = original_trans_prob


def tune_d_safe(grid, candidates, n_probe=8, seed_base=300,
                 output_path="../results/d_safe_tuning_results.json"):
    print(f"{'D_SAFE':>7}  {'success':>8}  {'mean_len':>9}  {'mean_turns':>10}  "
          f"{'mean_clear(B)':>13}  {'collisions(B)':>13}  {'fallbacks':>10}")
    global D_SAFE
    rows = []
    for d in candidates:
        D_SAFE = d
        lens, turns, clears, ok, cols_tot, fallbacks = [], [], [], 0, 0, 0
        for i in range(n_probe):
            r = run_abaco_safety(grid, seed=seed_base + i)
            fallbacks += r.get("safety_fallback_count", 0)
            if r["best_path"]:
                ok += 1
                lens.append(r["best_distance"])
                turns.append(r["sharp_turns"])
                c, mc = execution_aligned_metrics(r, base)
                clears.append(mc)
                cols_tot += c

        row = {
            "d_safe": d,
            "probe_runs": n_probe,
            "successes": ok,
            "mean_length": float(np.mean(lens)) if lens else None,
            "mean_sharp_turns": float(np.mean(turns)) if turns else None,
            "mean_min_clearance": float(np.mean(clears)) if clears else None,
            "total_collision_events": int(cols_tot),
            "total_fallback_activations": int(fallbacks),
        }
        rows.append(row)

        print(f"{d:7.2f}  {ok:8d}/{n_probe}  "
              f"{row['mean_length'] if row['mean_length'] is not None else float('nan'):9.3f}  "
              f"{row['mean_sharp_turns'] if row['mean_sharp_turns'] is not None else float('nan'):10.3f}  "
              f"{row['mean_min_clearance'] if row['mean_min_clearance'] is not None else float('nan'):13.3f}  "
              f"{cols_tot:13d}  {fallbacks:10d}")

    out = os.path.abspath(os.path.join(os.path.dirname(__file__), output_path))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"Saved D_SAFE tuning results to: {out}")
    return rows


if __name__ == "__main__":
    grid = base.create_grid()
    print("Tuning D_SAFE on probe runs (Method B collisions/clearance)...")
    tune_d_safe(grid, [0.5, 0.75, 1.0, 1.5, 2.0, 2.5])
