"""Priority 13: multi-noise 300-seed main-environment evaluation.

Tuning is performed before confirmation on disjoint seeds, with the same six
candidate evaluations x 30 tuning seeds for HB, HBP and APF-predicted.
HBP/APFP are tuned separately at each nonzero noise level; HB is noise-invariant
and is tuned once on the clean block. Confirmation uses fresh seeds 10300-10599.
Noise levels: 5deg/10%, 15deg/20%, 30deg/40%.
"""
import os, json, time, itertools, argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import drsafe_lib as L
import ABACO_safety_pred as P

NOISES = {
    "n1": (5.0, 0.10),
    "n": (15.0, 0.20),
    "n3": (30.0, 0.40),
}
# Equal six-candidate budget for all three methods. APF's eta is tuned jointly
# with colony size/iterations rather than receiving an extra parameter sweep.
HB_CAND = [
    {"ants":20,"iterations":50,"label":"a20_i50"},
    {"ants":20,"iterations":100,"label":"a20_i100"},
    {"ants":40,"iterations":50,"label":"a40_i50"},
    {"ants":40,"iterations":100,"label":"a40_i100"},
    {"ants":60,"iterations":50,"label":"a60_i50"},
    {"ants":60,"iterations":100,"label":"a60_i100"},
]
APF_CAND = [
    {"ants":20,"iterations":50,"eta":1.0,"label":"a20_i50_e1"},
    {"ants":20,"iterations":100,"eta":2.0,"label":"a20_i100_e2"},
    {"ants":40,"iterations":50,"eta":2.0,"label":"a40_i50_e2"},
    {"ants":40,"iterations":100,"eta":4.0,"label":"a40_i100_e4"},
    {"ants":60,"iterations":50,"eta":4.0,"label":"a60_i50_e4"},
    {"ants":60,"iterations":100,"eta":8.0,"label":"a60_i100_e8"},
]
TUNE_SEEDS = list(range(9000,9030))
CONF_SEEDS = list(range(10300,10600))
ROOT = L.ROOT
OUTDIR = os.path.join(ROOT, "results", "priority13")
os.makedirs(OUTDIR, exist_ok=True)

def run_candidate(task):
    method, seed, noise_name, params = task
    noise = NOISES.get(noise_name, (0.0,0.0))
    old_a, old_i = L.base.NUM_ANTS, L.base.NUM_ITERATIONS
    try:
        L.base.NUM_ANTS, L.base.NUM_ITERATIONS = params["ants"], params["iterations"]
        if method == "HB":
            r = L.run_hb(seed)
        elif method == "HBP":
            r = L._flat(P.run_abaco_safety_pred(L.GRID, seed, noise=noise, mode="hb"), L.base)
        elif method == "APFP":
            old_k = L.base.K_PENALTY
            L.base.K_PENALTY = params.get("eta", 2.0)
            try:
                r = L._flat(P.run_abaco_safety_pred(L.GRID, seed, noise=noise, mode="apf"), L.base)
            finally:
                L.base.K_PENALTY = old_k
        else: raise ValueError(method)
        return {"method":method,"seed":seed,"noise":noise_name,"params":params,"result":r}
    finally:
        L.base.NUM_ANTS, L.base.NUM_ITERATIONS = old_a, old_i

def score(rows):
    # Same scalar tuning rule for all methods: prioritize collision avoidance,
    # then failed-path rate, then sharp turns. This is a tuning criterion only.
    n=len(rows)
    coll=sum((r["coll"] or 0) for r in rows)/n
    fail=sum(not r["ok"] for r in rows)/n
    turns=[r["turns"] for r in rows if r["ok"]]
    t=(sum(turns)/len(turns) if turns else 999.0)/30.0
    return 0.50*coll + 0.25*fail + 0.25*t

def tune(method, noise_name):
    cands = HB_CAND if method in ("HB","HBP") else APF_CAND
    tasks=[(method,s,noise_name,p) for p in cands for s in TUNE_SEEDS]
    rows=[]
    with ProcessPoolExecutor(max_workers=5) as ex:
        futs=[ex.submit(run_candidate,t) for t in tasks]
        for fut in as_completed(futs): rows.append(fut.result())
    by={}
    for r in rows: by.setdefault(r["params"]["label"],[]).append(r["result"])
    summary=[]
    for p in cands:
        rr=by[p["label"]]
        summary.append({"params":p,"score":score(rr),"n":len(rr),
                        "collision_rate":sum((x["coll"] or 0) for x in rr)/len(rr),
                        "failure_rate":sum(not x["ok"] for x in rr)/len(rr),
                        "mean_turns_successful":sum(x["turns"] for x in rr if x["ok"])/max(1,sum(x["ok"] for x in rr))})
    best=min(summary,key=lambda x:x["score"])
    path=os.path.join(OUTDIR,f"tuning_{method}_{noise_name}.json")
    json.dump({"method":method,"noise":NOISES.get(noise_name,(0,0)),"tuning_seeds":TUNE_SEEDS,"candidates":summary,"selected":best},open(path,"w"),indent=2)
    return best

def confirm(method, noise_name, params):
    tasks=[(method,s,noise_name,params) for s in CONF_SEEDS]
    rows=[]
    with ProcessPoolExecutor(max_workers=5) as ex:
        futs=[ex.submit(run_candidate,t) for t in tasks]
        for i,fut in enumerate(as_completed(futs),1):
            rows.append(fut.result())
            if i%25==0: print(method,noise_name,i,"/",len(tasks),flush=True)
    rows=sorted(rows,key=lambda x:x["seed"])
    path=os.path.join(OUTDIR,f"confirmation_{method}_{noise_name}.json")
    json.dump({"method":method,"noise":NOISES.get(noise_name,(0,0)),"confirmation_seeds":CONF_SEEDS,"params":params,"runs":rows},open(path,"w"),indent=2)
    return path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--skip-tuning",action="store_true"); args=ap.parse_args()
    selected={}
    if not args.skip_tuning:
        selected["HB"]=tune("HB","clean")
        for nz in NOISES:
            selected[f"HBP_{nz}"]=tune("HBP",nz)
            selected[f"APFP_{nz}"]=tune("APFP",nz)
        json.dump(selected,open(os.path.join(OUTDIR,"selected_tuning.json"),"w"),indent=2)
    else:
        selected=json.load(open(os.path.join(OUTDIR,"selected_tuning.json")))
    hb_params=selected["HB"]["params"]
    # HB is noise-invariant: evaluate once, then use the same 300-run block for each noise comparison.
    confirm("HB","clean",hb_params)
    for nz in NOISES:
        confirm("HBP",nz,selected[f"HBP_{nz}"]["params"])
        confirm("APFP",nz,selected[f"APFP_{nz}"]["params"])
    json.dump({"tuning_seeds":TUNE_SEEDS,"confirmation_seeds":CONF_SEEDS,"noise_levels":NOISES,"selected":selected},open(os.path.join(OUTDIR,"protocol.json"),"w"),indent=2)

if __name__=='__main__': main()
