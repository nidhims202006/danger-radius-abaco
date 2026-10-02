"""
broaden_validation.py

Re-runs the existing baseline/novelty ABACO pipeline on additional
environments to address the reviewer's "broaden the experimental
validation" request:

  - Environment A: smaller grid, sparser static obstacles, 1 dynamic
    obstacle.
  - Environment B: larger grid, denser static obstacles, 5 dynamic
    obstacles.
  - Environment C: the original 18x18 grid/obstacle layout, but one of
    the three dynamic obstacles changes heading partway through the run
    (instead of constant-velocity-only motion).

It also runs a small K_PENALTY sensitivity sweep on the original
environment, mirroring the existing R sweep (Figure 3).

No changes are made to ABACO_baseline.py / ABACO_novelty.py: this script
monkey-patches their module-level globals (GRID_SIZE, START, GOAL,
RAW_OBS_CELLS, make_dyn_obs, K_PENALTY) for the duration of each run and
restores the originals afterwards, so it reuses the exact same ACO/ABACO
planner as the main experiment.

Collisions/clearance are computed with exec_aligned_metrics.py's
execution-aligned (Method B, corrected) definition, same as every other
experiments/ script -- NOT by reading run_abaco()'s own 'collisions'/
'min_clearance' fields, which use an unrelated, uncorrected, from-t=0
indexing. (This script previously did read those fields directly; that was
a bug, silently inconsistent with rerun_generalization_methodb.py and the
rest, now fixed.)

Usage:
    python broaden_validation.py
"""

import math
import random
import copy
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

import ABACO_baseline as base
import ABACO_novelty as novelty
from exec_aligned_metrics import execution_aligned_metrics as exec_aligned

N_RUNS_PER_ENV = 20
SEED_BASE = 42
OUT_DIR = "figures"


# ─────────────────────── environment helpers ───────────────────────

def gen_clusters(grid_size, n_target_cells, seed, avoid):
    """Procedurally place small obstacle clusters (matching the shapes
    used in the original hand-built layout: singles, pairs, 3- and
    4-cell rows), keeping clear of `avoid` points (start/goal)."""
    rng = random.Random(seed)
    cells = set()
    tries = 0
    while len(cells) < n_target_cells and tries < 2000:
        tries += 1
        shape = rng.choice(["single", "pair_h", "pair_v", "row3", "row4"])
        r0 = rng.randint(1, grid_size - 3)
        c0 = rng.randint(1, grid_size - 3)
        if shape == "single":
            block = [(r0, c0)]
        elif shape == "pair_h":
            block = [(r0, c0), (r0, c0 + 1)]
        elif shape == "pair_v":
            block = [(r0, c0), (r0 + 1, c0)]
        elif shape == "row3":
            block = [(r0, c0 + i) for i in range(3)]
        else:
            block = [(r0, c0 + i) for i in range(4)]
        if any(not (0 <= r < grid_size and 0 <= c < grid_size) for r, c in block):
            continue
        if any(abs(r - a[0]) + abs(c - a[1]) < 3 for r, c in block for a in avoid):
            continue
        if cells & set(block):
            continue
        cells.update(block)
    return cells


def set_environment(module, grid_size, start, goal, obstacle_cells, dyn_obs_factory):
    module.GRID_SIZE = grid_size
    module.START = start
    module.GOAL = goal
    module.RAW_OBS_CELLS = obstacle_cells
    module.make_dyn_obs = dyn_obs_factory


def snapshot_module(module):
    return dict(GRID_SIZE=module.GRID_SIZE, START=module.START, GOAL=module.GOAL,
                RAW_OBS_CELLS=module.RAW_OBS_CELLS, make_dyn_obs=module.make_dyn_obs)


def restore_module(module, snap):
    module.GRID_SIZE = snap["GRID_SIZE"]
    module.START = snap["START"]
    module.GOAL = snap["GOAL"]
    module.RAW_OBS_CELLS = snap["RAW_OBS_CELLS"]
    module.make_dyn_obs = snap["make_dyn_obs"]


def heading_change_subclass(module):
    """Build a DynObs subclass, bound to `module`'s own GRID_SIZE global
    (via inheritance), that switches heading after a fixed number of
    steps -- used for the "varying dynamic obstacle behaviour" test."""
    class HeadingChangeObs(module.DynObs):
        def __init__(self, r, c, v, angle_deg, change_step, new_angle_deg, name=""):
            super().__init__(r, c, v, angle_deg, name)
            self.change_step = change_step
            self.new_theta = math.radians(new_angle_deg)
            self._n = 0

        def step(self):
            self._n += 1
            if self._n == self.change_step:
                self.theta = self.new_theta
            return super().step()
    return HeadingChangeObs


# ─────────────────────── environment definitions ───────────────────────

