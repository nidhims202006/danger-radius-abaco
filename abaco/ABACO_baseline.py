"""
ABACO baseline path-planning demo.

FIX (vs. original): dynamic obstacles used to only be created when
use_novelty=True, which meant this "baseline" script never actually
encountered a moving obstacle. Obstacle existence is now unconditional;
use_novelty only switches the penalty rule inside trans_prob. This makes
the baseline a true "hard block" comparison against the novelty script's
"soft distance-based cost" — same environment, same obstacle motion,
same RNG stream, only the rule differs.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from matplotlib import animation
import math, random, time, sys
from exec_aligned_metrics import execution_aligned_metrics

# ══════════════════════ PARAMETERS ══════════════════════
GRID_SIZE        = 18
ALPHA, BETA      = 1.0, 5.0
RHO              = 0.3
NUM_ANTS         = 40
NUM_ITERATIONS   = 100
INITIAL_PHEROMONE = 1.0
# Q range
MAX_Q, MIN_Q     = 100.0, 10.0
MAX_STEPS        = 500
K_PENALTY        = 2.0
DANGER_RADIUS    = 3.5
EPSILON          = 0.1
FITNESS_EPSILON  = np.finfo(float).eps
NUM_EXPERIMENT_RUNS = 10
SEED             = 42          # paired runs share the same base seed;
                                # deterministic obstacle motion is identical.
                                # Random streams may desynchronise after paths diverge.

# Angle above which a heading change counts as a "sharp turn"
SHARP_TURN_DEG   = 45.0

START = (0, 0)
GOAL  = (17, 17)
DIRS  = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

# ══════════════════════ ENVIRONMENT ══════════════════════
# Static obstacles (0-indexed)
RAW_OBS_CELLS = {
    (2, 3),          # Obs1
    (1, 10),         # Obs2
    (6, 7), (6, 8), (6, 9), (6, 10),   # Obs3
    (8, 1),          # Obs4
    (9, 9),          # Obs5
    (5, 15),         # Obs6
    (12, 2), (12, 3), (12, 4), (12, 5), # Obs7
    (14, 13), (14, 14), (14, 15),        # Obs8
}

def create_grid():
    """0: free, 1: buffer, 2: obstacle."""
    g = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    for (r, c) in RAW_OBS_CELLS:
        # Buffer around obstacle
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    if (nr, nc) not in ((0, 0), (GRID_SIZE-1, GRID_SIZE-1)):
                        if g[nr, nc] == 0:
                            g[nr, nc] = 1
        g[r, c] = 2
    return g

STATIC_OBS_LABELS = {
    (2, 3):  "Obs1",
    (1, 10): "Obs2",
    (6, 7):  "Obs3", (6, 8): "Obs3", (6, 9): "Obs3", (6, 10): "Obs3",
    (8, 1):  "Obs4",
    (9, 9):  "Obs5",
    (5, 15): "Obs6",
    (12, 2): "Obs7", (12, 3): "Obs7", (12, 4): "Obs7", (12, 5): "Obs7",
    (14, 13):"Obs8", (14, 14):"Obs8", (14, 15): "Obs8",
}

# ══════════════════════ DYNAMIC OBSTACLES ══════════════════════
class DynObs:
    def __init__(self, r, c, v, angle_deg, name=""):
        self.x, self.y = float(c), float(r)
        self.v = v; self.theta = math.radians(angle_deg)
        self.traj = [(r, c)]; self.name = name
    def step(self):
        nx = self.x + self.v * math.cos(self.theta)
        ny = self.y + self.v * math.sin(self.theta)
        if nx < 0 or nx >= GRID_SIZE:
            self.theta = math.pi - self.theta
            nx = np.clip(nx, 0, GRID_SIZE-1)
        if ny < 0 or ny >= GRID_SIZE:
            self.theta = -self.theta
            ny = np.clip(ny, 0, GRID_SIZE-1)
        self.x, self.y = nx, ny
        pos = (int(round(self.y)), int(round(self.x)))
        self.traj.append(pos)
        return pos
    @property
    def pos(self): return (int(round(self.y)), int(round(self.x)))

def make_dyn_obs():
    return [
        DynObs(8,  8,  0.45, 45,  "DynObs1 (v=0.45, θ=45°)"),
        DynObs(4,  13, 0.40, 210, "DynObs2 (v=0.40, θ=210°)"),
        DynObs(13, 10, 0.38, 135, "DynObs3 (v=0.38, θ=135°)"),
    ]

# ══════════════════════ CORE ACO HELPERS ══════════════════════
dist = lambda a,b: math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

def neighbors(g, n):
    r,c = n; out = []
    for dr,dc in DIRS:
        nr,nc = r+dr, c+dc
        if 0<=nr<GRID_SIZE and 0<=nc<GRID_SIZE and g[nr,nc]==0:
            out.append((nr,nc))
    return out

class Pher:
    def __init__(self): self.m={}
    def get(self,a,b): return self.m.get(tuple(sorted((a,b))),INITIAL_PHEROMONE)
    def evap(self):
        for e in self.m: self.m[e]*=(1-RHO)
    def dep(self,a,b,amt):
        e=tuple(sorted((a,b))); self.m[e]=self.m.get(e,INITIAL_PHEROMONE)+amt

def trans_prob(cur, nbs, goal, ph, dyn_pos=None, use_novelty=False):
    """use_novelty=False (this script): a candidate cell within 0.5 of a
    moving obstacle is treated as effectively blocked (heavy fixed penalty),
    mirroring the base paper's binary occupied/free rule. The obstacle's
    *currently occupied* cell is already hard-blocked directly on the grid
    in run_abaco(); this penalty additionally discourages stepping onto a
    cell an obstacle is about to occupy this same instant."""
    ds = []
    for nb in nbs:
        tau = ph.get(cur, nb)
        eta = 1.0 / (dist(cur, nb) + FITNESS_EPSILON)
        if dyn_pos:
            if use_novelty:
                pen = sum(K_PENALTY/(dist(nb,op)+EPSILON)
                          for op in dyn_pos if dist(nb,op)<DANGER_RADIUS)
                eta /= (1.0 + pen)
            else:
                pen = sum(10.0 for op in dyn_pos if dist(nb,op)<0.5)
                eta /= (1.0 + pen)
        ds.append((tau**ALPHA)*(eta**BETA))
    t = sum(ds)
    return [d/t for d in ds] if t>0 else [1/len(nbs)]*len(nbs)

# ══════════════════════ RUN SIMULATION ══════════════════════
def path_fitness(path_length):
    """Fitness of a path."""
    return 1.0 / (path_length + FITNESS_EPSILON)


def construct_abaco_solution(grid, pheromone, dyn_pos, use_novelty, rng):
    """Build one path."""
    current = START
    path = [current]
    path_length = 0.0
    tabu = np.zeros((GRID_SIZE, GRID_SIZE), dtype=bool)
    tabu[current] = True

    for _layer in range(MAX_STEPS):
        if current == GOAL:
            return path, path_length, tabu
        feasible = [node for node in neighbors(grid, current) if not tabu[node]]
        if not feasible:
            break
        probabilities = trans_prob(current, feasible, GOAL, pheromone,
                                   dyn_pos, use_novelty)
        next_node = rng.choices(feasible, weights=probabilities, k=1)[0]
        path_length += dist(current, next_node)
        current = next_node
        path.append(current)
        tabu[current] = True
    return None, float('inf'), tabu


def age_based_q_values(lengths, rng):
    """Give higher Q values to shorter paths."""
    sampled_q = sorted((rng.uniform(MIN_Q, MAX_Q) for _ in lengths), reverse=True)
    shortest_first = np.argsort(lengths)
    return {int(ant_index): q for ant_index, q in zip(shortest_first, sampled_q)}


def count_sharp_turns(path, angle_threshold_deg=SHARP_TURN_DEG):
    """Number of heading changes greater than the threshold along a path.
    This is the key smoothness metric for comparing baseline vs. novelty."""
    if not path or len(path) < 3:
        return 0
    turns = 0
    for i in range(1, len(path) - 1):
        v1 = (path[i][0]-path[i-1][0], path[i][1]-path[i-1][1])
        v2 = (path[i+1][0]-path[i][0], path[i+1][1]-path[i][1])
        n1, n2 = math.hypot(*v1), math.hypot(*v2)
        if n1 == 0 or n2 == 0:
            continue
        cosang = max(-1.0, min(1.0, (v1[0]*v2[0]+v1[1]*v2[1])/(n1*n2)))
        ang = math.degrees(math.acos(cosang))
        if ang > angle_threshold_deg:
            turns += 1
    return turns


def run_abaco(grid, use_novelty=False, seed=SEED):
    """Run ABACO once. Dynamic obstacles are ALWAYS present; use_novelty
    only changes the penalty rule inside trans_prob (see docstring there)."""
    rng = random.Random(seed)
    np.random.seed(seed)
    ph = Pher()
    dyn = make_dyn_obs()          # <-- FIX: no longer gated on use_novelty
    best_p, best_d, best_g = [], float('inf'), 0.0
    conv = 0; sr_list = []; snapshots = []; iter_dists = []
    dyn_snap = []

    t0 = time.time()
    for it in range(NUM_ITERATIONS):
        dyn_pos = [o.step() for o in dyn]
        tg = grid.copy()
        for dp in dyn_pos:
            r,c = dp
            if 0<=r<GRID_SIZE and 0<=c<GRID_SIZE: tg[r,c]=1

        paths, dists, fitnesses = [], [], []
        sample_paths = []
        for ai in range(NUM_ANTS):
            path, path_length, _tabu = construct_abaco_solution(
                tg, ph, dyn_pos, use_novelty, rng)
            if path is not None:
                paths.append(path)
                dists.append(path_length)
                fitnesses.append(path_fitness(path_length))
                if ai < 5:
                    sample_paths.append(path)

        sr = len(paths)/NUM_ANTS*100; sr_list.append(sr)
        if not paths:
            iter_dists.append(best_d)
            snapshots.append({'best': list(best_p), 'samples': [], 'dyn': list(dyn_pos)})
            dyn_snap.append(list(dyn_pos))
            continue

        ph.evap()
        si = np.argsort(dists)
        q_by_ant = age_based_q_values(dists, rng)
        for idx in si:
            dep = q_by_ant[int(idx)] / dists[idx]
            for i in range(len(paths[idx])-1):
                ph.dep(paths[idx][i], paths[idx][i+1], dep)

        iteration_best = int(np.argmax(fitnesses))
        if fitnesses[iteration_best] > best_g:
            best_g = fitnesses[iteration_best]
            best_d = dists[iteration_best]
            best_p = paths[iteration_best]
            conv = it + 1

        iter_dists.append(best_d)
        snapshots.append({'best': list(best_p), 'samples': sample_paths, 'dyn': list(dyn_pos)})
        dyn_snap.append(list(dyn_pos))

    ct = time.time()-t0
    # Use the single repository-wide execution-aligned safety metric.
    # The returned safety fields use the repository-wide execution-aligned Method B metric.
    safety_collisions, safety_min_clearance = execution_aligned_metrics(
        {
            'best_path': best_p,
            'convergence': conv,
            'dyn_obs': dyn,
        },
        sys.modules[__name__]
    )
    sharp_turns = count_sharp_turns(best_p)

    return {
        'best_path': best_p, 'best_distance': best_d,
        'best_fitness': best_g,
        'computation_time': ct, 'convergence': conv,
        'success_rates': sr_list, 'iter_dists': iter_dists,
        'snapshots': snapshots, 'collisions': safety_collisions,
        'min_clearance': safety_min_clearance, 'dyn_obs': dyn,
        'sharp_turns': sharp_turns,
    }


def run_abaco_experiment(grid, runs=NUM_EXPERIMENT_RUNS, use_novelty=False,
                         seed=SEED):
    """Run the experiment several times."""
    results = [run_abaco(grid, use_novelty=use_novelty, seed=seed + run)
               for run in range(runs)]
    successful = [result for result in results if result['best_path']]
    if not successful:
        raise RuntimeError('ABACO found no feasible path in any execution.')

    best = min(successful, key=lambda result: result['best_distance'])
    distances = np.array([result['best_distance'] for result in successful])
    times = np.array([result['computation_time'] for result in successful])
    convergence = np.array([result['convergence'] for result in successful])
    turns = np.array([result['sharp_turns'] for result in successful])
    return {
        'runs': results,
        'best_run': best,
        'summary': {
            'runs': runs,
            'successful_runs': len(successful),
            'shortest_path': float(distances.min()),
            'mean_path': float(distances.mean()),
            'worst_path': float(distances.max()),
            'path_std': float(distances.std(ddof=0)),
            'mean_fitness': float(np.mean([r['best_fitness'] for r in successful])),
            'best_convergence_iteration': int(best['convergence']),
            'mean_convergence_iteration': float(convergence.mean()),
            'mean_execution_time': float(times.mean()),
            'mean_sharp_turns': float(turns.mean()),
            'best_sharp_turns': int(best['sharp_turns']),
        },
    }


def plot_convergence(results, title='ABACO convergence curve'):
    """Plot best path length by iteration."""
    values = np.asarray(results['iter_dists'], dtype=float)
    finite = np.isfinite(values)
    if not finite.any():
        raise RuntimeError('Cannot plot convergence: no feasible path was found.')
    values[~finite] = values[finite][0]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(np.arange(1, len(values) + 1), values, color='#d62728', linewidth=2)
    ax.set(xlabel='Iteration', ylabel='Best path length (m)', title=title)
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    return fig, ax

# ══════════════════════ ANIMATION HELPER ══════════════════════
def animate_exploration(results, grid, title_prefix, is_novelty=False):
    snaps = results['snapshots']
    frames = list(range(0, len(snaps), 2))
    if frames[-1] != len(snaps)-1: frames.append(len(snaps)-1)

    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')

    def update(frame_idx):
        ax.clear()
        it = frames[frame_idx]
        snap = snaps[it]
        bd = results['iter_dists'][it] if it < len(results['iter_dists']) else results['best_distance']
        sr = results['success_rates'][it] if it < len(results['success_rates']) else 0

        cmap = ListedColormap(['#e8e8e8', '#888888', '#1a1a1a'])
        ax.imshow(grid, cmap=cmap, origin='upper', extent=[0,GRID_SIZE,GRID_SIZE,0], vmin=0, vmax=2)
        ax.set_xticks(np.arange(0,GRID_SIZE+1,1))
        ax.set_yticks(np.arange(0,GRID_SIZE+1,1))
        ax.grid(which='major', color='#555555', linewidth=0.3)
        ax.set_xlim(0,GRID_SIZE); ax.set_ylim(GRID_SIZE,0)
        ax.tick_params(colors='white', labelsize=7)
        for spine in ax.spines.values(): spine.set_color('white')

        labeled = set()
        for (r,c), lbl in STATIC_OBS_LABELS.items():
            if lbl not in labeled:
                ax.text(c+0.5, r+0.5, lbl, ha='center', va='center',
                        fontsize=6, color='#ff6b6b', fontweight='bold')
                labeled.add(lbl)

        if snap['dyn']:
            dyn_colors = ['#ff00ff', '#ff8c00', '#00ffff']
            for di, dp in enumerate(snap['dyn']):
                if is_novelty:
                    for br in range(GRID_SIZE):
                        for bc in range(GRID_SIZE):
                            if dist((br, bc), dp) < DANGER_RADIUS:
                                buf = mpatches.Rectangle((bc, br), 1, 1,
                                                         color='gold', alpha=0.15, ec='none')
                                ax.add_patch(buf)
                ax.scatter(dp[1]+0.5, dp[0]+0.5, c=dyn_colors[di],
                           s=300, marker='s', edgecolors='white',
                           linewidths=2, zorder=8)
                ax.annotate(f"DynObs{di+1}", (dp[1]+0.5, dp[0]+0.5),
                            textcoords="offset points", xytext=(8,-12),
                            fontsize=7, color=dyn_colors[di], fontweight='bold')

        for sp in snap.get('samples', []):
            if sp:
                px = [n[1]+0.5 for n in sp]
                py = [n[0]+0.5 for n in sp]
                ax.plot(px, py, color='#aaaaaa', linewidth=0.8, alpha=0.4)

        bp = snap['best']
        path_color = '#4fc3f7' if is_novelty else '#ff5252'
        if bp:
            px = [n[1]+0.5 for n in bp]
            py = [n[0]+0.5 for n in bp]
            ax.plot(px, py, color=path_color, linewidth=3, marker='.',
                    markersize=6, zorder=6, alpha=0.9)

        ax.scatter(START[1]+0.5, START[0]+0.5, c='#00ff00', s=250,
                   marker='o', edgecolors='white', linewidths=2, zorder=10)
        ax.scatter(GOAL[1]+0.5, GOAL[0]+0.5, c='#00e5ff', s=250,
                   marker='X', edgecolors='white', linewidths=2, zorder=10)
        ax.set_title(f"{title_prefix}", fontsize=14, fontweight='bold', color='white', pad=10)

        metrics_text = (
            f"Iteration: {it+1}/{NUM_ITERATIONS}\n"
            f"Distance Covered: {bd:.2f} m"
        )
        ax.text(0.02, 0.04, metrics_text, color='#ffd700', fontsize=12, fontweight='bold',
                transform=ax.transAxes,
                bbox=dict(facecolor='#1a1a2e', edgecolor='#ffd700', alpha=0.9, pad=8),
                verticalalignment='bottom')

        handles = [
            mpatches.Patch(color='#1a1a1a', label='Static Obstacles (fixed)'),
            plt.Line2D([],[],color=path_color,lw=3,label='Best Path So Far'),
            plt.Line2D([],[],color='#aaaaaa',lw=1,label='Ant Exploration Paths'),
            mpatches.Patch(color='#ff00ff',label='Dynamic Obstacle (moving)')
        ]
        if is_novelty:
            handles.append(mpatches.Patch(color='gold', alpha=0.3, label='Safety Buffer Zone (Grid)'))

        ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1.04, 1),
                  fontsize=10, facecolor='#2c2c54', edgecolor='white', labelcolor='white')

    anim = animation.FuncAnimation(fig, update, frames=len(frames),
                                   interval=150, repeat=False)
    plt.subplots_adjust(top=0.90, bottom=0.05, left=0.05, right=0.7)
    plt.show()
    return anim


if __name__ == '__main__':
    print('=' * 60)
    print('  BASELINE ABACO (hard block, dynamic obstacles present)')
    print('=' * 60)

    grid = create_grid()
    print(f'\nRunning {NUM_EXPERIMENT_RUNS} baseline ABACO executions...')
    experiment = run_abaco_experiment(
        grid, runs=NUM_EXPERIMENT_RUNS, use_novelty=False, seed=SEED)
    best_run = experiment['best_run']
    summary = experiment['summary']

    print('\nResults')
    print(f"Successful runs: {summary['successful_runs']}/{summary['runs']}")
    print(f"Shortest path:   {summary['shortest_path']:.4f} m")
    print(f"Mean path:       {summary['mean_path']:.4f} m")
    print(f"Worst path:      {summary['worst_path']:.4f} m")
    print(f"Path std. dev.:  {summary['path_std']:.4f} m")
    print(f"Best convergence iteration: {summary['best_convergence_iteration']}")
    print(f"Mean execution time: {summary['mean_execution_time']:.3f} s")
    print(f"Mean sharp turns (>{SHARP_TURN_DEG:.0f}\u00b0): {summary['mean_sharp_turns']:.2f}")
    print(f"Best-run sharp turns: {summary['best_sharp_turns']}")

    animation_reference = animate_exploration(
        best_run, grid, 'BASELINE ABACO', is_novelty=False)
    convergence_figure, _ = plot_convergence(
        best_run, 'Baseline ABACO: convergence curve (best of 10 executions)')
    convergence_figure.show()
