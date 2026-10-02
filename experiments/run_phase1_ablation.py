"""Phase-1 implementation ablation for the continuous DR-T cost.

Uses the frozen v22 main environment and paired seeds 10000--10299 only as an
implementation sanity check. The frozen planner is not modified. Frozen v22
reference values are read from results/ablation_main.json; only the new
continuous implementation is executed here.
"""
import json, os, sys, time
import drsafe_lib as L
import ABACO_safety_pred_continuous as NEW

ROOT = L.ROOT
OUT = os.path.join(ROOT, "results", "phase1_continuous_ablation.json")
OLD_REF = os.path.join(ROOT, "results", "ablation_main.json")


def flat(res):
    return L._flat(res, L.base)


def run(seed, d_safe):
    return flat(NEW.run_abaco_safety_pred(L.GRID, seed=seed, d_safe=d_safe, R=4.5, K=2.0, mode="safe"))


def main(lo, hi):
    t0=time.time()
    ck=L.load_ckpt(OUT, {"meta": {"seeds":"10000-10299", "R":4.5, "K":2.0,
        "cost_old":"K/(d+eps) for d<R", "cost_new":"K*max(0,1/(d+eps)-1/(R+eps))",
        "reference":"results/ablation_main.json"}, "runs": {}})
    for seed in range(lo, hi):
        rec=ck["runs"].setdefault(str(seed), {})
        if "SOFT_CONT" not in rec: rec["SOFT_CONT"]=run(seed, 0.0)
        if "DRSAFE_CONT" not in rec: rec["DRSAFE_CONT"]=run(seed, 1.5)
        L.save_ckpt(OUT, ck)
    print(f"complete {lo}-{hi-1} ({time.time()-t0:.1f}s)")

if __name__ == "__main__":
    lo=int(sys.argv[1]) if len(sys.argv)>1 else 10000
    hi=int(sys.argv[2]) if len(sys.argv)>2 else 10300
    main(lo,hi)
