

"""
generate_paper_figures.py
 
Runs both ABACO_baseline.py and ABACO_novelty.py (unmodified) and produces
the seven comparison figures used in the paper:
 
  Figure 1 - grid environment (static obstacles, start, goal)
  Figure 2 - cell cost around a moving obstacle: hard block vs. soft cost
  Figure 3 - effect of danger radius R on smoothness / path length
  Figure 4 - best path over 10 runs: baseline (hard block) vs novelty
  Figure 5 - convergence curves: best run of each condition
  Figure 6 - path length / sharp turns / min clearance, per paired run
  Figure 7 - novelty path progression through 4 iterations, buffer zone shown
 
Usage:
    python generate_paper_figures.py
 
Figures are written to ./figures/Figure1.png ... Figure7.png
 
Notes on Figure 4
------------------
The version of this plot that shipped in the paper PDF has a rendering bug:
fig.suptitle() and each subplot's ax.set_title() land at almost the same
y-position, so the shared title text visually collides with the per-panel
titles. That is fixed here by:
  1. giving the figure extra headroom (a taller figsize),
  2. pushing the suptitle up with a dedicated y= value,
  3. pushing each subplot title down with pad=,
  4. reserving space between them with tight_layout(rect=...) instead of
     a bare tight_layout()/subplots_adjust() call.
Figure 4 is also offered in a stacked (top/bottom) layout as an alternative
to side-by-side, since the two panels are square and don't share an axis --
stacking avoids the horizontal-squeeze that caused the collision in the
first place. Toggle with FIG4_LAYOUT below.
"""
 
import os
import copy
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from scipy import stats
 
import ABACO_baseline as base
import ABACO_novelty as novelty
 
OUT_DIR = "figures"
os.makedirs(OUT_DIR, exist_ok=True)

# Sample size used for the paired baseline/novelty comparison (Figures 4-6).
# Raised from the original 10 to 50 after the significance-analysis review
# showed 10 paired runs was underpowered and the sign-test p-value reported
# in the original draft did not match the underlying run-by-run data.
N_RUNS = 50
 
# "side" (left/right, spaced) or "stacked" (top/bottom)
FIG4_LAYOUT = "side"
 
GRID_SIZE = base.GRID_SIZE
START = base.START
GOAL = base.GOAL
STATIC_OBS_LABELS = base.STATIC_OBS_LABELS
DANGER_RADIUS = novelty.DANGER_RADIUS
K_PENALTY = novelty.K_PENALTY
EPSILON = novelty.EPSILON
 
GRID_CMAP = ListedColormap(["#ffffff", "#a9a9a9", "#000000"])  # free, buffer, obstacle
 
 
# ─────────────────────────── shared helpers ───────────────────────────
 
def draw_grid(ax, grid):
    ax.imshow(grid, cmap=GRID_CMAP, origin="upper",
              extent=[0, GRID_SIZE, GRID_SIZE, 0], vmin=0, vmax=2)
    ax.set_xticks(np.arange(0, GRID_SIZE + 1, 1))
    ax.set_yticks(np.arange(0, GRID_SIZE + 1, 1))
    ax.grid(which="major", color="#cccccc", linewidth=0.5)
    ax.set_xlim(0, GRID_SIZE)
    ax.set_ylim(GRID_SIZE, 0)
    ax.tick_params(labelsize=7)
 
 
def draw_path(ax, path, color, lw=2.2):
    if not path:
        return
    px = [n[1] + 0.5 for n in path]
    py = [n[0] + 0.5 for n in path]
    ax.plot(px, py, color=color, linewidth=lw, zorder=6)
 
 
def draw_start_goal(ax):
    ax.scatter(START[1] + 0.5, START[0] + 0.5, c="green", s=90,
               marker="o", edgecolors="black", linewidths=0.8, zorder=10)
    ax.scatter(GOAL[1] + 0.5, GOAL[0] + 0.5, c="blue", s=110,
               marker="X", edgecolors="black", linewidths=0.8, zorder=10)
 
 
