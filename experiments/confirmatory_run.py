"""
confirmatory_run.py -- large-N paired evaluation on FRESH seeds, storing every
per-run value (the old batch script only kept the total collision count, which
made a paired collision test impossible).

Arms (all share the same seed per index => same obstacle motion / RNG start):
    HB    hard block
    DR    plain danger-radius at (R, K) = (3.5, 2.0)     [paper values]
    DRS   DR-SAFE at (3.5, 2.0, D_SAFE=1.5)              [paper values]
    DRST  DR-SAFE at the parameters selected by analyze_rk_sweep.py   (optional)
    DRT   plain DR at its own selected parameters                      (optional)

Two uses:
    pilot (re-creates the paper's N=50 with per-run collisions):
        python experiments/confirmatory_run.py --seed-base 42 --n 50 \
               --out results/pilot_n50_perrun.json
    confirmatory (fresh seeds, N chosen by power_analysis.py):
        python experiments/confirmatory_run.py --seed-base 10000 --n 300 \
               --tuned-drs 4.5,3.0 --tuned-dr 3.5,2.0 --out results/confirmatory_perrun.json

Checkpointed after every seed; re-invoke to resume.
"""
import argparse, os, time
import drsafe_lib as L


def parse_pair(s):
    if not s:
        return None
    r, k = s.split(",")
    return float(r), float(k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-base", type=int, required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tuned-drs", default="", help="R,K selected for DR-SAFE")
    ap.add_argument("--tuned-dr", default="", help="R,K selected for plain DR")
    a = ap.parse_args()
    out = a.out if os.path.isabs(a.out) else os.path.join(L.ROOT, a.out)
    tdrs, tdr = parse_pair(a.tuned_drs), parse_pair(a.tuned_dr)

    ck = L.load_ckpt(out, {"meta": dict(seed_base=a.seed_base, n=a.n, tuned_drs=tdrs, tuned_dr=tdr,
                                        default=[L.DEFAULT_R, L.DEFAULT_K, L.DEFAULT_D_SAFE]),
                           "runs": {}})
    runs = ck["runs"]
    t0 = time.time()
    for i in range(a.n):
        seed = a.seed_base + i
        rec = runs.setdefault(str(seed), {})
        if "HB" not in rec:
            rec["HB"] = L.run_hb(seed)
        if "DR" not in rec:
            rec["DR"] = L.run_dr(seed)
        if "DRS" not in rec:
            rec["DRS"] = L.run_drs(seed)
        if tdrs and "DRST" not in rec:
            rec["DRST"] = L.run_drs(seed, R=tdrs[0], K=tdrs[1])
        if tdr and "DRT" not in rec:
            rec["DRT"] = L.run_dr(seed, R=tdr[0], K=tdr[1])
        L.save_ckpt(out, ck)
        if (i + 1) % 5 == 0 or i + 1 == a.n:
            print(f"seed {seed} ({i+1}/{a.n}) elapsed {time.time()-t0:.0f}s", flush=True)
    print("complete")


if __name__ == "__main__":
    main()