def env_A_factories():
    """Small grid (12x12), sparse static obstacles, 1 dynamic obstacle."""
    obstacles = gen_clusters(12, 8, seed=101, avoid=[(0, 0), (11, 11)])

    def base_dyn():
        return [base.DynObs(5, 5, 0.35, 60, "DynObs1 (v=0.35, \u03b8=60\u00b0)")]

    def novelty_dyn():
        return [novelty.DynObs(5, 5, 0.35, 60, "DynObs1 (v=0.35, \u03b8=60\u00b0)")]

    return dict(name="A: small/sparse (12\u00d712, 1 dyn. obs.)",
                grid_size=12, start=(0, 0), goal=(11, 11),
                obstacles=obstacles, base_dyn=base_dyn, novelty_dyn=novelty_dyn)


def env_B_factories():
    """Large grid (25x25), dense static obstacles, 5 dynamic obstacles,
    including a pair with intersecting paths."""
    obstacles = gen_clusters(25, 42, seed=7, avoid=[(0, 0), (24, 24)])

    def base_dyn():
        return [
            base.DynObs(6, 6, 0.45, 30, "DynObs1"),
            base.DynObs(18, 5, 0.40, 320, "DynObs2"),
            base.DynObs(12, 20, 0.42, 200, "DynObs3"),
            base.DynObs(20, 20, 0.38, 135, "DynObs4"),
            base.DynObs(9, 15, 0.36, 250, "DynObs5"),  # crosses DynObs3's path
        ]

    def novelty_dyn():
        return [
            novelty.DynObs(6, 6, 0.45, 30, "DynObs1"),
            novelty.DynObs(18, 5, 0.40, 320, "DynObs2"),
            novelty.DynObs(12, 20, 0.42, 200, "DynObs3"),
            novelty.DynObs(20, 20, 0.38, 135, "DynObs4"),
            novelty.DynObs(9, 15, 0.36, 250, "DynObs5"),
        ]

    return dict(name="B: large/dense (25\u00d725, 5 dyn. obs.)",
                grid_size=25, start=(0, 0), goal=(24, 24),
                obstacles=obstacles, base_dyn=base_dyn, novelty_dyn=novelty_dyn)


def env_C_factories():
    """Original 18x18 map, but DynObs2 changes heading partway through
    the run instead of moving at constant velocity throughout."""
    obstacles = set(base.RAW_OBS_CELLS)  # reuse the original hand-built layout
    HC_base = heading_change_subclass(base)
    HC_novelty = heading_change_subclass(novelty)

    def base_dyn():
        return [
            base.DynObs(8, 8, 0.45, 45, "DynObs1 (v=0.45, \u03b8=45\u00b0)"),
            HC_base(4, 13, 0.40, 210, 50, 300, "DynObs2 (heading change @50)"),
            base.DynObs(13, 10, 0.38, 135, "DynObs3 (v=0.38, \u03b8=135\u00b0)"),
        ]

    def novelty_dyn():
        return [
            novelty.DynObs(8, 8, 0.45, 45, "DynObs1 (v=0.45, \u03b8=45\u00b0)"),
            HC_novelty(4, 13, 0.40, 210, 50, 300, "DynObs2 (heading change @50)"),
            novelty.DynObs(13, 10, 0.38, 135, "DynObs3 (v=0.38, \u03b8=135\u00b0)"),
        ]

    return dict(name="C: original 18\u00d718 map, heading-change obstacle",
                grid_size=18, start=(0, 0), goal=(17, 17),
                obstacles=obstacles, base_dyn=base_dyn, novelty_dyn=novelty_dyn)


# ─────────────────────── run + analyse one environment ───────────────────────

def run_environment(env, n_runs=N_RUNS_PER_ENV, seed_base=SEED_BASE):
    base_snap = snapshot_module(base)
    novelty_snap = snapshot_module(novelty)
    try:
        set_environment(base, env["grid_size"], env["start"], env["goal"],
                         env["obstacles"], env["base_dyn"])
        set_environment(novelty, env["grid_size"], env["start"], env["goal"],
                         env["obstacles"], env["novelty_dyn"])

        grid = base.create_grid()  # identical layout used for both conditions

        b_len, n_len, b_turns, n_turns, b_clear, n_clear = [], [], [], [], [], []
        b_coll, n_coll = [], []
        for i in range(n_runs):
            seed = seed_base + i
            br = base.run_abaco(grid, use_novelty=False, seed=seed)
            nr = novelty.run_abaco(grid, use_novelty=True, seed=seed)
            bc, bmc = exec_aligned(br, base)
            nc, nmc = exec_aligned(nr, novelty)
            b_len.append(br["best_distance"]); n_len.append(nr["best_distance"])
            b_turns.append(br["sharp_turns"]); n_turns.append(nr["sharp_turns"])
            b_clear.append(bmc); n_clear.append(nmc)
            b_coll.append(bc); n_coll.append(nc)

        def summarize(b, n):
            b = np.asarray(b, dtype=float); n = np.asarray(n, dtype=float)
            diff = n - b
            try:
                _, wp = stats.wilcoxon(b, n)
            except ValueError:
                wp = float("nan")
            d = diff.mean() / diff.std(ddof=1) if diff.std(ddof=1) > 0 else float("nan")
            return dict(b_mean=b.mean(), n_mean=n.mean(), wilcoxon_p=wp, cohend=d)

        result = dict(
            name=env["name"], n_runs=n_runs,
            path_length=summarize(b_len, n_len),
            sharp_turns=summarize(b_turns, n_turns),
            clearance=summarize(b_clear, n_clear),
            collisions=(int(sum(b_coll)), int(sum(n_coll))),
            grid_size=env["grid_size"], n_static=len(env["obstacles"]),
            n_dyn=len(env["base_dyn"]()),
        )
        return result
    finally:
        restore_module(base, base_snap)
        restore_module(novelty, novelty_snap)