def draw_obstacle_trajectory(ax, dyn_obs_list):
    for o in dyn_obs_list:
        xs = [p[1] + 0.5 for p in o.traj]
        ys = [p[0] + 0.5 for p in o.traj]
        ax.plot(xs, ys, color="orange", linestyle="--", linewidth=0.8, alpha=0.8, zorder=3)
        ax.scatter(xs[-1], ys[-1], c="orange", s=45, marker="s",
                   edgecolors="black", linewidths=0.5, zorder=9)
 
 
# ─────────────────────────── Figure 1 ───────────────────────────
 
def make_figure1(grid):
    fig, ax = plt.subplots(figsize=(6, 6))
    draw_grid(ax, grid)
    draw_start_goal(ax)
    ax.set_title(f"{GRID_SIZE}\u00d7{GRID_SIZE} grid environment: 8 static obstacle groups")
    handles = [
        plt.Line2D([], [], marker="o", color="w", markerfacecolor="green",
                    markeredgecolor="black", markersize=9, label="Start"),
        plt.Line2D([], [], marker="X", color="w", markerfacecolor="blue",
                    markeredgecolor="black", markersize=10, label="Goal"),
    ]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=True)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "Figure1_grid_environment.png"), dpi=150)
    plt.close(fig)
 
 
# ─────────────────────────── Figure 2 ───────────────────────────
 
