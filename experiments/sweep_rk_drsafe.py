"""
sweep_rk_drsafe.py  --  joint R x K re-sweep for DR-SAFE (and DR, for symmetry)

WHY THIS EXISTS
    The paper's R = 3.5 / K = 2.0 were chosen from two one-dimensional,
    5-run sweeps on *plain DR*. DR-SAFE -- the method actually proposed --
    was never swept. This script sweeps R and K *jointly* for DR-SAFE, and
    for plain DR on the identical grid, so that in the confirmatory run each
    method can be reported both at the original parameters and at its own
    tuned parameters.

PROTOCOL (fixed before running; do not edit after seeing results)
    * TUNING seeds  : seed_base .. seed_base+n-1  with seed_base = 5000.
                      Disjoint from the paper's N=50 seeds (42..91), from the
                      old sweeps (100..104), from the D_SAFE probes (300..)
                      and from the confirmatory seeds (10000+). Tuning and
                      evaluation therefore never share seeds.
    * Grid          : R in {2.5, 3.0, 3.5, 4.0, 4.5, 5.5}
                      K in {1.0, 2.0, 3.0, 4.0}
                      D_SAFE fixed at 1.5 (value used in the paper).
    * n per cell    : 30 paired seeds (same seeds for every cell and for HB).
    * Selection rule: implemented in analyze_rk_sweep.py (equal-weight
                      composite of z-scored turns, length, collisions/run and
                      -clearance across grid cells; lowest wins).

Checkpointed: re-invoking resumes. Loops seed-major so that an interrupted
sweep still has equal n in every cell.

Usage:  python experiments/sweep_rk_drsafe.py [--n 30] [--seed-base 5000]
"""
import argparse, os, time
import drsafe_lib as L

R_GRID = [2.5, 3.0, 3.5, 4.0, 4.5, 5.5]
K_GRID = [1.0, 2.0, 3.0, 4.0]
OUT = os.path.join(L.RESULTS_DIR, "rk_sweep_drsafe.json")


def key(method, R, K, seed):
    return f"{method}|{R}|{K}|{seed}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--seed-base", type=int, default=5000)
    ap.add_argument("--no-dr", action="store_true", help="skip the plain-DR grid")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()

    ck = L.load_ckpt(a.out, {"meta": dict(r_grid=R_GRID, k_grid=K_GRID,
                                          d_safe=L.DEFAULT_D_SAFE,
                                          seed_base=a.seed_base, n=a.n),
                             "runs": {}})
    runs = ck["runs"]
    t0 = time.time()
    for i in range(a.n):
        seed = a.seed_base + i
        todo = []
        if key("HB", "-", "-", seed) not in runs:
            todo.append(("HB", None, None))
        for R in R_GRID:
            for K in K_GRID:
                if key("DRS", R, K, seed) not in runs:
                    todo.append(("DRS", R, K))
                if not a.no_dr and key("DR", R, K, seed) not in runs:
                    todo.append(("DR", R, K))
        if not todo:
            continue
        for m, R, K in todo:
            if m == "HB":
                r = L.run_hb(seed)
            elif m == "DR":
                r = L.run_dr(seed, R=R, K=K)
            else:
                r = L.run_drs(seed, R=R, K=K)
            runs[key(m, R if R is not None else "-", K if K is not None else "-", seed)] = r
        L.save_ckpt(a.out, ck)
        print(f"seed {seed} ({i+1}/{a.n}) done; elapsed {time.time()-t0:.0f}s", flush=True)
    print("sweep complete")


if __name__ == "__main__":
    main()