# ─────────────────────── K sensitivity sweep ───────────────────────

def k_sensitivity_sweep(grid, k_values=(1.0, 1.5, 2.0, 2.5, 3.0), runs_per_point=5,
                         seed_base=100):
    original_k = novelty.K_PENALTY
    mean_turns, mean_lengths = [], []
    try:
        for K in k_values:
            novelty.K_PENALTY = K
            lengths, turns = [], []
            for run in range(runs_per_point):
                result = novelty.run_abaco(grid, use_novelty=True, seed=seed_base + run)
                lengths.append(result["best_distance"])
                turns.append(result["sharp_turns"])
            mean_lengths.append(float(np.mean(lengths)))
            mean_turns.append(float(np.mean(turns)))
    finally:
        novelty.K_PENALTY = original_k

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax2 = ax1.twinx()
    ax1.plot(k_values, mean_turns, "o-", color="#1f77b4")
    ax1.set_xlabel("Penalty constant K")
    ax1.set_ylabel("Mean sharp turns", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")
    ax2.plot(k_values, mean_lengths, "s-", color="#d62728")
    ax2.set_ylabel("Mean path length (m)", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")
    ax1.axvline(novelty.K_PENALTY, color="gray", linestyle="--", linewidth=1)
    ax1.set_title(
        f"Effect of penalty constant K on smoothness and path length\n"
        f"(R fixed at {novelty.DANGER_RADIUS}, {runs_per_point} runs per point, "
        f"dashed line = value used elsewhere)",
        fontsize=10,
    )
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/Figure8_k_sensitivity.png", dpi=150)
    plt.close(fig)
    return dict(k_values=list(k_values), mean_turns=mean_turns, mean_lengths=mean_lengths)


# ─────────────────────── generalization summary figure ───────────────────────

def make_generalization_figure(env_results, main_result):
    labels = ["Main\n(18\u00d718, 3 obs.)"] + [r["name"].split(":")[0] for r in env_results]
    turn_pct = [main_result["turn_pct"]] + [
        100 * (1 - r["sharp_turns"]["n_mean"] / r["sharp_turns"]["b_mean"]) for r in env_results
    ]
    len_pct = [main_result["len_pct"]] + [
        100 * (1 - r["path_length"]["n_mean"] / r["path_length"]["b_mean"]) for r in env_results
    ]

    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - w / 2, turn_pct, w, label="Sharp turns reduced by (%)", color="#1f77b4")
    ax.bar(x + w / 2, len_pct, w, label="Path length reduced by (%)", color="#d62728")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("% reduction, danger-radius vs. hard-block")
    ax.set_title("Danger-radius improvement across environments")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/Figure9_generalization.png", dpi=150)
    plt.close(fig)


# ─────────────────────── driver ───────────────────────

def main():
    print("Running Environment A (small/sparse)...")
    resA = run_environment(env_A_factories())
    print("Running Environment B (large/dense)...")
    resB = run_environment(env_B_factories())
    print("Running Environment C (heading-change obstacle)...")
    resC = run_environment(env_C_factories())

    for r in (resA, resB, resC):
        print(f"\n--- {r['name']} (n={r['n_runs']}) ---")
        print(f"  static cells={r['n_static']}, dyn obs={r['n_dyn']}")
        for metric in ("path_length", "sharp_turns", "clearance"):
            m = r[metric]
            print(f"  {metric}: baseline={m['b_mean']:.3f} novelty={m['n_mean']:.3f} "
                  f"Wilcoxon p={m['wilcoxon_p']:.4f} d={m['cohend']:.3f}")
        print(f"  collisions: baseline={r['collisions'][0]} novelty={r['collisions'][1]}")

    # main-environment percentages (from the N=50 headline result) for the
    # comparison figure
    main_result = dict(turn_pct=100 * (1 - 12.16 / 13.80), len_pct=100 * (1 - 34.87 / 35.98))

    print("\nRunning K-sensitivity sweep on the main environment...")
    grid = base.create_grid()
    k_sweep = k_sensitivity_sweep(grid)
    print("K sweep mean turns:", k_sweep["mean_turns"])
    print("K sweep mean lengths:", k_sweep["mean_lengths"])

    make_generalization_figure([resA, resB, resC], main_result)
    print("\nFigures written to ./figures/Figure8_k_sensitivity.png and "
          "./figures/Figure9_generalization.png")

    return dict(A=resA, B=resB, C=resC, k_sweep=k_sweep, main=main_result)


if __name__ == "__main__":
    import json
    results = main()
    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        return o
    with open("broaden_validation_results.json", "w") as f:
        json.dump(clean(results), f, indent=2)
    print("\nSaved broaden_validation_results.json")