def make_figure2():
    # synthetic cost field around a single moving obstacle at the centre
    # of a 15x15 patch, using the same penalty formulas as trans_prob()
    span = 15
    center = (span // 2, span // 2)
    yy, xx = np.meshgrid(np.arange(span), np.arange(span), indexing="ij")
    d = np.sqrt((yy - center[0]) ** 2 + (xx - center[1]) ** 2)
 
    hard_block = np.where(d < 0.5, 20.0, 0.0)
    soft_cost = np.where(d < DANGER_RADIUS, K_PENALTY / (d + EPSILON), 0.0)
 
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    fig.suptitle("Cell cost around a moving obstacle: hard block vs. danger-radius", y=1.02)
 
    im0 = axes[0].imshow(hard_block, cmap="YlOrRd", vmin=0, vmax=20, origin="upper")
    axes[0].set_title("Hard block (HB)\n(cost is 0 or \u221e, changes only at contact)", fontsize=10)
    axes[0].set_xticks([]); axes[0].set_yticks([])
    axes[0].scatter(center[1], center[0], marker="s", s=40, facecolor="darkred", edgecolor="black")
 
    im1 = axes[1].imshow(soft_cost, cmap="YlOrRd", vmin=0, vmax=20, origin="upper")
    axes[1].set_title("Danger-radius (DR)\n(cost fades smoothly with distance)", fontsize=10)
    axes[1].set_xticks([]); axes[1].set_yticks([])
    axes[1].scatter(center[1], center[0], marker="s", s=40, facecolor="darkred", edgecolor="black")
 
    cbar = fig.colorbar(im1, ax=axes, fraction=0.035, pad=0.02)
    cbar.set_label("Added cost term (pen)")
 
    fig.savefig(os.path.join(OUT_DIR, "Figure2_cost_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
 
 
# ─────────────────────────── Figure 3 ───────────────────────────
 
def make_figure3(grid, radii=(1.5, 2.5, 3.5, 4.5, 5.5), runs_per_point=5, seed_base=100):
    """Sweep DANGER_RADIUS (novelty module) holding K_PENALTY fixed."""
    mean_turns, mean_lengths = [], []
    original_radius = novelty.DANGER_RADIUS
    try:
        for R in radii:
            novelty.DANGER_RADIUS = R
            lengths, turns = [], []
            for run in range(runs_per_point):
                result = novelty.run_abaco(grid, use_novelty=True, seed=seed_base + run)
                lengths.append(result["best_distance"])
                turns.append(result["sharp_turns"])
            mean_lengths.append(float(np.mean(lengths)))
            mean_turns.append(float(np.mean(turns)))
    finally:
        novelty.DANGER_RADIUS = original_radius  # always restore the global
 
    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax2 = ax1.twinx()
 
    ax1.plot(radii, mean_turns, "o-", color="#1f77b4")
    ax1.set_xlabel("Danger radius R (cells)")
    ax1.set_ylabel("Mean sharp turns", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")
 
    ax2.plot(radii, mean_lengths, "s-", color="#d62728")
    ax2.set_ylabel("Mean path length (m)", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")
 
    used = novelty.DANGER_RADIUS
    ax1.axvline(used, color="gray", linestyle="--", linewidth=1)
    ax1.set_title(
        f"Effect of danger radius R on smoothness and path length\n"
        f"(K_PENALTY fixed at {K_PENALTY}, {runs_per_point} runs per point, "
        f"dashed line = value used elsewhere)",
        fontsize=10,
    )
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "Figure3_danger_radius_effect.png"), dpi=150)
    plt.close(fig)
 
 
# ─────────────────────────── Figure 4 ───────────────────────────
 
def make_figure4(grid, base_best, novelty_best, layout=FIG4_LAYOUT):
    def panel(ax, result, color, label):
        draw_grid(ax, grid)
        draw_obstacle_trajectory(ax, result["dyn_obs"])
        draw_path(ax, result["best_path"], color)
        draw_start_goal(ax)
        ax.set_title(
            f"{label}\nlen={result['best_distance']:.2f} m, "
            f"sharp turns={result['sharp_turns']}",
            fontsize=10, pad=10,
        )
 
    if layout == "stacked":
        fig, axes = plt.subplots(2, 1, figsize=(6, 12))
    else:
        fig, axes = plt.subplots(1, 2, figsize=(13, 6.2))
        fig.subplots_adjust(wspace=0.35)  # extra breathing room between panels
 
    panel(axes[0], base_best, "red", "Hard block (HB)")
    panel(axes[1], novelty_best, "blue", "Danger-radius (DR)")
 
    # suptitle sits well above both panel titles instead of overlapping them
    fig.suptitle(
        f"Hard block vs. danger-radius: best path over {N_RUNS} runs (orange dashed = obstacle trajectory)",
        y=1.04, fontsize=12,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(OUT_DIR, "Figure4_best_path_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
 
 
# ─────────────────────────── Figure 5 ───────────────────────────
 
def make_figure5(base_best, novelty_best):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(np.arange(1, len(base_best["iter_dists"]) + 1), base_best["iter_dists"],
            color="red", linewidth=1.8, label="Hard block (HB)")
    ax.plot(np.arange(1, len(novelty_best["iter_dists"]) + 1), novelty_best["iter_dists"],
            color="blue", linewidth=1.8, label="Danger-radius (DR)")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Best path length (m)")
    ax.set_title("Convergence: hard block vs. danger-radius")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "Figure5_convergence.png"), dpi=150)
    plt.close(fig)
 
 
# ─────────────────────────── Figure 6 ───────────────────────────
 
def _wilcoxon_p(base_vals, novelty_vals):
    try:
        _, p = stats.wilcoxon(base_vals, novelty_vals)
    except ValueError:
        p = float("nan")
    return p


def make_figure6(base_results, novelty_results):
    n = len(base_results)
    idx = np.arange(n)
    w = 0.35

    base_len = [r["best_distance"] for r in base_results]
    nov_len = [r["best_distance"] for r in novelty_results]
    base_turns = [r["sharp_turns"] for r in base_results]
    nov_turns = [r["sharp_turns"] for r in novelty_results]
    base_clear = [r["min_clearance"] for r in base_results]
    nov_clear = [r["min_clearance"] for r in novelty_results]

    # Wilcoxon signed-rank p-values, reported alongside each panel so the
    # figure matches the significance test used in Table 3 / Section 5.3
    # rather than only showing raw per-run bars.
    p_len = _wilcoxon_p(base_len, nov_len)
    p_turns = _wilcoxon_p(base_turns, nov_turns)
    p_clear = _wilcoxon_p(base_clear, nov_clear)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    fig.suptitle(f"Hard block vs. danger-radius over {n} paired runs", y=1.03)

    axes[0].bar(idx - w / 2, base_len, w, color="red", label="Hard block (HB)")
    axes[0].bar(idx + w / 2, nov_len, w, color="blue", label="Danger-radius (DR)")
    axes[0].set_title(f"Path length per seed\nWilcoxon p={p_len:.4f}", fontsize=10)
    axes[0].set_xlabel("Run (seed index)")
    axes[0].set_ylabel("m")
    axes[0].legend(fontsize=8)

    axes[1].bar(idx - w / 2, base_turns, w, color="red", label="Hard block (HB)")
    axes[1].bar(idx + w / 2, nov_turns, w, color="blue", label="Danger-radius (DR)")
    axes[1].set_title(f"Sharp turns (>45\u00b0) per seed\nWilcoxon p={p_turns:.4f}", fontsize=10)
    axes[1].set_xlabel("Run (seed index)")
    axes[1].set_ylabel("count")

    axes[2].bar(idx - w / 2, base_clear, w, color="red", label="Hard block (HB)")
    axes[2].bar(idx + w / 2, nov_clear, w, color="blue", label="Danger-radius (DR)")
    axes[2].set_title(f"Minimum clearance per seed\nWilcoxon p={p_clear:.4f}", fontsize=10)
    axes[2].set_xlabel("Run (seed index)")
    axes[2].set_ylabel("cells")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "Figure6_per_run_metrics.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
 
 
# ─────────────────────────── Figure 7 ───────────────────────────
 
def make_figure7(grid, novelty_best, iterations=(25, 50, 75, 100), layout="2x2"):
    snaps = novelty_best["snapshots"]
 
    if layout == "2x2":
        fig, axes = plt.subplots(2, 2, figsize=(11, 11))
        axes = axes.ravel()
    else:
        fig, axes = plt.subplots(1, 4, figsize=(20, 5.5))
 
    for ax, it in zip(axes, iterations):
        snap = snaps[it - 1]
        draw_grid(ax, grid)
 
        for dp in snap["dyn"]:
            for br in range(GRID_SIZE):
                for bc in range(GRID_SIZE):
                    if novelty.dist((br, bc), dp) < DANGER_RADIUS:
                        ax.add_patch(mpatches.Rectangle((bc, br), 1, 1, color="gold", alpha=0.25, ec="none"))
            ax.scatter(dp[1] + 0.5, dp[0] + 0.5, c="magenta", s=70, marker="s",
                       edgecolors="black", linewidths=0.8, zorder=8)
 
        draw_path(ax, snap["best"], "#1f77b4", lw=2.2)
        draw_start_goal(ax)
        ax.set_title(f"Iteration {it}/{novelty.NUM_ITERATIONS}", fontsize=11)
 
    fig.suptitle("Danger-radius (DR) path progression with buffer zone (gold) around moving obstacles", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(OUT_DIR, "Figure7_path_progression.png"), dpi=150)
    plt.close(fig)
 
 
# ─────────────────────────── driver ───────────────────────────
 
def main():
    grid = base.create_grid()
 
    print(f"Running baseline experiment ({N_RUNS} paired runs)...")
    base_experiment = base.run_abaco_experiment(grid, runs=N_RUNS,
                                                 use_novelty=False, seed=base.SEED)
    print(f"Running novelty experiment ({N_RUNS} paired runs)...")
    novelty_experiment = novelty.run_abaco_experiment(grid, runs=N_RUNS,
                                                       use_novelty=True, seed=novelty.SEED)
 
    base_results = base_experiment["runs"]
    novelty_results = novelty_experiment["runs"]
    base_best = base_experiment["best_run"]
    novelty_best = novelty_experiment["best_run"]
 
    print("Figure 1 - grid environment")
    make_figure1(grid)
 
    print("Figure 2 - cost field comparison")
    make_figure2()
 
    print("Figure 3 - danger radius sensitivity (this reruns the novelty experiment "
          "5 times per radius value, so it takes the longest)")
    make_figure3(grid)
 
    print("Figure 4 - best path comparison")
    make_figure4(grid, base_best, novelty_best)
 
    print("Figure 5 - convergence curves")
    make_figure5(base_best, novelty_best)
 
    print("Figure 6 - per-run metrics")
    make_figure6(base_results, novelty_results)
 
    print("Figure 7 - novelty path progression")
    make_figure7(grid, novelty_best)
 
    print(f"\nAll figures written to ./{OUT_DIR}/")
 
 
if __name__ == "__main__":
    main()
 
