"""Priority-13 extension: add continuous time-aligned DR-T and DR-SAFE-T.

This is deliberately a separate supplementary fixed-grid extension of the
existing Priority-13 study. It uses danger_radius/ABACO_safety_pred_continuous.py,
not the Phase-2 closed-loop v2 adapter, so it must not be merged with the
closed-loop confirmation numbers.

Protocol is matched to Priority-13:
- estimation-noise levels: n1=(5 deg,10%), n=(15 deg,20%), n3=(30 deg,40%)
- tuning seeds: 9000-9029
- confirmation seeds: 10300-10599
- six candidates per method/noise block
- candidate budget is identical for DR-T and DR-SAFE-T
- R sweep explicitly includes 3.5, 4.5, 5.5
- K is swept jointly; DR-SAFE-T keeps D_SAFE=1.5 fixed
"""
import os, json, argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

import drsafe_lib as L
import ABACO_safety_pred_continuous_v2 as C

NOISES = {
    "n1": (5.0, 0.10),
    "n": (15.0, 0.20),
    "n3": (30.0, 0.40),
}
TUNE_SEEDS = list(range(9000, 9030))
CONF_SEEDS = list(range(10300, 10600))
D_SAFE = 1.5
# Six candidates, identical search budget for DR-T and DR-SAFE-T.
CANDS = [
    {"R":3.5,"K":2.0,"d_safe":D_SAFE,"ants":20,"iterations":50,"label":"a20_i50_R3.5"},
    {"R":4.5,"K":2.0,"d_safe":D_SAFE,"ants":20,"iterations":100,"label":"a20_i100_R4.5"},
    {"R":5.5,"K":2.0,"d_safe":D_SAFE,"ants":40,"iterations":50,"label":"a40_i50_R5.5"},
    {"R":3.5,"K":2.0,"d_safe":D_SAFE,"ants":40,"iterations":100,"label":"a40_i100_R3.5"},
    {"R":4.5,"K":2.0,"d_safe":D_SAFE,"ants":60,"iterations":50,"label":"a60_i50_R4.5"},
    {"R":5.5,"K":2.0,"d_safe":D_SAFE,"ants":60,"iterations":100,"label":"a60_i100_R5.5"},
]
ROOT = L.ROOT
OUT = os.path.join(ROOT,"results","priority13_drt_extension_v3_clean")
os.makedirs(OUT,exist_ok=True)

def run_one(task):
    method, seed, noise_name, p = task
    noise = NOISES[noise_name]
    mode = "apf" if method == "APFP" else ("hb" if method == "HBP" else "safe")
    if method == "DRT":
        mode = "drt"
    old_a, old_i = L.base.NUM_ANTS, L.base.NUM_ITERATIONS
    try:
        L.base.NUM_ANTS, L.base.NUM_ITERATIONS = p["ants"], p["iterations"]
        # continuous module uses global hooks internally and restores them per run
        r = C.run_abaco_safety_pred(L.GRID, seed=seed, d_safe=p.get("d_safe",D_SAFE),
                                    R=p["R"], K=p["K"], mode=mode, noise=noise)
    finally:
        L.base.NUM_ANTS, L.base.NUM_ITERATIONS = old_a, old_i
    # The continuous module's DR-T mode is the same continuous time-aligned
    # soft term, without the floor. Flatten with the novelty metric definition.
    ok = bool(r.get("best_path"))
    if ok:
        c, mc = L.execution_aligned_metrics(r, L.base)
        out = {"ok":ok,"conv":int(r["convergence"]),"fb":int(r.get("safety_fallback_count",0)),
               "len":float(r["best_distance"]),"turns":int(r["sharp_turns"]),
               "clear":float(mc),"coll":int(c)}
    else:
        out = {"ok":False,"conv":int(r["convergence"]),"fb":int(r.get("safety_fallback_count",0)),
               "len":None,"turns":None,"clear":None,"coll":None}
    return {"method":method,"seed":seed,"noise":noise_name,"params":p,"result":out}

def score(rows):
    n=len(rows)
    coll=sum((r["coll"] or 0) for r in rows)/n
    fail=sum(not r["ok"] for r in rows)/n
    turns=[r["turns"] for r in rows if r["ok"]]
    t=(sum(turns)/len(turns) if turns else 999.0)/30.0
    return 0.50*coll + 0.25*fail + 0.25*t

def tune(method, noise_name):
    tasks=[(method,s,noise_name,p) for p in CANDS for s in TUNE_SEEDS]
    rows=[]
    with ProcessPoolExecutor(max_workers=6) as ex:
        futs=[ex.submit(run_one,t) for t in tasks]
        for f in as_completed(futs): rows.append(f.result())
    by={}
    for x in rows: by.setdefault(x["params"]["label"],[]).append(x["result"])
    summary=[]
    for p in CANDS:
        rr=by[p["label"]]
        oks=[x for x in rr if x["ok"]]
        summary.append({"params":p,"score":score(rr),"n":len(rr),
                        "collision_rate":sum((x["coll"] or 0)>0 for x in rr)/len(rr),
                        "failure_rate":sum(not x["ok"] for x in rr)/len(rr),
                        "mean_turns_successful":sum(x["turns"] for x in oks)/max(1,len(oks))})
    best=min(summary,key=lambda x:x["score"])
    data={"method":method,"noise":NOISES[noise_name],"tuning_seeds":TUNE_SEEDS,
          "candidate_count":len(CANDS),"candidates":summary,"selected":best}
    with open(os.path.join(OUT,f"tuning_{method}_{noise_name}.json"),"w") as f: json.dump(data,f,indent=2)
    print("TUNED",method,noise_name,best["params"],best["score"],flush=True)
    return best

def confirm(method, noise_name, params):
    tasks=[(method,s,noise_name,params) for s in CONF_SEEDS]
    rows=[]
    with ProcessPoolExecutor(max_workers=6) as ex:
        futs=[ex.submit(run_one,t) for t in tasks]
        for i,f in enumerate(as_completed(futs),1):
            rows.append(f.result())
            if i%50==0: print("CONF",method,noise_name,i,"/",len(tasks),flush=True)
    rows.sort(key=lambda x:x["seed"])
    with open(os.path.join(OUT,f"confirmation_{method}_{noise_name}.json"),"w") as f:
        json.dump({"method":method,"noise":NOISES[noise_name],"confirmation_seeds":CONF_SEEDS,
                   "params":params,"runs":rows},f,indent=2)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--skip-tuning",action="store_true"); args=ap.parse_args()
    selected={}
    if args.skip_tuning:
        selected=json.load(open(os.path.join(OUT,"selected_tuning.json")))
    else:
        for nz in NOISES:
            selected[f"DRT_{nz}"]=tune("DRT",nz)
            selected[f"DRSAFE_{nz}"]=tune("DRSAFE",nz)
        with open(os.path.join(OUT,"selected_tuning.json"),"w") as f: json.dump(selected,f,indent=2)
    for nz in NOISES:
        confirm("DRT",nz,selected[f"DRT_{nz}"]["params"])
        confirm("DRSAFE",nz,selected[f"DRSAFE_{nz}"]["params"])
    with open(os.path.join(OUT,"protocol.json"),"w") as f:
        json.dump({"noise_levels":NOISES,"tuning_seeds":TUNE_SEEDS,"confirmation_seeds":CONF_SEEDS,
                   "candidate_count":6,"candidates":CANDS,"D_SAFE":D_SAFE,
                   "selected":selected,
                   "scope":"supplementary fixed-grid Priority-13 extension; not the Phase-2 closed-loop confirmation"},f,indent=2)

if __name__ == '__main__': main()
